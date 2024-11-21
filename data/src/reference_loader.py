import json

import psycopg2


class ReferenceLoader:
    """
    Class to load references into database, initially from intermediate json file.
    """

    def __init__(self, config):
        self.conf = config
        self.conn = None
        self.data = None

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


    def load_json(self, filepath=None):
        """
        Load reference data from intermediate json file. This contains processed references, with DOI lookup performed
        """

        if not filepath:
            filepath = self.conf["processed_references_json"]
            print("References filepath retrieved from config file.")

        with open(filepath) as file:
            self.data = json.load(file)

    def create_table(self):
        """
        Create a references table if it does not exist.
        """

        create_table_query = """
        CREATE TABLE IF NOT EXISTS "references" (
            article_id INTEGER PRIMARY KEY,
            type VARCHAR(50),
            doi VARCHAR(255),
            link TEXT,
            link_replacement TEXT,
            title TEXT,
            authors TEXT,
            date VARCHAR(50),
            journal TEXT,
            issue TEXT
        );
        """

        try:
            self.cur.execute(create_table_query)
            self.conn.commit()

        except Exception as e:
            print(f"Error creating references table: {e}")

    def validate_record(self, record):
        """
        Ensure a record has the correct fields before inserting.
        """

        required_fields = ["article_id", "type", "doi", "link", "title", "authors", "date", "journal", "issue"]

        return all(field in record for field in required_fields)

    def insert_data(self):
        """
        Insert loaded data to references table.
        """

        if self.data is None:
            raise ValueError("No reference data loaded. Use the load_json() method to load references.")

        insert_query = """
        INSERT INTO "references" (article_id, type, doi, link, link_replacement, title, authors, date, journal, issue)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (article_id) DO NOTHING;
        """

        for key, record in self.data.items():
            if self.validate_record(record):
                self.cur.execute(
                    insert_query,
                    (
                        record["article_id"],
                        record["type"],
                        record["doi"],
                        record["link"],
                        record["link_replacement"],
                        record["title"],
                        record["authors"],
                        record["date"],
                        record["journal"],
                        record["issue"],
                    ),
                )
        self.conn.commit()
        print("Reference data inserted successfully.")

    def drop_table(self):
        """
        Drop references table if it exists.
        """

        drop_table_query = 'DROP TABLE IF EXISTS "references";'
        self.cur.execute(drop_table_query)
        self.conn.commit()

    def close(self):
        """
        Close connection to host.
        """

        self.cur.close()
        self.conn.close()

    def load_all_references(self, filepath=None):
        """
        Method to be called in the builder. Sequence to load all references.
        """

        self.connect_to_db()
        self.load_json(filepath)
        self.create_table()
        self.insert_data()
        self.close()
