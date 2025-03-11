/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import React, { useEffect, useState } from "react";

import { defaultState } from "../../utils/defaultState";

const zoomLevels = {
    boundary_uk_counties: 8,
    boundary_la_districts: 8,
    boundary_parishes: 10,
    boundary_msoa: 10,
    boundary_sc_dz: 10,
    boundary_lsoa: 10,
    boundary_ni_dz: 10,
    boundary_iom: 8,
};

const IMDMap = ({ regions, regionType }) => {
    const [averageCenter, setAverageCenter] = useState(defaultState.mapCenter);
    const [zoomLevel, setZoomLevel] = useState(8);

    const calculateAverageCenter = (regions) => {
        if (!regions?.length) return null;

        let totalLat = 0;
        let totalLon = 0;

        regions.forEach(({ regionCenter }) => {
            totalLat += regionCenter.lat;
            totalLon += regionCenter.lon;
        });

        return {
            lat: totalLat / regions.length,
            lon: totalLon / regions.length,
        };
    };

    useEffect(() => {
        // Recalculate the average center of selected regions
        const average = calculateAverageCenter(regions);
        if (average) setAverageCenter(average);

        // Set zoom level based on region type
        setZoomLevel(zoomLevels[regionType]);
    }, [regions, regionType]);

    // Construct link to CDRC page
    const mapUrl = `https://mapmaker.cdrc.ac.uk/#/index-of-multiple-deprivation?d=11110000&m=imdh19_dc&lon=${averageCenter.lon}&lat=${averageCenter.lat}&zoom=${zoomLevel}`;

    return (
        <div>
            <h1>Deprivation Indices</h1>
            <p>
                The English indices of deprivation measure relative deprivation in small areas in England called
                lower-layer super output areas. The index of multiple deprivation is the most widely used of these
                indices.
            </p>
            <p>
                Please click this link to view the{" "}
                <a href={mapUrl} target="_blank" rel="noopener noreferrer">
                    CDRC IMD map tool
                </a>
                .
            </p>
        </div>
    );
};

export default IMDMap;
