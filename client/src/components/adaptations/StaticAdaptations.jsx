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
import { adaptationBodyKeys, CCCAdaptationThemes, IPCCCategories } from "./AdaptationCategories";
import StaticAdaptation from "./StaticAdaptation";

const StaticAdaptations = (props) => {
    const [selectedBody, setSelectedBody] = useState("CCC");
    const [filterState, setFilterState] = useState("No filter applied");

    // Get the correct key based on the selectedBody
    const selectedKey = adaptationBodyKeys[selectedBody];
    const adaptationCategories = selectedBody === "CCC" ? CCCAdaptationThemes : IPCCCategories;

    // Reset filterState if selectedBody changes
    useEffect(() => {
        setFilterState("No filter applied");
    }, [selectedBody]);

    // Filter adaptation list based on selectedBody (i.e. CCC or IPCC) and filterState
    const filteredAdaptations = adaptationData.filter((adaptation) => {
        const hazardName = props.selectedHazardName.toLowerCase();
        const layers = adaptation.attributes.layer.map((layer) => layer.toLowerCase());
        const bodyData = adaptation.attributes[selectedKey];

        if (!bodyData) return;

        if (filterState === "No filter applied") {
            return layers.some((layer) => layer.includes(hazardName + " in full"));
        } else {
            return layers.some((layer) => layer.includes(hazardName + " in full")) && bodyData.includes(filterState);
        }
    });

    if (!adaptationData) {
        return <div>Loading...</div>;
    }

    return (
        <LoadingOverlay active={props.loading} spinner text={"Loading adaptations"}>
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
                    value={props.selectedHazardName}
                    onChange={(e) => {
                        props.setSelectedHazardName(e.target.value);
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
                    <li>{filteredAdaptations.length} climate adaptations were found.</li>
                    <li>
                        Filter category:{"  "}
                        <select
                            value={selectedBody}
                            onChange={(e) => {
                                setSelectedBody(e.target.value);
                            }}
                        >
                            <option value="CCC">Climate Change Committee adaptation themes</option>
                            <option value="IPCC">Intergovernmental Panel on Climate Change activity types</option>
                        </select>
                    </li>
                    <li>
                        Apply filter:{"  "}
                        <select
                            value={filterState}
                            onChange={(e) => {
                                setFilterState(e.target.value);
                            }}
                        >
                            <option value="No filter applied">No filter applied</option>
                            {adaptationCategories.map((category, index) => (
                                <option value={category} key={index}>
                                    {category}
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
                                adaptation={adaptation.attributes}
                                selectedHazardName={props.selectedHazardName}
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
