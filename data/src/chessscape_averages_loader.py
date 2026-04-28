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


class ChessScapeAveragesLoader:
    """
    Class to create an averages table for the CHESS-SCAPE data. We will create decade slices as before,
    and then find UK averages/mean values across all cells. We need to do this for bias and
    non-bias corrected data separately, meaning we do not need to use the labelled masks as before.

    There is a lot of overlap with the ChessScapeLoader class. However, it was much easier to create a
    separate class to create the averages table than integrate into the existing code. This adds a huge
    inefficiency to the database build, as we are opening, reading and closing NetCDF files for all variables
    twice, once in the original class, and once in this class. TODO: aggregate these classes.
    """

    def __init__(self: "ChessScapeAveragesLoader", config: dict) -> None:
        self.conf = config
        self.conn: psycopg2.extensions.connection | None = None
        self.cur: psycopg2.extensions.cursor | None = None

        self.data_location = None

        self.current_netcdf_data = None
        self.extracted_data = {}

        self.season = None
        self.rcp = None
        self.variable = None
        self.is_bias_corrected = None

        self.table_name = "chess_scape_uk_averages"
        self.row_id = 0

        self.transform_performed = False
        self.set_data_location()

    def set_data_location(
        self: "ChessScapeAveragesLoader", filepath: str | None = None
    ) -> None:
        """
        Set the location of the CHESS-SCAPE netcdf data folder.
        """

        if not filepath:
            filepath = self.conf["chess_scape_netcdf_location"]
            print("CHESS-SCAPE data location retrieved from config file.")

        self.data_location = filepath

    def connect_to_db(
        self: "ChessScapeAveragesLoader",
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

    def open_netcdf_file(
        self: "ChessScapeAveragesLoader", filepath: str
    ) -> xr.Dataset | None:
        """
        Lazy load a netcdf file with xarray and return.
        """

        try:
            return xr.open_dataset(filepath, engine="netcdf4")

        except Exception as e:
            print(f"netcdf file open failed with error: {e}")

    def close_netcdf_file(self: "ChessScapeAveragesLoader") -> None:
        """
        Close netcdf file and release any resources associated with it.
        """
        if self.current_netcdf_data is not None:
            self.current_netcdf_data.close()
            self.current_netcdf_data = None

    def load_netcdf(
        self: "ChessScapeAveragesLoader",
        is_bias_corrected: bool,
        season: str,
        rcp: int,
        variable: str,
    ) -> None:
        """
        Given parameters and data required, load the correct netcdf file, and set some variables.
        Note that folder structure matches raw data in repository.

        Variables can be as follows:
          - is_bias_corrected = True or False
          - season: string - "annual", "winter" or "summer"
          - rcp: int - 60 or 85
          - variable: string - "pr", "rsds", "sfcWind", "tas", "tasmax" or "tasmin"
        """

        # Set variables
        self.season = season
        self.rcp = rcp
        self.variable = variable
        self.is_bias_corrected = is_bias_corrected

        # Clear other variables
        self.transform_performed = False
        # Ensure extracted data is cleared
        self.extracted_data = {}

        filepath = self.get_netcdf_filepath(is_bias_corrected, season, rcp, variable)

        # Load netcdf file
        if os.path.exists(filepath):
            self.current_netcdf_data = self.open_netcdf_file(filepath)

        else:
            print(f"Incorrect filepath: {filepath}")
            self.current_netcdf_data = None

    def get_netcdf_filepath(
        self: "ChessScapeAveragesLoader",
        is_bias_corrected: bool,
        season: str,
        rcp: int,
        variable: str,
    ) -> str:
        """
        Build filepath for source and derived files.
        """
        if not self.data_location:
            raise ValueError("Data location is not set")

        bias_corrected_folder = "_bias-corrected" if is_bias_corrected else ""
        season_folder = "seasonal" if season != "annual" else "annual"

        sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/01/{season_folder}"

        if variable in [
            "tropical_nights",
            "hot_heat_days",
            "heavy_rain_days",
            "dry_days",
            "windy_days",
        ]:
            filename = f"chess-scape_rcp{rcp}{bias_corrected_folder}_01_{variable}_uk_1km_{season}_19801201-20801130.nc"
        elif variable == "tasmax_99_percentile":
            filename = (
                f"chess-scape_rcp{rcp}{bias_corrected_folder}_01_tasmax_99_percentile"
                f"_uk_1km_{season}_19801201-20801130.nc"
            )
        elif variable == "tasmin_1_percentile":
            filename = (
                f"chess-scape_rcp{rcp}{bias_corrected_folder}_01_tasmin_1_percentile"
                f"_uk_1km_{season}_19801201-20801130.nc"
            )
        else:
            filename = (
                f"chess-scape_rcp{rcp}{bias_corrected_folder}_01_{variable}"
                f"_uk_1km_{season_folder}_19801201-20801130.nc"
            )

        return os.path.join(self.data_location, sub_folders, filename)

    def _normalise_decade_coord(
        self: "ChessScapeAveragesLoader", decade_coord: int
    ) -> int | None:
        """
        Convert decade coordinate values into decade years.
        """
        decade_coord = int(decade_coord)

        if decade_coord >= 1900:
            return decade_coord

        if 0 <= decade_coord <= 20:
            return 1980 + decade_coord * 10

        return None

    def _get_dataset_variable_data(
        self: "ChessScapeAveragesLoader", dataset: xr.Dataset, variable: str
    ) -> xr.DataArray | None:
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
                if any(
                    token in var_name_lower
                    for token in ["tropical", "hot", "rain", "dry", "windy"]
                ):
                    return dataset[var_name]

        for var_name in dataset.data_vars:
            if "quantile" in str(var_name).lower():
                return dataset[var_name]

        return None

    def calculate_uk_averages_mean(
        self: "ChessScapeAveragesLoader",
        data: xr.DataArray,
        lower_bound: int,
        higher_bound: int,
        step: int,
    ) -> xr.DataArray:
        """
        Calculate mean values of netcdf file in time dimension, and then in spatial dimensions (i, j).
        """

        # Slice the time dimension only to perform some checks
        time_slice = data.time[lower_bound:higher_bound:step].to_numpy()

        # Check we always take mean over 10 years
        if len(time_slice) != 10:
            raise ValueError("Dataset slice does not contain 10 values.")

        # Check we always only select time points in Jan and Jul in our time slice
        if self.season != "annual":
            month_check = 1 if self.season == "winter" else 7

            if not np.all(np.array([date.month for date in time_slice]) == month_check):
                raise ValueError("Different months identified in time slice")

        # Perform the same slicing operation on the data itself
        return data[lower_bound:higher_bound:step].mean(dim="time").mean()

    def process_decade(self: "ChessScapeAveragesLoader", data: xr.Dataset) -> None:
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

        data_array = self._get_dataset_variable_data(data, self.variable or "")
        if data_array is None:
            raise ValueError(f"Could not find data variable for '{self.variable}'")

        # Derived outputs already contain decade coordinates.
        if "decade" in data_array.dims:
            data_by_decade = {}
            for decade_coord in data_array.decade.to_numpy():
                decade_tag = self._normalise_decade_coord(decade_coord)
                if decade_tag is None:
                    print(f"Skipping unrecognized decade coordinate: {decade_coord}")
                    continue

                decade_slice = data_array.sel(decade=decade_coord)
                data_by_decade[decade_tag] = decade_slice.mean()

            self.extracted_data = dict(sorted(data_by_decade.items()))
            return

        # Set slice period and step. Seasonal: 1 decade is 40 data points. Annual: 1 decade is 10 data points
        period = 10 if self.season == "annual" else 40
        step = int(period / 10)

        # Set range start. Annual and winter start at 0. Summer starts at 2
        start = 2 if self.season == "summer" else 0

        # Get total years from the dataset
        stop = len(data_array.time)

        # Create all data values
        data_by_decade = {}

        # Get lower and higher slice bounds
        for lower_bound in range(start, stop, period):
            higher_bound = int(lower_bound + period)
            decade_tag = 1980 + int(lower_bound / step)

            # Get extracted data dict containing mean and key by decade
            data_by_decade[decade_tag] = self.calculate_uk_averages_mean(
                data_array, lower_bound, higher_bound, step
            )

        self.extracted_data = data_by_decade

    def transform_dataset(
        self: "ChessScapeAveragesLoader", data: xr.DataArray
    ) -> xr.DataArray:
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

    def transform_data(self: "ChessScapeAveragesLoader") -> None:
        """
        Perform transformations on data values away from SI units, where required.
        """

        if self.transform_performed:
            raise ValueError("Transforms already performed on values.")

        for data_by_decade in self.extracted_data.values():
            self.transform_dataset(data_by_decade)

        # Flag that transforms have been performed
        self.transform_performed = True

    def create_table(self: "ChessScapeAveragesLoader") -> None:
        """
        Create table if it does not already exist.
        """

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{self.table_name}" (
            row_id INTEGER PRIMARY KEY,
            is_bias_corrected BOOLEAN,
            rcp VARCHAR(10),
            season VARCHAR(10),
            variable VARCHAR(64),
            decade INTEGER,
            mean FLOAT
        );
        """

        try:
            self.cur.execute(create_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error creating CHESS-SCAPE table: {e}")

    def drop_table(self: "ChessScapeAveragesLoader") -> None:
        """
        Drop the table associated with the current variables if it exists.
        """

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{self.table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping CHESS-SCAPE table: {e}")

    def insert_data_multiple_decades(self: "ChessScapeAveragesLoader") -> None:
        """
        Create rows from the extracted averages data, and insert into the database with a stringIO buffer.
        """

        assert self.cur is not None, "Not connected. Call connect_to_db() first."
        assert self.conn is not None, "Not connected. Call connect_to_db() first."
        output = io.StringIO()

        try:
            for decade, data_array in self.extracted_data.items():
                # Prepare row and convert to string format
                row = [
                    self.row_id,
                    self.is_bias_corrected,
                    f"rcp{self.rcp}",
                    self.season,
                    self.variable,
                    decade,
                    data_array.to_numpy(),
                ]
                output.write(",".join(map(str, row)) + "\n")

                # Increment row_id for the next row
                self.row_id += 1

            # Move cursor to start of buffer
            output.seek(0)

            column_names = [
                "row_id",
                "is_bias_corrected",
                "rcp",
                "season",
                "variable",
                "decade",
                "mean",
            ]

            self.cur.copy_from(output, self.table_name, sep=",", columns=column_names)
            self.conn.commit()

        except Exception as e:
            print(f"Database insert failed: {e}")

            # Rollback if fail
            self.conn.rollback()

        finally:
            output.close()

    def process_all_variables(
        self: "ChessScapeAveragesLoader", season: str, rcp: int, is_bias_corrected: bool
    ) -> None:
        """
        Create a table of data for a single variable, containing an ID column and 10 decade averaged columns.
        """

        source_variables = ["pr", "rsds", "sfcWind", "tas", "tasmax", "tasmin"]
        potential_derived = [
            "tasmax_99_percentile",
            "tasmin_1_percentile",
            "tropical_nights",
            "hot_heat_days",
            "heavy_rain_days",
            "dry_days",
            "windy_days",
        ]

        derived_variables = []
        for variable in potential_derived:
            filepath = self.get_netcdf_filepath(
                is_bias_corrected, season, rcp, variable
            )
            if os.path.exists(filepath):
                derived_variables.append(variable)
            else:
                print(
                    f"Derived variable file not found, skipping: {os.path.basename(filepath)}"
                )

        variables = source_variables + derived_variables

        print("############################")
        print(f"### Processing all variables for dataset: bias_corrected: {is_bias_corrected}, {season}, rcp{rcp}.\n")

        for variable in variables:
            print(f"### Processing variable: {variable}")

            self.load_netcdf(is_bias_corrected, season, rcp, variable)
            if self.current_netcdf_data is None:
                print(f"### Skipping variable (failed to load): {variable}\n")
                continue

            self.process_decade(self.current_netcdf_data)
            self.transform_data()
            self.insert_data_multiple_decades()
            self.close_netcdf_file()

            print(f"### Processing complete: {variable}\n")

        print(f"### Processing complete for dataset: bias_corrected: {is_bias_corrected}, {season}, rcp{rcp}.")
        print("############################\n")

    def process_all_seasons(
        self: "ChessScapeAveragesLoader", rcp: int, is_bias_corrected: bool
    ) -> None:
        """
        Process all variables for all seasons.
        """

        seasons = ["annual", "winter", "summer"]

        for season in seasons:
            self.process_all_variables(season, rcp, is_bias_corrected)

    def process_all_rcps(
        self: "ChessScapeAveragesLoader", is_bias_corrected: bool
    ) -> None:
        """
        Process all seasons and variables for all RCPs.
        """

        rcps = [60, 85]

        for rcp in rcps:
            self.process_all_seasons(rcp, is_bias_corrected)

    @timefn
    def process_all_data(self: "ChessScapeAveragesLoader") -> None:
        """
        Process all bias and non bias corrected averages data.
        """

        self.drop_table()
        self.create_table()

        for is_bias_corrected in [True, False]:
            self.process_all_rcps(is_bias_corrected)
