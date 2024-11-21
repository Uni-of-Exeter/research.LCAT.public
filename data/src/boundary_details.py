import psycopg2


class DetailsGenerator:
    """
    Create a boundary_details table store information related to the boundary_identifiers.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.cur = None

        self.table_name = "boundary_details"

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

    def drop_table(self, table_name=None):
        """
        Drop the table associated with the current variables if it exists.
        """

        try:
            drop_table_query = f'DROP TABLE IF EXISTS "{table_name}";'
            self.cur.execute(drop_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error dropping CHESS-SCAPE table: {e}")

    def create_table(self):
        """
        Create table if it does not already exist.
        """

        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS "{self.table_name}" (
            boundary_identifier VARCHAR PRIMARY KEY,
            print_name VARCHAR NOT NULL,
            shapefile_name_col VARCHAR NOT NULL,
            source_srid INTEGER NOT NULL,
            db_srid INTEGER NOT NULL,
            boundary_table_name VARCHAR NOT NULL,
            overlap_table_name VARCHAR NOT NULL,
            method VARCHAR NOT NULL
        );
        """

        try:
            self.cur.execute(create_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error creating CHESS-SCAPE table: {e}")

    def insert_boundary_details(self, boundary_details):
        """
        Insert boundary details from the dictionary into the table.
        """

        insert_query = f"""
        INSERT INTO "{self.table_name}" (boundary_identifier, print_name, shapefile_name_col, source_srid, db_srid, boundary_table_name, overlap_table_name, method)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            for boundary_identifier, details in boundary_details.items():
                self.cur.execute(
                    insert_query,
                    (
                        boundary_identifier,
                        details["print_name"],
                        details["shapefile_name_col"],
                        details["source_srid"],
                        details["db_srid"],
                        f"boundary_{boundary_identifier}",
                        f"grid_overlaps_{boundary_identifier}",
                        details["method"],
                    ),
                )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting boundary details: {e}")

    def process_data(self, boundary_details):
        """
        Run table creation process.
        """

        self.drop_table(self.table_name)
        self.create_table()
        self.insert_boundary_details(boundary_details)
