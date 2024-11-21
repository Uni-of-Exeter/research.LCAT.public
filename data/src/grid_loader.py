import io
import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
import xarray as xr
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from matplotlib.path import Path
from shapely.geometry import Polygon


class GridLoader:
    """
    Class to handle loading of the CHESS-SCAPE grid. This contains cell boundary information for each of the cells
    that the netcdf data are recorded on. The netcdf data are provided at points in time and space, on ESPG 27700.
    The grid table will contain the calculated boundaries of each cell that has a data point at its centre. Null
    data cells are not stored in the database table.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None
        self.variable = None
        self.data = {}
        self.masks = {}
        self.table_name = "chess_scape_grid"

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
        Lazy load a netcdf file with xarray.
        """

        try:
            data = xr.open_dataset(filepath, engine="netcdf4")
            print(f"Loaded file into xarray with sizes y: {data.y.size}, x: {data.x.size}, t: {data.time.size}")

        except Exception as e:
            print(f"netcdf file open failed with error: {e}")

        return data

    def open_netcdf_files(
        self,
        filepath_bias_corrected=None,
        filepath_non_bias_corrected=None,
        variable=None,
    ):
        """
        Load two netcdf files. One should be bias-corrected, one should not be bias-corrected. We need to load both to aggregate the grids,
        whilst also cleaning up the NI grid.
        """

        if not filepath_bias_corrected or not filepath_non_bias_corrected or not variable:
            filename_bias_corrected = "data/rcp60_bias-corrected/01/annual/chess-scape_rcp60_bias-corrected_01_tas_uk_1km_annual_19801201-20801130.nc"
            filepath_bias_corrected = os.path.join(self.data_location, filename_bias_corrected)

            filename_non_bias_corrected = (
                "data/rcp60/01/annual/chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc"
            )
            filepath_non_bias_corrected = os.path.join(self.data_location, filename_non_bias_corrected)
            variable = "tas"

            print(
                "At least one value not supplied. Loading bias and non-bias corrected netcdf files from folder structure for variable: tas."
            )

        self.data["bias_corrected"] = self.open_netcdf_file(filepath_bias_corrected)
        self.data["non_bias_corrected"] = self.open_netcdf_file(filepath_non_bias_corrected)
        self.variable = variable

    def create_polygon_mask(self, polygon_vertices, y_size, x_size):
        """
        Given a list of polygon_vertices (i.e. [(x, y), ...]), and the size of the mask, create a boolean mask
        with True inside the polygon bounds and False outside the bounds.
        """

        # Create numpy array
        polygon_coords = np.array(polygon_vertices)

        # 2. Create a mask of coordinates (pixel positions in the array)
        y, x = np.mgrid[:y_size, :x_size]
        points = np.vstack((x.ravel(), y.ravel())).T

        # 3. Create a Path object for the polygon
        polygon_path = Path(polygon_coords)

        # 4. Determine which points are inside the polygon
        points_check = polygon_path.contains_points(points)

        # 5. Reshape to the original array shape
        polygon_mask_reshaped = points_check.reshape(y_size, x_size)

        # 6. Apply the mask to the array
        polygon_mask = np.where(polygon_mask_reshaped, True, False)

        return polygon_mask

    def get_mask(self, bias_corrected_key):
        """
        Get the mask for the required bias or non-bias corrected data (i.e. where the data is not nan).
        """

        data = self.data[bias_corrected_key]

        if bias_corrected_key == "bias_corrected":
            return ~data[self.variable][0].isnull().values

        # If not bias corrected, we need to clean up the mask to select just NI data and Scilly Isles data
        dirty_mask = ~data[self.variable][0].isnull().values

        # Define coordinates for a polygon that encompasses NI non-bias corrected data
        a = (0, 460)
        b = (200, 460)
        c = (200, 500)
        d = (135, 620)
        e = (0, 600)

        # Define coordinates for a polygon that encompasses Scilly Isles non-bias corrected data
        f = (75, 0)
        g = (75, 50)
        h = (100, 50)
        i = (100, 0)

        # Create masks defined by the polygon bounds
        ni_polygon_vertices = [a, b, c, d, e]
        scilly_isles_polygon_vertices = [f, g, h, i]

        y_size, x_size = data.sizes["y"], data.sizes["x"]

        ni_polygon_mask = self.create_polygon_mask(ni_polygon_vertices, y_size, x_size)
        scilly_isles_polygon_mask = self.create_polygon_mask(scilly_isles_polygon_vertices, y_size, x_size)

        # Get combined polygon mask
        combined_polygon_mask = ni_polygon_mask | scilly_isles_polygon_mask

        # Get the total mask (i.e. get the non-bias corrected data that exists within each polygon mask)
        non_bias_mask = dirty_mask & combined_polygon_mask

        return non_bias_mask

    def cache_masks(self):
        """
        Assuming two masks have been loaded, create and cache both.
        """

        if len(self.data) != 2:
            raise ValueError("Warning: netcdf data not loaded. Please load to continue.")

        for key in self.data:
            self.masks[key] = self.get_mask(key)

    def aggregate_cached_masks(self):
        """
        For the bias and non-bias corrected masks create an aggregated mask.
        """

        if "bias_corrected" not in self.masks or "non_bias_corrected" not in self.masks:
            raise ValueError("Warning: masks not cached. Please cache masks to continue.")

        self.masks["aggregated"] = self.masks["bias_corrected"] + self.masks["non_bias_corrected"]

    def create_aggregated_labelled_mask(self):
        """
        Create a labelled mask. False == 0, bias_corrected == 1, non_bias_corrected = 2.
        """

        self.masks["aggregated_labelled"] = self.masks["bias_corrected"].astype(int) + 2 * self.masks[
            "non_bias_corrected"
        ].astype(int)

    def plot_mask(self, mask, key):
        """
        Plot mask with matplotlib. Note EPSG 27700 is used.
        """

        plt.figure(figsize=(6, 8))
        ax = plt.axes(projection=ccrs.epsg(27700), transform=ccrs.epsg(27700))
        ax.pcolormesh(mask)
        ax.set_title(f"CHESS-SCAPE grid: {key}")

        draw_labels = False
        gl = ax.gridlines(draw_labels=draw_labels)
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xformatter = plt.FuncFormatter(lambda x, _: f"{x:.2f}°")
        gl.yformatter = plt.FuncFormatter(lambda y, _: f"{y:.2f}°")

    def plot_all_grids(self):
        """
        Plot all masks that have been created & cached.
        """

        for key, mask in self.masks.items():
            self.plot_mask(mask, key)

    def drop_table(self, table_name=None):
        """
        Drop table given its name.
        """

        if not table_name:
            table_name = self.table_name

        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping boundary table: {e}")

    def create_table(self):
        """
        Create table if it does not exist.
        """

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{self.table_name}" (
            grid_cell_id INTEGER PRIMARY KEY,
            geometry GEOMETRY(POLYGON, 27700) NOT NULL,
            bias_corrected BOOLEAN NOT NULL
        );
        """

        try:
            self.cur.execute(create_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error creating CHESS-SCAPE grid table: {e}")

    def create_grid_data_rows(self):
        """
        Using the aggregated, labelled mask and any netcdf data (bias or non-bias corrected), create the
        rows of data to be inserted into the table. The netcdf data is used to calculate the grid edges.
        The mask is used to check whether the cells should be stored in the database: if a cell has data
        associated with it, we store it in the database. Polygons are initially created as WKT representations.

        Note that similar logic is used in ChessScapeLoader to loop through the mask, and select climate data
        to load into the database.
        """

        x = self.data["bias_corrected"]["x"].values
        y = self.data["bias_corrected"]["y"].values

        # Compute cell width and construct edge coordinates
        dx = np.diff(x)[0]
        dy = np.diff(y)[0]

        x_edges = np.concatenate([x - dx / 2, [x[-1] + dx / 2]])
        y_edges = np.concatenate([y - dy / 2, [y[-1] + dy / 2]])

        # Prepare data rows for insertion
        rows = []

        # For each cell in the mask, check its value
        mask = self.masks["aggregated_labelled"]

        for i, j in np.ndindex(mask.shape):
            # If mask cell has value of 0, skip
            if mask[i, j] == 0:
                continue

            # If mask cell is 1 label as bias corrected ("TRUE"), if 2 label as non-bias corrected ("FALSE")
            tag = "TRUE" if mask[i, j] == 1 else "FALSE"

            # Create polygon and prepare the row
            poly = Polygon(
                [
                    (x_edges[j], y_edges[i]),
                    (x_edges[j + 1], y_edges[i]),
                    (x_edges[j + 1], y_edges[i + 1]),
                    (x_edges[j], y_edges[i + 1]),
                ]
            )

            grid_cell_id = i * mask.shape[1] + j
            rows.append((grid_cell_id, poly.wkt, tag))

        return rows

    def insert_data(self):
        """
        Bulk insert data into database with StringIO buffer and copy_from.
        """

        print("############################")
        print("### Calculating grid cell locations and inserting...\n")

        rows = self.create_grid_data_rows()

        # Prepare the StringIO buffer
        output = io.StringIO()

        for row in rows:
            output.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")

        # Move cursor to start of buffer
        output.seek(0)

        column_names = ["grid_cell_id", "geometry", "bias_corrected"]
        self.cur.copy_from(output, self.table_name, sep="\t", columns=column_names)

        self.conn.commit()
        output.close()

        print("### Grid cell insertion complete.")
        print("############################\n")

    def process_masks(self, plot_labelled_mask=False):
        """
        Process masks ready for database insert.
        """

        print("############################")
        print("### Mask processing starting...\n")

        self.cache_masks()
        self.aggregate_cached_masks()
        self.create_aggregated_labelled_mask()

        print("### Mask creation complete.")
        print("############################\n")

        if plot_labelled_mask:
            self.plot_mask(self.masks["aggregated_labelled"], "aggregated & labelled")

    def process_grid(self):
        """
        Run mask creation and database insert process.
        """

        self.process_masks(plot_labelled_mask=True)
        self.drop_table()
        self.create_table()
        self.insert_data()
