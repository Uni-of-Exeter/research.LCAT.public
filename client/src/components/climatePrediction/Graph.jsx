/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import { useEffect, useRef, useState } from "react";
import { useCollapse } from "react-collapsed";
import LoadingOverlay from "react-loading-overlay-ts";
import Plot from "react-plotly.js";

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
    const [containerWidth, setContainerWidth] = useState(undefined);
    const [avgMin, setAvgMin] = useState([]);
    const [avgMax, setAvgMax] = useState([]);

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
        if (variable == "tas") return "Temperature (°C)";
        if (variable == "pr") return "Rainfall (mm/day)";
        if (variable == "sfcWind") return "Wind (m/s)";
        return "Cloudiness (W/m²)";
    };

    useEffect(() => {
        if (climatePrediction.length === 0 || !climatePrediction[0][`${variable}_1980_mean`]) return;
        console.log(climateAverageRanges)
        const years = [1980, 2030, 2040, 2050, 2060, 2070];

        const data = years.map((year) => ({
            x: year === 1980 ? "1980 baseline" : `${year}`,
            y: climatePrediction[0]?.[`${variable}_${year}_mean`] ?? null,
            min: climatePrediction[0]?.[`${variable}_${year}_min`] ?? null,
            max: climatePrediction[0]?.[`${variable}_${year}_max`] ?? null,
        }));

        const av = years.map((year) => ({ x: year === 1980 ? "1980 baseline" : `${year}`, y: climateAverages[year]?.mean ?? null }));
        const avMin = years.map((year) => climateAverages[year]?.min ?? null);
        const avMax = years.map((year) => climateAverages[year]?.max ?? null);

        setAvg(av);
        setData(data);
        setAvgMin(avMin);
        setAvgMax(avMax);
    }, [climatePrediction, rcp, season, showAverage, variable, climateAverages]);

    useEffect(() => {
        if (regions.length === 0) {
            setExpanded(false);
            setAvg([]);
            setData([]);
        }
    }, [regions]);

    const handleOnClick = () => {
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

  const formatHover = (y) => (y == null ? '' : Number(y).toFixed(2));
  const hoverTemplate = '%{customdata}<extra></extra>';

  const traces = [
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
    // Mean line
    {
      x: xValues,
      y: yValues,
      type: "scatter",
      mode: "lines+markers",
      name: "Your areas (mean)",
      marker: { color: selectedRegionsLine },
      line: { color: selectedRegionsLine, width: 3 },
      legendgroup: "your-areas-mean",
      textposition: "top center",
      showlegend: true,
      customdata: yValues.map(formatHover),
      hovertemplate: hoverTemplate,
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
  ];

  if (showAverage) {
    // UK max line
    traces.push({
      x: xValues,
      y: avgMax,
      type: "scatter",
      mode: "lines+markers",
      name: "UK average (max)",
      marker: { color: averageUKLine, symbol: "circle-open" },
      line: { color: averageUKLine, width: 2, dash: "dot" },
      opacity: 0.5,
      hoverinfo: "y",
      legendgroup: "uk-average-max",
      showlegend: true,
      visible: "legendonly",
      customdata: avgMax.map(formatHover),
      hovertemplate: hoverTemplate,
    });
    // Shading between UK mean and max (linked to max line)
    traces.push({
      x: [...xValues, ...xValues.slice().reverse()],
      y: [...avgY, ...avgMax.slice().reverse()],
      fill: "toself",
      fillcolor: averageUKShade,
      line: { color: "rgba(0,0,0,0)" },
      hoverinfo: "skip",
      name: "UK average (mean-max range)",
      showlegend: false,
      legendgroup: "uk-average-max",
      visible: "legendonly",
    });
    // UK mean line
    traces.push({
      x: xValues,
      y: avgY,
      type: "scatter",
      mode: "lines+markers",
      name: "UK average (mean)",
      marker: { color: averageUKLine },
      line: { color: averageUKLine, width: 3, dash: "dash" },
      legendgroup: "uk-average-mean",
      textposition: "top center",
      showlegend: true,
      customdata: avgY.map(formatHover),
      hovertemplate: hoverTemplate,
    });
    // Shading between UK min and mean (linked to min line)
    traces.push({
      x: [...xValues, ...xValues.slice().reverse()],
      y: [...avgMin, ...avgY.slice().reverse()],
      fill: "toself",
      fillcolor: averageUKShade,
      line: { color: "rgba(0,0,0,0)" },
      hoverinfo: "skip",
      name: "UK average (min-mean range)",
      showlegend: false,
      legendgroup: "uk-average-min",
      visible: "legendonly",
    });
    // UK min line
    traces.push({
      x: xValues,
      y: avgMin,
      type: "scatter",
      mode: "lines+markers",
      name: "UK average (min)",
      marker: { color: averageUKLine, symbol: "circle-open" },
      line: { color: averageUKLine, width: 2, dash: "dot" },
      opacity: 0.5,
      hoverinfo: "y",
      legendgroup: "uk-average-min",
      showlegend: true,
      visible: "legendonly",
      customdata: avgMin.map(formatHover),
      hovertemplate: hoverTemplate,
    });
  }


  // Pad by 5% either side
  const variableRange = climateAverageRanges[variable];
    const paddedRange = variableRange
        ? [
            variableRange[0] - 0.05 * (variableRange[1] - variableRange[0]),
            variableRange[1] + 0.05 * (variableRange[1] - variableRange[0])
        ]
        : undefined;

  // Layout with dynamic margins & axis labels
  const layout = {
    margin: { l: 60, r: 20, b: 60, t: 10 },
    xaxis: {
      title: { text: "Decades", font: { size: 18 } },
      type: "category",
      tickfont: { size: 18 },
    },
    yaxis: {
      title: { text: getYAxis(), font: { size: 18 } },
      automargin: true,
      tickfont: { size: 18 },
      range: paddedRange,
    },
    font: { size: 18 },
    height: 400, // fixed height for consistent appearance
    width: containerWidth, // let Plotly fill the container width
    paper_bgcolor: "rgba(0,0,0,0)", // transparent background
    plot_bgcolor: "rgba(0,0,0,0)",  // transparent plot area
    // Vertical grey bar to indicate x axis discontinuity
    shapes: [
        {
        type: "rect",
        xref: "x",
        yref: "paper",
        x0: 0.46,
        x1: 0.54,
        y0: 0,
        y1: 1,
        fillcolor: "rgba(120,120,120,0.3)",
        line: { width: 0 },
        layer: "above"
        }
    ]
  };

  const config = {
    responsive: true,
    displayModeBar: false,
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
                                &nbsp;minimum, maximum and average values for&nbsp;
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
                            <div className="graph-horiz-container" ref={graphContainerRef}>
                <Plot
                  data={traces}
                  layout={layout}
                  config={config}
                  style={{ width: "100%" }}
                />
                            </div>
                        </div>
                    </LoadingOverlay>
                </div>
            </div>
            <p className="note">
                You can hover over points to see their values. Use the legend to show or hide lines, or double-click to focus on a single line.  
                Adjust the axes by dragging, or zoom in by drawing a box around an area of interest.  
                Double-click the graph to reset the view.
                <br />
                Note: The vertical grey bar indicates a 50-year gap between the 1980 baseline and 2030 data points.
                <br /><br />
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
                    href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE-June-2025-update.pdf"
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
