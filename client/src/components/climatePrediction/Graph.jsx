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

import "./Graph.css";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import { useCollapse } from "react-collapsed";
import LoadingOverlay from "react-loading-overlay-ts";
import PlotModule from "react-plotly.js";

import { climateVariables, getClimateVariableByKey, getGraphDecadesForVariable } from "../../utils/climateUtils";
import { CHESS_SCAPE_URL, LCAT_HANDBOOK_URL } from "../../utils/constants";
import { andify, rcpText, seasonText } from "../../utils/utils";

const Plot = PlotModule.default || PlotModule;

// Define graph colours
const selectedRegionsLine = "rgba(33,99,49,1)";
const selectedRegionsShade = "rgba(33,99,49,0.15)";
const averageUKLine = getComputedStyle(document.documentElement).getPropertyValue("--color-button-hover").trim();

const Graph = (props) => {
    const {
        regions,
        season,
        rcp,
        setSeason,
        setRcp,
        loading,
        climatePrediction,
        climateAverages,
        variable,
        setVariable,
    } = props;

    const [showAverage, setShowAverage] = useState(false);
    const [showDataTable, setShowDataTable] = useState(false);
    const [isExpanded, setExpanded] = useState(false);
    const effectiveExpanded = isExpanded && regions.length > 0;
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded: effectiveExpanded });
    const graphContainerRef = useRef(null);
    const chartSummaryId = useId();
    const [isMobile, setIsMobile] = useState(false);
    const [containerWidth, setContainerWidth] = useState(undefined);
    const hasTrackedCollapsibleOpen = useRef(false);

    useEffect(() => {
        // Responsive layout for mobile devices
        const checkMobile = () => setIsMobile(window.innerWidth < 600);
        checkMobile();
        window.addEventListener("resize", checkMobile);
        return () => window.removeEventListener("resize", checkMobile);
    }, []);

    useEffect(() => {
        if (!graphContainerRef.current) return;
        const observer = new window.ResizeObserver((entries) => {
            for (let entry of entries) {
                if (entry.contentRect) {
                    setContainerWidth(entry.contentRect.width);
                }
            }
        });
        observer.observe(graphContainerRef.current);
        // Set initial width
        setContainerWidth(graphContainerRef.current.offsetWidth);
        return () => observer.disconnect();
    }, []);

    const getYAxis = () => {
        const metric = getClimateVariableByKey(variable);
        if (!metric) return "Climate metric";

        if (metric.units === "days") {
            return season === "annual" ? `${metric.name} (days/year)` : `${metric.name} (days/season)`;
        }

        return `${metric.name} (${metric.units})`;
    };

    const data = useMemo(() => {
        if (climatePrediction.length === 0 || climatePrediction[0]?.[`${variable}_1980`] == null) return [];
        const years = getGraphDecadesForVariable(variable);
        return years.map((year) => ({
            x: year === 1980 ? "1980 baseline" : `${year}`,
            y: climatePrediction[0]?.[`${variable}_${year}`] ?? null,
            min: climatePrediction[0]?.[`tasmin_1_percentile_${year}`] ?? null,
            max: climatePrediction[0]?.[`tasmax_99_percentile_${year}`] ?? null,
        }));
    }, [climatePrediction, variable]);

    const avg = useMemo(() => {
        if (climatePrediction.length === 0 || climatePrediction[0]?.[`${variable}_1980`] == null) return [];
        const years = getGraphDecadesForVariable(variable);
        return years.map((year) => ({
            x: year === 1980 ? "1980 baseline" : `${year}`,
            y: climateAverages[year] ?? null,
        }));
    }, [climatePrediction, variable, climateAverages]);

    useEffect(() => {
        if (regions.length === 0) {
            hasTrackedCollapsibleOpen.current = false;
        }
    }, [regions]);

    const handleOnClick = () => {
        // Track first-time opening of collapsible
        if (!isExpanded && !hasTrackedCollapsibleOpen.current && typeof gtag !== "undefined") {
            gtag("event", "collapsible_open", {
                section: "climate_details",
            });
            hasTrackedCollapsibleOpen.current = true;
        }
        setExpanded(!isExpanded);
    };

    if (regions.length === 0) {
        return null;
    }

    // Extract arrays for Plotly
    const xValues = data.map((d) => d.x);
    const yValues = data.map((d) => d.y);
    const minY = data.map((d) => d.min);
    const maxY = data.map((d) => d.max);
    const avgY = avg.map((d) => d.y);
    const showGapIndicator = xValues.length >= 2;
    const gapCenter = showGapIndicator ? 0.5 / (xValues.length - 1) : 0.1;
    const gapHalfWidth = 0.015;

    const formatHover = (y) => (y == null ? "" : Number(y).toFixed(2));
    const formatTableValue = (y) => (y == null ? "-" : Number(y).toFixed(2));
    const hoverTemplate = "%{customdata}<extra></extra>";

    const tableRows = data.map((point, index) => ({
        decade: point.x,
        yourAreas: yValues[index],
        yourAreasMin: minY[index],
        yourAreasMax: maxY[index],
        ukAverage: avgY[index],
    }));

    const traces = [
        // Mean line
        {
            x: xValues,
            y: yValues,
            type: "scatter",
            mode: "lines+markers",
            name: "Your areas",
            marker: { color: selectedRegionsLine },
            line: { color: selectedRegionsLine, width: 3 },
            legendgroup: "your-areas-mean",
            textposition: "top center",
            showlegend: true,
            customdata: yValues.map(formatHover),
            hovertemplate: hoverTemplate,
        },
    ];

    if (variable === "tas") {
        traces.push(
            // Max line
            {
                x: xValues,
                y: maxY,
                type: "scatter",
                mode: "lines+markers",
                name: "Your areas (max)",
                marker: { color: selectedRegionsLine, symbol: "circle-open" },
                line: { color: selectedRegionsLine, width: 2, dash: "dot" },
                opacity: 0.5,
                hoverinfo: "y",
                legendgroup: "your-areas-max",
                showlegend: true,
                customdata: maxY.map(formatHover),
                hovertemplate: hoverTemplate,
            },
            // Shading between mean and max (linked to max line)
            {
                x: [...xValues, ...xValues.slice().reverse()],
                y: [...yValues, ...maxY.slice().reverse()],
                fill: "toself",
                fillcolor: selectedRegionsShade,
                line: { color: "rgba(0,0,0,0)" },
                hoverinfo: "skip",
                name: "Your areas (mean-max range)",
                showlegend: false,
                legendgroup: "your-areas-max",
                visible: true,
            },
            // Shading between min and mean (linked to min line)
            {
                x: [...xValues, ...xValues.slice().reverse()],
                y: [...minY, ...yValues.slice().reverse()],
                fill: "toself",
                fillcolor: selectedRegionsShade,
                line: { color: "rgba(0,0,0,0)" },
                hoverinfo: "skip",
                name: "Your areas (min-mean range)",
                showlegend: false,
                legendgroup: "your-areas-min",
                visible: true,
            },
            // Min line
            {
                x: xValues,
                y: minY,
                type: "scatter",
                mode: "lines+markers",
                name: "Your areas (min)",
                marker: { color: selectedRegionsLine, symbol: "circle-open" },
                line: { color: selectedRegionsLine, width: 2, dash: "dot" },
                opacity: 0.5,
                hoverinfo: "y",
                legendgroup: "your-areas-min",
                showlegend: true,
                customdata: minY.map(formatHover),
                hovertemplate: hoverTemplate,
            },
        );
    }

    if (showAverage) {
        // UK mean line
        traces.push({
            x: xValues,
            y: avgY,
            type: "scatter",
            mode: "lines+markers",
            name: "UK average",
            marker: { color: averageUKLine },
            line: { color: averageUKLine, width: 3, dash: "dash" },
            legendgroup: "uk-average-mean",
            textposition: "top center",
            showlegend: true,
            customdata: avgY.map(formatHover),
            hovertemplate: hoverTemplate,
        });
    }

    // 'Temporary' hardcoded y-axis ranges
    const yAxisRanges = {
        pr: [0, 15],
        tas: [-10, 40],
        sfcWind: [0, 10],
        rsds: [0, 300],
        tropical_nights: [0, 50],
        hot_heat_days: [0, 35],
        heavy_rain_days: [0, 10],
        dry_days: [0, 290],
        windy_days: [0, 195],
    };

    const layout = {
        legend: isMobile ? { orientation: "h", x: 0, y: -0.3 } : { orientation: "v", x: 1.02, y: 1 },
        margin: isMobile ? { l: 0, r: 10, b: 60, t: 10 } : { l: 60, r: 20, b: 60, t: 10 },
        xaxis: {
            title: { text: "Decades" },
            type: "category",
        },
        yaxis: {
            title: { text: getYAxis(), standoff: isMobile ? 10 : 40 },
            automargin: true,
            range: yAxisRanges[variable],
        },
        font: isMobile ? { size: 12 } : { size: 18 },
        height: 400, // fixed height for consistent appearance
        width: containerWidth, // let Plotly fill the container width
        paper_bgcolor: "rgba(0,0,0,0)", // transparent background
        plot_bgcolor: "rgba(0,0,0,0)", // transparent plot area
        // Vertical grey bar to indicate the gap between baseline and first projection point.
        shapes: showGapIndicator
            ? [
                  {
                      type: "rect",
                      xref: "paper",
                      yref: "paper",
                      x0: Math.max(0, gapCenter - gapHalfWidth),
                      x1: Math.min(1, gapCenter + gapHalfWidth),
                      y0: 0,
                      y1: 1,
                      fillcolor: "rgb(165, 162, 162)",
                      line: { width: 0 },
                      layer: "above",
                  },
              ]
            : [],
    };

    const chartSummary = `Line chart showing projected ${variable} for ${andify(regions.map((region) => region.name))}, ` +
        `${season} averages, ${rcp === "rcp60" ? "RCP 6.0" : "RCP 8.5"} scenario. ` +
        `Full data available in the table below the chart.`;

    return (
        <div>
            <div className="collapsible">
                <div
                    className="header graph-collapsible-header"
                    role="button"
                    tabIndex={0}
                    {...getToggleProps({})}
                    onClick={handleOnClick}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") handleOnClick();
                    }}
                >
                    {isExpanded ? "Hide" : "Explore"} climate details
                </div>
                <div {...getCollapseProps()}>
                    <LoadingOverlay active={loading} spinner text="Loading climate data">
                        <div className="content">
                            <h1>Climate details</h1>
                            <p className="graph-description">
                                The graph below shows the future climate change expected in&nbsp;
                                <span className={"projected-regions"}>{andify(regions.map((e) => e.name))}</span>
                                &nbsp;under&nbsp;
                                <select
                                    aria-label="Climate scenario"
                                    value={rcp}
                                    onChange={(e) => {
                                        setRcp(e.target.value);
                                    }}
                                >
                                    <option value="rcp60">{rcpText.rcp60}</option>
                                    <option value="rcp85">{rcpText.rcp85}</option>
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
                                    aria-label="Season"
                                    value={season}
                                    onChange={(e) => {
                                        setSeason(e.target.value);
                                    }}
                                >
                                    <option value="annual">{seasonText.annual}</option>
                                    <option value="summer">{seasonText.summer}</option>
                                    <option value="winter">{seasonText.winter}</option>
                                </select>
                                &nbsp;averages for&nbsp;
                                <select
                                    aria-label="Climate variable"
                                    value={variable}
                                    onChange={(e) => {
                                        setVariable(e.target.value);
                                    }}
                                >
                                    {climateVariables.map((item) => (
                                        <option key={item.variable} value={item.variable}>
                                            {item.graphLabel}
                                        </option>
                                    ))}
                                </select>
                                &nbsp;for&nbsp;
                                <select
                                    aria-label="Displayed area"
                                    onChange={(e) => {
                                        setShowAverage(e.target.value === "1");
                                    }}
                                >
                                    <option value="0">your selected areas only</option>
                                    <option value="1">your areas vs the UK</option>
                                </select>
                            </p>
                            <div ref={graphContainerRef} className="graph-plot-container">
                                <div className="graph-table-toggle-container">
                                    <button
                                        className="graph-table-toggle"
                                        type="button"
                                        aria-expanded={showDataTable}
                                        aria-controls="climate-details-data-table"
                                        onClick={() => setShowDataTable(!showDataTable)}
                                    >
                                        {showDataTable ? "Hide" : "Show"} data table
                                    </button>
                                </div>
                                <figure className="graph-chart-figure" aria-describedby={chartSummaryId}>
                                    <Plot
                                        data={traces}
                                        layout={{ ...layout, width: undefined, height: 400, autosize: true }}
                                        config={{ displayModeBar: false, responsive: true }}
                                        className="graph-plot"
                                    />
                                    <figcaption id={chartSummaryId} className="graph-visually-hidden">
                                        {chartSummary}
                                    </figcaption>
                                </figure>
                            </div>
                            {showDataTable && (
                                <div id="climate-details-data-table" className="graph-data-table-container">
                                    <table className="graph-data-table">
                                        <caption>
                                            Data table alternative for the climate graph
                                        </caption>
                                        <thead>
                                            <tr>
                                                <th scope="col">
                                                    Decade
                                                </th>
                                                <th scope="col">
                                                    Your areas
                                                </th>
                                                {variable === "tas" && (
                                                    <>
                                                        <th scope="col">
                                                            Your areas (min)
                                                        </th>
                                                        <th scope="col">
                                                            Your areas (max)
                                                        </th>
                                                    </>
                                                )}
                                                {showAverage && <th scope="col">UK average</th>}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {tableRows.map((row) => (
                                                <tr key={row.decade}>
                                                    <th scope="row">{row.decade}</th>
                                                    <td>{formatTableValue(row.yourAreas)}</td>
                                                    {variable === "tas" && (
                                                        <>
                                                            <td>{formatTableValue(row.yourAreasMin)}</td>
                                                            <td>{formatTableValue(row.yourAreasMax)}</td>
                                                        </>
                                                    )}
                                                    {showAverage && <td>{formatTableValue(row.ukAverage)}</td>}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    </LoadingOverlay>
                    <p className="note graph-note-bottom">
                        {variable === "tas" && (
                            <span className="graph-temperature-note">
                                The min and max numbers here do not account for extreme temperatures, which will still
                                occur, but instead show the range of what normal and expected temperatures will be.
                            </span>
                        )}
                        You can hover over points to see their values. Use the legend to show or hide lines, or
                        double-click to focus on a single line. Adjust the axes by dragging, or zoom in by drawing a box
                        around an area of interest. Double-click the graph to reset the view.
                        <br />
                        Note: The vertical grey bar indicates the gap between the 1980 baseline and the first future
                        projection point.
                    </p>
                    <div className="graph-collapsible-spacer" />
                </div>
            </div>
            <p className="note graph-note-top">
                Data source: The current iteration of the tool uses climate data from the{" "}
                <a href={CHESS_SCAPE_URL} target="_blank" rel="noreferrer">
                    CHESS-SCAPE
                </a>{" "}
                dataset. CHESS-SCAPE provides bias-corrected data for England, Scotland, Wales, and the Isle of Man.
                CHESS-SCAPE provides non bias-corrected data for Northern Ireland and the Isles of Scilly. The tool
                displays RCP 6.0 and RCP 8.5. For more information, please see the{" "}
                <a href={LCAT_HANDBOOK_URL} target="_blank" rel="noreferrer">
                    LCAT Handbook.
                </a>
            </p>
        </div>
    );
};

export default Graph;
