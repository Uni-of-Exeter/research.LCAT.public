# Development before 2024 Copyright (C) Then Try This and University of Exeter
# Development from 2024 Copyright (C) University of Exeter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Common Good Public License Beta 1.0 as
# published at http://www.cgpl.org
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Common Good Public License Beta 1.0 for more details.

# This script creates a command line interface for building and updating
# the climate tool database, as well as providing documentation of the
# recipes for how it's done

# link counties -> msoa -> lsoa to speed up average calculations

from shapely.geometry import shape, Point


def load_centroids(db):
    q = f"select gid,ST_AsGeoJSON(ST_Transform(geom,4326))::json from lsoa;"
    db.cur.execute(q)
    print("executed...")
    lsoas = []
    r = db.cur.fetchone()
    while r:
        print(r[0])
        lsoas.append([r[0], shape(r[1]).centroid])
        r = db.cur.fetchone()
    return lsoas


def lsoa_to_msoa(db):
    db.create_tables({"hierarchy_lsoa_to_msoa": [["msoa", "int"], ["lsoa", "int"]]})

    print("loading lsoa geom")
    lsoas = load_centroids(db)

    # for each msoa
    q = f"select gid from msoa;"
    db.cur.execute(q)
    for msoa_geo_id in db.cur.fetchall():
        q = f"select ST_AsGeoJSON(ST_Transform(geom,4326))::json from msoa where gid={msoa_geo_id[0]}"
        db.cur.execute(q)
        msoa_geo = shape(db.cur.fetchone()[0])
        count = 0
        for lsoa in lsoas:
            if msoa_geo.contains(lsoa[1]):
                count += 1
                q = f"insert into hierarchy_lsoa_to_msoa (msoa, lsoa) values ({msoa_geo_id[0]},{lsoa[0]});"
                db.cur.execute(q)
        print("msoa " + str(msoa_geo_id) + " has " + str(count) + " lsoas inside")
        db.conn.commit()


def lsoa_to_counties(db):
    db.create_tables({"hierarchy_lsoa_to_counties": [["county", "int"], ["lsoa", "int"]]})

    print("loading lsoa geom")
    lsoas = load_centroids(db)

    # for each msoa
    q = f"select gid from counties;"
    db.cur.execute(q)
    for county_geo_id in db.cur.fetchall():
        q = f"select ST_AsGeoJSON(ST_Transform(geom,4326))::json from counties where gid={county_geo_id[0]}"
        db.cur.execute(q)
        county_geo = shape(db.cur.fetchone()[0])
        count = 0
        for lsoa in lsoas:
            if county_geo.contains(lsoa[1]):
                count += 1
                q = f"insert into hierarchy_lsoa_to_counties (county, lsoa) values ({county_geo_id[0]},{lsoa[0]});"
                db.cur.execute(q)
        print("county " + str(county_geo_id) + " has " + str(count) + " lsoas inside")
        db.conn.commit()
