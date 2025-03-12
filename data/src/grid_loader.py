import io
import os

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
import xarray as xr
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from matplotlib.path import Path
from scipy.ndimage import binary_erosion, binary_fill_holes, convolve, label
from scipy.ndimage import sum as ndi_sum
from shapely.geometry import Polygon


class GridLoader:
    """
    Class to handle loading of the CHESS-SCAPE grid. This contains cell boundary information for each of the cells
    that the netcdf data are recorded on. The netcdf data are provided at points in time and space, on ESPG 27700.
    The grid table will contain the calculated boundaries of each cell that has a data point at its centre. Null
    data cells are not stored in the database table.

    This class is responsible for creating a mask of bias and non-bias-corrected cells from the NetCDF files. We
    select bias-corrected data where possible, and non-bias-corrected data for Northern Ireland and the Isles of
    Scilly. There are some additional non-bias-corrected cells present around mainland UK: we discount these.

    This class also identifies this data from the raw CHESS-SCAPE files, and stores it in a Postgres table. We store the
    following data for each grid cell:

        - grid_cell_id: primary key, integer
        - geometry: geometry (postgis geometry type, 1km by 1km square)
        - bias_corrected: boolean, whether the cell has bias-corrected data for it or not
        - coastal_info: charvar, string to identify coastline, land, or 5*10km inwards bands
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
        Get the mask for the required bias or non-bias corrected data (i.e. where the data is not nan). For the bias
        corrected data, we return the mask of where the NetCDF file is non-zero, i.e. where we have bias-corrected
        data. For the non-bias-corrected data, we need to manually select the non-bias-corrected cells that we want
        to keep.

        Broadly, we want to keep the non bias-corrected data for Northern Ireland and the Isles of Scilly. There are
        also some non-bias-corrected cells around the UK: we want to discount these. Hence we draw a polygon around
        these two regions, selecting all non-bias-cells in these polygons, to create the non-bias-corrected mask.
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
        Assuming two data files have been loaded, create and cache masks for both data files.
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
        Create a labelled mask. We use the following labels:

            - False == 0
            - bias_corrected == 1
            - non_bias_corrected = 2

        This is our final mask, and can be thought of as bias-corrected data where possible (England, Wales, Scotland),
        but non-bias-corrected data over Northern Ireland and the Isles of Scilly.
        """

        self.masks["aggregated_labelled"] = self.masks["bias_corrected"].astype(int) + 2 * self.masks[
            "non_bias_corrected"
        ].astype(int)

    def _create_filled_land_mask(self, land_mask, size_threshold=15):
        """
        Given a land mask, with some internal lakes, create a filled land mask (with small lakes filled).
        """

        # Previously:
        # filled_land_mask = binary_fill_holes(land_mask)

        # Now:
        # Identify all holes (connected components of False inside True regions)
        inverse_mask = ~land_mask
        labeled_holes, num_holes = label(inverse_mask)

        # Compute the size of each hole
        hole_sizes = ndi_sum(inverse_mask, labeled_holes, index=range(1, num_holes + 1))

        # Create a mask for small holes
        small_holes_mask = np.isin(labeled_holes, np.where(hole_sizes <= size_threshold)[0] + 1)

        # Fill only the small holes
        filled_land_mask = land_mask | small_holes_mask

        return filled_land_mask

    def create_coastline_mask(self):
        """
        Create a coastline mask from a NetCDF dataset. We create a convolution, and count the number of cells around
        each cell. A cell surrounded by land on all sides has a value of 9. An ocean cell surrounded by ocean on all
        sides has a value of 0. We filter the convolved data: any cells in the land mask with a count greater than 0
        and less than 9 are deemed coastline.
        """
        # Create boolean land mask (False where no data)
        land_mask = self.masks["aggregated_labelled"].astype(bool)

        # Create filled land mask
        filled_land_mask = self._create_filled_land_mask(land_mask)

        # Define 8-neighbor kernel
        kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

        # Count land cell neighbors for each cell
        land_neighbours = convolve(filled_land_mask.astype(int), kernel, mode="constant", cval=0)

        # Create coastline mask
        coastline_mask = land_mask & (land_neighbours > 0) & (land_neighbours < 9)

        self.masks["coastline"] = coastline_mask

    def create_inland_mask(self, land_mask, filled_land_mask, radius):
        """
        Using a circular structuring element, create an inland mask from the edge of a given mask pair, using erosion.
        """

        y, x = np.ogrid[-radius : radius + 1, -radius : radius + 1]
        circular_structure = (x**2 + y**2) <= radius**2

        # Apply erosion to shrink the land mask inward by n cells
        eroded_land_mask = binary_erosion(filled_land_mask, structure=circular_structure)

        # Extract the n-cell inland boundary by subtracting the eroded mask from the original land mask
        return land_mask & ~eroded_land_mask

    def create_coastal_mask_with_inland_regions(self):
        """
        Create a coastline mask with inland regions a specified distance away from the coast tagged.
        The following classifications are used:

         - 0 = Ocean (or inland water body, not present in final database)
         - 1 = Coastline
         - 2 = Land
         - 10 = Land (10km from the coast)
         - 20 = Land (20km from the coast)
         - 30 = Land (30km from the coast)
         - 40 = Land (40km from the coast)
         - 50 = Land (50km from the coast)
        """

        # Store the map for use later on
        self.coastal_map = {
            0: "ocean",
            1: "coastline",
            2: "land",
            10: "10km from coast",
            20: "20km from coast",
            30: "30km from coast",
            40: "40km from coast",
            50: "50km from coast",
        }

        land_mask = self.masks["aggregated_labelled"].astype(bool)
        filled_land_mask = binary_fill_holes(land_mask)

        # Create a number of 10km bands
        inward_10_mask = self.create_inland_mask(land_mask, filled_land_mask, 10)
        inward_20_mask = self.create_inland_mask(land_mask, filled_land_mask, 20)
        inward_30_mask = self.create_inland_mask(land_mask, filled_land_mask, 30)
        inward_40_mask = self.create_inland_mask(land_mask, filled_land_mask, 40)
        inward_50_mask = self.create_inland_mask(land_mask, filled_land_mask, 50)

        # Initialize the final mask with 0 (ocean)
        final_mask = np.zeros_like(land_mask, dtype=int)

        # Set land cells to 2 (excluding coast and inward bands)
        final_mask[land_mask] = 2

        # Assign land masks from inside to outside
        final_mask[inward_50_mask] = 50
        final_mask[inward_40_mask] = 40
        final_mask[inward_30_mask] = 30
        final_mask[inward_20_mask] = 20
        final_mask[inward_10_mask] = 10

        # Finally assign coastline cells
        coastline_mask = self.masks["coastline"]
        final_mask[coastline_mask] = 1

        self.masks["final_coastal_mask"] = final_mask

    def plot_mask(self, mask, key):
        """
        Plot mask with matplotlib. Note EPSG 27700 is used.
        """

        plt.figure(figsize=(40, 30))
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
            bias_corrected BOOLEAN NOT NULL,
            coastal_info VARCHAR(20)
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
        coastal_mask = self.masks["final_coastal_mask"]

        if mask.shape != coastal_mask.shape:
            raise ValueError(f"Shape mismatch: mask shape {mask.shape} != coastal_mask shape {coastal_mask.shape}")

        for i, j in np.ndindex(mask.shape):
            # If mask cell has value of 0, skip
            if mask[i, j] == 0:
                continue

            # Get the coastal mask value for the cell, and the correct string label from the map
            coastal_mask_value = coastal_mask[i, j]
            coastal_label = self.coastal_map[coastal_mask_value]

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
            rows.append((grid_cell_id, poly.wkt, tag, coastal_label))

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
            output.write(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\n")

        # Move cursor to start of buffer
        output.seek(0)

        column_names = ["grid_cell_id", "geometry", "bias_corrected", "coastal_info"]
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
        self.create_coastline_mask()
        self.create_coastal_mask_with_inland_regions()

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
