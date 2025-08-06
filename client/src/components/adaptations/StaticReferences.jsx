/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./StaticReferences.css";

import { useState } from "react";
import { useCollapse } from "react-collapsed";

import adaptationRefs from "../../kumu/parsed/processed_references.json";
import Reference from "./Reference";

// Component for a collapsible reference group
const ReferenceGroup = ({ type, references }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });

    return (
        <div className="reference-group">
            <div 
                className="reference-group-header" 
                {...getToggleProps({ onClick: () => setIsExpanded((prev) => !prev) })}
            >
                <span className="reference-type-label">
                    {type} ({references.length})
                </span>
            </div>
            <div {...getCollapseProps()}>
                <div className="reference-group-content">
                    {references.map((ref) => (
                        <Reference
                            key={ref.article_id}
                            link={ref.link}
                            title={ref.title}
                            type={ref.type}
                            article_id={ref.article_id}
                            authors={ref.authors}
                            journal={ref.journal}
                            issue={ref.issue}
                            date={ref.date}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

// All references component
const StaticReferences = ({ referenceIds }) => {
    const filteredRefs = referenceIds.map((id) => adaptationRefs[id.toString()]).filter(Boolean);

    if (!filteredRefs.length) return null;

    // Group references by type
    const groupedRefs = filteredRefs.reduce((groups, ref) => {
        const type = ref.type || "Other";
        if (!groups[type]) {
            groups[type] = [];
        }
        groups[type].push(ref);
        return groups;
    }, {});

    // Sort reference types for consistent ordering
    const sortedTypes = Object.keys(groupedRefs).sort((a, b) => {
        const typeOrder = ['Journal Article', 'Book', 'Report', 'Web Page', 'Other'];
        const aIndex = typeOrder.indexOf(a);
        const bIndex = typeOrder.indexOf(b);
        
        if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
        if (aIndex !== -1) return -1;
        if (bIndex !== -1) return 1;
        return a.localeCompare(b);
    });

    return (
        <div className="static-references">
            <b className="reference-emphasis">References:</b>
            {sortedTypes.map((type) => (
                <ReferenceGroup
                    key={type}
                    type={type}
                    references={groupedRefs[type]}
                />
            ))}
        </div>
    );
};

export default StaticReferences;