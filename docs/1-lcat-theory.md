# LCAT - Theory

## Visual guide - start here

A visual PDF guide to this process can be found [here](https://github.com/Uni-of-Exeter/research.LCAT.public/blob/autumn-clean-up/docs/files/lcat_data_pipeline_overview.pdf), or at `docs/files/lcat_data_pipeline_overview.pdf`.

## Introduction

LCAT links together boundary information and climate predictions, allowing users to view predictions for their selected regions. The general process is as follows:

1. For each region, find the overlapping climate grid cells
2. Average the climate data for these overlapping cells
3. Serve this to the user

## Climate data



## Methods

LCAT uses two methods to serve the user climate predictions for their selected regions. When selecting a single region, these methods result in the same climate data served. For both methods, we have already stored the overlapping climate grid cells for each region in the database.

### 1. Cell method

This method is used when regions are smaller, and overlap fewer climate grid cells. The computational cost of calculating the average climate prediction of a smaller number of grid cells is lower. Given we have already calculated the overlapping grid cells and stored these in the database, the following is performed on the fly:

1. For the selected regions, get the unique overlapping climate grid cells from the database
2. Calculate the unique overlapping cells (the discrete, or the mathematical set)
3. Get and average the climate data for these cells
4. Serve this to the user

### 2. Cache method

As some larger regions cover thousands of cells, we need to cache some of these average climate results to ensure acceptable performance in the tool. We perform the following cache method for UK Counties, LA Districts, and the Isle of Man:

1. For each unique region in the boundary (i.e. every county), get the overlapping climate grid cells
2. Get and average the climate data for these overlapping cells
3. Store this averaged climate data for the unique region in the database

We then have two cases:

* a. User selects single region: we serve the single cached row of climate data
* b. User selects multiple regions: for each region, we get each cached row, and serve the average of these cached rows

Whilst this cache method speeds up the tool performance, there is an accuracy penalty. In case b, when the user selects multiple adjacent regions, some grid cells will be "counted twice." For example, if the user selects Devon and Cornwall, cells along the boundary between the two counties will be included in the cached rows for both regions.

In the cell method, we have the chance to take the discrete overlapping cells, but we cannot do this for the cache method. However, as these regions are large, the effect of this should be small.
