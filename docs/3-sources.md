# LCAT - Data sources

All the sources of data used for LCAT are listed here, including their authorities, and links to the original downloads. Some details regarding the climate variables used are provided, but further documentation on these will be added in due course.

## Boundaries

LCAT uses a number of boundary datasets, which are used to communicate local climate predictions. The following boundary datasets are currently used in the tool:

| Regions | Type | Notes | Time span | LCAT postgres table/col | Original Format | Coordinate system | Source | Authority |
| - | -| - | - | - | - | - | - | - |
| UK | Counties | Includes Northern Ireland Districts | Dec 2023  | `boundary_uk_counties` | ESRI shapefile | EPSG 27700 | <https://geoportal.statistics.gov.uk/datasets/3188a83fb19f42818acb213cffc64c58_0/explore?location=53.281691%2C-3.316939%2C5.64> | ONS |
| UK | Local Authority Districts | Includes Northern Ireland Districts | Dec 2023 | `boundary_la_districts` | ESRI shapefile | EPSG 27700 | <https://geoportal.statistics.gov.uk/datasets/8148555d1e104ead8887b7939eb47ab3_0/explore?location=51.690437%2C-2.041250%2C6.71> | ONS |
| England and Wales | Parishes | England/Wales only | May 2023 | `boundary_parishes` | ESRI shapefile | EPSG 27700 | <https://geoportal.statistics.gov.uk/datasets/3cc64670a1d443369db274861689d3a9_0/explore?location=52.723973%2C-2.489483%2C6.78> | ONS |
| England and Wales | LSOA | Areas with average population 1500 people or 650 households | Dec 2021 | `boundary_lsoa` | ESRI shapefile | EPSG 27700 | <https://geoportal.statistics.gov.uk/datasets/d082c4679075463db28bcc8ca2099ade_0/explore?location=55.249653%2C-2.419198%2C8.00> | ONS |
| England and Wales | MSOA | | Dec 2021  | `boundary_msoa` | ESRI shapefile | EPSG 27700 | <https://geoportal.statistics.gov.uk/maps/ed5c7b7d733d4fd582281f9bfc9f02a2> | ONS |
| Scotland | Data Zones | Scottish eqv. of LSOA | 2011 (revised Oct 2021) | `boundary_sc_dz` | ESRI shapefile | EPSG 27700 | <https://spatialdata.gov.scot/geonetwork/srv/api/records/7d3e8709-98fa-4d71-867c-d5c8293823f2> | spatialdata.gov.scot |
| Northern Ireland | Data Zones | Northern Ireland eqv. of LSOA | 2021 | `boundary_ni_dz` | ESRI shapefile | EPSG 29902 | <https://www.nisra.gov.uk/support/geography/data-zones-census-2021> | NISRA |
| Isle of Man | Regional boundary | Island boundary only (no districts) | 2015 | `boundary_iom` | ESRI shapefile | EPSG 4326 | <https://purl.stanford.edu/nk743nh6214> | Stanford |

## Climate model

Climate data used in LCAT are through the CHESS-SCAPE dataset. This is an ensemble dataset derived from the 2018 UK Climate Projections, itself produced by the Met Office Hadley Centre. CHESS-SCAPE provides future projections of meteorological variables across the United Kingdom and Northern Ireland, downscaling them to a 1 km grid.

This data can be accessed through the CEDA archive [here](https://catalogue.ceda.ac.uk/uuid/8194b416cbee482b89e0dfbe17c5786c/). Please note that the whole dataset is 11 TB: LCAT uses only 10 GB of this, as daily variable predictions are not required in the tool. Details on exactly which files are used will be provided soon. Further details on CHESS-SCAPE can be found in the accompanying documents, for example, in the [release article](https://essd.copernicus.org/articles/15/5371/2023/).

Please note that LCAT now processes the raw NetCDF files directly to create its intermediate tables and database. These scripts will be provided so that interested parties can run the tool locally if desired.

| Type | Notes | Time span | Regions | Original Format | Coordinate system | Source URL | Authority |
| -| - | - | - | - | - | - | - |
| NetCDF climate projections | Annual and Seasonal files for RCP 6.0 and RCP 8.5 | 1980-2079 | Great Britain & IoM | NetCDF | EPSG 27700 | <https://uk-scape.ceh.ac.uk> | CEDA |

### Climate variables

Predictions for the following climate variables are extracted from the NetCDF files. Currently Min and Max Temperatures are stored in the database but not used.

| Variable Name| Shorthand Name | Source Units | LCAT Units | Climate phenomenon it relates to |
| -| - | - | - | - |
| Precipitation | pr | kg/m2/s | mm/day | Rainfall |
| Wind speed | sfcWind | m/s | m/s | Windiness |
| Downward shortwave radiation | rsds | W/m2 | W/m2 | Cloudiness (inverse) |
| Air temperature | tas | K | deg Celsius | Temperature |
| Max air temperature | tasmax | K | deg Celsius | Max temperature |
| Min air temperature | tasmin | K | deg Celsius | Min temperature |

These predictions are across the following Representative Concentration Pathways (RCP's):

| RCPs | Seasons | Decades | Variables | No. data tables/cols |
| -| - | - | - | - |
| 6.0, 8.5 (2 RCPs) | Annual, summer, winter (3 seasons) | 1980 – 2070 (10 decades) | 6 variables | 6 tables each with ~60 columns |

### Climate data files

The whole CHESS-SCAPE dataset is ~11 TB, due to the inclusion of daily climate predictions. LCAT only needs a subset of these files, which are shown using `tree` below:

```markdown
chess-scape
│
└── data
    ├── rcp60
    │   └── 01
    │       ├── annual
    │       │   ├── chess-scape_rcp60_01_pr_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_01_rsds_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_01_sfcWind_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_01_tasmax_uk_1km_annual_19801201-20801130.nc
    │       │   └── chess-scape_rcp60_01_tasmin_uk_1km_annual_19801201-20801130.nc
    │       └── seasonal
    │           ├── chess-scape_rcp60_01_pr_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_01_rsds_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_01_sfcWind_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_01_tas_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_01_tasmax_uk_1km_seasonal_19801201-20801130.nc
    │           └── chess-scape_rcp60_01_tasmin_uk_1km_seasonal_19801201-20801130.nc
    ├── rcp60_bias-corrected
    │   └── 01
    │       ├── annual
    │       │   ├── chess-scape_rcp60_bias-corrected_01_pr_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_bias-corrected_01_rsds_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_bias-corrected_01_sfcWind_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_bias-corrected_01_tas_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp60_bias-corrected_01_tasmax_uk_1km_annual_19801201-20801130.nc
    │       │   └── chess-scape_rcp60_bias-corrected_01_tasmin_uk_1km_annual_19801201-20801130.nc
    │       └── seasonal
    │           ├── chess-scape_rcp60_bias-corrected_01_pr_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_bias-corrected_01_rsds_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_bias-corrected_01_sfcWind_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_bias-corrected_01_tas_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp60_bias-corrected_01_tasmax_uk_1km_seasonal_19801201-20801130.nc
    │           └── chess-scape_rcp60_bias-corrected_01_tasmin_uk_1km_seasonal_19801201-20801130.nc
    ├── rcp85
    │   └── 01
    │       ├── annual
    │       │   ├── chess-scape_rcp85_01_pr_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp85_01_rsds_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp85_01_sfcWind_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp85_01_tas_uk_1km_annual_19801201-20801130.nc
    │       │   ├── chess-scape_rcp85_01_tasmax_uk_1km_annual_19801201-20801130.nc
    │       │   └── chess-scape_rcp85_01_tasmin_uk_1km_annual_19801201-20801130.nc
    │       └── seasonal
    │           ├── chess-scape_rcp85_01_pr_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp85_01_rsds_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp85_01_sfcWind_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp85_01_tas_uk_1km_seasonal_19801201-20801130.nc
    │           ├── chess-scape_rcp85_01_tasmax_uk_1km_seasonal_19801201-20801130.nc
    │           └── chess-scape_rcp85_01_tasmin_uk_1km_seasonal_19801201-20801130.nc
    └── rcp85_bias-corrected
        └── 01
            ├── annual
            │   ├── chess-scape_rcp85_bias-corrected_01_pr_uk_1km_annual_19801201-20801130.nc
            │   ├── chess-scape_rcp85_bias-corrected_01_rsds_uk_1km_annual_19801201-20801130.nc
            │   ├── chess-scape_rcp85_bias-corrected_01_sfcWind_uk_1km_annual_19801201-20801130.nc
            │   ├── chess-scape_rcp85_bias-corrected_01_tas_uk_1km_annual_19801201-20801130.nc
            │   ├── chess-scape_rcp85_bias-corrected_01_tasmax_uk_1km_annual_19801201-20801130.nc
            │   └── chess-scape_rcp85_bias-corrected_01_tasmin_uk_1km_annual_19801201-20801130.nc
            └── seasonal
                ├── chess-scape_rcp85_bias-corrected_01_pr_uk_1km_seasonal_19801201-20801130.nc
                ├── chess-scape_rcp85_bias-corrected_01_rsds_uk_1km_seasonal_19801201-20801130.nc
                ├── chess-scape_rcp85_bias-corrected_01_sfcWind_uk_1km_seasonal_19801201-20801130.nc
                ├── chess-scape_rcp85_bias-corrected_01_tas_uk_1km_seasonal_19801201-20801130.nc
                ├── chess-scape_rcp85_bias-corrected_01_tasmax_uk_1km_seasonal_19801201-20801130.nc
                └── chess-scape_rcp85_bias-corrected_01_tasmin_uk_1km_seasonal_19801201-20801130.nc
```

## References

LCAT serves the user references, articles, and other pieces of research related to the options they have selected in the tool. These have been aggregated by the LCAT team, and can be found [here](https://docs.google.com/spreadsheets/d/18c_5SSG9VmagkX3bdC_F2eDtzFz9oQJvPQbhEfwmUNc/edit?gid=0#gid=0). They are reviewed periodically by the team.

### Licenses

Digital boundary products and reference maps are used under the Open Government Licence. For UK county, LA district, Parish, LSOA, MSOA, and Northern Ireland Data Zone boundary data, the following apply:

- Source: Office for National Statistics licensed under the Open Government Licence v.3.0
- Contains OS data © Crown copyright and database right 2024

For Scotland Data Zone boundary data, the following applies:

- Contains public sector information licensed under the Open Government Licence v3.0

And for Isle of Man boundary data, the license conditions can be found at the source URL.
