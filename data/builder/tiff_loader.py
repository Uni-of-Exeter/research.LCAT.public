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

# Functions to read (and write) GeoTiff climate model files

import rasterio
from builder import climate_db
from psycopg2.extras import execute_values
import numpy
import geojson
from rasterio.plot import show
from pyproj import Transformer

seasons = ["winter", "spring", "summer", "autumn", "annual"]
decades = ["1980", "1990", "2000", "2010", "2020", "2030", "2040", "2050", "2060", "2070"]


def nuke(db, table):
    data_cols = {table: [["id", "serial primary key"]]}

    # optimising for reading - store all the variables for each decade
    # together, this means it's a single select averaging them together
    # across primary key location ids
    for decade in decades:
        data_cols[table].append(["tas_" + decade, "real"])
        data_cols[table].append(["tasmax_" + decade, "real"])
        data_cols[table].append(["tasmin_" + decade, "real"])
        data_cols[table].append(["sfcWind_" + decade, "real"])
        data_cols[table].append(["pr_" + decade, "real"])
        data_cols[table].append(["rsds_" + decade, "real"])

    db.create_tables(data_cols)


def test_print(arr, w, h):
    for x in range(0, h, 10):
        r = ""
        for y in range(0, w, 10):
            v = arr[x][y]
            if v < -9999:
                r += " "
            else:
                r += str(int(v))
        print(r)


def print_check(t, start, end, skip):
    seasons = ["winter", "spring", "summer", "autumn"]
    print(int(t / 4) + 1980, seasons[t % 4], int(start / 4) + 1980, int(end / 4) + 1980)


def avg_slice(start, end, skip, img):
    count = 0
    total = 0
    arr = numpy.zeros((img.height, img.width), numpy.float)
    for t in range(start, end, skip):
        print_check(t, start, end, skip)
        image = img.read(t + 1)
        count += 1
        arr = arr + image
    arr /= count
    test_print(arr, img.width, img.height)
    return arr


def build_season_avg(img, season):
    return [avg_slice(season + d * 40, season + (d + 1) * 40, 4, img) for d in range(0, 10)]


def build_avg(img):
    return [avg_slice(d * 40, (d + 1) * 40, 1, img) for d in range(0, 10)]


def save_tiff(img, arr, table, rcp, variable, season, decade):
    with rasterio.Env():
        profile = img.profile
        profile.update(dtype=rasterio.float32, count=1, compress="lzw")

        fn = table + "_" + rcp + "_" + variable + "_" + seasons[season] + "_" + decades[decade] + ".tif"

        with rasterio.open(fn, "w", **profile) as dst:
            dst.write(arr.astype(rasterio.float32), 1)


def save_averages(db, rcp, fn, table, variable):
    img = rasterio.open(fn)

    for decade in range(0, 10):
        # winter/summer
        for season in [0, 2]:
            print(rcp, variable)
            arr = avg_slice(season + decade * 40, season + (decade + 1) * 40, 4, img)
            save_tiff(img, arr, table, rcp, variable, season, decade)

    # annual
    for decade in range(0, 10):
        print(rcp, variable)
        arr = avg_slice(decade * 40, (decade + 1) * 40, 1, img)
        save_tiff(img, arr, table, rcp, variable, 4, decade)


def print_crs(fn):
    print("hello")
    img = rasterio.open(fn)
    print(img.crs)


def load_grid(db, fn):
    img = rasterio.open(fn)

    print(img.crs)

    time_size = img.count
    x_size = img.width
    y_size = img.height

    data_cols = {
        "chess_scape_grid": [["id", "serial"], ["geom", "geometry(geometry, 4326)"], ["properties", "jsonb"]],
    }

    db.create_tables(data_cols)

    transformer = Transformer.from_crs(img.crs, 4326)

    features = []
    # assumptions to check - coord is centre of pixel?
    for x in range(0, x_size):
        for y in range(0, y_size):

            pos = img.xy(y, x)

            a = transformer.transform(pos[0] - 500, pos[1] - 500)
            b = transformer.transform(pos[0] + 500, pos[1] - 500)
            c = transformer.transform(pos[0] + 500, pos[1] + 500)
            d = transformer.transform(pos[0] - 500, pos[1] + 500)

            # lat/lng = y/x
            features.append(
                geojson.Feature(
                    id=x * y_size + y,
                    geometry=geojson.Polygon([[(a[1], a[0]), (b[1], b[0]), (c[1], c[0]), (d[1], d[0])]], properties={}),
                )
            )
        print("loading grid " + str(int((x / x_size) * 100)) + "%")

    db.import_geojson_feature("chess_scape_grid", "4326", geojson.FeatureCollection(features))
    db.conn.commit()


def load_data(db, fn, table, decade, variable):
    img = rasterio.open(fn)

    vardec = variable + "_" + decade

    time_size = img.count
    x_size = img.width
    y_size = img.height

    print("updating: " + table + " " + variable + " decade:" + decade)

    for y in range(0, y_size):
        values = img.read(1)[y]
        dat = []
        for x in range(0, x_size):
            value = values[x]
            grid_id = x * y_size + y
            if value > -9999:
                dat.append([grid_id, float(value)])

        q = f"""with new_values (id,{vardec}) as (values %s),
        upsert as ( update {table} m set {vardec} = nv.{vardec}
        from new_values nv
        where m.id = nv.id
        returning m.* )
        insert into {table} (id,{vardec})
        select id,{vardec}
        from new_values
        where not exists (select 1 from upsert up where up.id=new_values.id)"""

        # q=f"insert into {table} (location,season,{variable}) values %s on conflict (location,season) do update set {variable} = excluded.{variable};"
        execute_values(db.cur, q, dat)
        db.conn.commit()


def test_data(db, fn, table, variable):
    img = rasterio.open(fn)

    for x in range(0, img.height, 10):
        r = ""
        for y in range(0, img.width, 10):
            v = img.read(1)[x][y]
            if v > -9999:
                r += " "
            else:
                r += str(int(v))
        print(r)


def import_tiffs(db, path, rcp, variable):
    for season in ["annual", "summer", "winter"]:
        for decade in ["1980", "1990", "2000", "2010", "2020", "2030", "2040", "2050", "2060", "2070"]:
            fn = "chess_scape_" + rcp + "_" + variable + "_" + season + "_" + decade + ".tif"
            load_data(db, path + fn, "chess_scape_" + rcp + "_" + season, decade, variable)


def import_grid(db, path, fn):
    load_grid(db, path + fn)


def create_averages(db, rcp, path, variable):
    fn = "chess-scape_" + rcp + "_bias-correctedMEAN_" + variable + ".tif"
    save_averages(db, rcp, path + fn, "chess_scape", variable)
