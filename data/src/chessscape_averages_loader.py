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

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None

        self.data_location = None

        self.current_netcdf_data = {}
        self.extracted_data = {}

        self.season = None
        self.rcp = None
        self.variable = None
        self.is_bias_corrected = None

        self.table_name = "chess_scape_uk_averages"
        self.row_id = 0

        self.transform_performed = False
        self.set_data_location()

    def set_data_location(self, filepath=None):
        """
        Set the location of the CHESS-SCAPE netcdf data folder.
        """

        if not filepath:
            filepath = self.conf["chess_scape_netcdf_location"]
            print("CHESS-SCAPE data location retrieved from config file.")

        self.data_location = filepath

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

    def close_netcdf_file(self):
        """
        Close netcdf file and release any resources associated with it.
        """

        self.current_netcdf_data.close()

    def load_netcdf(self, is_bias_corrected, season, rcp, variable):
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

        # Create filepath folder adjustments
        bias_corrected_folder = "_bias-corrected" if is_bias_corrected else ""
        season_folder = "seasonal" if season != "annual" else "annual"

        # Create filepath
        sub_folders = f"data/rcp{rcp}{bias_corrected_folder}/01/{season_folder}"
        filename = (
            f"chess-scape_rcp{rcp}{bias_corrected_folder}_01_{variable}_uk_1km_{season_folder}_19801201-20801130.nc"
        )
        filepath = os.path.join(self.data_location, sub_folders, filename)

        # Load netcdf file
        if os.path.exists(filepath):
            self.current_netcdf_data = self.open_netcdf_file(filepath)

        else:
            print(f"Incorrect filepath: {filepath}")

    def calculate_uk_averages_min_mean_max(self, data, lower_bound, higher_bound, step):
        """
        Calculate min, mean, and max values of netcdf file in time dimension, and then in spatial dimensions (i, j).
        """

        # Slice the time dimension only to perform some checks
        time_slice = data.time[lower_bound:higher_bound:step].values

        # Check we always take mean over 10 years
        if len(time_slice) != 10:
            raise ValueError("Dataset slice does not contain 10 values.")

        # Check we always only select time points in Jan and Jul in our time slice
        if self.season != "annual":
            month_check = 1 if self.season == "winter" else 7

            if not np.all(np.array([date.month for date in time_slice]) == month_check):
                raise ValueError("Different months identified in time slice")

        # Perform the same slicing operation on the data itself
        data_slice = data[self.variable][lower_bound:higher_bound:step]

        # Return dict of three scalar values
        return {
            "min": data_slice.min(dim="time").min(),
            "mean": data_slice.mean(dim="time").mean(),
            "max": data_slice.max(dim="time").max(),
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
            data_by_decade[decade_tag] = self.calculate_uk_averages_min_mean_max(data, lower_bound, higher_bound, step)

        self.extracted_data = data_by_decade

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

    def transform_data(self):
        """
        Perform transformations on data values away from SI units, where required.
        """

        if self.transform_performed:
            raise ValueError("Transforms already performed on values.")

        for decade, min_mean_max_dict in self.extracted_data.items():
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
            row_id INTEGER PRIMARY KEY,
            is_bias_corrected BOOLEAN,
            rcp VARCHAR(10),
            season VARCHAR(10),
            variable VARCHAR(10),
            decade INTEGER,
            min FLOAT,
            mean FLOAT,
            max FLOAT
        );
        """

        try:
            self.cur.execute(create_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error creating CHESS-SCAPE table: {e}")

    def drop_table(self):
        """
        Drop the table associated with the current variables if it exists.
        """

        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{self.table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping CHESS-SCAPE table: {e}")

    def insert_data_multiple_decades(self):
        """
        Create rows from the extracted averages data, and insert into the database with a stringIO buffer.
        """

        output = io.StringIO()

        try:
            for decade, min_mean_max_dict in self.extracted_data.items():
                min_val = min_mean_max_dict["min"].values
                mean_val = min_mean_max_dict["mean"].values
                max_val = min_mean_max_dict["max"].values

                # Prepare row and convert to string format
                row = [
                    self.row_id,
                    self.is_bias_corrected,
                    f"rcp{self.rcp}",
                    self.season,
                    self.variable,
                    decade,
                    min_val,
                    mean_val,
                    max_val,
                ]
                output.write(",".join(map(str, row)) + "\n")

                # Increment row_id for the next row
                self.row_id += 1

            # Move cursor to start of buffer
            output.seek(0)

            column_names = ["row_id", "is_bias_corrected", "rcp", "season", "variable", "decade", "min", "mean", "max"]

            self.cur.copy_from(output, self.table_name, sep=",", columns=column_names)
            self.conn.commit()

        except Exception as e:
            print(f"Database insert failed: {e}")

            # Rollback if fail
            self.conn.rollback()

        finally:
            output.close()

    def process_all_variables(self, season, rcp, is_bias_corrected):
        """
        Create a table of data for a single variable, containing an ID column and 10 decade averaged columns.
        """

        variables = ["pr", "rsds", "sfcWind", "tas", "tasmax", "tasmin"]

        print("############################")
        print(f"### Processing all variables for dataset: bias_corrected: {is_bias_corrected}, {season}, rcp{rcp}.\n")

        for variable in variables:
            print(f"### Processing variable: {variable}")

            self.load_netcdf(is_bias_corrected, season, rcp, variable)
            self.process_decade(self.current_netcdf_data)
            self.transform_data()
            self.insert_data_multiple_decades()
            self.close_netcdf_file()

            print(f"### Processing complete: {variable}\n")

        print(f"### Processing complete for dataset: bias_corrected: {is_bias_corrected}, {season}, rcp{rcp}.")
        print("############################\n")

    def process_all_seasons(self, rcp, is_bias_corrected):
        """
        Process all variables for all seasons.
        """

        seasons = ["annual", "winter", "summer"]

        for season in seasons:
            self.process_all_variables(season, rcp, is_bias_corrected)

    def process_all_rcps(self, is_bias_corrected):
        """
        Process all seasons and variables for all RCPs.
        """

        rcps = [60, 85]

        for rcp in rcps:
            self.process_all_seasons(rcp, is_bias_corrected)

    @timefn
    def process_all_data(self):
        """
        Process all bias and non bias corrected averages data.
        """

        self.drop_table()
        self.create_table()

        for is_bias_corrected in [True, False]:
            self.process_all_rcps(is_bias_corrected)
