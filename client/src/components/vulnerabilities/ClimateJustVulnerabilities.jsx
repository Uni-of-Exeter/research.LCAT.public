/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

// If not already imported globally, you'll also want to include Leaflet's CSS:
import "leaflet/dist/leaflet.css";

import L from "leaflet";
import React, { useEffect, useState } from "react";
import LoadingOverlay from "react-loading-overlay-ts";

const ClimateJustVulnerabilities = ({ regionBbox }) => {
    const [loadingVulnerabilities, setLoadingVulnerabilities] = useState(false);

    // Create a ref to attach the Leaflet map to a DOM element

    var container = L.DomUtil.get("vulnerabilityMap");
    if (container != null) {
        container._leaflet_id = null;
    }

    const getBboxCentre = (regionBbox) => {
        let bboxLonCentre = -1.8;
        let bboxLatCentre = 50.85;

        if (regionBbox.length === 4) {
            bboxLonCentre = (regionBbox[0] + regionBbox[2]) / 2;
            bboxLatCentre = (regionBbox[1] + regionBbox[3]) / 2;
        }
        return [bboxLatCentre, bboxLonCentre];
    };

    useEffect(() => {
        const bbox = regionBbox.join(",");
        // Initialize the map using the ref

        const bboxCentre = getBboxCentre(regionBbox);

        const vulnerabilityMap = L.map("vulnerabilityMap").setView(bboxCentre, 9);

        // Add a basemap layer
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
        }).addTo(vulnerabilityMap);

        // Define the bounding box – can be dynamic, if you like
        // const bbox = "-3.2,50.5,-1.5,51.2"; // xmin, ymin, xmax, ymax

        // Construct the ArcGIS FeatureServer URL with the bounding box filter
        const choroplethUrl = `https://services1.arcgis.com/SfF67lOzKAmtSACX/arcgis/rest/services/ClimateJust_FS_WFL3/FeatureServer/11/query?where=1=1&geometry=${bbox}&geometryType=esriGeometryEnvelope&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=true&f=geojson`;

        // (Optional) Layer with place names for each district
        const placesUrl =
            "https://services1.arcgis.com/SfF67lOzKAmtSACX/ArcGIS/rest/services/ClimateJust_FS_WFL3/FeatureServer/2/query?where=1=1&outFields=*&returnGeometry=true&f=geojson";
        let placesLayer = null; // if needed for referencing later

        setLoadingVulnerabilities(true);

        // Fetch the GeoJSON data for the choropleth layer
        fetch(choroplethUrl)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                if (!data || data.type !== "FeatureCollection") {
                    throw new Error("Invalid GeoJSON object");
                }

                // Define the color scale (example based on PeopleOver75)
                function getColor(value) {
                    return value > 20
                        ? "#BD0026"
                        : value > 15
                          ? "#E31A1C"
                          : value > 10
                            ? "#FC4E2A"
                            : value > 5
                              ? "#FD8D3C"
                              : value > 0
                                ? "#FEB24C"
                                : "#a0adff";
                }

                // Style function for each feature
                function style(feature) {
                    console.log(feature.properties)
                    return {
                        fillColor: getColor(feature.properties.PeopleOver75 || 0),
                        weight: 1,
                        opacity: 1,
                        color: "#cccccc",
                        dashArray: "3",
                        fillOpacity: 0.8,
                    };
                }

                // Add the GeoJSON layer with choropleth styling
                L.geoJSON(data, {
                    style,
                    onEachFeature: (feature, layer) => {
                        layer.bindPopup(`
              <b>Place (LSOA name):</b> ${feature.properties.LSOA11NM || "N/A"}<br/>
              <b>Vulnerability Due to Age:</b> ${feature.properties.PeopleOver75 || "N/A"}%
            `);
                    },
                }).addTo(vulnerabilityMap);

            })
            .catch((error) => console.error("Error fetching or processing data:", error))
            .finally(() => {
                // Regardless of success or error, we're done loading
                setLoadingVulnerabilities(false);
            });
    }, [regionBbox]);

    return (
        <div>
            <div>
                <h1>Climate Just Vulnerabilities</h1>

                <p>
                    This is a test of integrating the Climate Just vulnerabilities into LCAT via their ArcGIS feature
                    service. LSOA-level vulnerabilities are shown for the selected regions (defined by the bounding lat,
                    lon box of the selected regions).
                </p>
            </div>
            <LoadingOverlay active={loadingVulnerabilities} spinner text={"Loading vulnerabilities"}>
                <div id={"vulnerabilityMap"} style={{ height: "500px", width: "100%" }} />
            </LoadingOverlay>
        </div>
    );
};

export default ClimateJustVulnerabilities;
