# LCAT - Database build information

**Note**: Previous versions of the LCAT tool processed intermediate GeoTIFFs, derivatives of the original CHESS-SCAPE files.
These methods have been deprecated, in favour of processing the NetCDF files directly.
In addition, we offload as much processing to PostgreSQL as possible: this has reduced database build times by ~95%, to 5 minutes.
Please see the example notebooks in `data/examples` for more information.

## Theory

### Introduction

LCAT links together boundary information and climate predictions, allowing users to view predictions for their selected regions. The general process is as follows:

1. For each region, find the overlapping climate grid cells
2. Average the climate data for these overlapping cells
3. Serve this to the user

**Note**: A visual guide to this process can be found at `docs/files/lcat_data_pipeline_overview.pdf`.

### Methods

LCAT uses two methods to serve the user climate predictions for their selected regions. When selecting a single region, these methods are identical.

#### 1. Cell method

This method is used when regions are smaller, and overlap fewer climate grid cells. The computational cost of calculating the average climate prediction of a smaller number of cells is lower. The following is performed on the fly:

1. For the selected regions, get the unique overlapping climate grid cells (the discrete cells, or the set) from the database
2. Average the climate data for these cells
3. Serve this to the user

#### 2. Cache method

As some larger regions cover many thousands of cells, we need to cache some of these results to ensure good performance in the tool. We perform the following cache method for UK Counties, LA Districts, and the Isle of Man:

1. For each unique region in the boundary (i.e. every county), find the overlapping climate grid cells
2. Average the climate data for these overlapping cells
3. Store this averaged climate data for the unique region in the database

We then have two cases:

* a. User selects single region: serve the single cached row of climate data
* b. User selects multiple regions: serve the average of the cached rows

Whilst this cache method speeds up the tool performance, there is an accuracy penalty. In case b, when the user selects multiple adjacent regions, some grid cells will be "counted twice." For example, if the user selects Devon and Cornwall, cells along the boundary between the counties will be included in the cached rows for both regions.

In the cell method, we have the chance to take the discrete overlapping cells, but we cannot do this for the cache method. However, as these regions are large, the effect of this should be small.

## Building from raw data

Follow along with the notebook at `data/examples/building_from_data.ipynb`.

## Restoring from backup

Follow along with the notebook at `data/examples/restoring_from_backup.ipynb`.
