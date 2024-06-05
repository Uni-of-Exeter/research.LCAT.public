# Development before 2024 Copyright (C) Then Try This and University of Exeter
# Development from 2024 Copyright (C) University of Exeter

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Common Good Public License Beta 1.0 as
# published at http://www.cgpl.org

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Common Good Public License Beta 1.0 for more details.

import netCDF4 as nc
from builder import climate_db
from psycopg2.extras import execute_values
import numpy
import geojson


def print_info(path):
    ds = nc.Dataset(path)
    print(ds)


def load_grid(db, fn):
    data_cols = {
        "chessscape_grid": [
            ["id", "serial"],
            ["geom", "geometry(geometry, 4326)"],
            ["properties", "jsonb"],
        ],
    }

    db.create_tables(data_cols)

    features = []

    ds = nc.Dataset(fn)
    print(ds.variables)
    print(ds.dimensions)
    y_size = ds.dimensions["y"].size
    x_size = ds.dimensions["x"].size
    features = []
    for x in range(0, x_size - 1):
        for y in range(0, y_size - 1):
            features.append(
                geojson.Feature(
                    id=x * y_size + y,
                    geometry=geojson.Polygon(
                        [
                            [
                                (float(ds["lon"][y][x]), float(ds["lat"][y][x])),
                                (
                                    float(ds["lon"][y + 1][x]),
                                    float(ds["lat"][y + 1][x]),
                                ),
                                (
                                    float(ds["lon"][y + 1][x + 1]),
                                    float(ds["lat"][y + 1][x + 1]),
                                ),
                                (
                                    float(ds["lon"][y][x + 1]),
                                    float(ds["lat"][y][x + 1]),
                                ),
                            ]
                        ]
                    ),
                    properties={},
                )
            )
        print(x / x_size)

    db.import_geojson_feature(
        "chessscape_grid", "4326", geojson.FeatureCollection(features)
    )
    db.conn.commit()


def nuke(db, table):
    data_cols = {
        table: [
            ["id", "serial primary key"],
            ["location", "int"],
            ["season", "int"],
            ["tas", "real"],
            ["tasmax", "real"],
            ["tasmin", "real"],
            ["sfcWind", "real"],
            ["pr", "real"],
            ["rlds", "real"],
            ["rsds", "real"],
        ]
    }
    db.create_tables(data_cols)


def convert_value(variable, value):
    # convert from kelvin to celsius
    if variable in ["tas", "tasmin", "tasmax"]:
        value -= 273.15
    # convert from kg/m2/s to mm/day (seconds per day)
    # 1kg of rain over 1 m2 is equivalent to 1mm
    if variable == "pr":
        value *= 86400
    return float(value)


def load_data(db, fn, table, variable):
    ds = nc.Dataset(fn)
    time_size = ds.dimensions["time"].size  # P3M = 3 months?
    y_size = ds.dimensions["y"].size
    x_size = ds.dimensions["x"].size
    ## load baseline (0=winter 1980) and future (396=winter 2079)
    for t in range(0, time_size, 396):
        for y in range(0, y_size):
            values = ds[variable][t][y]
            dat = []
            for x in range(0, x_size):
                value = values[x]
                grid_id = x * y_size + y
                if value is not numpy.ma.masked:
                    dat.append([grid_id, t, convert_value(variable, value)])

                    # q=f"""update {table} set {variable}=%s where location=%s and season=%s;
                    #       insert into {table} (location,season,{variable})
                    #       select %s,%s,%s
                    #       where not exists (select 1 from {table} where location=%s and season=%s)
                    #       """
                    # db.cur.execute(q,(float(value), grid_id, t,
                    #                   float(value), grid_id, t,
                    #                   grid_id, t))

            q = f"""with new_values (location,season,{variable}) as (values %s),
                  upsert as ( update {table} m set {variable} = nv.{variable}
                         from new_values nv
                         where m.location = nv.location and m.season=nv.season
                         returning m.* )
                  insert into {table} (location,season,{variable})
                  select location,season,{variable}
                  from new_values
                  where not exists (select 1 from upsert up where up.location=new_values.location and up.season=new_values.season)"""

            print(
                "updating: "
                + variable
                + " "
                + str(y)
                + " of "
                + str(y_size)
                + " t:"
                + str(t)
            )
            # q=f"insert into {table} (location,season,{variable}) values %s on conflict (location,season) do update set {variable} = excluded.{variable};"
            execute_values(db.cur, q, dat)
            db.conn.commit()


# wget -r -nH --cut-dirs=5 -nc "ftp://username:password@ftp.ceda.ac.uk//badc/deposited2021/chess-scape/data/rcp85_bias-corrected/01/seasonal"


def nuke_averages(db, table):
    data_cols = {
        table: [
            ["location", "int primary key"],
            ["tas", "real"],
            ["tasmax", "real"],
            ["tasmin", "real"],
            ["sfcWind", "real"],
            ["pr", "real"],
            ["rlds", "real"],
            ["rsds", "real"],
        ]
    }
    db.create_tables(data_cols)


# def load_averages(db,fn,table,variable):
#     ds = nc.Dataset(fn)
#     time_size = ds.dimensions['time'].size # P3M = 3 months?
#     y_size = ds.dimensions['y'].size
#     x_size = ds.dimensions['x'].size

#     print(type(ds[variable]))

#     print(np.mean(ds[variable].reshape(-1, 3), axis=1)


#     ## load baseline (0=winter 1980) and future (396=winter 2079)
#     for y in range(0,y_size):
#         dat = []
#         for x in range(0,x_size):
#             grid_id = x*y_size+y
#             acc = 0
#             count = 0
#             for t in range(0,time_size,396):
#                 value = ds[variable][t][y][x]
#                 if value is not numpy.ma.masked:
#                     acc+=convert_value(variable,value)
#                     count+=1
#             if count>0:
#                 v = acc/float(count)
#                 print(grid_id,v)
#                 dat.append([grid_id,v])


#         q=f"""with new_values (location,{variable}) as (values %s),
#               upsert as ( update {table} m set {variable} = nv.{variable}
#                          from new_values nv
#                          where m.location = nv.location
#                          returning m.* )
#                   insert into {table} (location,{variable})
#                   select location,{variable}
#                   from new_values
#                   where not exists (select 1 from upsert up where up.location=new_values.location)"""

#         print("updating: "+variable+" "+str(y)+" of "+str(y_size))
#         #q=f"insert into {table} (location,season,{variable}) values %s on conflict (location,season) do update set {variable} = excluded.{variable};"
#         execute_values(db.cur,q,dat)
#         db.conn.commit()


def import_grid(db):
    variable = "tas"
    path = "/home/dave/projects/climate/v2-data/chess/rcp85_bias-corrected/01/seasonal/"
    fn = (
        "chess-scape_rcp85_bias-corrected_01_"
        + variable
        + "_uk_1km_seasonal_19801201-20801130.nc"
    )
    load_grid(db, path + fn)


def import_seasonal_data(db, path, variable):
    fn = (
        "chess-scape_rcp85_bias-corrected_01_"
        + variable
        + "_uk_1km_seasonal_19801201-20801130.nc"
    )
    print(variable)
    load_data(db, path + fn, "chessscape_seasonal", variable)


def import_seasonal_averages(db, path, variable):
    fn = (
        "chess-scape_rcp85_bias-corrected_01_"
        + variable
        + "_uk_1km_seasonal_19801201-20801130.nc"
    )
    print(variable)


#    load_averages(db,path+fn,"chessscape_seasonal_averages",variable)
