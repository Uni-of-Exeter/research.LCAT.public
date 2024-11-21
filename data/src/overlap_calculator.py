import matplotlib.pyplot as plt
import psycopg2
from matplotlib.ticker import ScalarFormatter
from shapely import wkb
from shapely.geometry import MultiPolygon, Polygon


def plot_geometry(geometry, ax=None, **kwargs):
    """
    Plot geometry using matplotlib. Handles both Polygon and MultiPolygon.
    """

    if ax is None:
        fig, ax = plt.subplots()

    geom = wkb.loads(geometry, hex=True)

    # Check if the geometry is a Polygon
    if isinstance(geom, Polygon):
        x, y = geom.exterior.xy
        ax.plot(x, y, **kwargs)

    # Check if the geometry is a MultiPolygon
    elif isinstance(geom, MultiPolygon):
        for poly in geom.geoms:
            x, y = poly.exterior.xy
            ax.plot(x, y, **kwargs)

    return ax

class OverlapCalculator:
    """
    Class to determine grid cell overlaps between boundary/shapefile regions, and grid cells.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None

        self.grid_table_name = "chess_scape_grid"
        self.boundary_table_name = None
        self.new_table_name = None
        self.boundary_identifier = None

        self.no_overlap_regions = {}
        self.no_overlap_closest_cells = {}

    def set_boundary_table(self, boundary_identifier):
        """
        Given a boundary identifier, set the boundary_table_name.
        """

        self.boundary_table_name = f"boundary_{boundary_identifier}"
        self.new_table_name = f"grid_overlaps_{boundary_identifier}"
        self.boundary_identifier = boundary_identifier

        self.no_overlap_regions = {}
        self.no_overlap_closest_cells = {}

    #########################################################################
    ### Database operators
    #########################################################################

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

        self.conn = psycopg2.connect(
            host=host, dbname=dbname, user=user, password=password
        )
        self.cur = self.conn.cursor()

        print("Connection successful.")

    def drop_table(self, table_name):
        """
        Drop table given its name.
        """

        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping boundary table: {e}")

    def create_overlap_table(self):
        """
        Create new table to store the overlapping cells by region ID.
        """

        if not self.boundary_table_name:
            raise ValueError("Please set boundary identifier, i.e. 'uk_counties'.")

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{self.new_table_name}" (
            gid INTEGER,
            grid_cell_id INTEGER,
            is_overlap BOOLEAN,
            bias_corrected BOOLEAN
        );
        """

        self.cur.execute(create_table_query)
        self.conn.commit()

    def ensure_spatial_index(self, table_name, column_name):
        """
        Ensure a spatial index exists on the specified geometry column, so that ST_Envelope runs a bit quicker.
        """

        index_name = f"{table_name}_{column_name}_idx"
        create_index_query = f'CREATE INDEX IF NOT EXISTS {index_name} ON "{table_name}" USING GIST ({column_name});'

        self.cur.execute(create_index_query)
        self.conn.commit()

    #########################################################################
    ### Regular overlap processing code
    #########################################################################

    def insert_overlaps_optimised(self):
        """
        Given a table of regions, find the overlapping grid cells with these regions, and insert into the new overlap table.
        """

        # Find overlaps and insert directly into the new table
        insert_overlaps_query = f"""
        INSERT INTO "{self.new_table_name}" (gid, grid_cell_id, is_overlap, bias_corrected)
        SELECT s.gid, g.grid_cell_id, TRUE, g.bias_corrected
        FROM {self.grid_table_name} g
        JOIN {self.boundary_table_name} s
        ON ST_Intersects(g.geometry, s.geom)
        WHERE ST_Intersects(ST_Envelope(g.geometry), ST_Envelope(s.geom));
        """

        self.cur.execute(insert_overlaps_query)
        self.conn.commit()

        print("Inserted all overlaps into new table.")

    #########################################################################
    ### No overlap processing methods
    #########################################################################

    def find_no_overlap_regions(self):
        """
        Find the regions with no overlaps. Store these for easy analysis later.
        """

        find_no_overlap_gids_query = f"""
        SELECT s.gid
        FROM {self.boundary_table_name} s
        WHERE s.gid NOT IN (
            SELECT DISTINCT gid
            FROM {self.new_table_name}
        );
        """
        self.cur.execute(find_no_overlap_gids_query)
        no_overlap_regions = self.cur.fetchall()

        return [i[0] for i in no_overlap_regions]

        self.no_overlap_regions[self.new_table_name] = no_overlap_regions
        print(f"No overlaps: {self.new_table_name} {len(no_overlap_regions)}")

    def get_bounding_box(self, region_geom, scale_factor=1.0):
        """
        Calculate the bounding box of the region's geometry, scaling it while keeping the centroid fixed.
        """

        # Get the centroid of the region geometry
        get_centroid_query = """
        SELECT ST_Centroid(%s::geometry)
        """

        self.cur.execute(get_centroid_query, (region_geom,))
        centroid = self.cur.fetchone()[0]

        # Scale the bounding box around the centroid
        get_scaled_bbox_query = """
        SELECT ST_Envelope(
            ST_Translate(
                ST_Scale(
                    ST_Translate(%s::geometry, -ST_X(%s::geometry), -ST_Y(%s::geometry)),
                    %s, %s
                ),
                ST_X(%s::geometry), ST_Y(%s::geometry)
            )
        )
        """

        self.cur.execute(
            get_scaled_bbox_query,
            (
                region_geom,
                centroid,
                centroid,
                scale_factor,
                scale_factor,
                centroid,
                centroid,
            ),
        )

        bounding_box = self.cur.fetchone()[0]

        return bounding_box

    def get_candidate_cells(self, bounding_box):
        """
        Retrieve the grid cells that intersect with the given bounding box.
        """

        get_candidate_cells_query = f"""
        SELECT g.grid_cell_id, g.geometry, g.bias_corrected
        FROM {self.grid_table_name} g
        WHERE ST_Intersects(g.geometry, %s)
        """

        self.cur.execute(get_candidate_cells_query, (bounding_box,))
        candidate_cells = self.cur.fetchall()

        return candidate_cells

    def find_closest_grid_cell(self, region_geom, candidate_cells):
        """
        Find the closest grid cell to the region's geometry from a list of candidate cells, returning the gid,
        the geometry, and whether the cell is bias corrected or not.
        """
        if not candidate_cells:
            return None, None, None

        # Convert the candidate_cells list to a string that can be used in the VALUES clause
        candidate_values = ", ".join(
            [f"({cell_id}, '{geometry}', '{bias_corrected}')" for cell_id, geometry, bias_corrected in candidate_cells]
        )

        find_closest_grid_cell_query = f"""
        SELECT g.grid_cell_id, g.geometry, g.bias_corrected
        FROM (VALUES {candidate_values}) AS g(grid_cell_id, geometry, bias_corrected)
        ORDER BY g.geometry <-> %s::geometry
        LIMIT 1;
        """

        self.cur.execute(find_closest_grid_cell_query, (region_geom,))
        closest_grid_cell_data = self.cur.fetchone()

        return closest_grid_cell_data[0], closest_grid_cell_data[1], closest_grid_cell_data[2]

    def insert_closest_cell(self, gid, closest_grid_cell_id, bias_corrected):
        """
        Insert the closest grid cell for the specified region into the database.
        """

        insert_closest_cell_query = f"""
        INSERT INTO "{self.new_table_name}" (gid, grid_cell_id, is_overlap, bias_corrected)
        VALUES (%s, %s, FALSE, %s);
        """

        self.cur.execute(insert_closest_cell_query, (gid, closest_grid_cell_id, bias_corrected))
        self.conn.commit()

        print(f"Inserted closest grid cell {closest_grid_cell_id} for region {gid}.")

    def find_closest_cell(self, gid):
        """
        For a region with no overlapping grid cells, find the closest grid cell and insert it into the database.
        Expands the search area iteratively by enlarging the bounding box around centroid if no cells are found.
        """
        # Step 1: Get the region's geometry
        region_geom = self.get_region_geometry(gid)

        # Step 2: Initialize variables for bounding box expansion
        expansion_factor = 1.5
        bbox_expansion = 1.0  # No expansion at first
        closest_grid_cell_id = None

        # Step 3: Iteratively search for the closest grid cell
        while closest_grid_cell_id is None:
            # Step 3a: Get the expanded bounding box
            bounding_box = self.get_bounding_box(region_geom, bbox_expansion)

            # Step 3b: Retrieve candidate grid cells within the bounding box
            candidate_cells = self.get_candidate_cells(bounding_box)

            # Step 3c: Find the closest grid cell among the candidates
            closest_grid_cell_id, _, bias_corrected = self.find_closest_grid_cell(
                region_geom, candidate_cells
            )

            if closest_grid_cell_id is None:
                # Expand the bounding box if no cell is found
                bbox_expansion *= expansion_factor

            # Break if we dont find cells early enough
            # if bbox_expansion >= 3:
            #     break

        return closest_grid_cell_id, bbox_expansion, bias_corrected

    def process_no_overlap_regions(self, only_show_plots=False):
        """
        Find regions with no overlaps, then for each region, find closest grid cell.
        """

        no_overlap_regions = self.find_no_overlap_regions()

        print(f"{len(no_overlap_regions)} no overlap regions found.\n")

        for gid in no_overlap_regions:
            closest_grid_cell_id, bbox_expansion, bias_corrected = self.find_closest_cell(gid)

            if only_show_plots:
                print(f"Closest grid cell ID: {closest_grid_cell_id}, bbox expansion reached: {bbox_expansion}")
                self.plot_region_and_candidates(gid, scale_factor=bbox_expansion)

            if closest_grid_cell_id:
                self.insert_closest_cell(gid, closest_grid_cell_id, bias_corrected)

    #########################################################################
    ### Processing all
    #########################################################################

    def process_all_boundary_overlaps(self, process_no_overlaps=False):
        """
        For each of the boundaries, calculate grid cell overlaps and create a table. If process_no_overlaps set to True,
        regions with no overlaps are also processed.
        """

        boundary_identifiers = [
            "uk_counties",
            "la_districts",
            "lsoa",
            "msoa",
            "parishes",
            "sc_dz",
            "ni_dz",
            "iom",
        ]

        print("############################")
        print("### Processing all boundaries...\n")

        for boundary_identifier in boundary_identifiers:
            print(f"### Calculating grid cell overlaps: {boundary_identifier}")

            self.set_boundary_table(boundary_identifier)
            self.drop_table(self.new_table_name)
            self.create_overlap_table()
            self.ensure_spatial_index(self.grid_table_name, "geometry")
            self.ensure_spatial_index(self.boundary_table_name, "geom")
            self.insert_overlaps_optimised()

            print(f"Overlap insertion complete: {boundary_identifier}\n")

            if process_no_overlaps:
                print(f"### Processing regions with no overlaps: {boundary_identifier}")
                self.process_no_overlap_regions()
                print(f"### No overlap processing complete: {boundary_identifier}\n")

        print("### Overlaps inserted for all boundaries.")
        print("############################\n")

    #########################################################################
    ### Plotting code
    #########################################################################

    def plot_region_and_candidates(self, gid, scale_factor):
        """
        Plot the region, its bounding box, and the candidate grid cells. Keep in mind which boundary has been loaded.
        """

        boundary_identifier = self.boundary_identifier

        region_geom = self.get_region_geometry(gid)
        region_name = self.get_region_name(gid)
        bounding_box_geom = self.get_bounding_box(region_geom, scale_factor)
        candidate_cells = self.get_candidate_cells(bounding_box_geom)
        closest_grid_cell_id, _ = self.find_closest_grid_cell(
            region_geom, candidate_cells
        )
        closest_grid_cell_geom = self.get_grid_cell_geometry(closest_grid_cell_id)

        fig, ax = plt.subplots()

        # Plot the region
        ax = plot_geometry(
            region_geom, ax=ax, color="red", linewidth=1, label="Region"
        )

        # Plot the bounding box/envelope we are using to find grid cells
        ax = plot_geometry(
            bounding_box_geom,
            ax=ax,
            color="green",
            linewidth=1,
            linestyle="--",
            label="Bounding Box",
        )

        # Plot the candidate grid cells
        for grid_cell_id, grid_cell_geom in candidate_cells:
            ax = plot_geometry(grid_cell_geom, ax=ax, color="pink", linewidth=0.5)

        # If we have a closest grid cell, plot on this centroid with a black cross
        if closest_grid_cell_geom is not None:
            closest_geom = wkb.loads(closest_grid_cell_geom, hex=True)
            x, y = closest_geom.centroid.xy
            ax.plot(x, y, "x", color="black", markersize=15, label="Closest Grid Cell")

        ax.set_xlabel("Easting")
        ax.set_ylabel("Northing")
        ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='sci', axis='both', scilimits=(0,0))

        ax.set_title(
            f"{boundary_identifier}: closest grid cell to no overlap region: {closest_grid_cell_id} - {region_name}"
        )
        plt.show()

    #########################################################################
    ### Query tools
    #########################################################################

    def get_region_geometry(self, gid):
        """
        Retrieve the geometry of the region with the specified gid.
        """

        find_region_geom_query = f"""
        SELECT s.geom
        FROM {self.boundary_table_name} s
        WHERE s.gid = %s;
        """

        self.cur.execute(find_region_geom_query, (gid,))
        region_geom = self.cur.fetchone()[0]

        return region_geom

    def get_region_name(self, gid):
        """
        Given a gid, get the region name from the boundary table name.
        """

        name_cols = {
            "uk_counties": "CTYUA23NM",
            "la_districts": "LAD23NM",
            "lsoa": "LSOA21NM",
            "msoa": "MSOA21NM",
            "parishes": "PAR23NM",
            "sc_dz": "Name",
            "ni_dz": "DZ2021_nm",
            "iom": "NAME_ENGLI",
        }

        column_name = name_cols[self.boundary_identifier]

        get_region_name_query = f"""
        SELECT {column_name}
        FROM {self.boundary_table_name}
        WHERE gid = %s
        """

        self.cur.execute(get_region_name_query, (gid,))
        region_name = self.cur.fetchone()[0]

        return region_name

    def get_grid_cell_geometry(self, grid_cell_id):
        """
        Given a grid cell ID, get the geometry.
        """

        get_cell_geometry_query = f"""
        SELECT g.geometry
        FROM {self.grid_table_name} g
        WHERE g.grid_cell_id = %s;
        """

        self.cur.execute(get_cell_geometry_query, (int(grid_cell_id),))
        geometry = self.cur.fetchone()

        if geometry:
            return geometry[0]

        return geometry

    def select_overlaps_from_overlap_table(self, gid):
        """
        Get overlap cells from new overlap table given a gid.
        """

        get_overlap_query = f"""
        SELECT grid_cell_id
        FROM "{self.new_table_name}"
        WHERE gid = %s;
        """

        self.cur.execute(get_overlap_query, (gid,))
        raw_overlapping_cells = self.cur.fetchall()
        overlapping_cells = [cell[0] for cell in raw_overlapping_cells]

        print(f"Overlapping cells found: {len(overlapping_cells)}")

        return overlapping_cells

    def detect_and_select_overlaps_boundary_table(self, gid):
        """
        Given a region/shapefile gid, calculate the grid cells that the region overlaps, first selecting the region by gid
        from the boundary table, and then calculating the overlapping cells.
        """

        if not self.boundary_table_name:
            raise ValueError("Please set boundary identifier, i.e. 'uk_counties'.")

        overlap_query = f"""
        SELECT g.grid_cell_id
        FROM {self.grid_table_name} g
        JOIN {self.boundary_table_name} s
        ON ST_Intersects(g.geometry, s.geom)
        WHERE s.gid = %s;
        """

        self.cur.execute(overlap_query, (int(gid),))
        raw_overlapping_cells = self.cur.fetchall()
        overlapping_cells = [cell[0] for cell in raw_overlapping_cells]

        print(f"Overlapping cells found: {len(overlapping_cells)}")

        return overlapping_cells

    #########################################################################
    ### Old code
    #########################################################################

    def insert_overlaps_simple(self):
        """
        Insert overlaps for each gid in the boundary table, store the results in the new table.
        """

        # Create the new table
        self.create_overlap_table()

        # Find overlaps and insert directly into the new table
        insert_overlaps_query = f"""
        INSERT INTO "{self.new_table_name}" (gid, grid_cell_id)
        SELECT s.gid, g.grid_cell_id
        FROM {self.grid_table_name} g
        JOIN {self.boundary_table_name} s
        ON ST_Intersects(g.geometry, s.geom);
        """

        self.cur.execute(insert_overlaps_query)
        self.conn.commit()

        print("Inserted all overlaps into new table.")
