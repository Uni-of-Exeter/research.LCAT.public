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

import React, { useState } from "react";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import LoadingOverlay from "react-loading-overlay-ts";

import GeoJSONLoader from "./GeoJSONLoader.jsx";

const tileLayer = {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
};

const center = [55.8, -3.2];
const highlightCol = "#ffd768ff";

const ClimateMap = ({ regions, setRegions, regionType, setRegionType }) => {
    const [geojsonKey, setGeojsonKey] = useState(0);
    const [geojson, setGeojson] = useState(false);
    const [loading, setLoading] = useState(true);
    const [triggerLoadingIndicator, setTriggerLoadingIndicator] = useState(true);

    const regionsIncludes = (id) => regions.some((e) => e.id === id);

    const onEachFeature = async (feature, layer) => {
        let col = "#00000000";
        let gid = feature.properties.gid;

        layer.bindTooltip(feature.properties.name);
        layer.setStyle({
            color: "#115158ff",
            weight: 3,
            fillColor: col,
            fillOpacity: 1,
        });

        if (regionsIncludes(gid)) {
            layer.setStyle({ fillColor: highlightCol });
        }

        layer.on("mouseover", () => {
            layer.bringToFront();
            layer.setStyle({ weight: 6 });
        });

        layer.on("mouseout", () => {
            layer.setStyle({ weight: 3 });
        });

        layer.on("click", () => {
            setRegions((prev) => {
                if (!regionsIncludes(gid)) {
                    layer.setStyle({ fillColor: highlightCol, fillOpacity: 1 });
                    return [
                        ...prev,
                        {
                            id: gid,
                            name: feature.properties.name,
                            properties: feature.properties,
                            clearMe: () => layer.setStyle({ fillColor: col, fillOpacity: 1 }),
                        },
                    ];
                } else {
                    layer.setStyle({ fillColor: col, fillOpacity: 1 });
                    return prev.filter((r) => r.id !== gid);
                }
            });
        });
    };

    const clear = () => {
        regions.forEach((r) => r.clearMe());
        setRegions([]);
        setGeojsonKey((prev) => prev + 1);
    };

    const geojsonCallback = (data) => {
        if (data.features != null) {
            setGeojson(data);
            setGeojsonKey((prev) => prev + 1);
        } else {
            setGeojson({ features: [] });
            setGeojsonKey((prev) => prev + 1);
        }
        setTriggerLoadingIndicator(false);
    };

    const regionTypeToName = (type) => {
        const mapping = {
            boundary_uk_counties: "UK Counties",
            boundary_la_districts: "Local Authority Districts",
            boundary_lsoa: "LSOA",
            boundary_msoa: "MSOA (Eng/Wales)",
            boundary_parishes: "Parishes (Eng/Wales)",
            boundary_sc_dz: "Data Zones (Scotland)",
            boundary_ni_dz: "Data Zones (Northern Ireland)",
            boundary_iom: "Isle of Man",
        };
        return mapping[type] || "";
    };

    return (
        <div>
            <h1>Select your area</h1>
            <p>
                To begin, select the area/s you are interested in by clicking on the map. Climate data for your chosen
                area/s will appear below. The map units can be changed to explore the UK and the Isle of Man via the
                following dropdown:
                <select
                    onChange={(e) => {
                        setRegionType(e.target.value);
                        setRegions([]);
                        setTriggerLoadingIndicator(true);
                    }}
                    value={regionType}
                >
                    <option value="boundary_uk_counties">UK Counties</option>
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
                <div className="climate-map">
                    <LoadingOverlay
                        active={loading && triggerLoadingIndicator}
                        spinner
                        text={"Loading " + regionTypeToName(regionType)}
                    >
                        <MapContainer center={center} zoom={6} minZoom={5} scrollWheelZoom={true}>
                            <GeoJSONLoader
                                apicall="/api/region"
                                table={regionType}
                                loadingCallback={(isLoading) => setLoading(isLoading)}
                                callback={geojsonCallback}
                            />
                            {geojson && <GeoJSON key={geojsonKey} data={geojson} onEachFeature={onEachFeature} />}
                            <TileLayer {...tileLayer} />
                        </MapContainer>
                    </LoadingOverlay>
                </div>
                <div className="map-selection">
                    <h2>{regionTypeToName(regionType)} selected</h2>
                    {regions.map((r) => (
                        <ul key={r.name}>{r.name}</ul>
                    ))}
                    {regions.length > 0 && <button onClick={clear}>Clear selection</button>}
                </div>
            </div>

            <p className="note">
                Data source: The boundaries are from
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
