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
    setClimatePrediction,
    setIsPredictionLoading,
    setRegionBbox,
}) => {
    useEffect(() => {
        // Load data only if regions are provided
        if (regions.length === 0) return;

        const gids = regions.map((region) => region.id);

        const fetchClimatePrediction = async () => {
            // Set loading state to true before starting the fetch
            setIsPredictionLoading(true);

            try {
                const prepend = process.env.NODE_ENV === "development" ? "http://localhost:3000" : "";

                // Construct query
                const queryParams = new URLSearchParams({
                    rcp,
                    season,
                    boundary: regionType,
                    locations: gids,
                });

                const url = `${prepend}/api/chess_scape?${queryParams}`;

                // Fetch data
                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.statusText}`);
                }

                const data = await response.json();

                // Invoke callback with fetched data
                setClimatePrediction(data);
            } catch (error) {
                console.error("Error fetching climate prediction:", error);
            } finally {
                // Set loading state to false after fetch completes
                setIsPredictionLoading(false);
            }
        };

        fetchClimatePrediction();
    }, [regions, season, rcp, regionType, setClimatePrediction, setIsPredictionLoading]);

    // Get bounding box from array of gid arrays
    useEffect(() => {
        // If no regions, nothing to fetch
        if (regions.length === 0) return;

        const gids = regions.map((region) => region.id);

        const fetchBoundingBox = async () => {
            try {
                // Construct base URL
                const prepend = process.env.NODE_ENV === "development" ? "http://localhost:3000" : "";

                // Build query params (tableName + multiple gids)
                const queryParams = new URLSearchParams();
                queryParams.append("tableName", regionType);
                gids.forEach((gid) => queryParams.append("gids", gid));

                const bboxUrl = `${prepend}/api/bounding_box?${queryParams}`;
                const response = await fetch(bboxUrl);

                if (!response.ok) {
                    throw new Error(`Failed to fetch bounding box: ${response.statusText}`);
                }

                const data = await response.json();

                setRegionBbox(data.bbox ?? null);
            } catch (error) {
                console.error("Error fetching bounding box:", error);
            }
        };

        fetchBoundingBox();
    }, [regions, regionType, setRegionBbox]);

    return null;
};

export default ClimatePredictionLoader;
