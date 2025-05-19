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
        const baseline = parseFloat(prediction[0][`${variable}_1980_mean`]);
        const predict = parseFloat(prediction[0][`${variable}_${year}_mean`]);
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
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="pr"
                        name="Rainfall"
                        units="mm/day"
                        Icon={RainSvg}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="rsds"
                        name="Cloudiness"
                        units="Watts/m2"
                        Icon={CloudSvg}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="sfcWind"
                        name="Windiness"
                        units="m/sec"
                        Icon={WindSvg}
                    />
                </div>
                <p>
                    Note: Yearly average climate change does not always reflect the extremes of summer and winter.
                    Change the drop-down menu above to see the predictions for the different seasons.
                </p>
            </div>
        </LoadingOverlay>
    );
};

export default ClimateSummary;
