# LCAT - Theory

## Visual guide - start here

A visual PDF guide to this process can be found [here](https://github.com/Uni-of-Exeter/research.LCAT.public/blob/autumn-clean-up/docs/files/lcat_data_pipeline_overview.pdf), or at `docs/files/lcat_data_pipeline_overview.pdf`.

## Introduction

LCAT links together boundary information and climate predictions, allowing users to view predictions for their selected regions. The general process is as follows:

1. For each region, find the overlapping climate grid cells
2. Average the climate data for these overlapping cells
3. Serve this to the user

## Climate data

LCAT uses the [CHESS-SCAPE](https://catalogue.ceda.ac.uk/uuid/8194b416cbee482b89e0dfbe17c5786c/) dataset, a dataset that provides climate predictions for different variables up to 2080. This dataset is an ensemble of four different realisations of future climate for each of four different representative concentration pathway scenarios (RCP2.6, RCP4.5, RCP6.0 and RCP8.5), provided both with and without bias correction.

From the release article abstract by `Robinson et al`, which can be found [here](https://essd.copernicus.org/articles/15/5371/2023/):

```text
"CHESS-SCAPE is a 1 km resolution dataset containing 11 near-surface meteorological variables that can be used to as input to many different impact models. The variables are available at several time resolutions, from daily to decadal means, for the years 1980–2080. It was derived from the state-of-the art regional climate projections in the United Kingdom Climate Projections 2018 (UKCP18) regional climate model (RCM) 12 km ensemble, downscaled to 1 km using a combination of physical and empirical methods to account for local topographic effects. CHESS-SCAPE has four ensemble members, which were chosen to span the range of temperature and precipitation change in the UKCP18 ensemble, representing the ensemble climate model uncertainty.

CHESS-SCAPE consists of projections for four emissions scenarios, given by the Representative Concentration Pathways 2.6, 4.5, 6.0 and 8.5, which were derived from the UKCP18 RCM RCP8.5 scenarios using time shifting and pattern scaling. These correspond to UK annual warming projections of between 0.9–1.9 K for RCP2.6 up to 2.8–4.3 K for RCP8.5 between 1980–2000 and 2060–2080. Little change in annual precipitation is projected, but larger changes in seasonal precipitation are seen with some scenarios projecting large increases in precipitation in the winter (up to 22 %) and large decreases in the summer (up to −39 %). All four RCP scenarios and ensemble members are also provided with bias correction, using the CHESS-met historical gridded dataset as a baseline."
```

```text
Robinson, E.L. et al. (2023) ‘Chess-scape: High-resolution future projections of multiple climate scenarios for the United Kingdom derived from downscaled United Kingdom Climate Projections 2018 regional climate model output’, Earth System Science Data, 15(12), pp. 5371–5401. doi:10.5194/essd-15-5371-2023. 
```

Please note that LCAT uses Ensemble 1, and RCPs 6.0 and 8.5 only. Bias corrected data are used in LCAT where possible, however, for some regions (Northern Ireland and the Isles of Scilly) only non-bias corrected data are available.

## Methods

LCAT uses two methods to serve the user climate predictions for their selected regions. When selecting a single region, these methods result in the same climate data served. For both methods, we have already stored the overlapping climate grid cells for each region in the database.

### 1. Cell method

This method is used when regions are smaller, and overlap fewer climate grid cells. The computational cost of calculating the average climate prediction of a smaller number of grid cells is lower. Given we have already calculated the overlapping grid cells and stored these in the database, the following is performed on the fly:

1. For the selected regions, get the unique overlapping climate grid cells from the database
2. Calculate the unique overlapping cells (the discrete, or the mathematical set)
3. Get and average the climate data for these cells
4. Serve this to the user

### 2. Cache method

As some larger regions cover thousands of cells, we need to cache some of these average climate results to ensure acceptable performance in the tool. We perform the following cache method for UK Counties and Unitary Authorities, LA Districts, and the Isle of Man:

1. For each unique region in the boundary (i.e. every county), get the overlapping climate grid cells
2. Get and average the climate data for these overlapping cells
3. Store this averaged climate data for the unique region in the database

We then have two cases:

* a. User selects single region: we serve the single cached row of climate data
* b. User selects multiple regions: for each region, we get each cached row, and serve the average of these cached rows

Whilst this cache method speeds up the tool performance, there is an accuracy penalty. In case b, when the user selects multiple adjacent regions, some grid cells will be "counted twice." For example, if the user selects Devon and Cornwall, cells along the boundary between the two counties will be included in the cached rows for both regions.

In the cell method, we have the chance to take the discrete overlapping cells, but we cannot do this for the cache method. However, as these regions are large, the effect of this should be small.
