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
import LoadingOverlay from "react-loading-overlay-ts";

import adaptationData from "../../kumu/parsed/adaptation_data.json";
import { pathways } from "../climateImpacts/ClimateImpactSummaryData";
import { adaptationFilters } from "./AdaptationCategories";
import AdaptationGrid from "./AdaptationGrid";
import StaticAdaptation from "./StaticAdaptation";

const StaticAdaptations = (props) => {
    const { selectedHazardName, setSelectedHazardName } = props;

    const defaultFilterName = adaptationFilters[0].filterName;
    const defaultFilterCategory = adaptationFilters[0].category;

    const [filterName, setFilterName] = useState(defaultFilterName);
    const [filterCategory, setFilterCategory] = useState(defaultFilterCategory);
    const [loading, setLoading] = useState(false);

    // Handle change in filter: set filterName and filterCategory when dropdown is used
    const handleFilterChange = (e) => {
        const selectedFilterName = e.target.value;
        const selectedFilter = adaptationFilters.find((filter) => filter.filterName === selectedFilterName);

        if (selectedFilter) {
            setFilterName(selectedFilter.filterName);
            setFilterCategory(selectedFilter.category);
        }
    };

    // Filter adaptations using filterName and filterCategory
    const filteredAdaptations = adaptationData.filter((adaptation) => {
        const hazardName = selectedHazardName.toLowerCase();
        const layers = adaptation.attributes.layer.map((layer) => layer.toLowerCase());
        const adaptationCategories = adaptation.attributes[filterCategory] || [];

        if (filterName === defaultFilterName) {
            return layers.some((layer) => layer.includes(hazardName + " in full"));
        } else {
            return (
                layers.some((layer) => layer.includes(hazardName + " in full")) &&
                adaptationCategories.includes(filterName)
            );
        }
    });

    if (!adaptationData) {
        return <div>Loading...</div>;
    }

    return (
        <LoadingOverlay active={loading} spinner text={"Loading adaptations"}>
            <h1>Adaptation Grid</h1>

            <p>
                This is a mock-up of an adaptation data grid. It allows users to filter and sort adaptations more easily.
            </p>

            <AdaptationGrid adaptationData={adaptationData} pathways={pathways}/>

            <h1>Adaptations</h1>
            <p>
                Based on the expected climate change and resulting impacts in the UK, the following adaptations should
                be considered. These adaptations were identified to reduce risk to humans and the environment while
                providing co-benefits where possible. Use the dropdown options to view adaptations by climate impact
                pathway, adaptation theme, and activity type.
            </p>
            <p>
                <b className="static-adaptation-emphasis">Selected climate impact pathway: </b>
                <select
                    value={selectedHazardName}
                    onChange={(e) => {
                        setSelectedHazardName(e.target.value);
                    }}
                >
                    {pathways.map((pathway) => (
                        <option value={pathway.name} key={pathway.id}>
                            {pathway.name}
                        </option>
                    ))}
                </select>
            </p>
            <ul>
                <li>
                    {filteredAdaptations.length} climate adaptation
                    {filteredAdaptations.length === 1 ? " was" : "s were"} found
                </li>
                <li>
                    These adaptations can be filtered by theme:{"  "}
                    <select value={filterName} onChange={handleFilterChange}>
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
        </LoadingOverlay>
    );
};

export default StaticAdaptations;
