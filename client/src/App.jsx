/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

/* global gtag */

import "./App.css";

import { useEffect, useRef,useState } from "react";

import StaticAdaptations from "./components/adaptations/StaticAdaptations";
import ClimateHazardRisk from "./components/climateHazard/ClimateHazardRisk";
import ClimateImpactSummary from "./components/climateImpacts/ClimateImpactSummary";
import KumuImpactPathway from "./components/climateImpacts/KumuImpactPathway";
import ClimateMap from "./components/climateMap/ClimateMap";
import ClimateSettings from "./components/climatePrediction/ClimateSettings";
import ClimateSummary from "./components/climatePrediction/ClimateSummary";
import Graph from "./components/climatePrediction/Graph";
import CookieConsent from "./components/cookies/ConsentBanner";
import Footer from "./components/footer/Footer";
import LCATHeader from "./components/header/Header";
import Introduction from "./components/header/Introduction";
import AllRegionLoader from "./components/loaders/AllRegionLoader";
import ClimateAveragesLoader from "./components/loaders/ClimateAveragesLoader";
import ClimatePredictionLoader from "./components/loaders/ClimatePredictionLoader";
import IsCoastalLoader from "./components/loaders/CoastalFilterLoader";
import IMDMap from "./components/vulnerabilities/IMDMap";
import PersonalSocialVulnerabilities from "./components/vulnerabilities/PersonalSocialVulnerabilities";
import { defaultState } from "./utils/defaultState";

const useScrollTracking = () => {
    const sectionsRef = useRef(new Set());
    
    useEffect(() => {
        
        const handleScroll = () => {
            const sections = document.querySelectorAll('[data-section]');
            
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
                                
                if (isVisible && !sectionsRef.current.has(section.dataset.section)) {
                    
                    // Track section view
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'section_view', {
                            section_name: section.dataset.section,
                            timestamp: Date.now()
                        });
                    }
                    
                    sectionsRef.current.add(section.dataset.section);
                }
            });
        };

        window.addEventListener('scroll', handleScroll);
        handleScroll(); // Check initial state
        
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);
};

const App = () => {
    const [regions, setRegions] = useState(defaultState.regions);
    const [regionType, setRegionType] = useState(defaultState.regionType);
    const [allRegions, setAllRegions] = useState(defaultState.allRegions);
    const [climatePrediction, setClimatePrediction] = useState(defaultState.climatePrediction);
    const [climateAverages, setClimateAverages] = useState(defaultState.climateAverages);
    //const [climateAverageRanges, setClimateAverageRanges] = useState(defaultState.climateAverageRanges);
    const [season, setSeason] = useState(defaultState.season);
    const [rcp, setRcp] = useState(defaultState.rcp);
    const [year] = useState(defaultState.year);
    const [variable, setVariable] = useState(defaultState.variable);
    const [isPredictionLoading, setIsPredictionLoading] = useState(defaultState.isPredictionLoading);
    const [areAveragesLoading, setAreAveragesLoading] = useState(defaultState.areAveragesLoading);
    const [selectedHazardName, setSelectedHazardName] = useState(defaultState.selectedHazardName);
    const [applyCoastalFilter, setApplyCoastalFilter] = useState(defaultState.applyCoastalFilter);

    useScrollTracking();

    useEffect(() => {
        if (regions.length === 0) {
            setSeason(defaultState.season);
            setRcp(defaultState.rcp);
            setVariable(defaultState.variable);
            setClimatePrediction(defaultState.climatePrediction)
            setClimateAverages(defaultState.climateAverages)
            setSelectedHazardName(defaultState.selectedHazardName)
            setApplyCoastalFilter(defaultState.applyCoastalFilter)
        }
    }, [regions]);

    return (
        <>
            <div className="App">
                <LCATHeader />
                <Introduction />

                <AllRegionLoader regionType={regionType} setAllRegions={setAllRegions} />
                <IsCoastalLoader regionType={regionType} regions={regions} setApplyCoastalFilter={setApplyCoastalFilter} />

                <ClimatePredictionLoader
                    regions={regions}
                    season={season}
                    rcp={rcp}
                    regionType={regionType}
                    setClimatePrediction={setClimatePrediction}
                    setIsPredictionLoading={setIsPredictionLoading}
                />

            <ClimateAveragesLoader
                rcp={rcp}
                season={season}
                variable={variable}
                setClimateAverages={setClimateAverages}
                setAreAveragesLoading={setAreAveragesLoading}
            />

             {/* <ClimateAverageRangesLoader
                setClimateAverageRanges={setClimateAverageRanges}
            /> */}

                <div data-section="map" className="white-section">
                    <ClimateMap
                        regions={regions}
                        setRegions={setRegions}
                        allRegions={allRegions}
                        regionType={regionType}
                        setRegionType={setRegionType}
                    />
                </div>

                {regions.length > 0 && (
                    <div data-section="details" className="grey-section">
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
                        loading={isPredictionLoading || areAveragesLoading}
                        climateAverages={climateAverages}
                        climateAverageRanges={0}
                        variable={variable}
                        setVariable={setVariable}
                    />
                </div>
            )}

                {regions.length > 0 && (
                    <div data-section="hazard" className="white-section">
                        <ClimateHazardRisk applyCoastalFilter={applyCoastalFilter} />
                    </div>
                )}

                {regions.length > 0 && (
                    <div data-section="impacts" className="grey-section">
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
                    <div data-section="vulnerabilities" className="white-section">
                        <PersonalSocialVulnerabilities />
                        {regionType !== "boundary_iom" && <IMDMap regions={regions} regionType={regionType} />}
                    </div>
                )}

                {regions.length > 0 && (
                    <div data-section="adaptations" className="grey-section">
                        <StaticAdaptations
                            selectedHazardName={selectedHazardName}
                            applyCoastalFilter={applyCoastalFilter}
                        />
                    </div>
                )}

                <Footer 
                    regions={regions}
                    climatePrediction={climatePrediction}
                    selectedHazardName={selectedHazardName}
                    rcp={rcp}
                    season={season}
                />
            </div>
            <CookieConsent />
        </>
    );
};

export default App;
