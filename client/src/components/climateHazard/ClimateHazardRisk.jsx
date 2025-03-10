/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./ClimateHazardRisk.css";

import React, { useEffect, useState } from "react";

import { climateHazardsData } from "./ClimateHazardData";

const ClimateHazardRisk = ({ applyCoastalFilter }) => {
    const [selectedHazard, setSelectedHazard] = useState(null);
    const [filteredClimateHazardData, setFilteredClimateHazardData] = useState([]);

    useEffect(() => {
        if (applyCoastalFilter) {
            setFilteredClimateHazardData(climateHazardsData.filter((hazard) => hazard.name !== "Coastal Erosion"));
        } else {
            setFilteredClimateHazardData(climateHazardsData);
        }
        setSelectedHazard(null);
    }, [applyCoastalFilter]);

    return (
        <div>
            <h1>Climate Hazard Risk</h1>

            <p>
                The hazards of climate change will occur in many forms. These hazards pose higher risks in some local
                areas than others. Exploring each icon will provide information about that climate hazard and links to
                relevant localised datasets.
            </p>

            <div className="horiz-container-hazard">
                {filteredClimateHazardData.map((hazard) => (
                    <button
                        className="vert-container-hazard"
                        key={hazard.name}
                        onClick={() => setSelectedHazard(hazard.name)}
                    >
                        <div className="hazard-text">
                            <strong>{hazard.name}</strong>
                        </div>
                        <div className="hazard-img">{React.cloneElement(hazard.icon, { selectedHazard })}</div>
                    </button>
                ))}
            </div>

            {selectedHazard ? (
                <div className="selected-hazard-details">
                    <h2>{selectedHazard}</h2>
                    {filteredClimateHazardData.find((hazard) => hazard.name === selectedHazard)?.details}
                </div>
            ) : (
                <div className="details-placeholder">
                    <p>Please click a climate hazard risk icon to view details.</p>
                </div>
            )}
        </div>
    );
};

export default ClimateHazardRisk;
