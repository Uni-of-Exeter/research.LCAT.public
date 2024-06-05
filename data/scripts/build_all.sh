#!/bin/bash

# Development before 2024 Copyright (C) Then Try This and University of Exeter
# Development from 2024 Copyright (C) University of Exeter

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Common Good Public License Beta 1.0 as
# published at http://www.cgpl.org

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Common Good Public License Beta 1.0 for more details.

# Run build commands in sequence
./build chess_tiff_nuke
./build chess_tiff_import
./build chess_tif_grid chess_scape_rcp60_pr_annual_1980.tif

./build boundary_lsoa
./build boundary_msoa
./build boundary_uk_counties
./build boundary_la_districts
./build boundary_sc_dz
./build boundary_parishes

./build link_uk_counties
./build link_lsoa
./build link_msoa
./build link_la_districts
./build link_sc_dz
./build link_parishes

./build cache_all_climate

./build link_all_to_lsoa
./build link_all_to_sc_dz

# Unused build scripts below

# ./build climatejust_load_nfvi
# ./build climatejust_average_nfvi

# ./build load_imd_from_csv
# ./build add_average_imd
# ./build stats

# extra stats
# ./build climate_stats
# ./build vuln_stats
# ./build vuln_avg

# ./build network_json
# ./build network_refs

# hazards/coast
# ./build hazards_coastal