# LCAT data module

## Summary

* This module contains classes to process CHESS-SCAPE NetCDF files and create a PostgreSQL database (or tables within).
* There is some setup required if you want to recreate the LCAT database. Please read the documentation at `research.lcat.public/docs` to get started.
* Once data has been downloaded and installed, run the example notebooks at `research.lcat.public/data/examples`.

## Running the tests

Unit tests are located in `data/tests/unit/` and are run from the `data/` directory using Poetry:

```bash
cd data
poetry install
poetry run pytest
```

Each source module in `data/src/` has a corresponding test file. Coverage is printed to the terminal automatically.
