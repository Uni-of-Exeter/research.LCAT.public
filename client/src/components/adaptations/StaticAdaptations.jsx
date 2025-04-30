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

import adaptationData from "../../kumu/parsed/adaptation_data.json";
import { pathways } from "../climateImpacts/ClimateImpactSummaryData";
import { adaptationFilters } from "./AdaptationCategories";
import StaticAdaptation from "./StaticAdaptation";

const StaticAdaptations = (props) => {
    const { selectedHazardName, applyCoastalFilter } = props;

    // Load filter options
    const defaultFilterName = adaptationFilters[0].filterName;
    const defaultFilterCategory = adaptationFilters[0].category;
    const [filterName, setFilterName] = useState(defaultFilterName);
    const [filterCategory, setFilterCategory] = useState(defaultFilterCategory);

    // Filter pathways if coastal filter is applied
    const [filteredPathwayData, setFilteredPathwayData] = useState(pathways);

    // Track array of selected hazards (controlled via buttons)
    const [selectedHazards, setSelectedHazards] = useState([selectedHazardName]);

    // Function for clicking on filter buttons: adding and removing hazards to array
    const toggleHazardSelection = (hazardName) => {
        setSelectedHazards((prev) => {
            // Check to see if new hazardName is selected
            const isSelected = prev.includes(hazardName);

            // If hazardName is selected and removing it wont empty array, remove it
            if (isSelected && prev.length > 1) {
                return prev.filter((n) => n !== hazardName);
            }

            // If not selected, add it to array
            if (!isSelected) {
                return [...prev, hazardName];
            }

            // If selected and the only one do nothing
            return prev;
        });
    };

    // When coastal filter is applied, filter pathways and reset selectedHazards
    useEffect(() => {
        if (applyCoastalFilter) {
            setFilteredPathwayData(pathways.filter((pathway) => !pathway.isCoastal));
        } else {
            setFilteredPathwayData(pathways);
        }
        setSelectedHazards([selectedHazardName]);
    }, [applyCoastalFilter, selectedHazardName]);

    // When a new selectedHazardName is applied, reset the list of hazards
    useEffect(() => {
        setSelectedHazards([selectedHazardName]);
    }, [selectedHazardName]);

    // Handle button change: set filterName and filterCategory when dropdown is used
    const handleButtonChange = (e) => {
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

        const matchesHazard = layers.some((layer) =>
            selectedHazards.some((hazard) => layer.includes(hazard.toLowerCase() + " in full")),
        );

        if (filterName === defaultFilterName) {
            return matchesHazard;
        } else {
            return matchesHazard && adaptationCategories.includes(filterName);
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
                Further filtering by adaptation theme is also possible.
            </p>
            <div style={{ display: "flex", justifyContent: "center" }}>
                <div
                    style={{
                        display: "flex",
                        gap: "1rem",
                        width: "90%",
                        justifyContent: "space-between",
                    }}
                >
                    {filteredPathwayData.map((pathway) => (
                        <button
                            key={pathway.id}
                            onClick={() => toggleHazardSelection(pathway.name)}
                            style={{
                                flex: "1",
                                background: selectedHazards.includes(pathway.name) ? "#e6eced" : "white",
                                border: "1px solid #ccc",
                                borderRadius: "8px",
                                padding: "0.5rem",
                                cursor: "pointer",
                                display: "flex",
                                flexDirection: "column",
                                alignItems: "center",
                                justifyContent: "center",
                                minWidth: "0",
                            }}
                        >
                            <div style={{ fontSize: "48px" }}>{pathway.emoji}</div>
                            <div style={{ fontSize: "12px" }}>{pathway.name}</div>
                        </button>
                    ))}
                </div>
            </div>
            <ul>
                <li>
                    {filteredAdaptations.length} climate adaptation
                    {filteredAdaptations.length === 1 ? " was" : "s were"} found
                </li>
                <li>
                    These adaptations can be filtered further by theme:{"  "}
                    <select value={filterName} onChange={handleButtonChange}>
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
                                selectedHazardName={selectedHazardName}
                            />
                        );
                    })
                ) : (
                    <h3>No adaptations found</h3>
                )}
            </div>

            <p className="note">
                Data source: The adaptation data is based on published scientific literature and reports. You can see
                the references used by expanding each adaptation.
            </p>
        </div>
    );
};

export default StaticAdaptations;
