/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./ClimateSummary.css";

import React, { useState } from "react";
import LoadingOverlay from "react-loading-overlay-ts";

import DecreaseSvg from "../../images/buttons/decrease";
import IncreaseSvg from "../../images/buttons/increase";
import CloudSvg from "../../images/climate/CloudCover";
import RainSvg from "../../images/climate/Rain";
import TempSvg from "../../images/climate/Temperature";
import WindSvg from "../../images/climate/WindSpeed";

// Function to parse the float values from the prediction
const climateChange = (prediction, variable, year) => {
    if (prediction.length > 0) {
        const baseline = parseFloat(prediction[0][`${variable}_1980`]);
        const predict = parseFloat(prediction[0][`${variable}_${year}`]);
        return baseline != null && predict != null ? predict - baseline : null;
    }
    return null;
};

// Function to render an arrow pointing up or down
const renderArrow = (value, variable) => {
    if (value == null) return null;
    // Invert value for rsds (more radiation = less cloud)
    const adjustedValue = variable === "rsds" ? -value : value;
    return adjustedValue < 0 ? <DecreaseSvg className="climate-arrow" /> : <IncreaseSvg className="climate-arrow" />;
};

// Component to create summary text for each climate variable
const PredictionSummary = ({ prediction, year, variable, name, units }) => {
    const value = climateChange(prediction, variable, year);
    if (value == null) {
        return <span>No data yet for this area, coming soon.</span>;
    }
    const adjustedValue = variable === "rsds" ? -value : value;
    const absoluteValue = Math.abs(adjustedValue).toFixed(2);
    const direction = adjustedValue === 0 ? "No change in" : adjustedValue > 0 ? "increases" : "decreases";

    return (
        <div className="summary-text">
            {adjustedValue === 0 ? (
                `${direction} ${name}`
            ) : (
                <>
                    {name} {direction} by {absoluteValue} {units}
                </>
            )}
        </div>
    );
};

// Component for arrow + prediction + icon for each climate variable
const ClimateVariable = ({ prediction, year, variable, name, units, Icon }) => {
    const value = climateChange(prediction, variable, year);

    return (
        <div className="vert-container">
            {renderArrow(value, variable)}
            <Icon className="climate-arrow" />
            <PredictionSummary prediction={prediction} year={year} variable={variable} name={name} units={units} />
        </div>
    );
};

// Final component for climate summary section
const ClimateSummary = ({ regions, loading, climatePrediction, year }) => {
    if (regions.length === 0) return null;

    const [selectedVariable, setSelectedVariable] = useState(null); // "tas" | "pr" | "rsds" | "sfcWind" | null

    const handleSelect = (variableKey) => {
        setSelectedVariable(variableKey);
    };

    const renderDetails = () => {
        if (!selectedVariable) {
            return (
                <div className="climate-details-placeholder">
                    <p>Please click a climate variable icon to view details.</p>
                </div>
            );
        }

        // For now, just some explanatory text per variable.
        // Later, you’ll plug the tropical nights block in here for "tas".
        if (selectedVariable === "tas") {
            return (
                <div className="climate-selected-details">
                    <h2>Temperature details</h2>
                    <p>
                        Here we will show additional information about temperature, such as tropical nights and how they
                        change under different climate scenarios.
                    </p>
                </div>
            );
        }

        if (selectedVariable === "pr") {
            return (
                <div className="climate-selected-details">
                    <h2>Rainfall details</h2>
                    <p>
                        Additional information about projected changes in rainfall intensity and seasonality will appear
                        here.
                    </p>
                </div>
            );
        }

        if (selectedVariable === "rsds") {
            return (
                <div className="climate-selected-details">
                    <h2>Cloudiness details</h2>
                    <p>
                        This section can describe changes in cloudiness and what that means for sunshine and solar gain.
                    </p>
                </div>
            );
        }

        if (selectedVariable === "sfcWind") {
            return (
                <div className="climate-selected-details">
                    <h2>Windiness details</h2>
                    <p>
                        This section can summarise how wind speeds may change and any implications for local hazards.
                    </p>
                </div>
            );
        }

        return null;
    };

    return (
        <LoadingOverlay active={loading} spinner text="Loading climate data">
                <div className="climate-summary">
                    <div className="horiz-container">
                        <button
                            type="button"
                            className={`vert-container climate-variable-button ${
                                selectedVariable === "tas" ? "climate-variable-selected" : ""
                            }`}
                            onClick={() => handleSelect("tas")}
                        >
                            <ClimateVariable
                                prediction={climatePrediction}
                                year={year}
                                variable="tas"
                                name="Temperature"
                                units="°C"
                                Icon={TempSvg}
                            />
                        </button>

                        <button
                            type="button"
                            className={`vert-container climate-variable-button ${
                                selectedVariable === "pr" ? "climate-variable-selected" : ""
                            }`}
                            onClick={() => handleSelect("pr")}
                        >
                            <ClimateVariable
                                prediction={climatePrediction}
                                year={year}
                                variable="pr"
                                name="Rainfall"
                                units="mm/day"
                                Icon={RainSvg}
                            />
                        </button>

                        <button
                            type="button"
                            className={`vert-container climate-variable-button ${
                                selectedVariable === "rsds" ? "climate-variable-selected" : ""
                            }`}
                            onClick={() => handleSelect("rsds")}
                        >
                            <ClimateVariable
                                prediction={climatePrediction}
                                year={year}
                                variable="rsds"
                                name="Cloudiness"
                                units="Watts/m2"
                                Icon={CloudSvg}
                            />
                        </button>

                        <button
                            type="button"
                            className={`vert-container climate-variable-button ${
                                selectedVariable === "sfcWind" ? "climate-variable-selected" : ""
                            }`}
                            onClick={() => handleSelect("sfcWind")}
                        >
                            <ClimateVariable
                                prediction={climatePrediction}
                                year={year}
                                variable="sfcWind"
                                name="Windiness"
                                units="m/sec"
                                Icon={WindSvg}
                            />
                        </button>
                    </div>

                {renderDetails()}

                <p>
                    Note: Yearly average climate change does not always reflect the extremes of summer and winter.
                    Change the drop-down menu above to see the predictions for the different seasons.
                </p>
            </div>
        </LoadingOverlay>
    );
};

export default ClimateSummary;
