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
    console.log(isSelected)
    return (
        <div className="vert-container">
            {renderArrow(value, variable)}
            <button
                type="button"
                className={`climate-icon-button ${isSelected ? "climate-variable-selected" : ""}`}
                onClick={onClick}
                disabled={!isAnnual}
            >
                <Icon
                    className="climate-arrow"
                    selected={isSelected}
                    isAnnual={isAnnual}
                />
            </button>
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

    return (
        <div className="vert-container">
            {renderArrow(value)}
            <Icon
                className="climate-arrow"
            />
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

    const renderDetails = () => {
        if (!selectedVariable) {
            return (
                <div className="climate-details-placeholder">
                    <p>Please click a climate variable icon to view details. <i> *Only annual predictions are available for these measures.</i>
                    </p>

                </div>
            );
        }

        if (selectedVariable === "tas") {
            return (
                <div className="climate-selected-details">
                    <h2>Additional temperature metrics</h2>
                    <div className="horiz-container">
                        <DetailClimateVariable
                            prediction={climatePrediction}
                            year={year}
                            variable="tropical_nights"
                            name="Tropical Nights"
                            units="nights/year"
                            Icon={TropicalNightsSvg}
                        />
                        <DetailClimateVariable
                            prediction={climatePrediction}
                            year={year}
                            variable="hot_heat_days"
                            name="Hot Heat Days"
                            units="days/year"
                            Icon={HotHeatDaysSvg}
                        />

                    </div>
                </div>
            );
        }

        if (selectedVariable === "pr") {
            return (
                <div className="climate-selected-details">
                    <h2>Rainfall details</h2>
                    <div className="horiz-container">
                        <DetailClimateVariable
                            prediction={climatePrediction}
                            year={year}
                            variable="heavy_rain_days"
                            name="Heavy Rain Days"
                            units="days/year"
                            Icon={HeavyRainDaysSvg}
                        />
                        <DetailClimateVariable
                            prediction={climatePrediction}
                            year={year}
                            variable="dry_days"
                            name="Dry Days"
                            units="days/year"
                            Icon={DryDaysSvg}
                        />
                    </div>
                </div>
            );
        }

        if (selectedVariable === "dry_days") {
            return (
                <div className="climate-selected-details">
                    <h2>Dry Days details</h2>
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
                        units="days/year"
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
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="windy_days"
                        name="Windy Days"
                        units="days/year"
                        Icon={WindSvg}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="windy_days"
                        name="Windy Days"
                        units="days/year"
                        Icon={WindSvg}
                    />
                </div>
                {isAnnual && renderDetails()}
                <p>
                    Note: Yearly average climate change does not always reflect the extremes of summer and winter.
                    Change the drop-down menu above to see the predictions for the different seasons.
                </p>
            </div>
        </LoadingOverlay>
    );
};

export default ClimateSummary;
