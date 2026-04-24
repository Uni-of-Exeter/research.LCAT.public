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

import "./ClimateImpactSummary.css";

import { useEffect, useRef, useState } from "react";
import LoadingOverlay from "react-loading-overlay-ts";

import { defaultState } from "../../utils/defaultState.js";
import { communityImpacts, impacts, pathways } from "./ClimateImpactSummaryData.jsx";

const ClimateImpactSummary = ({ loading, selectedImpactHazard, setSelectedImpactHazard, applyCoastalFilter }) => {
    const [filteredPathwayData, setFilteredPathwayData] = useState(pathways);
    const hasTrackedHazardSelection = useRef(false);

    // Filter pathways if coastal filter is applied
    useEffect(() => {
        if (applyCoastalFilter) {
            setFilteredPathwayData(pathways.filter((pathway) => !pathway.isCoastal));
        } else {
            setFilteredPathwayData(pathways);
        }
        setSelectedImpactHazard(defaultState.selectedImpactHazard);
    }, [applyCoastalFilter, setSelectedImpactHazard]);

    const handleHazardChange = (e) => {
        const newHazardName = e.target.value;

        // Track first-time hazard selection change
        if (!hasTrackedHazardSelection.current && typeof gtag !== "undefined") {
            gtag("event", "hazard_dropdown_used");
            hasTrackedHazardSelection.current = true;
        }

        setSelectedImpactHazard(newHazardName);
    };
    const selectedPathwayData = filteredPathwayData.find((item) => item.name === selectedImpactHazard);
    const filteredImpacts = impacts.filter((item) => item.inPathway.includes(selectedPathwayData.id));
    const filteredCommunityImpacts = communityImpacts.filter((item) => item.inPathway.includes(selectedPathwayData.id));

    return (
        <LoadingOverlay active={loading} spinner text={"Loading impact summaries"}>
            <h1>Climate Impact Summary</h1>

            <p>
                Below are summaries of the impacts expected from the identified climate change impact pathways. These
                impacts will vary by area, but the UK is likely to experience the following.
            </p>

            <p>
                You are viewing the <strong className="text-emphasis">climate</strong> impacts for&nbsp;
                <select value={selectedImpactHazard} onChange={handleHazardChange}>
                    {filteredPathwayData.map((pathway) => (
                        <option value={pathway.name} key={pathway.id}>
                            {pathway.name}
                        </option>
                    ))}
                </select>
            </p>

            <h2 className="health-impact-summary">Health impact summary</h2>

            <p>
                Climate change will have an overall <strong className="text-emphasis">negative impact</strong> on
                health, including{" "}
                <strong className="text-emphasis">
                    mental health disorders, wellbeing, and chronic health conditions.
                </strong>{" "}
                See below for additional health impacts for each pathway.{" "}
            </p>

            <p>
                You are viewing the climate impacts for{" "}
                <strong className="text-emphasis">{selectedImpactHazard}</strong>.
            </p>

            <div className="horiz-container-impact">
                {filteredImpacts.map((impact) => (
                    <div className="vert-container-impact" key={impact.id}>
                        <div className="icon">{impact.icon}</div>
                        <div className="impact-text">{impact.name}</div>
                    </div>
                ))}
            </div>

            <h2 className="community-impact-summary">Community Impact Summary</h2>

            <p>
                Climate change will have a <strong className="text-emphasis">negative impact</strong> on essential
                community infrastructures and services like{" "}
                <strong className="text-emphasis">systems failures of hospitals, transport, water, and energy.</strong>{" "}
                See below for additional community impacts for each pathway.
            </p>

            <p>
                You are viewing the climate impacts for{" "}
                <strong className="text-emphasis">{selectedImpactHazard}</strong>.
            </p>

            <div className="horiz-container-impact">
                {filteredCommunityImpacts.map((impact) => (
                    <div className="vert-container-impact" key={impact.id}>
                        <div className="icon">{impact.icon}</div>
                        <div className="impact-text">{impact.name}</div>
                    </div>
                ))}
            </div>
        </LoadingOverlay>
    );
};

export default ClimateImpactSummary;
