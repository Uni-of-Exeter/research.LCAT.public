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


def cache_climate(db, boundary_table, climate_table):
    table = "cache_" + boundary_table + "_to_" + climate_table
    variables = ["tas", "sfcWind", "pr", "rsds"]
    decades = [
        "1980",
        "1990",
        "2000",
        "2010",
        "2020",
        "2030",
        "2040",
        "2050",
        "2060",
        "2070",
    ]

    data_cols = {table: [["boundary_id", "int primary key"]]}

    vardec = []
    ivardec = []
    quotes = []
    for decade in decades:
        for variable in variables:
            data_cols[table].append([variable + "_" + decade, "real"])
            vardec.append("avg (" + variable + "_" + decade + ") as " + variable + "_" + decade)
            ivardec.append(variable + "_" + decade)
            quotes.append("%s")
    vardec_str = ",".join(vardec)
    ivardec_str = ",".join(ivardec)
    quotes_str = ",".join(quotes)

    db.create_tables(data_cols)

    q = f"select gid from {boundary_table}"
    db.cur.execute(q)
    for geo_id in db.cur.fetchall():
        print(table + " " + str(geo_id[0]))
        s = f"(select distinct tile_id from {boundary_table}_grid_mapping where geo_id={geo_id[0]})"
        q = f"select {vardec_str} from {climate_table} where id in {s}"
        db.cur.execute(q)
        values = db.cur.fetchall()
        q = f"insert into {table} (boundary_id,{ivardec_str}) values (%s,{quotes_str})"
        v = (geo_id[0],) + values[0]
        db.cur.execute(q, v)
        db.conn.commit()


# Lochaber West - 01
# Calculate impacts below using￼RCP 6.0 seasonal average￼Winter predictions for the decade￼2070's compared with the baseline climate records for the 1980's.
# Increased Temperature + 1.84 °C
# Increased Rainfall + 0.42 mm/year
# Decreased Cloudiness + 1.76 Watts/m2
# Decreased Windiness - 0.10 m/sec


# Calculate impacts below using￼RCP 6.0 seasonal average￼Winter predictions for the decade￼2070's compared with the baseline climate records for the 1980's.
# The climate forecast in Rosehearty and Strathbeg - 02 by 2070 is
# Increased Temperature + 2.06 °C
# Increased Rainfall + 0.00 mm/year
# Decreased Cloudiness + 1.97 Watts/m2
# Decreased Windiness - 0.15 m/sec

# Calculate impacts below using￼RCP 8.5 seasonal average￼Summer predictions for the decade￼2070's compared with the baseline climate records for the 1980's.
# The climate forecast in Rosehearty and Strathbeg - 02 by 2070 is
# Increased Temperature + 4.03 °C
# Increased Rainfall + 0.05 mm/year
# Decreased Cloudiness + 28.75 Watts/m2
# Decreased Windines - 0.29 m/sec
