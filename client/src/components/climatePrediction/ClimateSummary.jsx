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
import DryDaysSvg from "../../images/climate/DryDays";
import { ReactComponent as HeavyRainDaysSvg } from "../../images/climate/HeavyRainDays.svg";
import { ReactComponent as HotHeatDaysSvg } from "../../images/climate/HotHeatDays.svg";
import { ReactComponent as RadiationSvg } from "../../images/climate/Radiation.svg";
import RainSvg from "../../images/climate/Rain";
import TempSvg from "../../images/climate/Temperature";
import { ReactComponent as TropicalNightsSvg } from "../../images/climate/TropicalNights.svg";
import WindSvg from "../../images/climate/WindSpeed";
import { climateChange, formatClimateData } from "../../utils/climateUtils";
import HelpPopover from "./HelpPopover";

// Variable explanations
const VARIABLE_EXPLANATIONS = {
    dry_days: "Dry days are defined as days with less than 1mm of precipitation.",
    heavy_rain_days: "Heavy rain days are defined as days with 50mm or more of precipitation.",
    tropical_nights: "Tropical nights occur when the minimum daily temperature does not drop below 20°C.",
    hot_heat_days: "Hot heat days are defined as days when the maximum temperature exceeds 30°C.",
    windy_days: "Windy days are defined as days with average wind speeds exceeding 8 m/s.",
};

// Function to render an arrow pointing up or down
const renderArrow = (value) => {
    if (value == null) return null;
    return value < 0 ? <DecreaseSvg className="climate-arrow" /> : <IncreaseSvg className="climate-arrow" />;
};

// Component to create summary text for each climate variable
const PredictionSummary = ({ prediction, year, variable, name, units }) => {
    const climateData = formatClimateData(prediction, variable, name, units, year);
    return (
        <div className="summary-text">
            {climateData.change}
        </div>
    );
};

// Component for arrow + icon + summary text
// Only the icon is clickable – the rest of the box is not.
const ClimateVariable = ({ prediction, year, variable, name, units, Icon, onClick = undefined, isSelected = false, isAnnual = false }) => {
    const value = climateChange(prediction, variable, year);
    const explanation = VARIABLE_EXPLANATIONS[variable];

    return (
        <div className="vert-container">
            {renderArrow(value, variable)}
            <div className="climate-icon-wrapper">
                <button
                    type="button"
                    className={`climate-icon-button ${isSelected ? "climate-variable-selected" : ""}`}
                    onClick={onClick}
                >
                    <Icon
                        className="climate-arrow"
                        selected={isSelected}
                        isAnnual={isAnnual}
                    />
                </button>
                {explanation && (
                    <HelpPopover content={explanation} />
                )}
            </div>
            <PredictionSummary
                prediction={prediction}
                year={year}
                variable={variable}
                name={name}
                units={units}
            />
        </div>
    );
};

// Component for arrow + icon + summary text
// Only the icon is clickable – the rest of the box is not.
const DetailClimateVariable = ({ prediction, year, variable, name, units, Icon }) => {
    const value = climateChange(prediction, variable, year);
    const explanation = VARIABLE_EXPLANATIONS[variable];

    return (
        <div className="vert-container">
            {renderArrow(value)}
            <div className="climate-icon-wrapper">
                <Icon
                    className="climate-arrow"
                />
                {explanation && (
                    <HelpPopover content={explanation} />
                )}
            </div>
            <PredictionSummary
                prediction={prediction}
                year={year}
                variable={variable}
                name={name}
                units={units}
            />
        </div>
    );
};

// Final component for climate summary section
const ClimateSummary = ({ regions, loading, climatePrediction, year, season }) => {
    if (regions.length === 0) return null;

    const [selectedVariable, setSelectedVariable] = useState(null);

    const handleSelect = (variableKey) => {
        setSelectedVariable((prev) =>
            prev === variableKey ? null : variableKey
        );
    };


    const isAnnual = season === "annual";
    const dryDaysUnits = isAnnual ? "days/year" : "days/season";
    const derivedDayUnits = isAnnual ? "days/year" : "days/season";
    const derivedNightUnits = isAnnual ? "nights/year" : "nights/season";

    const renderDetails = () => {
        if (!selectedVariable) {
            return (
                <div className="climate-details-placeholder">
                    <p>Please click a climate variable icon to view additional metrics.
                    </p>
                </div>
            );
        }

        if (selectedVariable === "tas") {
            return (
                <div className="climate-selected-details">
                    <h2>temperature metrics</h2>
                    <div className="horiz-container">
                        <DetailClimateVariable
                            prediction={climatePrediction}
                            year={year}
                            variable="tropical_nights"
                            name="Tropical Nights"
                            units={derivedNightUnits}
                            Icon={TropicalNightsSvg}
                        />
                        <DetailClimateVariable
                            prediction={climatePrediction}
                            year={year}
                            variable="hot_heat_days"
                            name="Hot Heat Days"
                            units={derivedDayUnits}
                            Icon={HotHeatDaysSvg}
                        />

                    </div>
                </div>
            );
        }

        if (selectedVariable === "pr") {
            return (
                <div className="climate-selected-details">
                    <h2>Rainfall metrics</h2>
                    <div className="horiz-container">
                        <DetailClimateVariable
                            prediction={climatePrediction}
                            year={year}
                            variable="heavy_rain_days"
                            name="Heavy Rain Days"
                            units={derivedDayUnits}
                            Icon={HeavyRainDaysSvg}
                        />
                    </div>
                </div>
            );
        }

        if (selectedVariable === "dry_days") {
            return (
                <div className="climate-selected-details">
                    <h2>Dry Days metrics</h2>
                    <DetailClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="rsds"
                        name="Radiation"
                        units="Watts/m2"
                        Icon={RadiationSvg}
                    />
                </div>
            );
        }

        if (selectedVariable === "sfcWind") {
            return (
                <div className="climate-selected-details">
                    <h2>Windiness metrics</h2>
                    <DetailClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="windy_days"
                        name="Windy Days"
                            units={derivedDayUnits}
                        Icon={WindSvg}
                    />
                </div>
            );
        }

        return null;
    };

    return (
        <LoadingOverlay active={loading} spinner text="Loading climate data">
            <div className="climate-summary">
                <div className="horiz-container">
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="tas"
                        name="Temperature"
                        units="°C"
                        Icon={TempSvg}
                        onClick={() => handleSelect("tas")}
                        isSelected={selectedVariable === "tas"}
                        isAnnual={isAnnual}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="pr"
                        name="Rainfall"
                        units="mm/day"
                        Icon={RainSvg}
                        onClick={() => handleSelect("pr")}
                        isSelected={selectedVariable === "pr"}
                        isAnnual={isAnnual}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="dry_days"
                        name="Dry Days"
                        units={dryDaysUnits}
                        Icon={DryDaysSvg}
                        onClick={() => handleSelect("dry_days")}
                        isSelected={selectedVariable === "dry_days"}
                        isAnnual={isAnnual}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="sfcWind"
                        name="Windiness"
                        units="m/sec"
                        Icon={WindSvg}
                        onClick={() => handleSelect("sfcWind")}
                        isSelected={selectedVariable === "sfcWind"}
                        isAnnual={isAnnual}
                    />
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
