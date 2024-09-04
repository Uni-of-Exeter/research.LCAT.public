/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

var express = require("express");
var router = express.Router();

// PostgreSQL and PostGIS module and connection setup
const { Client, Query } = require("pg");

require("dotenv").config();

// Setup connection
var username = process.env.DB_USER;
var password = process.env.DB_PASS;
var host = process.env.DB_HOST;
var database = process.env.DB_DATABASE;
var conString = "postgres://" + username + ":" + password + "@" + host + "/" + database;

function is_valid_boundary(table) {
    return [
        "boundary_uk_counties",
        "boundary_la_districts",
        "boundary_lsoa",
        "boundary_msoa",
        "boundary_parishes",
        "boundary_sc_dz",
        "boundary_ni_dz",
        "boundary_iom",
    ].includes(table);
}

const boundary_details = {
    boundary_uk_counties: { name: "CTYUA23NM", srid: 27700, method: "cache" },
    boundary_la_districts: { name: "LAD23NM", srid: 27700, method: "cache" },
    boundary_lsoa: { name: "LSOA21NM", srid: 27700, method: "cell" },
    boundary_msoa: { name: "MSOA21NM", srid: 27700, method: "cell" },
    boundary_parishes: { name: "PAR23NM", srid: 27700, method: "cell" },
    boundary_sc_dz: { name: "Name", srid: 27700, method: "cell" },
    boundary_ni_dz: { name: "DZ2021_nm", srid: 27700, method: "cell" },
    boundary_iom: { name: "NAME_ENGLI", srid: 27700, method: "cell" },
};

const vardec = [];
for (let variable of ["tas", "sfcWind", "pr", "rsds"]) {
    for (let decade of ["1980", "1990", "2000", "2010", "2020", "2030", "2040", "2050", "2060", "2070"]) {
        vardec.push("avg(" + variable + "_" + decade + ") as " + variable + "_" + decade);
    }
}

// Get GeoJSONs of regions given a bounding box and detail
// Tolerance from zoom level
router.get("/region", async function (req, res) {
    try {
        // Sanitize and validate inputs
        let { table, tolerance, left, bottom, right, top } = req.query;

        tolerance = parseFloat(tolerance);
        left = parseFloat(left);
        bottom = parseFloat(bottom);
        right = parseFloat(right);
        top = parseFloat(top);

        if (isNaN(tolerance) || isNaN(left) || isNaN(bottom) || isNaN(right) || isNaN(top)) {
            return res.status(400).send({ error: "Invalid input parameters" });
        }

        // Retrieve table details safely
        const boundary = boundary_details[table];
        if (!boundary) {
            return res.status(400).send({ error: "Invalid table" });
        }

        const { name: name_col, srid } = boundary;

        // Use connection pool for better performance
        const client = new Client(conString);
        await client.connect();

        const props = ""; // Placeholder for additional properties

        // Query: Build GeoJSON object for the given bounding box
        const get_region_query = `
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(
                    json_build_object(
                        'type', 'Feature',
                        'properties', json_build_object(
                            'gid', gid,
                            'name', ${name_col}
                            ${props ? `, ${props}` : ""}
                        ),
                        'geometry', ST_AsGeoJSON(
                            ST_Transform(
                                ST_Simplify(
                                    ST_Transform(geom, 27700), $1
                                ), 4326
                            )
                        )::json
                    )
                )
            )
            FROM ${table}
            WHERE ST_Intersects(
                geom, 
                ST_Transform(ST_MakeEnvelope($2, $3, $4, $5, 4326), ${srid})
            );
        `;

        // Execute the query with parameterized inputs
        const result = await client.query(get_region_query, [tolerance, left, bottom, right, top]);

        // Send the result as GeoJSON
        if (result.rows.length > 0) {
            res.json(result.rows[0].json_build_object);
        } else {
            res.status(404).send({ error: "No data found" });
        }

        // Close the client connection
        await client.end();
    } catch (err) {
        console.error("Error:", err);
        res.status(500).send({ error: "Internal Server Error" });
    }
});

router.get("/chess_scape", function (req, res) {
    let locations = req.query.locations;
    let rcp = req.query.rcp;
    let season = req.query.season;
    let boundary = req.query.boundary;

    if (
        locations != undefined &&
        is_valid_boundary(boundary) &&
        ["summer", "winter", "annual"].includes(season) &&
        ["rcp60", "rcp85"].includes(rcp)
    ) {
        if (!Array.isArray(locations)) {
            locations = [locations];
        }

        q = "";
        // the two different methods of climate data averaging...
        if (boundary_details[boundary].method == "cell") {
            // for small boundaries or large cells
            let region_grid = boundary + "_grid_mapping";
            var sq = `(select distinct tile_id from ` + region_grid + ` where geo_id in (` + locations.join() + `))`;
            q = `select ` + vardec.join() + ` from chess_scape_` + rcp + `_` + season + ` where id in ` + sq + `;`;
        } else {
            // for large boundaries or small cells
            let cache_table = "cache_" + boundary + "_to_chess_scape_" + rcp + "_" + season;
            q =
                `select ` +
                vardec.join() +
                ` from ` +
                cache_table +
                ` where boundary_id in (` +
                locations.join() +
                `);`;
        }

        var client = new Client(conString);
        client.connect();
        var query = client.query(new Query(q));

        query.on("row", function (row, result) {
            result.addRow(row);
        });
        query.on("end", function (result) {
            res.send(result.rows);
            res.end();
            client.end();
        });
        query.on("error", function (err, result) {
            console.log("------------------error-------------------------");
            console.log(req);
            console.log(err);
        });
    }
});

// general purpose for debugging
router.get("/geojson", function (req, res) {
    let table = req.query.table;
    let tolerance = req.query.tolerance;
    let left = req.query.left;
    let bottom = req.query.bottom;
    let right = req.query.right;
    let top = req.query.top;

    var client = new Client(conString);
    client.connect();

    var str_query =
        `select json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(json_build_object(
                   'type', 'Feature',
                   'geometry', ST_AsGeoJSON(ST_Transform(geom,4326))::json
                   ))
              )
         	  from ` +
        table +
        ` where geom && ST_MakeEnvelope(` +
        left +
        `, ` +
        bottom +
        `, ` +
        right +
        `, ` +
        top +
        `, 4326);`;

    console.log(str_query);
    var query = client.query(new Query(str_query));

    query.on("row", function (row, result) {
        result.addRow(row);
    });
    query.on("end", function (result) {
        res.send(result.rows[0].json_build_object);
        res.end();
        client.end();
    });
});

router.get("/ping", function (req, res) {
    res.send();
    res.end();
});

module.exports = router;
