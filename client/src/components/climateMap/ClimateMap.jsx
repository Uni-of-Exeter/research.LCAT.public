/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./ClimateMap.css";

import React, { useEffect, useRef, useState } from "react";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import LoadingOverlay from "react-loading-overlay-ts";

import GeoJSONLoader from "./GeoJSONLoader.jsx";

const tileLayer = {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
};

const center = [55.8, -3.2];
const highlightCol = "#ffd768ff";

const mapping = {
    boundary_uk_counties: "UK Counties and Unitary Authorities",
    boundary_la_districts: "Local Authority Districts",
    boundary_lsoa: "LSOA",
    boundary_msoa: "MSOA (Eng/Wales)",
    boundary_parishes: "Parishes (Eng/Wales)",
    boundary_sc_dz: "Data Zones (Scotland)",
    boundary_ni_dz: "Data Zones (Northern Ireland)",
    boundary_iom: "Isle of Man",
};

const regionsToShowToggle = [
    "MSOA (Eng/Wales)",
    "Parishes (Eng/Wales)",
    "Data Zones (Scotland)",
    "Data Zones (Northern Ireland)",
];

const ClimateMap = ({ regions, setRegions, allRegions, regionType, setRegionType }) => {
    const [geojsonKey, setGeojsonKey] = useState(0);
    const [geojson, setGeojson] = useState(false);
    const [loading, setLoading] = useState(true);
    const [triggerLoadingIndicator, setTriggerLoadingIndicator] = useState(true);
    const [isDrawerOpen, setIsDrawerOpen] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");

    const layerMap = useRef(new Map());
    const [gidToFeatureMap, setGidToFeatureMap] = useState(new Map());

    const onEachFeature = (feature, layer) => {
        const col = "#00000000";
        const gid = feature.properties.gid;
        const name = feature.properties.name;
        const isCoastal = feature.properties.isCoastal;
        const regionCenter = feature.properties.geometricCenter;
        const isSelected = regions.some((e) => e.id === gid);

        layer.bindTooltip(name);
        layer.setStyle({
            color: "#115158ff",
            weight: 3,
            fillColor: isSelected ? highlightCol : col,
            fillOpacity: 1,
        });

        // Store the layer reference
        layerMap.current.set(gid, layer);

        layer.on("mouseover", () => {
            layer.bringToFront();
            layer.setStyle({ weight: 6 });
        });

        layer.on("mouseout", () => {
            layer.setStyle({ weight: 3 });
        });

        layer.on("click", () => toggleRegion(gid, name, isCoastal, regionCenter, layer));
    };

    const toggleRegion = (gid, name, isCoastal, regionCenter, layer = null) => {
        const col = "#00000000";
        const targetLayer = layer || layerMap.current.get(gid);

        setRegions((prevRegions) => {
            const alreadySelected = prevRegions.some((r) => r.id === gid);
            if (!alreadySelected) {
                targetLayer && targetLayer.setStyle({ fillColor: highlightCol, fillOpacity: 1 });
                return [
                    ...prevRegions,
                    {
                        id: gid,
                        name: name,
                        isCoastal: isCoastal,
                        regionCenter: regionCenter,
                        clearMe: () => targetLayer && targetLayer.setStyle({ fillColor: col, fillOpacity: 1 }),
                    },
                ];
            } else {
                targetLayer && targetLayer.setStyle({ fillColor: col, fillOpacity: 1 });
                return prevRegions.filter((r) => r.id !== gid);
            }
        });
    };

    const clear = () => {
        regions.forEach((r) => r.clearMe());
        setRegions([]);
        setGeojsonKey((prev) => prev + 1);
        layerMap.current.clear();
    };

    const handleSetGeojson = (data) => {
        const geojsonData = data.features ? data : { features: [] };

        const map = new Map();
        geojsonData.features.forEach((f) => {
            map.set(f.properties.gid, f);
        });

        setGeojson(geojsonData);
        setGidToFeatureMap(map);
        setGeojsonKey((prev) => prev + 1);
        setTriggerLoadingIndicator(false);
    };

    const regionTypeToName = (mapping, type) => {
        return mapping[type] || "";
    };

    const filteredRegions = allRegions
        ? allRegions
              .filter((region) => region.name.toLowerCase().includes(searchTerm.toLowerCase()))
              .sort((a, b) => a.name.localeCompare(b.name))
        : [];

    const toggleDrawer = () => {
        setIsDrawerOpen(!isDrawerOpen);
    };

    // Hide search drawer in map if window becomes narrow (or vice versa)
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth < 750) {
                setIsDrawerOpen(false);
            } else {
                setIsDrawerOpen(true);
            }
        };

        // Run once on mount to set the initial state
        handleResize();

        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    return (
        <div>
            <h1>Select your area</h1>
            <p>
                To begin, select the area/s you are interested in by clicking on the map. Climate data for your chosen
                area/s will appear below.{" "}
                <select
                    onChange={(e) => {
                        setRegionType(e.target.value);
                        setRegions([]);
                        setTriggerLoadingIndicator(true);
                    }}
                    value={regionType}
                >
                    <option value="boundary_uk_counties">UK Counties and Unitary Authorities</option>
                    <option value="boundary_la_districts">Local Authority Districts</option>
                    <option value="boundary_parishes">Parishes (Eng/Wales)</option>
                    <option value="boundary_msoa">MSOA (Eng/Wales)</option>
                    <option value="boundary_sc_dz">Data Zones (Scotland)</option>
                    <option value="boundary_lsoa">LSOA (Eng/Wales)</option>
                    <option value="boundary_ni_dz">Data Zones (Northern Ireland)</option>
                    <option value="boundary_iom">Isle of Man</option>
                </select>
            </p>

            <div className="map-container">
                <div className={`climate-map ${isDrawerOpen ? "drawer-open" : "drawer-closed"}`}>
                    <LoadingOverlay
                        active={loading && triggerLoadingIndicator}
                        spinner
                        text={"Loading " + regionTypeToName(mapping, regionType)}
                    >
                        <MapContainer center={center} zoom={6} minZoom={5} scrollWheelZoom={true}>
                            <GeoJSONLoader
                                apicall="/api/region"
                                table={regionType}
                                setLoading={setLoading}
                                handleSetGeojson={handleSetGeojson}
                            />
                            {geojson && <GeoJSON key={geojsonKey} data={geojson} onEachFeature={onEachFeature} />}
                            <TileLayer {...tileLayer} />
                        </MapContainer>
                    </LoadingOverlay>

                    <button className="drawer-toggle-button" onClick={toggleDrawer} aria-label="Toggle Search Drawer">
                        {isDrawerOpen ? "→" : "←"}
                    </button>

                    {isDrawerOpen && (
                        <div className="climate-map-search-container">
                            <div className="climate-map-search">
                                <input
                                    type="text"
                                    placeholder="Search regions..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                />
                            </div>
                            <div className="climate-map-checkbox-list">
                                {filteredRegions.map((region) => {
                                    const isSelected = regions.some((r) => r.id === region.gid);
                                    const checkboxId = `checkbox-${region.gid}`;
                                    return (
                                        <div key={region.gid}>
                                            <input
                                                type="checkbox"
                                                id={checkboxId}
                                                checked={isSelected}
                                                onChange={() => {
                                                    const feature = gidToFeatureMap.get(region.gid);
                                                    const isCoastal = feature?.properties?.isCoastal;
                                                    const regionCenter = feature?.properties?.geometricCenter;
                                                    toggleRegion(region.gid, region.name, isCoastal, regionCenter);
                                                }}
                                            />
                                            <label htmlFor={checkboxId}>{region.name}</label>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>

                <div className="map-selection">
                    <h2>{regionTypeToName(mapping, regionType)} selected</h2>
                    {regions.map((r) => (
                        <ul key={r.name}>{r.name}</ul>
                    ))}
                    {regions.length > 0 && <button onClick={clear}>Clear selection</button>}
                </div>
            </div>

            <p className="note">
                Data source: The boundaries are from{" "}
                <a
                    href="https://github.com/Uni-of-Exeter/research.LCAT.public/blob/main/docs/4-sources.md"
                    target="_blank"
                    rel="noreferrer"
                >
                    various sources listed here
                </a>
                .
            </p>
        </div>
    );
};

export default ClimateMap;
