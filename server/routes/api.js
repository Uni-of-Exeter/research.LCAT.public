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
var conString = "postgres://" + username + ":" + password + "@" + host + "/" + database; // Your Database Connection

function is_valid_boundary(table) {
    return [
        "boundary_lsoa",
        "boundary_msoa",
        "boundary_uk_counties",
        "boundary_la_districts",
        "boundary_parishes",
        "boundary_sc_dz",
    ].includes(table);
}

// const vulnerabilities = [
//     "imd_rank","imd_decile","a1","a2","h1","h2","i1","i2","i3","i4","i5","f1","f2","k1",
//     "t1","t2","m1","m2","m3","c1","l1","e1","n1","n2","n3","s1","s2","s3","s4"
// ]

const boundary_details = {
    boundary_uk_counties: { name: "name_2", srid: 32630, method: "cache" },
    boundary_la_districts: { name: "lad22nm", srid: 27700, method: "cache" },
    boundary_msoa: { name: "msoa11nm", srid: 27700, method: "cell" },
    boundary_parishes: { name: "parncp19nm", srid: 27700, method: "cell" },
    boundary_sc_dz: { name: "name", srid: 4326, method: "cell" },
    boundary_lsoa: { name: "lsoa11nm", srid: 27700, method: "cell" },
};

const vardec = [];
for (let variable of ["tas", "sfcWind", "pr", "rsds"]) {
    for (let decade of ["1980", "1990", "2000", "2010", "2020", "2030", "2040", "2050", "2060", "2070"]) {
        vardec.push("avg(" + variable + "_" + decade + ") as " + variable + "_" + decade);
    }
}

// get GeoJSONs of regions given a bounding box and detail
// tolerance from zoom level
router.get("/region", function (req, res) {
    let table = req.query.table;
    let tolerance = req.query.tolerance;
    let left = req.query.left;
    let bottom = req.query.bottom;
    let right = req.query.right;
    let top = req.query.top;

    var name_col = boundary_details[table].name;
    var srid = boundary_details[table].srid;

    if (is_valid_boundary(table)) {
        var client = new Client(conString);
        client.connect();

        let props = ""; //"'imdscore', imdscore";
        //props = propertyCols.map(key => "'"+key+"', "+key).join(", ");

        // build a new geojson in 4326 coords given the bounding box
        // and zoom detail, add the name of the region and it's IMD
        // score (simplify is specified in metres/pixel so need to
        // ensure geometry e.g. counties are in 27700 coords before
        // ST_Simplify)
        var lsoa_query =
            `select json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(json_build_object(
                   'type', 'Feature',
                   'properties', json_build_object('gid', gid,
                                                   'name', ` +
            name_col +
            ` 
                                                   ` +
            props +
            `),
                   'geometry', ST_AsGeoJSON(
                                 ST_Transform(
                                   ST_Simplify(
                                     ST_Transform(geom,27700),$1),4326))::json
                   ))
              )
         	  from ` +
            table +
            ` where geom && ST_TRANSFORM(ST_MakeEnvelope($2,$3,$4,$5,4326),` +
            srid +
            `);`;

        var query = client.query(new Query(lsoa_query, [tolerance, left, bottom, right, top]));

        query.on("row", function (row, result) {
            result.addRow(row);
        });
        query.on("end", function (result) {
            res.send(result.rows[0].json_build_object);
            res.end();
            client.end();
        });
        query.on("error", function (err, result) {
            console.log("------------------error-------------------------");
            //console.log(req);
            console.log(err);
        });
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
