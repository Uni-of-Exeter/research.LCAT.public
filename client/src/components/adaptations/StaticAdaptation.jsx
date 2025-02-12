/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./StaticAdaptation.css";

import { useEffect, useState } from "react";
import { useCollapse } from "react-collapsed";

import StaticReferences from "./StaticReferences";

const StaticAdaptation = ({ adaptation, selectedHazardName }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });

    // Collapse all sections when hazard changes
    useEffect(() => {
        setIsExpanded(false);
    }, [selectedHazardName]);

    // Ensure adaptation exists and has attributes
    const attributes = adaptation?.attributes || {};
    const aggregatedLayers = attributes.aggregated_layers || [];

    return (
        <div className="adaptation collapsible">
            <div className="adaptation header" {...getToggleProps({ onClick: () => setIsExpanded((prev) => !prev) })}>
                {attributes.label}
                <div className={isExpanded ? "arrow down" : "arrow right"} />
            </div>
            <div {...getCollapseProps()}>
                <div className="content">
                    <b className="static-adaptation-emphasis">Description:</b>
                    <p>{attributes.description || "No description available"}</p>
                    <b className="static-adaptation-emphasis">Related impact pathways:</b>
                    <p>This adaptation is also relevant to the following climate impact pathways:</p>
                    <ul>
                        {aggregatedLayers
                            .filter((item) => item !== selectedHazardName)
                            .map((item, index) => (
                                <li key={index}>{item}</li>
                            ))}
                    </ul>

                    <StaticReferences referenceIds={attributes.reference_id} />
                </div>
            </div>
        </div>
    );
};

export default StaticAdaptation;
