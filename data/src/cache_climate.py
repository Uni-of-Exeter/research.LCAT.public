import psycopg2


class CacheClimate:
    """
    Class to cache the climate data, based on region gid, its overlapping cells, and the relevant CHESS-SCAPE data.
    Note that not all regions use the cache method (and the cache tables) in the app. See the docs for more information
    about the cell method and the cache method.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None

        self.boundary_identifier = None
        self.overlap_table = None
        self.climate_table = None
        self.cache_table = None

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

    def drop_table(self, table_name):
        """
        Drop the table associated with the current variables if it exists.
        """

        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping CHESS-SCAPE table: {e}")

    def set_boundary(self, boundary_identifier):
        """
        Set the current boundary to be processed. This determines the overlap table to be used.
        """

        self.boundary_identifier = boundary_identifier
        self.overlap_table = f"grid_overlaps_{boundary_identifier}"

        self.climate_table = None
        self.cache_table = None

    def set_rcp_and_season(self, rcp, season):
        """
        Set rcp and season to determine the climate and cache tables to be used, i.e. rcp{60} or rcp{85}, or
        "annual", "summer" or "winter".
        """

        self.climate_table = f"chess_scape_rcp{rcp}_{season}"
        self.cache_table = f"cache_{self.boundary_identifier}_to_rcp{rcp}_{season}"

    def get_climate_column_names(self):
        """
        Select the column names from the loaded climate table.
        """

        select_column_name_query = f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{self.climate_table}'
        AND table_schema = 'public';
        """

        self.cur.execute(select_column_name_query)
        columns = self.cur.fetchall()

        column_names = [col[0] for col in columns if col[0] != "grid_cell_id"]

        return column_names

    def create_table(self):
        """
        Given the loaded variables, gets the column names, filters then, and creates a new table.
        """

        column_names = self.get_climate_column_names()
        columns_definition = ",\n    ".join([f'"{col}" DOUBLE PRECISION' for col in column_names])

        create_table_query = f"""
        CREATE TABLE "{self.cache_table}" (
            gid INT PRIMARY KEY,
            {columns_definition}
        )
        """

        try:
            self.cur.execute(create_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error creating CHESS-SCAPE table: {e}")

    def cache_all_gids(self):
        """
        Select all gids in the loaded boundary and cache their climate data.
        """

        # Get all column names in climate table
        column_names = self.get_climate_column_names()

        # Take the min of the min cells, mean of the mean cells, max of the max cells
        select_clause = ", ".join(
            [
                f'MIN("{col}") AS "{col}"'
                if col.endswith("_min")
                else f'AVG("{col}") AS "{col}"'
                if col.endswith("_mean")
                else f'MAX("{col}") AS "{col}"'
                for col in column_names
            ]
        )

        insert_clause = ", ".join([f'"{col}"' for col in column_names])

        cache_all_query = f"""
        INSERT INTO "{self.cache_table}" (gid, {insert_clause})
        SELECT ot.gid, {select_clause}
        FROM "{self.overlap_table}" ot
        JOIN "{self.climate_table}" ct ON ot.grid_cell_id = ct.grid_cell_id
        GROUP BY ot.gid
        """

        self.cur.execute(cache_all_query)
        self.conn.commit()

    def process_boundary(self, boundary_identifier):
        """
        For a given boundary, process each rcp and season.
        """

        self.set_boundary(boundary_identifier)

        print(f"### Caching {boundary_identifier}...\n")

        for rcp in [60, 85]:
            for season in ["annual", "summer", "winter"]:
                self.set_rcp_and_season(rcp, season)
                self.drop_table(self.cache_table)
                self.create_table()
                self.cache_all_gids()

    def process_all_boundaries(self):
        """
        Cache climate data for all boundaries.
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
        print("### Caching all boundaries...\n")

        for boundary_identifier in boundary_identifiers:
            self.process_boundary(boundary_identifier)

        print("### Caching complete for all boundaries.")
        print("############################\n")
