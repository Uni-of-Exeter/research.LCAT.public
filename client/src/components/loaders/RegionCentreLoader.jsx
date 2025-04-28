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

import { defaultState } from "../../utils/defaultState";

const RegionCentreLoader = ({ regionType, regions, setRegionsCentre }) => {
    useEffect(() => {
        const fetchRegionCentre = async () => {
            try {
                // do nothing if no regions
                if (!regionType || !regions || regions.length === 0) {
                    setRegionsCentre(defaultState.mapCenter);
                    return;
                }

                const prepend = process.env.NODE_ENV === "development" ? "http://localhost:3000" : "";

                const url = `${prepend}/api/gids_centre`;

                const gids = regions.map((region) => region.id);

                // Fetch data (POST as array of gids)
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        boundary: regionType,
                        gids: gids,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.statusText}`);
                }

                const data = await response.json();

                // Set or unset the centre of the selected regions
                if (data && typeof data.lat === "number" && typeof data.lon === "number") {
                    setRegionsCentre({ lat: data.lat, lon: data.lon });
                } else {
                    setRegionsCentre(defaultState.mapCenter);
                }
            } catch (error) {
                console.error("Error fetching region center:", error);
                setRegionsCentre(defaultState.mapCenter);
            }
        };

        fetchRegionCentre();
    }, [regionType, regions, setRegionsCentre]);

    return null;
};

export default RegionCentreLoader;
