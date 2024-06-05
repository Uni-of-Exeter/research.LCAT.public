/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import LoadingOverlay from "react-loading-overlay-ts";

import TempSvg from "../../images/climate/Temperature";
import RainSvg from "../../images/climate/Rain";
import WindSvg from "../../images/climate/WindSpeed";
import CloudSvg from "../../images/climate/CloudCover";
import IncreaseSvg from "../../images/increase";
import DecreaseSvg from "../../images/decrease";

import "./ClimateSummary.css";

function climateChange(prediction, variable, year) {
    if (prediction.length > 0) {
        if (prediction[0][variable + "_1980"] != null) {
            let baseline = parseFloat(prediction[0][variable + "_1980"]);
            let predict = parseFloat(prediction[0][variable + "_" + year]);
            return predict - baseline;
        }
    }
    return null;
}

function arrow(prediction, year, variable) {
    let v = climateChange(prediction, variable, year);
    if (v == null) return null;
    // more radiation = less cloud
    if (variable === "rsds") {
        v = -v;
    }
    if (v < 0) return <DecreaseSvg className="climate-arrow" />;
    else return <IncreaseSvg className="climate-arrow" />;
}

function predict(prediction, year, variable, name, units) {
    if (prediction.length > 0) {
        let v = climateChange(prediction, variable, year);
        if (v == null) return <span>No data yet for this area, coming soon.</span>;
        let pv = Math.abs(v).toFixed(2);
        if (variable === "rsds") {
            v = -v;
        }
        let dir = "increases";
        if (v < 0) dir = "decreases";
        if (v === 0) {
            return <span>No change in {name}</span>;
        }
        return (
            <div className="summary-text">
                {name} {dir} by {pv} {units}
            </div>
        );
    }
    return "Not loaded yet";
}

function ClimateSummary(props) {
    if (props.regions.length === 0) {
        return null;
    }
    return (
        <LoadingOverlay active={props.loading} spinner text={"Loading climate data"}>
            <div className="climate-summary">
                <div className="horiz-container">
                    <div className="vert-container">
                        {arrow(props.climatePrediction, props.year, "tas")}
                        <TempSvg className="climate-arrow" />
                        {predict(props.climatePrediction, props.year, "tas", "Temperature", "°C")}
                    </div>
                    <div className="vert-container">
                        {arrow(props.climatePrediction, props.year, "pr")}
                        <RainSvg className="climate-arrow" />
                        {predict(props.climatePrediction, props.year, "pr", "Rainfall", "mm/day")}
                    </div>
                    <div className="vert-container">
                        {arrow(props.climatePrediction, props.year, "rsds")}
                        <CloudSvg className="climate-arrow" />
                        {predict(props.climatePrediction, props.year, "rsds", "Cloudiness", "Watts/m2")}
                    </div>
                    <div className="vert-container">
                        {arrow(props.climatePrediction, props.year, "sfcwind")}
                        <WindSvg className="climate-arrow" />
                        {predict(props.climatePrediction, props.year, "sfcwind", "Windiness", "m/sec")}
                    </div>
                </div>
                <p>
                    Note: Yearly average climate change does not always reflect the extremes of summer and winter.
                    Change the drop down menu above to see the predictions for the different seasons.
                </p>
            </div>
        </LoadingOverlay>
    );
}

export default ClimateSummary;
