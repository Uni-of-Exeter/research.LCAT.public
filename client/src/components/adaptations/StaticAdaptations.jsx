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

import "./StaticAdaptations.css";

import React, { useEffect, useRef, useState } from "react";

import adaptationData from "../../kumu/parsed/adaptation_data.json";
import { pathways } from "../climateImpacts/ClimateImpactSummaryData";
import { adaptationFilters, defaultFilterCategory, defaultFilterName } from "./AdaptationCategories";
import StaticAdaptation from "./StaticAdaptation";

const StaticAdaptations = (props) => {
    const { selectedAdaptationHazards, setSelectedAdaptationHazards, applyCoastalFilter, filterName, setFilterName } =
        props;
    const [showDataSource, setShowDataSource] = useState(false);

    // Load filter category
    const [filterCategory, setFilterCategory] = useState(defaultFilterCategory);
    const hasTrackedAdaptationClick = useRef(false);

    // Filter pathways if coastal filter is applied
    const [filteredPathwayData, setFilteredPathwayData] = useState(pathways);

    // Function for clicking on filter buttons: adding and removing hazards to array
    const toggleHazardSelection = (hazardName) => {
        setSelectedAdaptationHazards((prev) => {
            // Check to see if new hazardName is selected
            const isSelected = prev.includes(hazardName);

            // If hazardName is selected, remove it
            if (isSelected) {
                return prev.filter((n) => n !== hazardName);
            }

            // If not selected, add it to array
            if (!isSelected) {
                return [...prev, hazardName];
            }

            // If selected and the only one do nothing
            return prev;
        });

        // Track first adaptation click
        if (!hasTrackedAdaptationClick.current && typeof gtag !== "undefined") {
            gtag("event", "adaptation_icon_clicked");
            hasTrackedAdaptationClick.current = true;
        }
    };

    // When coastal filter is applied, filter pathways and reset selectedHazards
    useEffect(() => {
        if (applyCoastalFilter) {
            setFilteredPathwayData(pathways.filter((pathway) => !pathway.isCoastal));
        } else {
            setFilteredPathwayData(pathways);
        }
        setSelectedAdaptationHazards(selectedAdaptationHazards);
    }, [applyCoastalFilter, setSelectedAdaptationHazards, selectedAdaptationHazards]);

    // Handle button change: set filterName and filterCategory when dropdown is used
    const handleDropdownChange = (e) => {
        const selectedFilterName = e.target.value;
        const selectedFilter = adaptationFilters.find((filter) => filter.filterName === selectedFilterName);

        if (selectedFilter) {
            setFilterName(selectedFilter.filterName);
            setFilterCategory(selectedFilter.category);
        }
    };

    // Filter adaptations based on the selectedHazards array and the filterName
    const filteredAdaptations = adaptationData.filter((adaptation) => {
        const layers = adaptation.attributes.layer.map((layer) => layer.toLowerCase());
        const adaptationCategories = adaptation.attributes[filterCategory] || [];

        // First check that the adaptation contains every hazard in the array of selectedHazards
        const matchesAllHazards = selectedAdaptationHazards.every((hazard) =>
            layers.some((layer) => layer.includes(hazard.toLowerCase() + " in full")),
        );

        // Then check if the adaptation category includes the category filter name
        if (filterName === defaultFilterName) {
            return matchesAllHazards;
        } else {
            return matchesAllHazards && adaptationCategories.includes(filterName);
        }
    });

    if (!adaptationData) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Adaptations</h1>
            <p>
                Based on the expected climate change and resulting impacts in the UK, the following adaptations should
                be considered. These adaptations were identified to reduce risk to humans and the environment while
                providing co-benefits where possible. Use the icons to filter adaptations by climate impact pathway.
                More than one icon can be selected to see the adaptations relevant to multiple pathways. Further
                filtering by adaptation theme is also possible.
            </p>
            <div className="horiz-container-pathway">
                {filteredPathwayData.map((pathway) => (
                    <button
                        className="vert-container-pathway"
                        key={pathway.id}
                        onClick={() => toggleHazardSelection(pathway.name)}
                    >
                        <div className="pathway-text">
                            <strong>{pathway.name}</strong>
                        </div>
                        <div className="icon">
                            {React.cloneElement(pathway.icon, {
                                selectedHazard: selectedAdaptationHazards.includes(pathway.name),
                            })}
                        </div>
                    </button>
                ))}
            </div>
            <div style={{ display: "flex", justifyContent: "center" }}>
                <button
                    onClick={() => setSelectedAdaptationHazards([])}
                    style={{
                        borderRadius: "8px",
                        padding: "1rem",
                        cursor: "pointer",
                        flexDirection: "column",
                        margin: "1em",
                    }}
                >
                    <div style={{ fontSize: "0.8em" }}>Reset adaptation filters</div>
                </button>
            </div>
            <ul>
                {filteredAdaptations.length > 0 && (
                    <li>
                        {filteredAdaptations.length} climate adaptation
                        {filteredAdaptations.length === 1 ? " was" : "s were"} found
                    </li>
                )}
                <li>
                    These adaptations can be filtered further by theme:{"  "}
                    <select aria-label="Adaptation theme" value={filterName} className="adaptation-theme-select" onChange={handleDropdownChange}>
                        {adaptationFilters.map((filter, index) => (
                            <option value={filter.filterName} key={index}>
                                {filter.displayName}
                            </option>
                        ))}
                    </select>
                </li>
            </ul>
            <div>
                {filteredAdaptations.length ? (
                    filteredAdaptations.map((adaptation) => {
                        return (
                            <StaticAdaptation
                                key={adaptation._id}
                                adaptation={adaptation}
                                selectedHazards={selectedAdaptationHazards}
                            />
                        );
                    })
                ) : (
                    <h3 style={{ textAlign: "center" }}>No adaptations found</h3>
                )}
            </div>

            <div className="data-source-section">
                <button
                    className={`data-source-header ${showDataSource ? "expanded" : ""}`}
                    onClick={() => setShowDataSource(!showDataSource)}
                >
                    <span>Reference source information</span>
                    <span>▼</span>
                </button>

                {showDataSource && (
                    <div className="data-source-content">
                        <p>
                            The adaptation data is based on published scientific literature and reports. You can see the
                            references used by expanding each adaptation. The references are collected in the following
                            categories:
                        </p>
                        <ul>
                            <li>
                                <strong>Journal Article:</strong> Scholarly publications reporting original research or
                                reviews of existing research
                            </li>
                            <li>
                                <strong>Report:</strong> Formal publications by organisations to communicate research,
                                guidelines, or other relevant materials
                            </li>
                            <li>
                                <strong>Web page:</strong> Online reference materials (archived at time of inclusion)
                            </li>
                            <li>
                                <strong>Book:</strong> Sections, chapters, and full books
                            </li>
                            <li>
                                <strong>Database:</strong> Collections of evidence, such as tools or lists
                            </li>
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StaticAdaptations;
