import psycopg2
from psycopg2 import sql


class DBManager:
    """
    Class to set up the LCAT database.
    """

    def __init__(self, superuser, superuser_pass, host, dbname, user, user_pass):
        self.superuser = superuser
        self.superuser_pass = superuser_pass
        self.host = host
        self.dbname = dbname
        self.user = user
        self.user_pass = user_pass

    def _connect_superuser(self, dbname=None):
        """
        Connect as a superuser to a given database, defaulting to the postgres table.
        """

        if not dbname:
            dbname = 'postgres'

        return psycopg2.connect(
            dbname=dbname,
            user=self.superuser,
            password=self.superuser_pass,
            host=self.host
        )

    def _connect_user(self, dbname=None):
        """
        Connect as the new user to a given database, defaulting to the postgres table.
        """

        if not dbname:
            dbname = 'postgres'

        return psycopg2.connect(
            dbname=dbname,
            user=self.user,
            password=self.user_pass,
            host=self.host
        )

    def create_user_role(self):
        """
        Connect as superuser and create a new role for self.user.
        """

        try:
            connection = self._connect_superuser()
            connection.autocommit = True
            cursor = connection.cursor()

            query = sql.SQL("CREATE ROLE {user} WITH PASSWORD %s NOSUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;").format(
                user=sql.Identifier(self.user)
            )
            cursor.execute(query, (self.user_pass,))
            cursor.close()
            connection.close()

            print(f"Role {self.user} created successfully.")
        except Exception as e:
            print(f"Error creating role: {e}")

    def create_database_with_role(self):
        """
        Set role to self.user and create a new database.
        """

        try:
            connection = self._connect_superuser()
            connection.autocommit = True
            cursor = connection.cursor()

            cursor.execute(sql.SQL("SET ROLE {user};").format(user=sql.Identifier(self.user)))
            cursor.execute(sql.SQL("CREATE DATABASE {dbname};").format(dbname=sql.Identifier(self.dbname)))

            cursor.close()
            connection.close()

            print(f"Database {self.dbname} owned by {self.user} created successfully.")
        except Exception as e:
            print(f"Error creating database: {e}")

    def add_postgis_extension(self):
        """
        Connect to the database as superuser and add PostGIS extension.
        """

        try:
            connection = self._connect_superuser(self.dbname)
            connection.autocommit = True
            cursor = connection.cursor()

            cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

            cursor.close()
            connection.close()

            print("PostGIS extension added successfully.")
        except Exception as e:
            print(f"Error adding PostGIS extension: {e}")

    def setup_database(self):
        """
        Run all commands required to set up the LCAT database.
        """

        self.create_user_role()
        self.create_database_with_role()
        self.add_postgis_extension()

    def test_new_user_capabilities(self):
        """
        Test whether the newly created role can:
            - Login
            - Create a database
            - Create a table
            - Insert data into the table
            - Select data from the table
            - Drop the table
            - Drop the database
        """

        test_dbname = f"{self.user}_test_db"

        try:
            # Step 1: Connect as the new user to the default database
            connection = self._connect_user()
            connection.autocommit = True
            cursor = connection.cursor()
            print(f"User {self.user} logged in successfully.")

            # Step 2: Create a new test database
            cursor.execute(sql.SQL("CREATE DATABASE {dbname};").format(dbname=sql.Identifier(test_dbname)))
            print(f"Test database '{test_dbname}' created successfully.")

            # Close the connection to the default database
            cursor.close()
            connection.close()

            # Step 3: Connect to the new test database as the new user
            connection = self._connect_user(dbname=test_dbname)
            connection.autocommit = True
            cursor = connection.cursor()

            # Step 4: Create a test table in the new test database
            create_table_query = sql.SQL("CREATE TABLE test_table (id SERIAL PRIMARY KEY, name TEXT NOT NULL);")
            cursor.execute(create_table_query)
            print("Test table created successfully.")

            # Step 5: Insert data into the test table
            insert_query = sql.SQL("INSERT INTO test_table (name) VALUES (%s);")
            cursor.execute(insert_query, ('Test Name 1',))
            cursor.execute(insert_query, ('Test Name 2',))
            cursor.execute(insert_query, ('Test Name 3',))
            print("Data inserted into test table successfully.")

            # Step 6: Select data from the test table
            cursor.execute("SELECT * FROM test_table;")
            rows = cursor.fetchall()
            print("Selecting data from test table...")
            for row in rows:
                print(row)
            print("Data selected successfully.")

            # Step 7: Drop the test table
            drop_table_query = sql.SQL("DROP TABLE test_table;")
            cursor.execute(drop_table_query)
            print("Test table dropped successfully.")

            # Close the cursor and connection to the test database
            cursor.close()
            connection.close()

            # Step 8: Connect as the user and drop the test database
            connection = self._connect_user()
            connection.autocommit = True
            cursor = connection.cursor()

            cursor.execute(sql.SQL("DROP DATABASE {dbname};").format(dbname=sql.Identifier(test_dbname)))
            print(f"Test database '{test_dbname}' dropped successfully.")

            # Close the cursor and connection
            cursor.close()
            connection.close()

        except Exception as e:
            print(f"Error testing new user capabilities: {e}")
