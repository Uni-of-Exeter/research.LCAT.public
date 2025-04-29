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

import adaptationRefs from "../../kumu/parsed/processed_references.json";
import Reference from "./Reference";

// All references component
const StaticReferences = ({ referenceIds }) => {
    const filteredRefs = referenceIds.map((id) => adaptationRefs[id.toString()]).filter(Boolean);

    if (!filteredRefs.length) return null;

    return (
        <div>
            <b className="reference-emphasis">References:</b>
            {filteredRefs.map((ref) => (
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
    );
};

export default StaticReferences;
