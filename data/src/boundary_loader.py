import os

import psycopg2


class BoundaryLoader:
    """
    Class to handle the loading of boundary files, provided as ESPG 27700 shapefiles by default.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None
        self.connection_string = None
        self.target_projection = None

        self.set_database_projection_code("27700")

    def set_database_projection_code(self, target_projection_code):
        """
        Set the projection codes of the database. This will be the SRID of the geometry column.
        """

        self.target_projection = target_projection_code

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

        self.connection_string = f"postgresql://{user}:{password}@{host}/{dbname}"

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

    def load_boundary(self, boundary_identifier, source_projection, filepath=None):
        """
        Drop boundary table and load into database with shp2pgsql.
        """

        key = f"{boundary_identifier}_shp"

        if not filepath:
            filepath = self.conf[key]

        table_name = f"boundary_{boundary_identifier}"

        cmd = f'shp2pgsql -I -d -s {source_projection}:{self.target_projection} "{filepath}" {table_name} | psql {self.connection_string}'

        try:
            os.system(cmd)

        except Exception as e:
            print(f"Error creating {boundary_identifier} table: {e}")

    def load_all_boundaries(self):
        """
        Load all 6 boundaries using boundary identifiers.
        """

        source_projections = {
            "uk_counties": "27700",
            "la_districts": "27700",
            "lsoa": "27700",
            "msoa": "27700",
            "parishes": "27700",
            "sc_dz": "27700",
            "ni_dz": "29902",
            "iom": "4326",
        }

        for boundary_identifier in source_projections:
            table_name = f"boundary_{boundary_identifier}"
            self.drop_table(table_name)

        print("############################")
        print("### Processing all boundaries...\n")

        for boundary_identifier, source_projection in source_projections.items():
            print(f"### Processing boundary: {boundary_identifier}")
            self.load_boundary(boundary_identifier, source_projection)
            print(f"### Processing complete: {boundary_identifier}\n")

        print("### Processing complete for all boundaries.")
        print("############################\n")
