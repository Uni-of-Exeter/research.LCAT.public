/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./App.css";

import React, { useState } from "react";

import StaticAdaptations from "./components/adaptations/StaticAdaptations";
import ClimateHazardRisk from "./components/climateHazard/ClimateHazardRisk";
import ClimateImpactSummary from "./components/climateImpacts/ClimateImpactSummary";
import KumuImpactPathway from "./components/climateImpacts/KumuImpactPathway";
import ClimateMap from "./components/climateMap/ClimateMap";
import ClimateSettings from "./components/climatePrediction/ClimateSettings";
import ClimateSummary from "./components/climatePrediction/ClimateSummary";
import Graph from "./components/climatePrediction/Graph";
import Feedback from "./components/feedback/Feedback";
import Footer from "./components/footer/Footer";
import LCATHeader from "./components/header/Header";
import Introduction from "./components/header/Introduction";
import ClimatePredictionLoader from "./components/loaders/ClimatePredictionLoader";
import PersonalSocialVulnerabilities from "./components/vulnerabilities/PersonalSocialVulnerabilities";
import { defaultState } from "./utils/defaultState";

function App() {
    const [regions, setRegions] = useState(defaultState.regions);
    const [regionType, setRegionType] = useState(defaultState.regionType);
    const [climatePrediction, setClimatePrediction] = useState(defaultState.climatePrediction);
    const [season, setSeason] = useState(defaultState.season);
    const [rcp, setRcp] = useState(defaultState.rcp);
    const [year, setYear] = useState(defaultState.year);
    const [loadingPrediction, setLoadingPrediction] = useState(defaultState.loadingPrediction);
    const [selectedHazardName, setSelectedHazardName] = useState(defaultState.selectedHazardName);

    return (
        <div className="App">
            <LCATHeader />
            <Introduction />

            <ClimatePredictionLoader
                regions={regions}
                season={season}
                rcp={rcp}
                regionType={regionType}
                callback={(prediction) => {
                    setClimatePrediction(prediction);
                    setLoadingPrediction(false);
                }}
                loadingCallback={() => {
                    setLoadingPrediction(true);
                }}
            />

            <div className="white-section">
                <ClimateMap
                    regionType={regionType}
                    regionsCallback={(newRegions, newRegionType) => {
                        setRegionType(newRegionType);
                        setRegions(newRegions);
                    }}
                />
            </div>

            {regions.length > 0 && (
                <div className="grey-section">
                    <ClimateSettings
                        regions={regions}
                        season={season}
                        rcp={rcp}
                        rcpCallback={setRcp}
                        seasonCallback={setSeason}
                        yearCallback={setYear}
                    />

                    <ClimateSummary
                        climatePrediction={climatePrediction}
                        year={year}
                        regions={regions}
                        loading={loadingPrediction}
                    />

                    <Graph
                        regions={regions}
                        boundary={regionType}
                        season={season}
                        rcp={rcp}
                        seasonCallback={setSeason}
                        rcpCallback={setRcp}
                    />
                </div>
            )}

            {regions.length > 0 && (
                <div className="white-section">
                    <ClimateHazardRisk loading={loadingPrediction} />
                </div>
            )}

            {regions.length > 0 && (
                <div className="grey-section">
                    <ClimateImpactSummary
                        loading={loadingPrediction}
                        selectedHazardName={selectedHazardName}
                        hazardCallback={setSelectedHazardName}
                    />
                    <KumuImpactPathway
                        regions={regions}
                        selectedHazardName={selectedHazardName}
                        hazardCallback={setSelectedHazardName}
                    />
                </div>
            )}

            {regions.length > 0 && (
                <div className="white-section">
                    <PersonalSocialVulnerabilities loading={loadingPrediction} />
                </div>
            )}

            {regions.length > 0 && (
                <div className="grey-section">
                    <StaticAdaptations
                        regions={regions}
                        selectedHazardName={selectedHazardName}
                        hazardCallback={setSelectedHazardName}
                    />
                </div>
            )}

            <Feedback />
            <Footer />
        </div>
    );
}

export default App;
