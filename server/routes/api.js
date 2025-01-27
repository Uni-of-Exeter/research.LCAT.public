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
const { Client } = require("pg");

require("dotenv").config();

// Setup connection
var username = process.env.DB_USER;
var password = process.env.DB_PASS;
var host = process.env.DB_HOST;
var database = process.env.DB_DATABASE;
var conString = "postgres://" + username + ":" + password + "@" + host + "/" + database;

// Load boundary details once at startup
let all_boundary_details = {};
initialiseBoundaryDetails();

/// GET BOUNDARY DATA FROM DB ///

// Function to fetch boundary details from the PostgreSQL table and store in memory
async function fetchBoundaryDetails() {
    try {
        const client = new Client(conString);
        await client.connect();

        const result = await client.query("SELECT * FROM boundary_details");
        const boundary_details = {};

        result.rows.forEach((row) => {
            let tableName = "boundary_" + row.boundary_identifier;

            boundary_details[tableName] = {
                identifier: row.boundary_identifier,
                print_name: row.print_name,
                name_col: row.shapefile_name_col,
                source_srid: row.source_srid,
                srid: row.db_srid,
                boundary_table_name: row.boundary_table_name,
                overlap_table_name: row.overlap_table_name,
                method: row.method,
            };
        });
        await client.end();
        console.log("Boundary details successfully fetched from the database.");
        return boundary_details;
    } catch (error) {
        console.error("Error fetching boundary details from the database:", error);
    }
}

// Initialise boundary details
async function initialiseBoundaryDetails() {
    try {
        all_boundary_details = await fetchBoundaryDetails();
    } catch (error) {
        console.error("Error initializing boundary details:", error);
    }
}

// For a given boundary dataset, get all region gids and names in geojson dataset
router.get("/all_regions", async function (req, res) {
    try {
        const { boundary } = req.query;

        // Validate query parameter
        if (!boundary) {
            return res.status(400).send({ error: "Missing 'boundary' parameter" });
        }

        // Ensure `all_boundary_details` is initialized
        if (Object.keys(all_boundary_details).length === 0) {
            await initialiseBoundaryDetails();
        }

        // Retrieve table details from `all_boundary_details`
        const boundaryDetails = all_boundary_details[boundary];
        if (!boundaryDetails) {
            return res.status(400).send({ error: "Invalid boundary table" });
        }

        const query = `
            SELECT gid, ${boundaryDetails.name_col} AS name
            FROM ${boundary};
        `;

        const client = new Client(conString);
        await client.connect();

        try {
            const result = await client.query(query);
            res.json(result.rows);
        } finally {
            await client.end();
        }
    } catch (err) {
        console.error("Error:", err.message || err);
        res.status(500).send({ error: "Internal Server Error" });
    }
});

// Get GeoJSONs of regions given a bounding box and detail
// Tolerance from zoom level
router.get("/region", async function (req, res) {
    try {
        let { table, tolerance, left, bottom, right, top } = req.query;

        tolerance = parseFloat(tolerance);
        left = parseFloat(left);
        bottom = parseFloat(bottom);
        right = parseFloat(right);
        top = parseFloat(top);

        if (isNaN(tolerance) || isNaN(left) || isNaN(bottom) || isNaN(right) || isNaN(top)) {
            return res.status(400).send({ error: "Invalid input parameters" });
        }

        if (Object.keys(all_boundary_details).length === 0) {
            await initialiseBoundaryDetails();
        }

        // Retrieve table details
        const boundaryDetails = all_boundary_details[table];
        if (!boundaryDetails) {
            return res.status(400).send({ error: "Invalid table" });
        }

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
                            'name', ${boundaryDetails.name_col}
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
                ST_Transform(ST_MakeEnvelope($2, $3, $4, $5, 4326), ${boundaryDetails.srid})
            );
        `;

        const result = await client.query(get_region_query, [tolerance, left, bottom, right, top]);

        // Send the result as GeoJSON
        if (result.rows.length > 0) {
            res.json(result.rows[0].json_build_object);
        } else {
            res.status(404).send({ error: "No data found" });
        }

        await client.end();
    } catch (err) {
        console.error("Error:", err);
        res.status(500).send({ error: "Internal Server Error" });
    }
});

// Get bounding box of array of regions
router.get("/bounding_box", async (req, res) => {
    const tableName = req.query.tableName;
    let gids = req.query.gids || [];

    if (!Array.isArray(gids)) {
        gids = [gids];
    }

    if (!tableName || gids.length === 0) {
        return res.status(400).json({ error: "Invalid parameters." });
    }

    const query = `
        SELECT
          ST_XMin(ext) AS min_lon,
          ST_YMin(ext) AS min_lat,
          ST_XMax(ext) AS max_lon,
          ST_YMax(ext) AS max_lat
        FROM (
          SELECT ST_Extent(
                   ST_Transform(geom, 4326)
                 ) AS ext
          FROM ${tableName}
          WHERE gid = ANY($1)
        ) sub;
      `;

    const client = new Client(conString);
    await client.connect();

    try {
        const result = await client.query(query, [gids]);

        // If there's no result or bounding box is null, respond accordingly
        if (result.rows.length === 0 || result.rows[0].min_lon == null) {
            return res.json({ bbox: null });
        }

        const row = result.rows[0];
        const bbox = [
            parseFloat(row.min_lon),
            parseFloat(row.min_lat),
            parseFloat(row.max_lon),
            parseFloat(row.max_lat),
        ];

        return res.json({ bbox });
    } catch (err) {
        console.error("Error fetching bounding box:", err);
        return res.status(500).json({ error: "Internal server error." });
    } finally {
        await client.end();
    }
});

/// GET CHESS-SCAPE CLIMATE DATA FROM DB ///

// CHESS-SCAPE helper function: generate climate column SQL
function buildAvgClimateCols() {
    const averageClimateColNames = [];
    const variables = ["tas", "sfcWind", "pr", "rsds"];
    const decades = ["1980", "1990", "2000", "2010", "2020", "2030", "2040", "2050", "2060", "2070"];

    for (const variable of variables) {
        for (const decade of decades) {
            averageClimateColNames.push(`AVG("${variable}_${decade}") as "${variable}_${decade}"`);
        }
    }

    return averageClimateColNames;
}

// Build query string: cache method - uses cache tables in database (large regions)
function buildCacheQuery(boundaryDetails, locations, rcp, season, averageColNames) {
    const cacheTable = `cache_${boundaryDetails.identifier}_to_${rcp}_${season}`;
    const locationGids = locations.join(",");

    return `
        SELECT ${averageColNames}
        FROM ${cacheTable}
        WHERE gid IN (${locationGids});
        `;
}

// Build query string: cell method - performs calculations on the fly from CHESS-SCAPE tables
function buildCellQuery(boundaryDetails, locations, rcp, season, averageColNames) {
    const gridTable = `grid_overlaps_${boundaryDetails.identifier}`;
    const chessTable = `chess_scape_${rcp}_${season}`;
    const locationGids = locations.join(",");

    const innerSelectCellsQuery = `
        (SELECT DISTINCT grid_cell_id
        FROM ${gridTable} 
        WHERE gid IN (${locationGids}))
        `;

    const selectClimateQuery = `
        SELECT ${averageColNames.join(",")} 
        FROM ${chessTable} 
        WHERE grid_cell_id IN ${innerSelectCellsQuery};
        `;

    return selectClimateQuery;
}

// Check table name helper function: check front end table name is valid
function is_valid_boundary(tableName) {
    return [
        "boundary_uk_counties",
        "boundary_la_districts",
        "boundary_lsoa",
        "boundary_msoa",
        "boundary_parishes",
        "boundary_sc_dz",
        "boundary_ni_dz",
        "boundary_iom",
    ].includes(tableName);
}

router.get("/chess_scape", async (req, res) => {
    try {
        const locations = Array.isArray(req.query.locations) ? req.query.locations : [req.query.locations];
        const rcp = req.query.rcp;
        const season = req.query.season;
        const boundaryTableName = req.query.boundary;

        // Validate input
        if (
            !locations ||
            !is_valid_boundary(boundaryTableName) ||
            !["summer", "winter", "annual"].includes(season) ||
            !["rcp60", "rcp85"].includes(rcp)
        ) {
            return res.status(400).send({ error: "Invalid parameters" });
        }

        const boundaryDetails = all_boundary_details[boundaryTableName];
        if (!boundaryDetails) {
            return res.status(400).send({ error: "Invalid boundary" });
        }

        // Get query method
        const method = boundaryDetails.method;
        const averageClimateColNames = buildAvgClimateCols();

        // Build query based on variables and method
        let query;
        if (method === "cell") {
            query = buildCellQuery(boundaryDetails, locations, rcp, season, averageClimateColNames);
        } else {
            query = buildCacheQuery(boundaryDetails, locations, rcp, season, averageClimateColNames);
        }

        // Connect and execute
        const client = new Client(conString);
        await client.connect();

        const result = await client.query(query);
        res.json(result.rows);

        await client.end();
    } catch (err) {
        console.error("Error while executing query:", err);
        res.status(500).send({ error: "An error occurred" });
    }
});

/// OTHER ROUTES ///

router.get("/ping", function (req, res) {
    res.send();
    res.end();
});

module.exports = router;
