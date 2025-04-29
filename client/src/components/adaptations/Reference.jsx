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
import LinkOutIcon from "../vulnerabilities/LinkOutIcon";

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
const Reference = ({ link, title, type, article_id, authors, journal, issue, date }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const { getCollapseProps, getToggleProps } = useCollapse({ isExpanded });

    const handleToggle = () => setIsExpanded((prev) => !prev);

    return (
        <div className="reference-container" onClick={handleToggle}>
            <div className="reference-title" {...getToggleProps()}>
                {title || `${link.slice(0, 40)}...`}
            </div>
            <div {...getCollapseProps()}>
                <p>
                    {type && (
                        <div>
                            <b>Type & ID:</b> {type} - {article_id}
                        </div>
                    )}
                    {authors && (
                        <div>
                            <b>Authors:</b> {formatAuthors(authors)}
                        </div>
                    )}
                    {journal && (
                        <div>
                            <b>Journal/Issue:</b> {journal} {issue} {date}
                        </div>
                    )}
                    <div>
                        <b>Source:</b>{" "}
                        <a href={link} target="_blank" rel="noopener noreferrer">
                            {baseURL(link, article_id)}
                            <LinkOutIcon size="1.2em" colour="black" />
                        </a>
                    </div>
                </p>
            </div>
        </div>
    );
};

export default Reference;
