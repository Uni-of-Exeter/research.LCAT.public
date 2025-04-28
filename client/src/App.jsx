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
import Footer from "./components/footer/Footer";
import LCATHeader from "./components/header/Header";
import Introduction from "./components/header/Introduction";
import AllRegionLoader from "./components/loaders/AllRegionLoader";
import ClimatePredictionLoader from "./components/loaders/ClimatePredictionLoader";
import IsCoastalLoader from "./components/loaders/CoastalFilterLoader";
import RegionCentreLoader from "./components/loaders/RegionCentreLoader";
import IMDMap from "./components/vulnerabilities/IMDMap";
import PersonalSocialVulnerabilities from "./components/vulnerabilities/PersonalSocialVulnerabilities";
import { defaultState } from "./utils/defaultState";

const App = () => {
    const [regions, setRegions] = useState(defaultState.regions);
    const [regionType, setRegionType] = useState(defaultState.regionType);
    const [allRegions, setAllRegions] = useState(defaultState.allRegions);
    const [regionsCentre, setRegionsCentre] = useState(defaultState.mapCenter)
    const [climatePrediction, setClimatePrediction] = useState(defaultState.climatePrediction);
    const [season, setSeason] = useState(defaultState.season);
    const [rcp, setRcp] = useState(defaultState.rcp);
    const [year] = useState(defaultState.year);
    const [variable, setVariable] = useState(defaultState.variable);
    const [isPredictionLoading, setIsPredictionLoading] = useState(defaultState.isPredictionLoading);
    const [selectedHazardName, setSelectedHazardName] = useState(defaultState.selectedHazardName);
    const [applyCoastalFilter, setApplyCoastalFilter] = useState(defaultState.applyCoastalFilter);

    return (
        <div className="App">
            <LCATHeader />
            <Introduction />

            <AllRegionLoader regionType={regionType} setAllRegions={setAllRegions} />
            <IsCoastalLoader regionType={regionType} regions={regions} setApplyCoastalFilter={setApplyCoastalFilter} />
            <RegionCentreLoader regionType={regionType} regions={regions} setRegionsCentre={setRegionsCentre} />

            <ClimatePredictionLoader
                regions={regions}
                season={season}
                rcp={rcp}
                regionType={regionType}
                setClimatePrediction={setClimatePrediction}
                setIsPredictionLoading={setIsPredictionLoading}
            />

            <div className="white-section">
                <ClimateMap
                    regions={regions}
                    setRegions={setRegions}
                    allRegions={allRegions}
                    regionType={regionType}
                    setRegionType={setRegionType}
                />
            </div>

            {regions.length > 0 && (
                <div className="grey-section">
                    <ClimateSettings
                        regions={regions}
                        season={season}
                        rcp={rcp}
                        setRcp={setRcp}
                        setSeason={setSeason}
                    />

                    <ClimateSummary
                        climatePrediction={climatePrediction}
                        year={year}
                        regions={regions}
                        loading={isPredictionLoading}
                    />

                    <Graph
                        regions={regions}
                        season={season}
                        rcp={rcp}
                        setSeason={setSeason}
                        setRcp={setRcp}
                        climatePrediction={climatePrediction}
                        variable={variable}
                        setVariable={setVariable}
                    />
                </div>
            )}

            {regions.length > 0 && (
                <div className="white-section">
                    <ClimateHazardRisk applyCoastalFilter={applyCoastalFilter} />
                </div>
            )}

            {regions.length > 0 && (
                <div className="grey-section">
                    <ClimateImpactSummary
                        loading={isPredictionLoading}
                        selectedHazardName={selectedHazardName}
                        setSelectedHazardName={setSelectedHazardName}
                        applyCoastalFilter={applyCoastalFilter}
                    />
                    <KumuImpactPathway
                        regions={regions}
                        selectedHazardName={selectedHazardName}
                        setSelectedHazardName={setSelectedHazardName}
                        applyCoastalFilter={applyCoastalFilter}
                    />
                </div>
            )}

            {regions.length > 0 && (
                <div className="white-section">
                    <PersonalSocialVulnerabilities />
                    <IMDMap regions={regions} regionType={regionType} regionsCentre={regionsCentre} />
                </div>
            )}

            {regions.length > 0 && (
                <div className="grey-section">
                    <StaticAdaptations
                        selectedHazardName={selectedHazardName}
                        setSelectedHazardName={setSelectedHazardName}
                        applyCoastalFilter={applyCoastalFilter}
                    />
                </div>
            )}

            <Footer />
        </div>
    );
};

export default App;
