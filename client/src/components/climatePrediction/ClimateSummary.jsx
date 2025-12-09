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
import { ReactComponent as DryDaysSvg } from "../../images/climate/DryDays.svg";
import { ReactComponent as HeavyRainDaysSvg } from "../../images/climate/HeavyRainDays.svg";
import { ReactComponent as HotHeatDaysSvg } from "../../images/climate/HotHeatDays.svg";
import RainSvg from "../../images/climate/Rain";
import TempSvg from "../../images/climate/Temperature";
import { ReactComponent as TropicalNightsSvg } from "../../images/climate/TropicalNights.svg";
import WindSvg from "../../images/climate/WindSpeed";
import { climateChange, formatClimateData } from "../../utils/climateUtils";

// Function to render an arrow pointing up or down
const renderArrow = (value, variable) => {
    if (value == null) return null;
    // Invert value for rsds (more radiation = less cloud)
    const adjustedValue = variable === "rsds" ? -value : value;
    return adjustedValue < 0 ? <DecreaseSvg className="climate-arrow" /> : <IncreaseSvg className="climate-arrow" />;
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
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="tropical_nights"
                        name="Tropical Nights"
                        units="nights/year"
                        Icon={TropicalNightsSvg}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="hot_heat_days"
                        name="Hot Heat Days"
                        units="days/year"
                        Icon={HotHeatDaysSvg}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="heavy_rain_days"
                        name="Heavy Rain Days"
                        units="days/year"
                        Icon={HeavyRainDaysSvg}
                    />
                    <ClimateVariable
                        prediction={climatePrediction}
                        year={year}
                        variable="dry_days"
                        name="Dry Days"
                        units="days/year"
                        Icon={DryDaysSvg}
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
