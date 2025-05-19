import io
import os
import time
from functools import wraps

import numpy as np
import psycopg2
import xarray as xr


def timefn(fn):
    @wraps(fn)
    def measure_time(*args, **kwargs):
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

    def __init__(self, config, mask):
        self.conf = config

        # psycopg2 connection and db cursor
        self.conn = None
        self.cur = None

        self.data_location = None
        self.mask = None
        self.bias_corrected_keys = []

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

    def set_data_location(self, filepath=None):
        """
        Set the location of the CHESS-SCAPE netcdf data folder.
        """

        if not filepath:
            filepath = self.conf["chess_scape_netcdf_location"]
            print("CHESS-SCAPE data location retrieved from config file.")

        self.data_location = filepath

    def load_mask(self, mask):
        """
        Load a given mask, and determine what data will be needed (i.e. bias corrected or non-bias corrected, or both).
        """

        if 0 not in mask:
            raise ValueError("Have you loaded a boolean mask? Please load labelled mask instead.")

        self.mask = mask

        if 1 in mask:
            self.bias_corrected_keys.append("bias_corrected")

        if 2 in mask:
            self.bias_corrected_keys.append("non_bias_corrected")

    def connect_to_db(self, host=None, dbname=None, user=None, password=None):
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

    def open_netcdf_file(self, filepath):
        """
        Lazy load a netcdf file with xarray and return.
        """

        try:
            return xr.open_dataset(filepath, engine="netcdf4")

        except Exception as e:
            print(f"netcdf file open failed with error: {e}")

    def close_netcdf_files(self):
        """
        Close netcdf files and release any resources associated with them.
        """

        for file in self.current_netcdf_data.values():
            file.close()

    def load_netcdf(self, season, rcp, bias_corrected_key, variable):
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
        season_folder = "seasonal" if season != "annual" else "annual"

        # Create filepath
        sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/01/{season_folder}"
        filename = (
            f"chess-scape_rcp{rcp}{bias_corrected_folder}_01_{variable}_uk_1km_{season_folder}_19801201-20801130.nc"
        )
        filepath = os.path.join(self.data_location, sub_folders, filename)

        # Load netcdf file
        if os.path.exists(filepath):
            self.current_netcdf_data[bias_corrected_key] = self.open_netcdf_file(filepath)

        else:
            print(f"Incorrect filepath: {filepath}")

    def load_all_netcdf(self, season, rcp, variable):
        """
        Load the correct data sets for the current parameters, given the labels in the mask.
        """

        for bias_corrected_key in self.bias_corrected_keys:
            self.load_netcdf(season, rcp, bias_corrected_key, variable)

        print(f"Loaded {len(self.bias_corrected_keys)} netcdf files into xarray.")

    def calculate_min_mean_max(self, data, lower_bound, higher_bound, step):
        """
        Calculate min, mean, and max values of netcdf file in time dimension, with upper and lower bounds.
        """

        # Slice the time dimension only to perform some checks
        time_slice = data.time[lower_bound:higher_bound:step].values

        # Check we always take mean, min and max over 10 year slice
        if len(time_slice) != 10:
            raise ValueError("Dataset slice does not contain 10 values.")

        # Check we always only select time points in Jan and Jul in our seasonal time slice
        if self.season != "annual":
            month_check = 1 if self.season == "winter" else 7

            if not np.all(np.array([date.month for date in time_slice]) == month_check):
                raise ValueError("Different months identified in time slice")

        # Perform the same slicing operation on the data itself
        data_slice = data[self.variable][lower_bound:higher_bound:step]

        return {
            "min": data_slice.min(dim="time"),
            "mean": data_slice.mean(dim="time"),
            "max": data_slice.max(dim="time"),
        }

    def process_decade(self, data):
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

            # Get extracted data dict containing min, mean and max and key by decade
            data_by_decade[decade_tag] = self.calculate_min_mean_max(data, lower_bound, higher_bound, step)

        return data_by_decade

    def process_bias_keys(self):
        """
        Extract data for each decade in bias and non bias corrected cases.
        """

        for bias_corrected_key in self.bias_corrected_keys:
            self.extracted_data[bias_corrected_key] = self.process_decade(self.current_netcdf_data[bias_corrected_key])

    def transform_dataset(self, data):
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

    def transform_all_means(self):
        """
        Perform transformations on data values away from SI units, where required.
        """

        if self.transform_performed:
            raise ValueError("Transforms already performed on values.")

        for bias_key, data_by_decade in self.extracted_data.items():
            for decade, min_mean_max_dict in data_by_decade.items():
                for key, value in min_mean_max_dict.items():
                    self.transform_dataset(value)

        # Flag that transforms have been performed
        self.transform_performed = True

    def create_table(self):
        """
        Create table if it does not already exist.
        """

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

    def drop_table(self, table_name=None):
        """
        Drop the table associated with the current variables if it exists.
        """

        if not table_name:
            table_name = self.table_name

        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping CHESS-SCAPE table: {e}")

    def add_multiple_columns(self, column_names):
        """
        Given a list of columns, add these to the database if they do not already exist.
        """

        for column_name in column_names:
            alter_table_query = f'ALTER TABLE "{self.table_name}" ADD COLUMN IF NOT EXISTS "{column_name}" FLOAT'
            self.cur.execute(alter_table_query)

        self.conn.commit()

    def insert_data_multiple_decades(self):
        """
        Bulk insert multiple columns of data (i.e. all decades for a variable). Note that this loads bias corrected
        and non-bias corrected into the same table (deliberately).
        """

        # Get a bias key
        bias_key = self.bias_corrected_keys[0]

        new_column_names = []
        for decade, min_mean_max_dict in self.extracted_data[bias_key].items():
            for key in min_mean_max_dict:
                if key not in ["min", "mean", "max"]:
                    raise ValueError("Column names incorrect")

                new_column_name = f"{self.variable}_{decade}_{key}"
                new_column_names.append(new_column_name)

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

            # Get correct climate data row with key
            climate_data = [
                self.extracted_data[bias_corrected_key][decade_key][key].values[i, j]
                for decade_key in self.extracted_data[bias_corrected_key]
                for key in ["min", "mean", "max"]
            ]

            # Get grid cell ID
            grid_cell_id = i * self.mask.shape[1] + j

            # Store data row in buffer
            row = [grid_cell_id] + climate_data
            output.write(",".join(map(str, row)) + "\n")

        # Move cursor to start
        output.seek(0)

        column_names = ["grid_cell_id"] + new_column_names
        self.cur.copy_from(output, self.table_name, sep=",", columns=column_names)

        self.conn.commit()
        output.close()

    def join_tables(self, variables):
        """
        Given multiple tables for variables, create a single table with a JOIN, and clean up afterwards.
        """

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

    def process_all_variables(self, season, rcp):
        """
        Create a table of data for a single variable, containing an ID column and 10 decade averaged columns.
        """

        variables = ["pr", "rsds", "sfcWind", "tas", "tasmax", "tasmin"]

        print("############################")
        print(f"### Data to be processed: {self.bias_corrected_keys}")
        print(f"### Processing all variables for dataset: {season}, rcp{rcp}.\n")

        for variable in variables:
            print(f"### Processing variable: {variable}")

            self.load_all_netcdf(season, rcp, variable)
            self.process_bias_keys()
            self.transform_all_means()
            self.drop_table()
            self.create_table()
            self.insert_data_multiple_decades()
            self.close_netcdf_files()

            print(f"### Processing complete: {variable}\n")

        self.join_tables(variables)

        print(f"### Processing complete for dataset: {season}, rcp{rcp}.")
        print("############################\n")

    def process_all_seasons(self, rcp):
        """
        Process all variables for all seasons.
        """

        seasons = ["annual", "winter", "summer"]

        for season in seasons:
            self.process_all_variables(season, rcp)

    @timefn
    def process_all_rcps(self):
        """
        Process all seasons and variables for all RCPs.
        """

        rcps = [60, 85]

        for rcp in rcps:
            self.process_all_seasons(rcp)
