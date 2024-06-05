# Development before 2024 Copyright (C) Then Try This and University of Exeter
# Development from 2024 Copyright (C) University of Exeter

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Common Good Public License Beta 1.0 as
# published at http://www.cgpl.org

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Common Good Public License Beta 1.0 for more details.

import geojson
import psycopg2
from shapely.geometry import shape, Point


def centroids(db, geo_table, base, base_epsg):
    # get the tile geometry in lat/lng
    db.create_tables(
        {f"{geo_table}_{base}_mapping": [["id", "serial primary key"], ["geo_id", "int"], ["lsoa_id", "int"]]}
    )

    print("loading geometry " + geo_table)
    q = f"select gid,ST_AsGeoJSON(ST_Transform(geom,4326))::json from {geo_table}"
    db.cur.execute(q)
    geometry = db.cur.fetchall()
    print("loaded geometry")

    for c, geo_id in enumerate(geometry):
        geo = geo_id[1]
        count = 0

        geo_shape = shape(geo)

        # load centroids of all lsoas within the current boundaries bounding box
        q = f"""select gid,ST_Centroid(ST_Transform(geom,4326))::json from boundary_{base} 
        where geom && ST_Transform(ST_MakeEnvelope({geo_shape.bounds[0]},{geo_shape.bounds[1]},{geo_shape.bounds[2]},{geo_shape.bounds[3]},4326),{base_epsg});"""
        db.cur.execute(q)
        lsoas = db.cur.fetchall()
        for n, lsoa in enumerate(lsoas):
            # find the lsoa that have centres inside of this boundary
            if geo_shape.contains(shape(lsoa[1])):
                q = f"insert into {geo_table}_{base}_mapping (geo_id,lsoa_id) values ({geo_id[0]},{lsoa[0]})"
                db.cur.execute(q)
                count += 1

        # none inside (problem with really small unaligned boundares like parishes)
        if count == 0:
            print("dropping through to adding all")
            for n, lsoa in enumerate(lsoas):
                # just add the closest anyway
                q = f"insert into {geo_table}_{base}_mapping (geo_id,lsoa_id) values ({geo_id[0]},{lsoa[0]})"
                db.cur.execute(q)
                count += 1

        db.conn.commit()
        print(geo_table + " " + str(count) + "/" + str(len(lsoas)) + ": " + str(int((c / len(geometry)) * 100)) + "%")
