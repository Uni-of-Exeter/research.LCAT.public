# Development before 2024 Copyright (C) Then Try This and University of Exeter
# Development from 2024 Copyright (C) University of Exeter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Common Good Public License Beta 1.0 as
# published at http://www.cgpl.org
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Common Good Public License Beta 1.0 for more details.

# This script imports climate predictions downloaded from the
# http://uk-cri.org climate risk indicators, these are based on the
# MET Office HADGEM RCP85 model. They are 12km gridded model
# predictions, and include other higher level risk indicators we might
# be able to make use of in future.

# We import a grid as GEOJSON geometry and the model data each into
# their own tables indexed by grid cell id

import csv
import yaml
import psycopg2
import geojson
import json

from builder import climate_db


def import_grid(db, fn):
    grid_cols = {"location": 0, "east": 1, "north": 2}
    features = []

    with open(fn) as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i > 0:
                x = int(row[grid_cols["east"]])
                y = int(row[grid_cols["north"]])
                size_metres_east = 12000
                size_metres_north = -12000
                features.append(
                    geojson.Feature(
                        id=row[grid_cols["location"]],
                        geometry=geojson.Polygon(
                            [
                                [
                                    (x, y),
                                    (x + size_metres_east, y),
                                    (x + size_metres_east, y + size_metres_north),
                                    (x, y + size_metres_north),
                                ]
                            ]
                        ),
                        properties={},
                    )
                )
    db.import_geojson_feature("uk_cri_grid", "27700", geojson.FeatureCollection(features))
    db.conn.commit()


def load_data(db, table, fn):
    grid_cols = {"year": 0, "location": 1, "lowest": 2, "2nd_low": 3, "median": 4, "2nd_high": 5, "highest": 6}
    print("loading " + table)
    with open(fn) as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i > 0:
                # only import median data for each location
                year = int(row[grid_cols["year"]])
                location = int(row[grid_cols["location"]])
                median = float(row[grid_cols["median"]])
                q = f"insert into {table} (location,year,median) values ({location},{year},{median});"
                db.cur.execute(q)
        db.conn.commit()


data_cols = {
    "uk_cri_grid": [["id", "serial primary key"], ["geom", "geometry(geometry, 27700)"], ["properties", "jsonb"]]
}

model = "hadgem_rcp85"
# temp average/min/max and rainfall predictions
variables = ["tavg", "tmin", "tmax", "rain"]
# annual and winter/summer months
periods = ["ann", "djf", "jja"]


def remove(db):
    tables = ["uk_cri_grid"]
    for variable in variables:
        for period in periods:
            tables.append(model + "_" + variable + "_" + period)

    db.delete_tables(tables)


def load(db, path):
    for variable in variables:
        for period in periods:
            data_cols[model + "_" + variable + "_" + period] = [
                ["id", "serial primary key"],
                ["location", "int"],
                ["year", "int"],
                ["median", "real"],
            ]

    db.create_tables(data_cols)

    # load the grid as a geojson
    import_grid(db, path + "location_codes.csv")

    # load the climate data into ordinary tables
    for variable in variables:
        for period in periods:
            table = variable + "_" + period
            fn = path + table + "_dc_ghadgem_rcp85_12km.csv"
            if variable == "rain":
                fn = path + table + "_pc_ghadgem_rcp85_12km.csv"
            load_data(db, model + "_" + table, fn)
