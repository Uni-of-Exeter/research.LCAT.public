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

import React, { useEffect, useMemo, useRef, useState } from "react";
import { useCollapse } from "react-collapsed";

import { andify } from "../../utils/utils";
import LinkOutIcon from "./LinkOutIcon";

// eslint-disable-next-line react-refresh/only-export-components
export const zoomFromBbox = (bbox) => {
    const span = Math.max(bbox.max_lat - bbox.min_lat, bbox.max_lon - bbox.min_lon);
    if (span > 8) return 5;
    if (span > 4) return 6;
    if (span > 2) return 7;
    if (span > 1) return 8;
    if (span > 0.5) return 9;
    if (span > 0.2) return 10;
    return 11;
};

// eslint-disable-next-line react-refresh/only-export-components
export const centreFromBbox = (bbox) => ({
    lat: (bbox.min_lat + bbox.max_lat) / 2,
    lon: (bbox.min_lon + bbox.max_lon) / 2,
});

const IMDMap = ({ regions, regionType }) => {
    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });
    const [englishBbox, setEnglishBbox] = useState(null);
    const [scottishBbox, setScottishBbox] = useState(null);
    const hasTrackedCollapsibleOpen = useRef(false);

    const englishRegions = useMemo(() => regions.filter((r) => r.country === "England"), [regions]);
    const scottishRegions = useMemo(() => regions.filter((r) => r.country === "Scotland"), [regions]);
    const welshRegions = useMemo(() => regions.filter((r) => r.country === "Wales"), [regions]);
    const niRegions = useMemo(() => regions.filter((r) => r.country === "Northern Ireland"), [regions]);

    useEffect(() => {
        if (!isExpanded || englishRegions.length === 0) return;
        const prepend = process.env.NODE_ENV === "development" ? "http://localhost:3000" : "";
        const fetchBbox = async () => {
            try {
                const response = await fetch(`${prepend}/api/gids_bbox`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ boundary: regionType, gids: englishRegions.map((r) => r.id) }),
                });
                if (response.ok) setEnglishBbox(await response.json());
            } catch (err) {
                console.error("Error fetching English region bounds:", err);
            }
        };
        fetchBbox();
    }, [isExpanded, englishRegions, regionType]);

    useEffect(() => {
        if (!isExpanded || scottishRegions.length === 0) return;
        const prepend = process.env.NODE_ENV === "development" ? "http://localhost:3000" : "";
        const fetchBbox = async () => {
            try {
                const response = await fetch(`${prepend}/api/gids_bbox`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ boundary: regionType, gids: scottishRegions.map((r) => r.id) }),
                });
                if (response.ok) setScottishBbox(await response.json());
            } catch (err) {
                console.error("Error fetching Scottish region bounds:", err);
            }
        };
        fetchBbox();
    }, [isExpanded, scottishRegions, regionType]);

    // Construct links to deprivation map pages
    const englishCentre = englishBbox ? centreFromBbox(englishBbox) : { lat: 52.5, lon: -1.5 };
    const englishZoom = englishBbox ? zoomFromBbox(englishBbox) : 8;
    const scottishCentre = scottishBbox ? centreFromBbox(scottishBbox) : { lat: 56.5, lon: -4.0 };
    const scottishZoom = scottishBbox ? zoomFromBbox(scottishBbox) : 8;
    const englandMapUrl = `https://mapmaker.cdrc.ac.uk/#/index-of-multiple-deprivation?d=01111100&m=imde25&lon=${englishCentre.lon}&lat=${englishCentre.lat}&zoom=${englishZoom}`;
    const scotlandMapUrl = `https://simd.scot/#/simd2020/BTTTFTT/${scottishZoom}/${scottishCentre.lon}/${scottishCentre.lat}/`;
    const walesMapUrl = "https://datamap.gov.wales/maps/welsh-index-of-multiple-deprivation-wimd-2025/view#/";
    const niMapUrl = "https://datavis.nisra.gov.uk/Deprivation/deprivation%202017/SOA_Deprivation_Map/atlas.html";

    useEffect(() => {
        setExpanded(false);
        setEnglishBbox(null);
        setScottishBbox(null);
    }, [regions]);

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
