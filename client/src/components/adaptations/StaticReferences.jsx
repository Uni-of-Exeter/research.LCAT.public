/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import React from "react";

import adaptationRefs from "../../kumu/parsed/processed_references.json";
import "./StaticReferences.css";

function formatAuthors(authorsString) {
    if (!authorsString) {
        return "";
    }
    let authors = authorsString.split(",");
    if (authors.length > 3) {
        return authors.slice(0, 2).join(", ") + " et al.";
    } else {
        return authorsString;
    }
}

function baseURL(url) {
    let domain = new URL(url);
    return domain.hostname;
}

function ArticleReference(props) {
    return (
        <div className="reference-container">
            <p>
                <a href={props.a.link} className="reference-title" target="_blank" rel="noreferrer">
                    {props.a.title}
                </a>
            </p>
            <p>
                {props.a.type && (
                    <>
                        <b>Type: </b>
                        {props.a.type}
                        <br />
                    </>
                )}
                {props.a.authors && (
                    <>
                        <b>Authors: </b>
                        {formatAuthors(props.a.authors)}
                        <br />
                    </>
                )}
                {props.a.journal && props.a.journal !== "" && (
                    <>
                        <b>Journal/Issue: </b>
                        {props.a.journal} {props.a.issue} {props.a.date}
                        <br />
                    </>
                )}
            </p>
        </div>
    );
}

function WebPageReference(props) {
    return (
        <div className="reference-container">
            <p>
                <a href={props.a.link} className="reference-title" target="_blank" rel="noreferrer">
                    {props.a.title}
                </a>
            </p>
            <p>
                {props.a.type && (
                    <>
                        <b>Type: </b>
                        {props.a.type}
                        <br />
                    </>
                )}
                <b>Source: </b>
                {baseURL(props.a.link)}
            </p>
        </div>
    );
}

function ReportReference(props) {
    return (
        <div className="reference-container">
            <p>
                <a href={props.a.link} className="reference-title" target="_blank" rel="noreferrer">
                    {props.a.title}
                </a>
            </p>
            <p>
                {props.a.type && (
                    <>
                        <b>Type: </b>
                        {props.a.type}
                        <br />
                    </>
                )}
                <b>Source: </b>
                {baseURL(props.a.link)}
            </p>
        </div>
    );
}

function BookSectionReference(props) {
    return (
        <div className="reference-container">
            <p>
                <a href={props.a.link} className="reference-title" target="_blank" rel="noreferrer">
                    {props.a.title}
                </a>
            </p>
            <p>
                {props.a.type && (
                    <>
                        <b>Type: </b>
                        {props.a.type}
                        <br />
                    </>
                )}
                <b>Source: </b>
                {baseURL(props.a.link)}
            </p>
        </div>
    );
}

function StaticReferences(props) {
    const filteredRefs = props.referenceIds.map((id) => adaptationRefs[id.toString()]).filter(Boolean);

    if (filteredRefs.length > 0) {
        return (
            <div>
                <b className="reference-emphasis">References:</b>
                {filteredRefs.map((r) => {
                    if (r.type === "Journal Article") return <ArticleReference key={r.article_id} a={r} />;
                    if (r.type === "Conference Proceedings") return <ArticleReference key={r.article_id} a={r} />;
                    if (r.type === "Book" || r.type === "Book Chapter")
                        return <ArticleReference key={r.article_id} a={r} />;
                    if (r.type === "Web Page") return <WebPageReference key={r.article_id} a={r} />;
                    if (r.type === "Report" || r.type === "Research Report" || r.type === "Report Section")
                        return <ReportReference key={r.article_id} a={r} />;
                    if (r.type === "Book Section") return <BookSectionReference key={r.article_id} a={r} />;
                    // return <p>{r.type}: not understood</p>;
                })}
            </div>
        );
    }
}

export default StaticReferences;
