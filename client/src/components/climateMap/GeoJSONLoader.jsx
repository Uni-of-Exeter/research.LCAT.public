/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import { useEffect } from "react";
import { useMap, useMapEvents } from "react-leaflet";

// Meters/Pixel Zoom Level (1-19) - requires geometry in OS 27700
const m2px = [
    78271.52, 39135.76, 19567.88, 9783.94, 4891.97, 2445.98, 1222.99, 611.5, 305.75, 152.87, 76.44, 38.22, 19.11, 9.55,
    4.78, 2.39, 1.19, 0.6, 0.3,
];

const GeoJSONLoader = ({ apicall, table, setLoading, handleSetGeojson }) => {
    const map = useMap();

    // Base URL prepend for development
    const getBaseURL = () => {
        return process.env.NODE_ENV === "development" ? "http://localhost:3000" : "";
    };

    // Function to fetch GeoJSON data
    const getGeojson = async () => {
        setLoading(true);
        try {
            const bounds = map.getBounds();
            const tolerance = m2px[map.getZoom() - 1];

            const params = new URLSearchParams({
                table,
                left: bounds._southWest.lng,
                bottom: bounds._southWest.lat,
                right: bounds._northEast.lng,
                top: bounds._northEast.lat,
                tolerance,
            });

            const response = await fetch(`${getBaseURL()}${apicall}?${params}`);
            const geojsonData = await response.json();

            handleSetGeojson(geojsonData);
        } catch (error) {
            console.error("Error fetching GeoJSON data:", error);
        } finally {
            setLoading(false);
        }
    };

    // Trigger GeoJSON load on region table change or map movement
    useMapEvents({
        moveend: getGeojson,
    });

    useEffect(() => {
        getGeojson();
    }, [table]);

    return null;
};

export default GeoJSONLoader;
