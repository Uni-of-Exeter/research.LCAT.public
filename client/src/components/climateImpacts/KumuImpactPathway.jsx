/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./KumuImpactPathway.css";

import React, { useEffect, useState } from "react";
import { useCollapse } from "react-collapsed";

import { defaultState } from "../../utils/defaultState.js";
import { pathways } from "./ClimateImpactSummaryData";

const KumuImpactPathway = ({ regions, selectedHazardName, setSelectedHazardName, applyCoastalFilter }) => {
    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });

    const [whichPathway, setWhichPathway] = useState("summary");
    const [filteredPathwayData, setFilteredPathwayData] = useState(pathways);

    // Filter pathways if coastal filter is applied
    useEffect(() => {
        if (applyCoastalFilter) {
            setFilteredPathwayData(pathways.filter((pathway) => !pathway.isCoastal));
        } else {
            setFilteredPathwayData(pathways);
        }
        setSelectedHazardName(defaultState.selectedHazardName);
    }, [applyCoastalFilter, setSelectedHazardName]);

    const pathway = filteredPathwayData.find((item) => item.name === selectedHazardName);

    let pathwayMap;
    switch (whichPathway) {
        case "summary":
            pathwayMap = pathway.summaryPathwayMap;
            break;
        case "complete":
            pathwayMap = pathway.completePathwayMap;
            break;
        case "complete (with adaptations)":
            pathwayMap = pathway.completePathwayMapWithAdaptations;
            break;
        default:
            pathwayMap = pathway.summaryPathwayMap;
    }

    const togglePathway = (value) => {
        if (value !== whichPathway) {
            setWhichPathway(value);
        }
    };

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
                    {isExpanded ? "Hide" : "Explore"} climate impact details
                </div>
                <div {...getCollapseProps()}>
                    <div className="content">
                        <h1>Climate Impact Details</h1>
                        <p>
                            The climate impact pathway below shows the direct and indirect impacts of climate change
                            hazards as understood through available evidence. These impacts are specific to the UK
                            rather than your selected area.
                        </p>
                        <p>
                            Both the nodes and the connections between them contain information. Clicking on the nodes
                            will show details for an impact. Clicking on the lines will show the relationship between
                            impacts.
                        </p>
                        <p>
                            You are viewing the{" "}
                            <select value={whichPathway} onChange={(event) => togglePathway(event.target.value)}>
                                <option value="summary">summary</option>
                                <option value="complete">complete</option>
                                <option value="complete (with adaptations)">complete (with adaptations)</option>
                            </select>{" "}
                            climate impacts for{" "}
                            <select
                                value={selectedHazardName}
                                onChange={(e) => {
                                    setSelectedHazardName(e.target.value);
                                }}
                            >
                                {filteredPathwayData.map((pathway) => (
                                    <option value={pathway.name} key={pathway.id}>
                                        {pathway.name}
                                    </option>
                                ))}
                            </select>
                        </p>
                        <div className="iframe-container">{pathwayMap}</div>
                    </div>
                </div>
            </div>
            <div>
                <p className="note">
                    Data source: The impact pathway data is based on published scientific literature and reports.{" "}
                    <a
                        href="https://docs.google.com/spreadsheets/d/18c_5SSG9VmagkX3bdC_F2eDtzFz9oQJvPQbhEfwmUNc/edit?usp=sharing"
                        target="_blank"
                        rel="noreferrer"
                    >
                        A full reference list is available here.
                    </a>
                </p>
            </div>
        </div>
    );
};

export default KumuImpactPathway;
