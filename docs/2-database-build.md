# LCAT - Database build information

## Introduction

The database links together open data from various public repositories. These files have been archived, and can be downloaded from, [here](http://data-lcat-uk.s3-website.eu-west-2.amazonaws.com/).

If not restoring the database from a backup, the scripts provided in the `data` folder can be used to process the raw data files, and rebuild the database.

## Theory

The database tables are designed to link climate information (the CHESS-SCAPE GeoTIFF files) and boundary information (the shapefiles), allowing users to quickly view climate information for a selected region.

* The original data is CHESS-SCAPE RCP 6.0 & 8.5, with 1 km grid cells. We use the seasonal mean of all 4 model runs. These have been generated by The Turing Institute.
* Intermediatory decade average GeoTIFF files for each variable and season (summer, winter and annual) have then been produced.
* Finally we put all decades and variables together in the same tables separated for RCP and season. These tables are indexed by grid cell location ID based on grid x/y position for quick access.

Two methods have been used, depending on the size of the boundary regions.

### Method 1: Cell lookup (MSOA, Parishes, Data zones, LSOA)

When requesting climate data we specify a list of regions. We lookup all the 1 km grid cells overlapped by all the regions, remove duplicates, and average across the climate model cells. This avoids counting grid cells twice if they overlap with multiple boundaries.

This method is best for larger grid cells or smaller boundaries, as overlaps will have more affect and averaging cells will be a relatively minor computation.

### Method 2: Cached averages (Counties and LA Districts)

We cache all the grid cell averages for each boundary. The computation on the server is simply a matter of averaging the boundaries the user has selected (no secondary conversion to grid cell required).

This method works better for smaller grid cells and larger boundaries. For example, the Scottish Highlands boundary covers thousands of 1 km grid cells. In these cases the effect of duplicating edge cells that overlap neighbouring boundaries will be minimal, and the computation cost becomes problematic.

## Python environment

[Poetry](https://python-poetry.org/) is used to create a virtual environment, and manage project dependencies. Ensure Poetry is available on your system.

Before starting, it can helpful to keep the `.venv` folder in the local project directory. This requires a local config change:

    ```bash
    poetry config virtualenvs.in-project true
    ```

Install dependencies with:

    ```bash
    cd data
    poetry install
    ```

Activate the virtual environment with:

    ```bash
    poetry shell
    ```

This should ensure that the virtual environment is correctly activated. To manually run a Python script with the Poetry environment, run:

    ```bash
    poetry run python my_script.py
    ```

## Setting up `config.yml`

A config file is used to store database credentials and file locations, both required by the data scripts to populate the database. Create `data/config.yml` and populate it with the information below:

    ```yml
    # Database authentication
    user: "<db_username>"
    password: "<db_password>"
    host: "localhost"
    dbname: "<db_name>"

    # Paths to ceda chess scape files
    chess_tiff_path: "<path/to/orignal/tiffs>"
    chess_tiff_decades_path: "<path/to/decades>"

    # Paths to boundary shapefiles
    lsoa_data_shp: "<path/to/shapefile>"
    msoa_data_shp: "<path/to/shapefile>"
    la_districts_data_shp: "<path/to/shapefile>"
    sc_dz_data_shp: "<path/to/shapefile>"
    uk_counties_data_shp: "<path/to/shapefile>"
    parishes_data_shp: "<path/to/shapefile>"
    ```

## Processing steps

With the Python environment set up, data files downloaded, and `config.yml` populated, run the build commands below. First, build all the decade averaged GeoTiff files from the yearly ones:

    ```bash
    ./build chess_tiff_create_batch
    ```

Create the tables with:

    ```bash
    ./build chess_tiff_nuke
    ```

Populate them with:

    ```bash
    ./build chess_tiff_import
    ```

This populates the database tables with all climate variables and decades so the server can provide them in a single select statement (averaged across boundaries)

We also need to load the grid used by the GeoTIFF files.

    ```bash
    ./build chess_tiff_grid <name_of_a_single_GeoTiff_file>
    ```

Once we have a climate data grid, we need to import the boundaries we wish to use and link them to the climate data grid:

    ```bash
    ./build boundary_<boundary_type>
    ./build link_<boundary_type>
    ```

Run these commands for each boundary. Linking creates a new table `<boundary_type>_grid_mapping`, which is a many to many mapping from boundary IDs to all the climate grid IDs they overlap or intersect with.

Create the caches: this works across all boundaries and all climate RCP/season tables.

    ```bash
    ./build cache_all_climate
    ```

A script has been provided in `data/scripts/build_all.sh`, which shows the build process line by line.

## Appendix A: GeoTIFF CRS

For reference, this is the coordinate reference system for the GeoTIFFs:

    ```wkt
    PROJCS["unnamed",
    GEOGCS["unknown",
        DATUM["unnamed",
        SPHEROID["Spheroid",6377563.396,299.3249646]
        ],
        PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]
    ],
    PROJECTION["Transverse_Mercator"],
    PARAMETER["latitude_of_origin",49],
    PARAMETER["central_meridian",-2],
    PARAMETER["scale_factor",1],
    PARAMETER["false_easting",400000],
    PARAMETER["false_northing",-100000],
    UNIT["metre",1,AUTHORITY["EPSG","9001"]],
    AXIS["Easting",EAST],
    AXIS["Northing",NORTH]
    ]
    ```