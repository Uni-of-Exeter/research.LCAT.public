/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

/* global gtag */

import React, { useEffect, useRef,useState } from "react";
import { useCollapse } from "react-collapsed";

import { defaultState } from "../../utils/defaultState";
import { andify } from "../../utils/utils";
import RegionCentreLoader from "../loaders/RegionCentreLoader";
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
    const [regionsCentre, setRegionsCentre] = useState(defaultState.mapCenter);
    const [scottishRegionsCentre, setScottishRegionsCentre] = useState(defaultState.mapCenter);
    const [zoomLevel, setZoomLevel] = useState(8);
    const hasTrackedCollapsibleOpen = useRef(false);

    const englishRegions = regions.filter((r) => r.country === "England");
    const scottishRegions = regions.filter((r) => r.country === "Scotland");
    const welshRegions = regions.filter((r) => r.country === "Wales");
    const niRegions = regions.filter((r) => r.country === "Northern Ireland");

    useEffect(() => {
        // Set zoom level based on region type
        setZoomLevel(zoomLevels[regionType]);
    }, [regionType]);

    // Construct links to deprivation map pages
    const englandMapUrl = `https://mapmaker.cdrc.ac.uk/#/index-of-multiple-deprivation?d=01111100&m=imde25&lon=${regionsCentre.lon}&lat=${regionsCentre.lat}&zoom=${zoomLevel}`;
    const scotlandMapUrl = `https://simd.scot/#/simd2020/BTTTFTT/${zoomLevel}/${scottishRegionsCentre.lon}/${scottishRegionsCentre.lat}/`;
    const walesMapUrl = "https://datamap.gov.wales/maps/welsh-index-of-multiple-deprivation-wimd-2025/view#/";
    const niMapUrl = "https://datavis.nisra.gov.uk/Deprivation/deprivation%202017/SOA_Deprivation_Map/atlas.html";

    useEffect(() => setExpanded(false), [regions]);

    function handleOnClick() {
        // Track first-time opening of collapsible
        if (!isExpanded && !hasTrackedCollapsibleOpen.current && typeof gtag !== 'undefined') {
            gtag('event', 'deprivation_details_opened');
            hasTrackedCollapsibleOpen.current = true;
        } 
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
                    {isExpanded && (
                        <RegionCentreLoader
                            regionType={regionType}
                            regions={englishRegions}
                            setRegionsCentre={setRegionsCentre}
                        />
                    )}
                    {isExpanded && scottishRegions.length > 0 && (
                        <RegionCentreLoader
                            regionType={regionType}
                            regions={scottishRegions}
                            setRegionsCentre={setScottishRegionsCentre}
                        />
                    )}
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

                        {englishRegions.length > 0 && (
                            <>
                                <p style={{ marginBottom: 0 }}>
                                    <a href={englandMapUrl} target="_blank" rel="noopener noreferrer">
                                        <LinkOutIcon size="2em" colour="black" />
                                        Click here to get mapped deprivation data for England
                                    </a>{" "}
                                    centered around{" "}
                                    {<strong className="text-emphasis">{andify(englishRegions.map((e) => e.name))}</strong>}.
                                </p>
                                <p className="note" style={{ marginTop: 0 }}>
                                    Data source: Index of Multiple Deprivation (IMD) data are provided by the{" "}
                                    <a href="https://data.cdrc.ac.uk/dataset/index-multiple-deprivation-imd" target="_blank" rel="noreferrer">
                                        Consumer Data Research Centre (CDRC).
                                    </a>
                                </p>
                            </>
                        )}
                        {scottishRegions.length > 0 && (
                            <>
                                <p style={{ marginBottom: 0 }}>
                                    <a href={scotlandMapUrl} target="_blank" rel="noopener noreferrer">
                                        <LinkOutIcon size="2em" colour="black" />
                                        Click here to get mapped deprivation data for Scotland
                                    </a>{" "}
                                    centered around{" "}
                                    {<strong className="text-emphasis">{andify(scottishRegions.map((e) => e.name))}</strong>}.
                                </p>
                                <p className="note" style={{ marginTop: 0 }}>
                                    Data source: Scottish Index of Multiple Deprivation (SIMD) 2020 data are provided by the{" "}
                                    <a href="https://www.gov.scot/collections/scottish-index-of-multiple-deprivation-2020/" target="_blank" rel="noreferrer">
                                        Scottish Government.
                                    </a>
                                </p>
                            </>
                        )}
                        {welshRegions.length > 0 && (
                            <>
                                <p style={{ marginBottom: 0 }}>
                                    <a href={walesMapUrl} target="_blank" rel="noopener noreferrer">
                                        <LinkOutIcon size="2em" colour="black" />
                                        Click here to get mapped deprivation data for Wales
                                    </a>.
                                </p>
                                <p className="note" style={{ marginTop: 0 }}>
                                    Data source: Welsh Index of Multiple Deprivation (WIMD) 2025 data are provided by{" "}
                                    <a href="https://www.gov.wales/welsh-index-multiple-deprivation" target="_blank" rel="noreferrer">
                                        Welsh Government / Stats Wales.
                                    </a>
                                </p>
                            </>
                        )}
                        {niRegions.length > 0 && (
                            <>
                                <p style={{ marginBottom: 0 }}>
                                    <a href={niMapUrl} target="_blank" rel="noopener noreferrer">
                                        <LinkOutIcon size="2em" colour="black" />
                                        Click here to get mapped deprivation data for Northern Ireland
                                    </a>.
                                </p>
                                <p className="note" style={{ marginTop: 0 }}>
                                    Data source: Multiple Deprivation Measure 2017 data are provided by{" "}
                                    <a href="https://www.nisra.gov.uk/statistics/deprivation/northern-ireland-multiple-deprivation-measure-2017-nimdm2017" target="_blank" rel="noreferrer">
                                        NISRA.
                                    </a>
                                </p>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IMDMap;
