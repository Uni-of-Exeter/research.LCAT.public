/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "../../../node_modules/react-vis/dist/style.css";
import "./Graph.css";

import React, { useEffect, useState } from "react";
import { useCollapse } from "react-collapsed";
import { ChartLabel, LabelSeries, makeWidthFlexible, VerticalBarSeries, XAxis, XYPlot, YAxis } from "react-vis";

import { climateAverages } from "../../core/climate";
import { andify } from "../../utils/utils";

const FlexibleXYPlot = makeWidthFlexible(XYPlot);
const winterCol = "#a4f9c8";
const summerCol = "#4c9f70";
const selectedRegionCol = "#216331";
const averageRegionCol = "#48b961";

const Graph = (props) => {
    const { regions, season, rcp, setSeason, setRcp, climatePrediction, climateAverages, variable, setVariable } =
        props;

    const [data, setData] = useState([]);
    const [avg, setAvg] = useState([]);
    const [labelData, setLabelData] = useState([]);
    const [avgLabel, setAvgLabel] = useState([]);
    const [showAverage, setShowAverage] = useState(false);
    const [margin, setMargin] = useState({
        bottom: undefined,
        left: undefined,
        height: 300,
    });

    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });

    useEffect(() => {
        function handleResize() {
            // ridiculous (fix, and that margins are defined in pixels)
            if (window.innerWidth < 700) {
                setMargin({
                    bottom: 30,
                    left: 50,
                    height: 300,
                });
            } else {
                if (window.innerWidth > 1300) {
                    setMargin({
                        bottom: 200,
                        left: 200,
                        height: 700,
                    });
                } else {
                    setMargin({
                        bottom: 100,
                        left: 100,
                        height: 450,
                    });
                }
            }
        }

        window.addEventListener("resize", handleResize);
        handleResize();
    }, []);

    const getYAxis = () => {
        if (variable == "tas") return "Temperature (°C)";
        if (variable == "pr") return "Rainfall (mm/day)";
        if (variable == "sfcWind") return "Wind (m/s)";
        return "Cloudiness (W/m²)";
    };

    const getLabel = (v) => {
        /*if (variable=="tas") return v.toFixed(2)+'°C';
        if (variable=="pr") return v.toFixed(2)+' mm/day';
        if (variable=="sfcWind") return v.toFixed(2)+' m/s';
        return v.toFixed(2)+' W/m²';*/
        return v.toFixed(2);
    };

    console.log(climatePrediction);

    useEffect(() => {
        if (climatePrediction.length === 0 || climatePrediction[0][`${variable}_1980_mean`] == null) return;

        const years = [1980, 2030, 2040, 2050, 2060, 2070];
        const offset = showAverage ? 2 : 0;

        const out = years.map((year) => {
            const labelYear = year === 1980 ? "1980 baseline" : `${year}`;
            const meanValue = climatePrediction[0][`${variable}_${year}_mean`];

            return { x: labelYear, y: meanValue };
        });

        const label = out.map(({ x, y }) => ({ x, y, xOffset: -offset }));

        const av = years.map((year) => ({ x: year === 1980 ? "1980 baseline" : `${year}`, y: climateAverages[year] }));
        const avlabel = av.map(({ x, y }) => ({ x, y, xOffset: offset }));

        setAvg(av);
        setAvgLabel(avlabel);
        setData(out);
        setLabelData(label);
    }, [climatePrediction, rcp, season, showAverage, variable, climateAverages]);

    useEffect(() => {
        if (regions.length === 0) {
            setExpanded(false);
            setAvg([]);
            setAvgLabel([]);
            setData([]);
            setLabelData([]);
        }
    }, [regions]);

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
                        {showAverage && (
                            <p>
                                Key: <span className="key-regional">Your area</span>{" "}
                                <span className="key-average">UK average</span>
                            </p>
                        )}

                        <div className="graph-horiz-container">
                            {/* <div className="graph-y-axis">{getYAxis()}</div> */}
                            <FlexibleXYPlot
                                height={margin.height}
                                margin={{ bottom: margin.bottom, left: margin.left, right: 0, top: 10 }}
                                xType="ordinal"
                            >
                                <ChartLabel
                                    text="Decades"
                                    className="graph-axes-label"
                                    includeMargin={false}
                                    xPercent={0.45}
                                    yPercent={1.3}
                                />
                                <ChartLabel
                                    text={getYAxis()}
                                    className="graph-axes-label"
                                    includeMargin={false}
                                    xPercent={-0.07}
                                    yPercent={0.25}
                                    style={{
                                        transform: "rotate(-90)",
                                        textAnchor: "end",
                                    }}
                                />
                                <XAxis />
                                <YAxis />
                                <VerticalBarSeries color={selectedRegionCol} data={data} />
                                <LabelSeries
                                    data={labelData}
                                    labelAnchorX={showAverage ? "end" : "middle"}
                                    getLabel={(d) => getLabel(d.y)}
                                />
                                {showAverage && <VerticalBarSeries color={averageRegionCol} data={avg} />}
                                {showAverage && (
                                    <LabelSeries
                                        data={avgLabel}
                                        labelAnchorX={"right"}
                                        getLabel={(d) => getLabel(d.y)}
                                    />
                                )}
                            </FlexibleXYPlot>
                        </div>
                        {/* <div className="graph-x-axis">Decades</div> */}
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
