# LCAT - Data module & database

## Introduction

Before we can run the application locally, we need to construct a database that the app can read from. This contains boundary information, processed and averaged climate data, and references. We use PostgreSQL, a common relational database framework, with the PostGIS extension installed.

To get a working LCAT database, we have two approaches. We can either rebuild the database from a database dump, or process the data files from scratch using the Python module in `data/`. Both methods are valid.

**Note**: Previous versions of the LCAT tool processed intermediate GeoTIFFs, derivatives of the original CHESS-SCAPE files. These methods have been deprecated, in favour of processing the NetCDF files directly.
In addition, we offload as much processing to PostgreSQL as possible: this has reduced database build times by ~95%, to 5 minutes.

## Install Postgres

**Note**: Instructions have been provided for MacOS. Feel free to use `brew`, however, instructions will not be identical if you do.

Before starting, Postgres needs to be installed on your system. Visit [here](https://postgresapp.com/) and download the Postgres application, following the setup instructions. Find the install location/data directory using the Postgres server settings button, and start the Postgres server with:

```bash
pg_ctl -D <postgres-data-directory> start
```

In my case, on an M2 MacBook Pro:

```bash
pg_ctl -D /Users/simonkirby/Library/Application\ Support/Postgres/var-16 start
```

This can also be done using the application, by clicking on the `start` button.

Note that for `brew` this would be:

```bash
brew services start postgresql
```

We can check that the server is active with `pgrep`:

```bash
pgrep -l postgres
```

Log in to the Postgres service, and then view users, using the following commands:

```bash
psql postgres
```

```bash
\du
```

Quit the service with `\q` or `ctrl-D`.

## Install data module

A Python module has been written to process the data files, mainly to build the LCAT database, but also with methods to perform some visualisation on a built database. We make heavy use of [Psycopg2](https://www.psycopg.org/docs/) as a database adaptor, and use [Poetry](https://python-poetry.org/) to manage dependencies. NetCDF file management is performed with [Xarray](https://docs.xarray.dev/en/stable/).

To install, first ensure Poetry is installed on your system. I would recommend changing this setting:

```bash
poetry config virtualenvs.in-project true
```

Run the following from the project root:

```bash
cd data
poetry install
```

A `.venv` folder will be created in the data module root. We will be able to select this as a kernel when running a notebook.

## Collect data files

Before we start, we will need to collect the data files required for processing by the data scripts, and set up the paths in `data/config.yml`. You will need the following files, as listed in `docs/sources.md`:

* CHESS-SCAPE data files (a subset, listed in the docs)
* Boundary Shapefiles (.shp)
* A references file (.csv)
* A Kumu export file (.json)

In the future, we hope to provide these files for download via an S3 bucket.

## Set up paths

We store path locations and database credentials in `data/config.yml`. Create this with;

```bash
cd data
touch config.yml
```

And enter the following data. Credential values are up to you, and paths will be unique to your system. remember that you will need to enter these values into a `server/.env` file later on.

```yml
# DATABASE CONFIG
superuser: postgres
superuser_pass: postgres
host: localhost
dbname: example_db_name
user: example_db_username
user_pass: example_db_password

# CHESS-SCAPE DATA
chess_scape_netcdf_location: "/data_store/chess-scape"

# BOUNDARY DATA: SHAPEFILES
uk_counties_shp: "/data_store/boundaries/uk_counties.shp"
la_districts_shp: "/data_store/boundaries/la_districts.shp"
lsoa_shp: "/data_store/boundaries/lsoa.shp"
msoa_shp: "/data_store/boundaries/msoa.shp"
parishes_shp: "/data_store/boundaries/parishes.shp"
sc_dz_shp: "/data_store/boundaries/sc_dz.shp"
ni_dz_shp: "/data_store/boundaries/ni_dz.shp"
iom_shp: "/data_store/boundaries/iom.shp"

# REFERENCES & KUMU EXPORT: .CSV (from Google Sheets) and JSON
references_csv: "/data_store/references/references.csv"
kumu_json: "/data_store/references/kumu_export.json"
```

## Build database

Two approaches are provided, the first operates on the raw data files, the second uses a compressed database dump to restore from.

### Approach a. Building from raw data

We can run the processing scripts on the raw data files. A notebook has been provided to do this in one shot. This can be found at [data/examples/build_db.ipynb](../data/examples/build_db.ipynb).

### Approach b. Restoring from dump

Alternatively, you can restore from a database dump using `pg_restore`. A notebook has also been provided at [data/examples/db_from_dump.ipynb](../data/examples/db_from_dump.ipynb).

Please note that the database dump required for this will be found on S3 shortly.

## Database visualisation

If you want to test the database works before installing the rest of the application, you can visualise some of the data with the notebook found at [data/examples/visualise_db.ipynb](../data/examples/visualise_db.ipynb).
