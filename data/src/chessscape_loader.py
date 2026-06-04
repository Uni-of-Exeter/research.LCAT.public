import io
import os
import time
from functools import wraps

import numpy as np
import psycopg2
import psycopg2.extensions
import xarray as xr


def timefn(fn):
    @wraps(fn)
    def measure_time(*args: object, **kwargs: object) -> object:
        t1 = time.time()
        result = fn(*args, **kwargs)
        t2 = time.time()
        print(f"@timefn: {fn.__name__} took {t2 - t1} seconds")
        return result

    return measure_time


class ChessScapeLoader:
    """
    Class to load data from CHESS-SCAPE netcdf files into database. The class determines which data (i.e. bias or
    non-bias corrected) to load from the labelled mask, which must be provided on instantiation. This mask tells this
    class that data for Northern Ireland and the Isles of Scilly is non-bias corrected, whilst data for the rest of
    the UK is.

    The general process for data extraction and loading is as follows:

        1. Initialise class with config and a labelled grid (i.e. a mask with bias and non bias grid cell locations)
        2. Connect to database
        3. Loop through all climate variables, opening up the relevant pair of netcdf files (bias and non bias data)
        4. Open the data with xarray and get decade mean, min and max data, performing transformations if required
        5. For each climate variable, create database table and insert data
        6. Aggregate multiple tables and clean up
    """

    def __init__(
        self: "ChessScapeLoader",
        config: dict,
        mask: np.ndarray,
        ensemble_member: int = 1,
    ) -> None:
        self.conf = config

        # psycopg2 connection and db cursor
        self.conn: psycopg2.extensions.connection | None = None
        self.cur: psycopg2.extensions.cursor | None = None

        self.data_location: str | None = None
        self.mask: np.ndarray | None = None
        self.bias_corrected_keys = []
        self.ensemble_member = ensemble_member

        # currently loaded CHESS-SCAPE file and associated extracted data
        self.current_netcdf_data = {}
        self.extracted_data = {}

        # current parameters
        self.season = None
        self.rcp = None
        self.variable = None
        self.table_name = None
        self.transform_performed = False

        self.set_data_location()
        self.load_mask(mask)

    def set_data_location(self: "ChessScapeLoader", filepath: str | None = None) -> None:
        """
        Set the location of the CHESS-SCAPE netcdf data folder.
        """

        if not filepath:
            filepath = self.conf["chess_scape_netcdf_location"]
            print("CHESS-SCAPE data location retrieved from config file.")

        self.data_location = filepath

    def load_mask(self: "ChessScapeLoader", mask: np.ndarray) -> None:
        """
        Load a given mask, and determine what data will be needed (i.e. bias corrected or non-bias corrected, or both).
        """
        # Reset internal state first
        self.mask = None
        self.bias_corrected_keys = []

        # Reject boolean masks explicitly
        if mask.dtype == bool:
            raise ValueError("Boolean mask not allowed. Please provide labelled mask (0, 1, 2).")

        self.mask = mask

        if 1 in mask:
            self.bias_corrected_keys.append("bias_corrected")

        if 2 in mask:
            self.bias_corrected_keys.append("non_bias_corrected")

    def connect_to_db(
        self: "ChessScapeLoader",
        host: str | None = None,
        dbname: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        """
        Connect to database with provided credentials, or those in config file.
        """

        if not host or not dbname or not user or not password:
            host = self.conf["host"]
            dbname = self.conf["dbname"]
            user = self.conf["user"]
            password = self.conf["user_pass"]

            print("Connecting using db config from config file...")

        self.conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password)
        self.cur = self.conn.cursor()

        print("Connection successful.")

    def open_netcdf_file(self: "ChessScapeLoader", filepath: str) -> xr.Dataset | None:
        """
        Lazy load a netcdf file with xarray and return.
        """

        try:
            return xr.open_dataset(filepath, engine="netcdf4")

        except Exception as e:
            print(f"netcdf file open failed with error: {e}")

    def close_netcdf_files(self: "ChessScapeLoader") -> None:
        """
        Close netcdf files and release any resources associated with them.
        """

        for file in self.current_netcdf_data.values():
            file.close()

    def load_netcdf(
        self: "ChessScapeLoader",
        season: str,
        rcp: int,
        bias_corrected_key: str,
        variable: str,
    ) -> None:
        """
        Given parameters and data required by mask, load the correct netcdf filse, and set some variables.
        Note that folder structure matches raw data in repository.

        Variables can be as follows:
          - season: string - "annual", "winter" or "summer"
          - rcp: int - 60 or 85
          - variable: string - "pr", "rsds", "sfcWind", "tas", "tasmax" or "tasmin"
        """

        # Set variables
        self.season = season
        self.rcp = rcp
        self.variable = variable
        self.table_name = f"chess_scape_rcp{self.rcp}_{self.season}_{self.variable}"
        self.aggregated_table_name = f"chess_scape_rcp{self.rcp}_{self.season}"

        # Clear other variables
        self.transform_performed = False
        # Ensure data means are removed
        self.extracted_data[bias_corrected_key] = {}

        # Create filepath folder adjustments
        bias_corrected_folder = "_bias-corrected" if bias_corrected_key == "bias_corrected" else ""
        ensemble_str = f"{self.ensemble_member:02d}"

        if variable in [
            "tropical_nights",
            "hot_heat_days",
            "heavy_rain_days",
            "dry_days",
            "windy_days",
        ]:
            season_folder = "seasonal" if season != "annual" else "annual"
            sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/{ensemble_str}/{season_folder}"
            filename = f"chess-scape_rcp{rcp}{bias_corrected_folder}_{ensemble_str}_{variable}_uk_1km_{season}_19801201-20801130.nc"
        elif variable in ["tasmax_99_percentile", "tasmin_1_percentile"] and season in [
            "summer",
            "winter",
        ]:
            # New single-season quantile files
            sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/{ensemble_str}/seasonal"
            quantile_num = "99" if "99" in variable else "1"
            base_var = "tasmax" if "tasmax" in variable else "tasmin"
            filename = (
                f"chess-scape_rcp{rcp}{bias_corrected_folder}_{ensemble_str}_"
                f"{base_var}_{quantile_num}_percentile_uk_1km_{season}_19801201-20801130.nc"
            )
        else:
            # Original files
            season_folder = "seasonal" if season != "annual" else "annual"
            sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/{ensemble_str}/{season_folder}"
            filename = f"chess-scape_rcp{rcp}{bias_corrected_folder}_{ensemble_str}_{variable}_uk_1km_{season_folder}_19801201-20801130.nc"

        if self.data_location is None:
            raise RuntimeError("Data location not set. Call set_data_location() first.")
        filepath = os.path.join(self.data_location, sub_folders, filename)

        # Load netcdf file
        if os.path.exists(filepath):
            self.current_netcdf_data[bias_corrected_key] = self.open_netcdf_file(filepath)
        else:
            print(f"File not found: {filepath}")

    def load_all_netcdf(self: "ChessScapeLoader", season: str, rcp: int, variable: str) -> None:
        """
        Load the correct data sets for the current parameters, given the labels in the mask.
        """

        for bias_corrected_key in self.bias_corrected_keys:
            self.load_netcdf(season, rcp, bias_corrected_key, variable)

        print(f"Loaded {len(self.bias_corrected_keys)} netcdf files into xarray.")

    def calculate_mean(
        self: "ChessScapeLoader",
        data: xr.DataArray,
        lower_bound: int,
        higher_bound: int,
        step: int,
    ) -> xr.DataArray:
        """
        Calculate mean values of netcdf file in time dimension.
        """

        # Slice the time dimension only to perform some checks
        time_da = data.time[lower_bound:higher_bound:step]
        time_slice = time_da.to_numpy()

        # Check we always take mean over 10 year slice
        if len(time_slice) != 10:
            raise ValueError("Dataset slice does not contain 10 values.")

        # Check we always only select time points in Jan and Jul in our seasonal time slice
        if self.season != "annual":
            month_check = 1 if self.season == "winter" else 7

            months = time_da.dt.month.to_numpy()
            if not np.all(months == month_check):
                raise ValueError("Different months identified in time slice")

        # Perform the same slicing operation on the data itself
        return data[lower_bound:higher_bound:step].mean(dim="time")

    def _get_dataset_variable_data(self: "ChessScapeLoader", dataset: xr.Dataset, variable: str) -> xr.DataArray | None:
        """
        Select the relevant data variable from a dataset for source and derived variables.
        """
        if variable in dataset.data_vars:
            return dataset[variable]

        if variable == "tasmax_99_percentile" and "quantile_99" in dataset.data_vars:
            return dataset["quantile_99"]

        if variable == "tasmin_1_percentile" and "quantile_1" in dataset.data_vars:
            return dataset["quantile_1"]

        if variable in [
            "tropical_nights",
            "hot_heat_days",
            "heavy_rain_days",
            "dry_days",
            "windy_days",
        ]:
            if "variable" in dataset.data_vars:
                return dataset["variable"]

            for var_name in dataset.data_vars:
                var_name_lower = str(var_name).lower()
                if any(token in var_name_lower for token in ["tropical", "hot", "rain", "dry", "windy"]):
                    return dataset[var_name]

        for var_name in dataset.data_vars:
            if "quantile" in str(var_name).lower():
                return dataset[var_name]

        return None

    def _normalise_decade_coord(self: "ChessScapeLoader", decade_coord: int) -> int | None:
        """
        Convert decade coordinate values into decade years.
        """
        if decade_coord >= 1900:
            return decade_coord

        if 0 <= decade_coord <= 20:
            return 1980 + decade_coord * 10

        return None

    def process_decade(self: "ChessScapeLoader", data: xr.DataArray) -> dict[int, xr.DataArray]:
        """
        Process NetCDF files by decade. Mins, means, and maxes are taken across decades.
        We perform this operation manually, rather than using xarray.resample.
        This means that our decades might by off by 1 year (1981 to 1991), but we can use
        the same approach for the seasonal dataset (which is more strongly binned into
        3 month seasons). More details are as follows (with the mean given as an example)

          * Annual file time dim is 100, with 1 data point per year.
            Means are averaging every 10 years, i.e. 10 chunks of 10 points.
            Slice for first decade would be dataset[0:10:1]
          * Seasonal file time dim is 400, with 4 data points per year.
            Means are averaging every season present in 10 years, i.e. every 4th value in 40 points.
            Slice for first decade would be dataset[0:40:4]

        Note that seasonal data contains readings for winter, spring, summer, and autumn, starting at
        indexes 0, 1, 2, 3 respectively.
        """

        # Set slice period and step. Seasonal: 1 decade is 40 data points. Annual: 1 decade is 10 data points
        period = 10 if self.season == "annual" else 40
        step = int(period / 10)

        # Set range start. Annual and winter start at 0. Summer starts at 2
        start = 2 if self.season == "summer" else 0

        # Get total years from the dataset
        stop = len(data.time)

        # Create all data values
        data_by_decade = {}

        # Get lower and higher slice bounds
        for lower_bound in range(start, stop, period):
            higher_bound = int(lower_bound + period)
            decade_tag = 1980 + int(lower_bound / step)

            # Get extracted data dict containing mean and key by decade
            data_by_decade[decade_tag] = self.calculate_mean(data, lower_bound, higher_bound, step)

        return data_by_decade

    def _extract_decades(self: "ChessScapeLoader", data: xr.DataArray) -> dict[int, xr.DataArray]:
        """
        Extract decade-keyed data from either decade- or time-indexed arrays.
        """
        if "decade" in data.dims:
            decade_dict = {}
            for decade_coord in data.decade.to_numpy():
                decade_year = self._normalise_decade_coord(int(decade_coord))
                if decade_year is None:
                    print(f"Unknown decade coordinate: {decade_coord}")
                    continue
                decade_dict[decade_year] = data.sel(decade=decade_coord)
            return decade_dict

        if "time" in data.dims:
            return self.process_decade(data)

        raise ValueError("DataArray must contain either 'decade' or 'time' dimension.")

    def process_bias_keys(self: "ChessScapeLoader") -> None:
        """
        Extract data for each decade in bias and non bias corrected cases.
        """
        self.extracted_data = {}

        for bias_corrected_key in self.bias_corrected_keys:
            if bias_corrected_key not in self.current_netcdf_data:
                print(f"### WARNING: No data loaded for bias key: {bias_corrected_key}")
                continue

            dataset = self.current_netcdf_data[bias_corrected_key]
            if dataset is None:
                print(f"### WARNING: Dataset is None for bias key: {bias_corrected_key}")
                continue

            if self.variable is None:
                print("### WARNING: Current variable is not set.")
                continue

            target_data = self._get_dataset_variable_data(dataset, self.variable)
            if target_data is None:
                print(f"### WARNING: Could not find data for variable '{self.variable}' in {bias_corrected_key}.")
                print(f"Available variables: {list(dataset.data_vars.keys())}")
                continue

            self.extracted_data[bias_corrected_key] = self._extract_decades(target_data)

    def transform_dataset(self: "ChessScapeLoader", data: xr.DataArray) -> xr.DataArray:
        """
        Perform any transformations necessary on a dataset.
        """

        # Convert from kelvin to celsius
        kelvin_to_celsius_vars = ["tas", "tasmin", "tasmax"]

        if self.variable in kelvin_to_celsius_vars:
            data -= 273.15

        # Convert from kg/m2/s to mm/day
        elif self.variable == "pr":
            data *= 86400

        return data

    def transform_all_means(self: "ChessScapeLoader") -> None:
        """
        Perform transformations on data values away from SI units, where required.
        """

        if self.transform_performed:
            raise ValueError("Transforms already performed on values.")

        for data_by_decade in self.extracted_data.values():
            for value in data_by_decade.values():
                self.transform_dataset(value)

        # Flag that transforms have been performed
        self.transform_performed = True

    def create_table(self: "ChessScapeLoader") -> None:
        """
        Create table if it does not already exist.
        """

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{self.table_name}" (
            grid_cell_id INTEGER PRIMARY KEY
        );
        """

        try:
            self.cur.execute(create_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error creating CHESS-SCAPE table: {e}")

    def drop_table(self: "ChessScapeLoader", table_name: str | None = None) -> None:
        """
        Drop the table associated with the current variables if it exists.
        """

        if not table_name:
            table_name = self.table_name

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping CHESS-SCAPE table: {e}")

    def add_multiple_columns(self: "ChessScapeLoader", column_names: list[str]) -> None:
        """
        Given a list of columns, add these to the database if they do not already exist.
        """

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        for column_name in column_names:
            alter_table_query = f'ALTER TABLE "{self.table_name}" ADD COLUMN IF NOT EXISTS "{column_name}" FLOAT'
            self.cur.execute(alter_table_query)

        self.conn.commit()

    def insert_data_multiple_decades(self: "ChessScapeLoader") -> None:
        """
        Bulk insert multiple columns of data (i.e. all decades for a variable). Note that this loads bias corrected
        and non-bias corrected into the same table (deliberately).
        """

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        assert self.mask is not None, "Mask not loaded. Call load_mask() first."
        assert self.table_name is not None, "Table name not set. Call load_netcdf() first."
        # Build a shared ordered decade list across available bias keys.
        # Derived files can sometimes have different decade coverage between
        # bias and non-bias datasets, so rows must still include all columns.
        available_decades = sorted({decade for decade_map in self.extracted_data.values() for decade in decade_map})

        if not available_decades:
            print("### WARNING: No data extracted for this variable.")
            return

        new_column_names = [f"{self.variable}_{decade}" for decade in available_decades]

        self.add_multiple_columns(new_column_names)

        # Create string buffer
        output = io.StringIO()

        # Loop through mask cells. If 0, skip. If 1, choose bias corrected data. If 2, choose non bias corrected data
        for i, j in np.ndindex(self.mask.shape):
            # If mask cell has value of 0, skip
            if self.mask[i, j] == 0:
                continue

            # If mask cell is 1, get bias corrected data
            if self.mask[i, j] == 1:
                bias_corrected_key = "bias_corrected"

            # If mask cell is 2, get non-bias corrected data
            elif self.mask[i, j] == 2:
                bias_corrected_key = "non_bias_corrected"

            # Skip any unexpected mask values.
            else:
                continue

            decade_map = self.extracted_data.get(bias_corrected_key, {})

            # Emit one value per shared decade column, filling gaps as NaN.
            climate_data = []
            for decade_key in available_decades:
                if decade_key in decade_map:
                    climate_data.append(decade_map[decade_key].to_numpy()[i, j])
                else:
                    climate_data.append(np.nan)
            # Get grid cell ID
            grid_cell_id = i * self.mask.shape[1] + j

            # Store data row in buffer
            row = [grid_cell_id, *climate_data]
            output.write(",".join(map(str, row)) + "\n")

        # Move cursor to start
        output.seek(0)

        column_names = ["grid_cell_id", *new_column_names]
        self.cur.copy_from(output, self.table_name, sep=",", columns=column_names)

        self.conn.commit()
        output.close()

    def join_tables(self: "ChessScapeLoader", variables: list[str]) -> None:
        """
        Given multiple tables for variables, create a single table with a JOIN, and clean up afterwards.
        """

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        self.drop_table(self.aggregated_table_name)

        base_table = f"{self.aggregated_table_name}_{variables[0]}"
        table_name_joins = [f'JOIN "{self.aggregated_table_name}_{var}" USING (grid_cell_id)' for var in variables[1:]]
        joins_string = " ".join(table_name_joins)

        join_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{self.aggregated_table_name}" AS
        SELECT *
        FROM {base_table}
        {joins_string}
        ORDER BY (grid_cell_id);
        """

        self.cur.execute(join_table_query)
        self.conn.commit()

        # Drop temporary variable tables
        for temp_table in [f"{self.aggregated_table_name}_{var}" for var in variables]:
            self.drop_table(temp_table)

    def process_all_variables(self: "ChessScapeLoader", season: str, rcp: int) -> None:
        """
        Create a table of data for a single variable, containing an ID column and decade columns.
        """

        # Base variables always available
        source_variables = ["pr", "rsds", "sfcWind", "tas", "tasmax", "tasmin"]

        # Derived variables - check availability for each season
        derived_variables = []
        potential_derived = [
            "tasmax_99_percentile",
            "tasmin_1_percentile",
            "tropical_nights",
            "hot_heat_days",
            "heavy_rain_days",
            "dry_days",
            "windy_days",
        ]

        for var in potential_derived:
            # Check file existence
            bias_corrected_folder = "_bias-corrected" if "bias_corrected" in self.bias_corrected_keys else ""

            ensemble_str = f"{self.ensemble_member:02d}"

            if var in [
                "tropical_nights",
                "hot_heat_days",
                "heavy_rain_days",
                "dry_days",
                "windy_days",
            ]:
                season_folder = "seasonal" if season != "annual" else "annual"
                sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/{ensemble_str}/{season_folder}"
                filename = f"chess-scape_rcp{rcp}{bias_corrected_folder}_{ensemble_str}_{var}_uk_1km_{season}_19801201-20801130.nc"
            elif season in ["summer", "winter"]:
                sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/{ensemble_str}/seasonal"
                quantile_num = "99" if "99" in var else "1"
                base_var = "tasmax" if "tasmax" in var else "tasmin"
                filename = (
                    f"chess-scape_rcp{rcp}{bias_corrected_folder}_{ensemble_str}_{base_var}_"
                    f"{quantile_num}_percentile_uk_1km_{season}_19801201-20801130.nc"
                )
            elif season == "annual":
                # Annual quantiles are in annual folder
                sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/{ensemble_str}/annual"
                quantile_num = "99" if "99" in var else "1"
                base_var = "tasmax" if "tasmax" in var else "tasmin"
                filename = (
                    f"chess-scape_rcp{rcp}{bias_corrected_folder}_{ensemble_str}_"
                    f"{base_var}_{quantile_num}_percentile_uk_1km_annual_19801201-20801130.nc"
                )
            else:
                continue

            if self.data_location is None:
                raise RuntimeError("Data location not set. Call set_data_location() first.")

            filepath = os.path.join(self.data_location, sub_folders, filename)

            if os.path.exists(filepath):
                derived_variables.append(var)
            else:
                print(f"Derived variable file not found: {filename}")

        variables = source_variables + derived_variables

        for variable in variables:
            self.load_all_netcdf(season, rcp, variable)
            self.process_bias_keys()

            if variable in source_variables:
                self.transform_all_means()

            self.drop_table()
            self.create_table()
            self.insert_data_multiple_decades()
            self.close_netcdf_files()

        self.join_tables(variables)

    def process_all_seasons(self: "ChessScapeLoader", rcp: int) -> None:
        """
        Process all variables for all seasons.
        """

        seasons = ["annual", "winter", "summer"]

        for season in seasons:
            self.process_all_variables(season, rcp)

    @timefn
    def process_all_rcps(self: "ChessScapeLoader") -> None:
        """
        Process all seasons and variables for all RCPs.
        """

        rcps = [60, 85]

        for rcp in rcps:
            self.process_all_seasons(rcp)
