# LCAT - Database build information

## Introduction

The database links together open data from various public repositories. These files have been archived [here](http://data-lcat-uk.s3-website.eu-west-2.amazonaws.com/).

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
