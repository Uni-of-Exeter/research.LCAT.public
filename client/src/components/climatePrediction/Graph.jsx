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

import { useEffect, useRef, useState } from "react";
import { useCollapse } from "react-collapsed";
import LoadingOverlay from "react-loading-overlay-ts";
import Plot from "react-plotly.js";

import { CHESS_SCAPE_URL, LCAT_HANDBOOK_URL } from "../../utils/constants";
import {
    getClimateVariableByKey,
    getGraphDecadesForVariable,
    graphSelectableClimateVariables,
} from "../../utils/climateUtils";
import { andify } from "../../utils/utils";

// Define graph colours
const selectedRegionsLine = "rgba(33,99,49,1)";
const selectedRegionsShade = "rgba(33,99,49,0.15)";
const averageUKLine = getComputedStyle(document.documentElement).getPropertyValue('--color-button-hover').trim();
const averageUKShade = "rgba(245,130,31,0.15)"; // averageUKLine with 15% opacity

const Graph = (props) => {
    const { regions, season, rcp, setSeason, setRcp, loading, climatePrediction, climateAverages, climateAverageRanges, variable, setVariable } =
        props;

    const [data, setData] = useState([]);
    const [avg, setAvg] = useState([]);
    const [showAverage, setShowAverage] = useState(false);
    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });
    const graphContainerRef = useRef(null);
    const [isMobile, setIsMobile] = useState(false);
    const [containerWidth, setContainerWidth] = useState(undefined);
    const hasTrackedCollapsibleOpen = useRef(false);
    // const [avgMin, setAvgMin] = useState([]);
    // const [avgMax, setAvgMax] = useState([]);

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

    useEffect(() => {
        if (climatePrediction.length === 0 || climatePrediction[0]?.[`${variable}_1980`] == null) return;
        const years = getGraphDecadesForVariable(variable);

        const data = years.map((year) => ({
            x: year === 1980 ? "1980 baseline" : `${year}`,
            y: climatePrediction[0]?.[`${variable}_${year}`] ?? null,
            min: climatePrediction[0]?.[`tasmin_1_percentile_${year}`] ?? null,
            max: climatePrediction[0]?.[`tasmax_99_percentile_${year}`] ?? null,
        }));

        const av = years.map((year) => ({ x: year === 1980 ? "1980 baseline" : `${year}`, y: climateAverages[year] ?? null }));
        // const avMin = years.map((year) => climateAverages[year]?.min ?? null);
        // const avMax = years.map((year) => climateAverages[year]?.max ?? null);

        setAvg(av);
        setData(data);
        // setAvgMin(avMin);
        // setAvgMax(avMax);
    }, [climatePrediction, rcp, season, showAverage, variable, climateAverages, climateAverageRanges]);

    useEffect(() => {
        if (regions.length === 0) {
            setExpanded(false);
            setAvg([]);
            setData([]);
            // Reset tracking flag when no regions selected  
            hasTrackedCollapsibleOpen.current = false;
        }
    }, [regions]);

    const handleOnClick = () => {
        // Track first-time opening of collapsible
        if (!isExpanded && !hasTrackedCollapsibleOpen.current && typeof gtag !== 'undefined') {
            gtag('event', 'collapsible_open', {
                section: 'climate_details'
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

  const formatHover = (y) => (y == null ? '' : Number(y).toFixed(2));
  const hoverTemplate = '%{customdata}<extra></extra>';

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
    )
  }

  if (showAverage) {
    // UK max line
    // traces.push({
    //   x: xValues,
    //   y: avgMax,
    //   type: "scatter",
    //   mode: "lines+markers",
    //   name: "UK average (max)",
    //   marker: { color: averageUKLine, symbol: "circle-open" },
    //   line: { color: averageUKLine, width: 2, dash: "dot" },
    //   opacity: 0.5,
    //   hoverinfo: "y",
    //   legendgroup: "uk-average-max",
    //   showlegend: true,
    //   visible: "legendonly",
    //   customdata: avgMax.map(formatHover),
    //   hovertemplate: hoverTemplate,
    // });
    // // Shading between UK mean and max (linked to max line)
    // traces.push({
    //   x: [...xValues, ...xValues.slice().reverse()],
    //   y: [...avgY, ...avgMax.slice().reverse()],
    //   fill: "toself",
    //   fillcolor: averageUKShade,
    //   line: { color: "rgba(0,0,0,0)" },
    //   hoverinfo: "skip",
    //   name: "UK average (mean-max range)",
    //   showlegend: false,
    //   legendgroup: "uk-average-max",
    //   visible: "legendonly",
    // });
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
    // Shading between UK min and mean (linked to min line)
    // traces.push({
    //   x: [...xValues, ...xValues.slice().reverse()],
    //   y: [...avgMin, ...avgY.slice().reverse()],
    //   fill: "toself",
    //   fillcolor: averageUKShade,
    //   line: { color: "rgba(0,0,0,0)" },
    //   hoverinfo: "skip",
    //   name: "UK average (min-mean range)",
    //   showlegend: false,
    //   legendgroup: "uk-average-min",
    //   visible: "legendonly",
    // });
    // // UK min line
    // traces.push({
    //   x: xValues,
    //   y: avgMin,
    //   type: "scatter",
    //   mode: "lines+markers",
    //   name: "UK average (min)",
    //   marker: { color: averageUKLine, symbol: "circle-open" },
    //   line: { color: averageUKLine, width: 2, dash: "dot" },
    //   opacity: 0.5,
    //   hoverinfo: "y",
    //   legendgroup: "uk-average-min",
    //   showlegend: true,
    //   visible: "legendonly",
    //   customdata: avgMin.map(formatHover),
    //   hovertemplate: hoverTemplate,
    // });
  }

    // Temporary hardcoded y-axis ranges
    const yAxisRanges = {
        pr: [0, 10],
        tas: [-10, 40],
        sfcWind: [0, 10],
        rsds: [0, 300],
        tropical_nights: [0, 60],
        hot_heat_days: [0, 40],
        heavy_rain_days: [0, 50],
        dry_days: [0, 280],
        windy_days: [0, 360],
    };

  // Pad by 5% either side
//   const variableRange = climateAverageRanges && climateAverageRanges[variable];
//     const paddedRange = variableRange
//         ? [
//             variableRange[0] - 0.05 * (variableRange[1] - variableRange[0]),
//             variableRange[1] + 0.05 * (variableRange[1] - variableRange[0])
//         ]
//         : undefined;

  const layout = {
    legend: isMobile
        ? { orientation: "h", x: 0, y: -0.3 }
        : { orientation: "v", x: 1.02, y: 1 },
    margin: isMobile 
        ? { l: 0, r: 10, b: 60, t: 10 }
        : { l: 60, r: 20, b: 60, t: 10 },
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
    plot_bgcolor: "rgba(0,0,0,0)",  // transparent plot area
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
                layer: "above"
            }
        ]
        : []
  };

    return (
        <div>
            <div className="collapsible">
                <div className="header" style={{ margin: "1em" }} {...getToggleProps({ onClick: handleOnClick })}>
                    {isExpanded ? "Hide" : "Explore"} climate details
                </div>
                <div {...getCollapseProps()}>
                    <LoadingOverlay active={loading} spinner text="Loading climate data">
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
                                    value={variable}
                                    onChange={(e) => {
                                        setVariable(e.target.value);
                                    }}
                                >
                                    {graphSelectableClimateVariables.map((item) => (
                                        <option key={item.variable} value={item.variable}>
                                            {item.graphLabel}
                                        </option>
                                    ))}
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
                            <div ref={graphContainerRef} style={{position: "relative", width: "100%", minHeight: "400px", overflow: "visible"}}>
                                <Plot
                                    data={traces}
                                    layout={{ ...layout, width: undefined, height: 400, autosize: true }}
                                    config={{ displayModeBar: false, responsive: true }}
                                    style={{ width: "100%", height: "100%", minWidth: 0 }}
                                />
                            </div>
                        </div>
                    </LoadingOverlay>
                    <p className="note">
                        You can hover over points to see their values. Use the legend to show or hide lines, or double-click to focus on a single line.  
                        Adjust the axes by dragging, or zoom in by drawing a box around an area of interest.  
                        Double-click the graph to reset the view.
                        <br />
                        Note: The vertical grey bar indicates the gap between the 1980 baseline and the first future projection point.
                    </p>
                </div>
            </div>
            <p className="note">
                Data source: The current iteration of the tool uses climate data from the{" "}
                <a
                    href={CHESS_SCAPE_URL}
                    target="_blank"
                    rel="noreferrer"
                >
                    CHESS-SCAPE
                </a>{" "}
                dataset. CHESS-SCAPE provides bias-corrected data for England, Scotland, Wales, and the Isle of Man.
                CHESS-SCAPE provides non bias-corrected data for Northern Ireland and the Isles of Scilly. The tool
                displays RCP 6.0 and RCP 8.5. For more information, please see the{" "}
                <a
                    href={LCAT_HANDBOOK_URL}
                    target="_blank"
                    rel="noreferrer"
                >
                    LCAT Handbook.
                </a>
            </p>
        </div>
    );
};

export default Graph;
