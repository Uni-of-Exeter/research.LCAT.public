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

const ClimatePredictionLoader = ({
    regions,
    season,
    rcp,
    regionType,
    callback,
    loadingCallback,
}) => {
    useEffect(() => {
        // Load data only if regions are provided
        if (regions.length === 0) return;

        const fetchClimatePrediction = async () => {
            // Set loading state to true before starting the fetch
            loadingCallback(true);

            try {
                const prepend =
                    process.env.NODE_ENV === "development"
                        ? "http://localhost:3000"
                        : "";

                // Construct query
                const queryParams = new URLSearchParams({
                    rcp,
                    season,
                    boundary: regionType,
                });

                regions.forEach((region) => {
                    queryParams.append("locations", region.id);
                });

                const url = `${prepend}/api/chess_scape?${queryParams}`;

                // Fetch data
                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.statusText}`);
                }

                const data = await response.json();

                // Invoke callback with fetched data
                callback(data);
            } catch (error) {
                console.error("Error fetching climate prediction:", error);
            } finally {
                // Set loading state to false after fetch completes
                loadingCallback(false);
            }
        };

        fetchClimatePrediction();
    }, [regions, season, rcp, regionType, callback, loadingCallback]);

    return null;
};

export default ClimatePredictionLoader;
