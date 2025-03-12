import psycopg2


class CoastalIdentifier:
    """
    Previously, when loading CHESS-SCAPE grid cells to the database using the GridLoader class, we tagged cells if they
    were coastline, land, or in 5*10km inland coastal bands. This was recorded in the chess_scape_grid postgres table,
    in the coastal_info column. We can identify whether a region is coastal based on this data.

    Based on the type of overlapping grid cells, determine if a region is coastal or not. We write this to a boolean
    column in the boundary table called is_coastal.

    Rules:
        - Define regions as coastal if they contain overlapping cells that are 20km or less to the coast. This can be
          updated as required.
        - If the region contains any of self.coastal_values, the region is deemed coastal.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None

        # Set the default distances for coastal identification
        self.coastal_values = ["20km from coast", "10km from coast", "coastline"]
        self.coastal_column_name = "is_coastal"

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

    def add_column(self, boundary_identifier, column_name):
        """
        Alter a boundary table to add a boolean column to it, of a given name.
        """

        alter_table_query = (
            f'ALTER TABLE "boundary_{boundary_identifier}" ADD COLUMN IF NOT EXISTS "{column_name}" BOOLEAN'
        )

        self.cur.execute(alter_table_query)
        self.conn.commit()

    def process_boundary(self, boundary_identifier):
        """
        Tag all regions in a boundary as coastal or not coastal. This was very slow in Python and very fast in
        PostgreSQL. For Northern Ireland, we deem all regions coastal, as the NetCDF data deems the land border with
        the rest of Ireland as coastline.
        """

        # Add a new boolean column if it doesn't exist
        self.add_column(boundary_identifier, self.coastal_column_name)

        try:
            if boundary_identifier == "ni_dz":
                # If the boundary is "ni_dz", mark all regions as coastal
                update_query = f"""
                    UPDATE boundary_{boundary_identifier}
                    SET is_coastal = TRUE;
                """
                self.cur.execute(update_query)

            else:
                # Make coastal values a tuple
                coastal_values = tuple(self.coastal_values)

                # Update all regions in a single query
                update_query = f"""
                    UPDATE boundary_{boundary_identifier} b
                    SET is_coastal = EXISTS (
                        SELECT 1
                        FROM grid_overlaps_{boundary_identifier} o
                        JOIN chess_scape_grid g ON o.grid_cell_id = g.grid_cell_id
                        WHERE o.gid = b.gid AND g.coastal_info IN %s
                    );
                """
                self.cur.execute(update_query, (coastal_values,))

            self.conn.commit()
            print(f"Boundary {boundary_identifier} processed successfully.")

        except psycopg2.Error as e:
            print(f"Database error processing {boundary_identifier}: {e}")
            self.conn.rollback()

    def process_all_boundaries(self):
        """
        Tag all regions in all boundaries as coastal or not coastal.
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
        print("### Tagging regions as coastal in all boundaries...\n")

        for boundary_identifier in boundary_identifiers:
            self.process_boundary(boundary_identifier)

        print("### Coastal tagging complete for all regions in all boundaries.")
        print("############################\n")
