# LCAT - Installation guide

## Introduction

LCAT (the Local Climate Adaptation Tool) is a 3-tier web application, consisting of a Node Express server, a React client, and a Postgres database. To run this project locally, begin by cloning the project:

    git clone https://github.com/Uni-of-Exeter/research.LCAT.public.git
    cd research.LCAT.public

## 1. Express server

A simple NodeJS [Express](https://expressjs.com/) server is provided. To set up, run:

    cd server
    npm install

Run the server with:

    npm run start

or for local development, Nodemon is provided, by running:

    npm run dev

In both cases, the server is started on port 3000.

## 2. React client

The front end is built in [React](https://react.dev/), using [Vite](https://vitejs.dev/). To set up, run:

    cd client
    npm install --legacy-peer-deps

To launch the Vite development server, run:

    npm run dev

This will launch the web app on port 3001. Access the application at `localhost:3001` in your browser.

### Client production build

To build the client for production, and copy the bundle to the server, run the following:

    npm run build
    mkdir -p server/public
    cp -R client/dist/* server/public

This will use Vite to produce a minified application bundle that is suitable to be statically served. This occurs on port 3000: to view this, visit `localhost:3000` with the server running.

## 3. Postgres database

LCAT uses a Postgres database to store climate data, which is provided to the user in the application via the API (located in the server module). To set this up locally from a database backup, follow the instructions (for macOS) below.

**Note**: You can find detailed instructions for rebuilding the database from the raw data files in `docs/2-database-build.md`. To shortcut this rebuild process, and restore from an existing database, you can download a database backup [here](http://data-lcat-uk.s3-website.eu-west-2.amazonaws.com/dumps/climate_geo_data2_prod_backup_20230829.sql.gz).

### Create .env file

In the server root directory, create a `.env` file containing the database login credentials:

    ```
    DB_USER=db_username
    DB_PASS=db_password
    DB_HOST=localhost:5432
    DB_DATABASE=db_name
    ```

We will use these going forwards.

### Set up & verification

Ensure that [Postgres](https://postgresapp.com/) is set up locally. Identify the install location (`<postgres-data-dir>`), and start the Postgres server:

    pg_ctl -D <postgres-data-dir> start

We can check that the server is active with `pgrep`:

    pgrep -l postgres

Log in to the Postgres service, and then view users, using the following commands:

    ```bash
    psql postgres
    \du
    ```

If at least one user is present, we can proceed. Quit the service with `\q` or `ctrl-d`.

### Create new database

We now need to create a new database with the `Postgis` extension, and a new user with elevated privileges. With the `Postgres` server started, log in as `postgres`:

    ```bash
    psql postgres
    ```

Create a new database. You can check its creation in the Postgres GUI if desired.

    ```bash
    create database db_name;
    ```

Connect to the new database as the `postgres` user (which should have superuser privileges):

    ```bash
    \connect db_name postgres
    ```

Create the `Postgis` extension:

    ```bash
    create extension postgis;
    ```

If `CREATE EXTENSION` is seen, then you have been successful. Log out with `\q`.

### Restore backup into new database

As discussed, the full rebuild process can be shortcut by restoring from a database backup, using the `pg_restore` utility. Download the `.sql` database backup from the `s3` link above. Identify the database backup location and run the following:

    ```bash
    pg_restore -d db_name <path_to_database_backup>
    ```

If the database is not completely empty, you might need to use the `-clean` flag. Once complete, check that the database now contains tables by connecting, and then running:

    ```bash
    \dt
    ```

Finish by quitting with `\q`.

### Create new user

With a populated database, we now need a new user that can connect and view the database/tables. With a started postgres server, create a new user with:

    ```bash
    create user db_username;
    ```

Ensure this username is the same in the `.env` file. If you see `CREATE ROLE`, this has been successful. Note that a `USER` is a `ROLE` with the ability to log in.

Add a password to the new user:

    ```bash
    alter user db_username with encrypted password 'db_password';
    ```

`ALTER ROLE` confirms that this has been successful.

Now grant database access to this user:

    ```bash
    grant all privileges on database db_name to db_username;
    ```

`GRANT` confirms this.

Finally, we also need to make the database tables accessible to the user. Connect to the new database as `postgres`, or another superuser:

    ```bash
    \connect db_name postgres
    ```

Grant new user access to tables:

    ```bash
    grant all privileges on all tables in schema public to db_username;
    ```

As before, `GRANT` confirms this. Disconnect as before with `\q`.

## Running everything

The application should now be fully functional. Launch the server and client (or serve the minified build), select a geographic region, and check that climate data can be viewed.
