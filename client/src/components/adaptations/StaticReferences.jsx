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

import React from "react";

import adaptationRefs from "../../kumu/parsed/processed_references.json";

// Function to format authors
const formatAuthors = (authorsString) => {
    if (!authorsString) return "";
    const authors = authorsString.split(",");
    return authors.length > 3 ? `${authors.slice(0, 2).join(", ")} et al.` : authors.join(", ");
};

// Function to extract domain from a URL
const baseURL = (url, id) => {
    try {
        return new URL(url).hostname;
    } catch {
        console.error(`${id} failed to produce a valid URL`);
        return "Invalid URL";
    }
};

// Reference Component
const Reference = ({ link, title, type, article_id, authors, journal, issue, date }) => (
    <div className="reference-container">
        <p>
            <a href={link} className="reference-title" target="_blank" rel="noreferrer">
                {title || `${link.substring(0, 40)}...`}
            </a>
        </p>
        <p>
            {type && (
                <>
                    <b>Type & ID: </b>
                    {type} - {article_id}
                    <br />
                </>
            )}
            {authors && (
                <>
                    <b>Authors: </b>
                    {formatAuthors(authors)}
                    <br />
                </>
            )}
            {journal && (
                <>
                    <b>Journal/Issue: </b>
                    {journal} {issue} {date}
                    <br />
                </>
            )}
            <b>Source: </b>
            {baseURL(link, article_id)}
        </p>
    </div>
);

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
