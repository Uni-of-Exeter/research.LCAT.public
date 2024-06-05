# LCAT - Database build information

## Introduction

The database links together open data from various public repositories. These files have been archived, and can be downloaded from, [here](http://data-lcat-uk.s3-website.eu-west-2.amazonaws.com/).

If not restoring the database from a backup, the scripts provided in the `data` folder can be used to process the raw data files, and rebuild the database.

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

## Appendix A: GeoTiff CRS

For reference, this is the coordinate reference system for the GeoTiffs:

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
