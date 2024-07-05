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

import { pathways } from "./ClimateImpactSummaryData";

const KumuImpactPathway = (props) => {
    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });
    const [whichPathway, setWhichPathway] = useState("summary");
    const pathway = pathways.find((item) => item.name === props.selectedHazardName);
    const pathwayMap = whichPathway === "summary" ? pathway.summaryPathwayMap : pathway.completePathwayMap;

    const togglePathway = () => {
        setWhichPathway(whichPathway === "summary" ? "complete" : "summary");
    };

    useEffect(() => setExpanded(false), [props.regions]);

    function handleOnClick() {
        setExpanded(!isExpanded);
    }

    if (props.regions.length === 0) {
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
                            <select value={whichPathway} onChange={togglePathway}>
                                <option value="summary">summary</option>
                                <option value="complete">complete</option>
                            </select>{" "}
                            climate impacts for{" "}
                            <select
                                value={props.selectedHazardName}
                                onChange={(e) => {
                                    props.hazardCallback(e.target.value);
                                }}
                            >
                                {pathways.map((pathway) => (
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
