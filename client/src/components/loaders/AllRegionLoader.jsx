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

const AllRegionLoader = ({ regionType, setAllRegions }) => {
    useEffect(() => {
        const fetchAllRegions = async () => {
            try {
                const prepend = process.env.NODE_ENV === "development" ? "http://localhost:3000" : "";

                // Construct query
                const queryParams = new URLSearchParams({
                    boundary: regionType,
                });

                const url = `${prepend}/api/all_regions?${queryParams}`;

                // Fetch data
                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.statusText}`);
                }

                const data = await response.json();

                // Set allRegions
                setAllRegions(data);
            } catch (error) {
                console.error("Error fetching all regions:", error);
            }
        };

        fetchAllRegions();
    }, [regionType, setAllRegions]);

    return null;
};

export default AllRegionLoader;
