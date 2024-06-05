# Development before 2024 Copyright (C) Then Try This and University of Exeter
# Development from 2024 Copyright (C) University of Exeter

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Common Good Public License Beta 1.0 as
# published at http://www.cgpl.org

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
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
import json, os
from psycopg2.extras import Json


class db:
    def __init__(self, config):
        self.conf = config
        self.conn = psycopg2.connect(
            f"host={config['host']}\
                                      dbname={config['dbname']} \
                                      user={config['user']} \
                                      password={config['password']}"
        )
        self.cur = self.conn.cursor()

    def create_tables(self, data_cols):
        for t, c in data_cols.items():
            self.cur.execute(f"drop table if exists {t}")
            cols = []
            for col in c:
                cols.append(f"{col[0]} {col[1]}")

            s = ", ".join(cols)
            q = f"create table {t} ({s});"
            print("adding table: " + q)
            self.cur.execute(q)
            self.conn.commit()

    def delete_tables(self, tables):
        for table in tables:
            q = f"drop table if exists {table}"
            print("dropping table: " + q)
            self.cur.execute(q)
            self.conn.commit()

    def import_geojson_feature(self, table, srid, feature_data):
        INSERT_STATEMENT = f"INSERT INTO {table} (id, geom, properties) VALUES (%s, ST_SetSRID(ST_GeomFromGeoJSON(%s), {srid}), %s);"
        if feature_data.get("type") == "FeatureCollection":
            for feature in feature_data["features"]:
                self.import_geojson_feature(table, srid, feature)
        elif feature_data.get("type") == "Feature":
            geojson = json.dumps(feature_data["geometry"])
            str_dict = dict(
                (str(k), str(v)) for k, v in feature_data["properties"].items()
            )
            self.cur.execute(
                INSERT_STATEMENT,
                (feature_data["id"], geojson, json.dumps(feature_data["properties"])),
            )

    def load_shp_geom(self, fn, table, projection):
        # import lsoa from GCS_OSGB_1936 (27700)
        self.delete_tables([table])
        cmd = f"shp2pgsql -I -s {projection} \"{fn}\" {table} | psql postgresql://{self.conf['user']}:{self.conf['password']}@{self.conf['host']}/{self.conf['dbname']}"

        # cmd = f"""ogr2ogr -f "PostgreSQL" PG:"host={self.conf['host']} user={self.conf['user']} dbname={self.conf['dbname']}" -nln {table} -nlt multipolygon {fn}"""

        os.system(cmd)
