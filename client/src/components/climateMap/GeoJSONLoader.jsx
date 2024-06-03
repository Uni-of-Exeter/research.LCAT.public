// Development before 2024 Copyright (C) Then Try This and University of Exeter
// Development from 2024 Copyright (C) University of Exeter
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the Common Good Public License Beta 1.0 as
// published at http://www.cgpl.org
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// Common Good Public License Beta 1.0 for more details.

import { useMap, useMapEvents } from "react-leaflet";
import { useEffect } from "react";

// Meters/Pixel Zoom Level (1-19) - requires geometry in OS 27700
const m2px = [
    78271.52, 39135.76, 19567.88, 9783.94, 4891.97, 2445.98, 1222.99, 611.5, 305.75, 152.87, 76.44, 38.22, 19.11, 9.55,
    4.78, 2.39, 1.19, 0.6, 0.3,
];

function GeoJSONLoader(props) {
    const map = useMap();

    async function getGeojson() {
        props.loadingCallback(true);
        try {
            let b = map.getBounds();
            let prepend = "";
            if (process.env.NODE_ENV === "development") {
                prepend = "http://localhost:3000";
            }

            let response = await fetch(
                prepend +
                    props.apicall +
                    "?" +
                    new URLSearchParams({
                        table: props.table,
                        left: b._southWest.lng,
                        bottom: b._southWest.lat,
                        right: b._northEast.lng,
                        top: b._northEast.lat,
                        tolerance: m2px[map.getZoom() - 1],
                    }),
            );
            response.json().then((v) => {
                props.loadingCallback(false);
                props.callback(v);
            });
        } catch (error) {
            console.error(error);
        }
    }
    // update when moved
    useMapEvents({
        moveend: (e) => {
            getGeojson();
        },
    });
    // update first time. or when the region table changes
    useEffect(() => {
        getGeojson();
    }, [props.table]);

    return null;
}

export default GeoJSONLoader;
