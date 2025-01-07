/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./Graph.css";

import React, { useEffect, useState } from "react";
import { useCollapse } from "react-collapsed";
import { CartesianGrid, Label, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// import { climateAverages } from "../../core/climate";
import { andify } from "../../utils/utils";

// const FlexibleXYPlot = makeWidthFlexible(XYPlot);
const winterCol = "#a4f9c8";
const summerCol = "#4c9f70";
const selectedRegionCol = "#216331";
const averageRegionCol = "#48b961";

const units = {
    tas: { label: "Temperature", unit: "°C" },
    pr: { label: "Rainfall", unit: "mm/day" },
    sfcWind: { label: "Wind", unit: "m/s" },
    rsds: { label: "Cloudiness", unit: "W/m²" },
    default: { label: "", unit: "" },
};

const Graph = (props) => {
    const { regions, season, rcp, setSeason, setRcp, climatePrediction, variable, setVariable } = props;

    const [data, setData] = useState([]);
    // const [showAverage, setShowAverage] = useState(false);

    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });

    const getYAxis = () => {
        const variableInfo = units[variable] || units.default;
        return `${variableInfo.label} (${variableInfo.unit})`;
    };

    const formatValueTo2SF = (value) => {
        const unit = units[variable]?.unit || units.default.unit;
        return `${Number(value).toFixed(2)} ${unit}`;
    };

    useEffect(() => {
        if (climatePrediction.length > 0) {
            const predictionData = climatePrediction[0];
            const years = [1980, 1990, 2000, 2020, 2030, 2040, 2050, 2060, 2070];

            const formattedData = years.map((year) => ({
                x: year === 1980 ? "1980 baseline" : String(year),
                y: predictionData[`${variable}_${year}`],
            }));

            setData(formattedData);
        }
    }, [climatePrediction, rcp, season, variable]);

    useEffect(() => setExpanded(false), [regions]);

    const handleOnClick = () => {
        setExpanded(!isExpanded);
    };

    if (regions.length === 0) {
        return null;
    }

    return (
        <div>
            <div className="collapsible">
                <div className="header" style={{ margin: "1em" }} {...getToggleProps({ onClick: handleOnClick })}>
                    {isExpanded ? "Hide" : "Explore"} climate details
                </div>
                <div {...getCollapseProps()}>
                    <div className="content">
                        <h1>Climate details</h1>
                        <p>
                            The graph below shows the future climate change expected in&nbsp;
                            <span className={"projected-regions"}>{andify(regions.map((e) => e.name))}</span>
                            &nbsp;under&nbsp;
                            <select
                                value={rcp}
                                onChange={(e) => {
                                    setRcp(e.target.value);
                                }}
                            >
                                <option value="rcp60">existing global policies</option>
                                <option value="rcp85">worst case scenario</option>
                            </select>
                            &nbsp;
                            {rcp == "rcp60" && (
                                <span>(equivalent to global warming level of 2.0-3.7C which is RCP 6.0)</span>
                            )}
                            {rcp == "rcp85" && (
                                <span>(equivalent to global warming level of 3.2-5.4C which is RCP 8.5)</span>
                            )}
                            ,&nbsp;and shows the&nbsp;
                            <select
                                value={season}
                                onChange={(e) => {
                                    setSeason(e.target.value);
                                }}
                            >
                                <option value="annual">yearly</option>
                                <option value="summer">summer</option>
                                <option value="winter">winter</option>
                            </select>
                            &nbsp;averages for&nbsp;
                            <select
                                onChange={(e) => {
                                    setVariable(e.target.value);
                                }}
                            >
                                <option value="tas">temperature</option>
                                <option value="pr">rain</option>
                                <option value="sfcWind">wind</option>
                                <option value="rsds">cloudiness</option>
                            </select>
                            &nbsp;for&nbsp;
                            <select
                                onChange={(e) => {
                                    setShowAverage(e.target.value === "1");
                                }}
                            >
                                <option value="0">your selected areas only</option>
                                <option value="1">your areas vs the UK</option>
                            </select>
                        </p>
                        {/* {showAverage && (
                            <p>
                                Key: <span className="key-regional">Your area</span>{" "}
                                <span className="key-average">UK average</span>
                            </p>
                        )} */}

                        <div className="graph-horiz-container">
                            <ResponsiveContainer width="85%" height={600}>
                                <LineChart
                                    data={data}
                                    margin={{
                                        top: 10,
                                        right: 10,
                                        left: 10,
                                        bottom: 50,
                                    }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="x">
                                        <Label value="Decades" offset={-40} position="insideBottom" />
                                    </XAxis>
                                    <YAxis>
                                        <Label
                                            value={getYAxis()}
                                            angle={-90}
                                            position="insideLeft"
                                            style={{ textAnchor: "middle" }}
                                        />
                                    </YAxis>
                                    <Tooltip formatter={formatValueTo2SF} />
                                    {/* <Legend /> */}
                                    <Line
                                        type="monotone"
                                        dataKey="y"
                                        stroke={selectedRegionCol}
                                        dot
                                        activeDot={{ r: 8 }}
                                    >
                                        {/* Adding a custom label for each point */}
                                        {/* <Label position="top" formatter={(v) => formatValueTo2SF(v)} /> */}
                                    </Line>
                                    {/* {showAverage && (
                                        <Line
                                            type="monotone"
                                            data={avg}
                                            dataKey="y"
                                            stroke={averageRegionCol}
                                            dot
                                            activeDot={{ r: 8 }}
                                        />
                                    )} */}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>
            <p className="note">
                Data source: The current iteration of the tool uses climate data from the{" "}
                <a
                    href="https://catalogue.ceda.ac.uk/uuid/8194b416cbee482b89e0dfbe17c5786c"
                    target="_blank"
                    rel="noreferrer"
                >
                    CHESS-SCAPE
                </a>{" "}
                dataset. CHESS-SCAPE provides bias-corrected data for England, Scotland, Wales, and the Isle of Man.
                CHESS-SCAPE provides non bias-corrected data for Northern Ireland and the Isles of Scilly. The tool
                displays RCP 6.0 and RCP 8.5. For more information, please see the{" "}
                <a
                    href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE_FINAL-Autumn-24.pdf"
                    target="_blank"
                    rel="noreferrer"
                >
                    LCAT User Guide.
                </a>
            </p>
        </div>
    );
};

export default Graph;
