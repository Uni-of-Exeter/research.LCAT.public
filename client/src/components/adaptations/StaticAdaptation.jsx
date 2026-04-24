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

import adaptationRefs from "../../kumu/parsed/processed_references.json";
import StaticReferences from "./StaticReferences";

const StaticAdaptation = ({ adaptation, selectedHazards }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });

    // Collapse all sections when hazard changes
    useEffect(() => {
        setIsExpanded(false);
    }, [selectedHazards]);

    // Ensure adaptation exists and has attributes
    const attributes = adaptation?.attributes || {};
    const aggregatedLayers = attributes.aggregated_layers || [];
    const referenceIds = attributes.reference_id || [];

    // Filter case studies from references
    const caseStudyRefs = referenceIds
        .map((id) => adaptationRefs[id.toString()])
        .filter((ref) => ref && ref.notes === "Case study");

    const relatedHazards = aggregatedLayers.filter((item) => !selectedHazards.includes(item));

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
                    {relatedHazards.length > 0 && (
                        <p className="pathways-inline">
                            <strong>Related impact pathways:</strong> {relatedHazards.join(", ")}
                        </p>
                    )}
                    {caseStudyRefs.length > 0 && (
                        <>
                            <b className="static-adaptation-emphasis">Case Studies:</b>
                            <ul>
                                {caseStudyRefs.map((ref) => (
                                    <li key={ref.article_id}>
                                        <a href={ref.link} target="_blank" rel="noopener noreferrer">
                                            {ref.title || ref.link}
                                        </a>
                                        {ref.authors && ` - ${ref.authors}`}
                                    </li>
                                ))}
                            </ul>
                        </>
                    )}
                    <StaticReferences referenceIds={attributes.reference_id} />
                </div>
            </div>
        </div>
    );
};

export default StaticAdaptation;
