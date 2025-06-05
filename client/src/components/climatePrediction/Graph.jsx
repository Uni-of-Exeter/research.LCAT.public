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

const winterCol = "#a4f9c8";
const summerCol = "#4c9f70";
const selectedRegionCol = "#216331";
const averageRegionCol = "#48b961";

const Graph = (props) => {
    const { regions, season, rcp, setSeason, setRcp, loading, climatePrediction, climateAverages, variable, setVariable } =
        props;

    const [data, setData] = useState([]);
    const [avg, setAvg] = useState([]);
    const [labelData, setLabelData] = useState([]);
    const [avgLabel, setAvgLabel] = useState([]);
    const [showAverage, setShowAverage] = useState(false);
    const [isExpanded, setExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });
    const graphContainerRef = useRef(null);
    const [containerWidth, setContainerWidth] = useState(undefined);

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

    const getLabel = (v) => {
        /*if (variable=="tas") return v.toFixed(2)+'°C';
        if (variable=="pr") return v.toFixed(2)+' mm/day';
        if (variable=="sfcWind") return v.toFixed(2)+' m/s';
        return v.toFixed(2)+' W/m²';*/
        return v.toFixed(2);
    };

    useEffect(() => {
        if (climatePrediction.length === 0 || climatePrediction[0][`${variable}_1980_mean`] == null) return;

        const years = [1980, 2030, 2040, 2050, 2060, 2070];
        const offset = showAverage ? 2 : 0;

        const out = years.map((year) => {
            const labelYear = year === 1980 ? "1980 baseline" : `${year}`;
            const meanValue = climatePrediction[0][`${variable}_${year}_mean`];

            return { x: labelYear, y: meanValue };
        });

        const label = out.map(({ x, y }) => ({
            x,
            y,
            labelText: getLabel(y),
        }));

        const av = years.map((year) => ({ x: year === 1980 ? "1980 baseline" : `${year}`, y: climateAverages[year] }));
        const avlabel = av.map(({ x, y }) => ({
            x,
            y,
            labelText: getLabel(y),
        }));

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

      // Extract arrays for Plotly
  const xValues = data.map((d) => d.x);
  const yValues = data.map((d) => d.y);
  const avgY = avg.map((d) => d.y);

  // Build traces
  const traces = [
    {
      x: xValues,
      y: yValues,
      type: "scatter",
      mode: "lines+markers",
      name: "Your area",
      marker: { color: selectedRegionCol },
      line: { color: selectedRegionCol, width: 3 },
      text: labelData.map((d) => d.labelText),
      textposition: "top center",
    },
  ];

  if (showAverage) {
    traces.push({
      x: xValues,
      y: avgY,
      type: "scatter",
      mode: "lines+markers",
      name: "UK average",
      marker: { color: averageRegionCol },
      line: { color: averageRegionCol, width: 3, dash: "dash" },
      text: avgLabel.map((d) => d.labelText),
      textposition: "top center",
    });
  }

  // Layout with dynamic margins & axis labels
  const layout = {
    // Remove barmode for line chart
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
    },
    font: { size: 18 },
    height: 400, // fixed height for consistent appearance
    width: containerWidth, // let Plotly fill the container width
    paper_bgcolor: "rgba(0,0,0,0)", // transparent background
    plot_bgcolor: "rgba(0,0,0,0)",  // transparent plot area
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
