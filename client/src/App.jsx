// Development before 2024 Copyright (C) Then Try This and University of Exeter
// Development from 2024 Copyright (C) University of Exeter
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the Common Good Public License Beta 1.0 as
// published at http://www.cgpl.org
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// Common Good Public License Beta 1.0 for more details.

import React from "react";

import Introduction from "./components/header/Introduction";
import LCATHeader from "./components/header/Header";

import ClimateHazardRisk from "./components/climateHazard/ClimateHazardRisk";
import ClimateImpactSummary from "./components/climateImpacts/ClimateImpactSummary";
import ClimateMap from "./components/climateMap/ClimateMap";
import ClimatePredictionLoader from "./components/loaders/ClimatePredictionLoader";
import ClimateSettings from "./components/climatePrediction/ClimateSettings";
import ClimateSummary from "./components/climatePrediction/ClimateSummary";
import Feedback from "./components/feedback/Feedback";
import Footer from "./components/footer/Footer";
import Graph from "./components/climatePrediction/Graph";

import KumuImpactPathway from "./components/climateImpacts/KumuImpactPathway";

import PersonalSocialVulnerabilities from "./components/vulnerabilities/PersonalSocialVulnerabilities";
import StaticAdaptations from "./components/adaptations/StaticAdaptations";

import "./App.css";

class App extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            regions: [],
            regionType: "counties",
            climatePrediction: [],
            season: "annual",
            rcp: "rcp60",
            year: 2070,
            loadingPrediction: false,
            selectedHazardName: "Extreme Storms",
        };
    }

    render() {
        return (
            <div className="App">
                <LCATHeader />
                <Introduction />

                <ClimatePredictionLoader
                    regions={this.state.regions}
                    season={this.state.season}
                    rcp={this.state.rcp}
                    regionType={this.state.regionType}
                    callback={(prediction) => {
                        this.setState(() => ({
                            climatePrediction: prediction,
                            loadingPrediction: false,
                        }));
                    }}
                    loadingCallback={() => {
                        this.setState(() => ({
                            loadingPrediction: true,
                        }));
                    }}
                />

                <div className="white-section">
                    <ClimateMap
                        regionType={this.state.regionType}
                        regionsCallback={(regions, regionType) => {
                            this.setState({
                                regionType: regionType,
                                regions: regions,
                            });
                        }}
                    />
                </div>

                {this.state.regions.length > 0 && (
                    <div className="grey-section">
                        <ClimateSettings
                            regions={this.state.regions}
                            season={this.state.season}
                            rcp={this.state.rcp}
                            rcpCallback={(rcp) => {
                                this.setState(() => ({
                                    rcp: rcp,
                                }));
                            }}
                            seasonCallback={(season) => {
                                this.setState(() => ({
                                    season: season,
                                }));
                            }}
                            yearCallback={(year) => {
                                this.setState(() => ({
                                    year: year,
                                }));
                            }}
                        />

                        <ClimateSummary
                            climatePrediction={this.state.climatePrediction}
                            year={this.state.year}
                            regions={this.state.regions}
                            loading={this.state.loadingPrediction}
                        />

                        <Graph
                            regions={this.state.regions}
                            boundary={this.state.regionType}
                            season={this.state.season}
                            rcp={this.state.rcp}
                            seasonCallback={(season) => {
                                this.setState(() => ({
                                    season: season,
                                }));
                            }}
                            rcpCallback={(rcp) => {
                                this.setState(() => ({
                                    rcp: rcp,
                                }));
                            }}
                        />
                    </div>
                )}

                {this.state.regions.length > 0 && (
                    <div className="white-section">
                        <ClimateHazardRisk loading={this.state.loadingPrediction} />
                    </div>
                )}

                {this.state.regions.length > 0 && (
                    <div className="grey-section">
                        <ClimateImpactSummary
                            loading={this.state.loadingPrediction}
                            selectedHazardName={this.state.selectedHazardName}
                            hazardCallback={(hazard) => {
                                this.setState(() => ({
                                    selectedHazardName: hazard,
                                }));
                            }}
                        />
                        <KumuImpactPathway
                            regions={this.state.regions}
                            selectedHazardName={this.state.selectedHazardName}
                            hazardCallback={(hazard) => {
                                this.setState(() => ({
                                    selectedHazardName: hazard,
                                }));
                            }}
                        />
                    </div>
                )}

                {this.state.regions.length > 0 && (
                    <div className="white-section">
                        <PersonalSocialVulnerabilities loading={this.state.loadingPrediction} />
                    </div>
                )}

                {this.state.regions.length > 0 && (
                    <div className="grey-section">
                        <StaticAdaptations
                            regions={this.state.regions}
                            selectedHazardName={this.state.selectedHazardName}
                            hazardCallback={(hazard) => {
                                this.setState(() => ({
                                    selectedHazardName: hazard,
                                }));
                            }}
                        />
                    </div>
                )}

                <Feedback />

                <Footer />
            </div>
        );
    }
}

export default App;
