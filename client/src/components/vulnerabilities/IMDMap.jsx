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
import { useCollapse } from "react-collapsed";

import { defaultState } from "../../utils/defaultState";
import { andify } from "../../utils/utils";
import LinkOutIcon from "./LinkOutIcon";

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
    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });
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
    const mapUrl = `https://mapmaker.cdrc.ac.uk/#/index-of-multiple-deprivation?d=01111100&m=imdh19_dc&lon=${averageCenter.lon}&lat=${averageCenter.lat}&zoom=${zoomLevel}`;

    useEffect(() => setExpanded(false), [regions]);

    function handleOnClick() {
        setExpanded(!isExpanded);
    }

    if (regions.length === 0) {
        return null;
    }

    return (
        <div>
            <div className="collapsible">
                <div className="header" style={{ margin: "1em" }} {...getToggleProps({ onClick: handleOnClick })}>
                    {isExpanded ? "Hide" : "Explore"} local deprivation data
                </div>
                <div {...getCollapseProps()}>
                    <div>
                        <h1>Local Index of Multiple Deprivation Data</h1>
                        <p>
                            The Indices or Index of Multiple Deprivation shows relative deprivation at a local level,
                            illustrating where the least and most deprived areas in a region are.
                        </p>

                        <p>
                            Since climate change impacts unfairly on those experiencing social and economic
                            disadvantage, measures of deprivation can support decision-makers to understand who might be
                            at more risk to climate impacts and where they are geographically.
                        </p>

                        <p>
                            This is just one helpful measure. Local areas may also hold their own localised data on
                            communities at risk. Other tools, like{" "}
                            <a href={"https://www.climatejust.org.uk/"} target="_blank" rel="noopener noreferrer">
                                ClimateJust
                            </a>
                            , can also support local areas to understand climate vulnerability.
                        </p>

                        <p>
                            <a href={mapUrl} target="_blank" rel="noopener noreferrer">
                                <LinkOutIcon size="2em" colour="black" />
                                Click here to get mapped deprivation data
                            </a>{" "}
                            centered around{" "}
                            {<strong className="text-emphasis">{andify(regions.map((e) => e.name))}</strong>}.
                        </p>
                    </div>
                    <div>
                        <p className="note">
                            Data source: Index of Multiple Deprivation (IMD) data are provided by the{" "}
                            <a
                                href="https://data.cdrc.ac.uk/dataset/index-multiple-deprivation-imd"
                                target="_blank"
                                rel="noreferrer"
                            >
                                Consumer Data Research Centre (CDRC).
                            </a>{" "}
                            The datasets used are the latest available.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IMDMap;
