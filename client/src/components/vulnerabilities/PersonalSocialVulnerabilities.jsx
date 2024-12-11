/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./PersonalSocialVulnerabilities.css";

import React, { useState } from "react";
import LoadingOverlay from "react-loading-overlay-ts";

import { vulnerabilityData } from "./PersonalSocialVulnerabilitiesData";

const PersonalSocialVulnerabilities = (props) => {
    const [selectedVulnerability, setSelectedVulnerability] = useState(null);

    const handleVulnerabilityClick = (vulnerability) => {
        setSelectedVulnerability(vulnerability);
    };

    return (
        <LoadingOverlay active={props.loading} spinner text={"Loading vulnerability data"}>
            <h1>Personal and Social Vulnerabilities</h1>

            <p>
                Everyone will be exposed to the impacts of climate change & extreme weather events but not everyone is
                affected equally.
            </p>

            <p>
                Some individuals or communities will be more exposed to hazards. Some may be more vulnerable due to
                personal and social vulnerabilities. These circumstances impact people’s ability to cope with, adapt to
                and recover from climate events and extreme weather. Those experiencing multiple vulnerabilities are
                more vulnerable to climate impacts.
            </p>

            <p>
                Click below to explore a shortlist of personal and social vulnerabilities to consider for your local
                area. Each provide a link to Climate Just’s data mapping tool so you can explore localised
                vulnerabilities.
            </p>

            <div className="horiz-container-vulnerability">
                {vulnerabilityData.map((vulnerability, index) => (
                    <div
                        className="vert-container-vulnerability"
                        key={index}
                        onClick={() => handleVulnerabilityClick(vulnerability.name)}
                    >
                        <div className="vulnerability-text">
                            <strong>{vulnerability.name}</strong>
                        </div>
                        <div className="vulnerability-img">
                            {React.cloneElement(vulnerability.icon, { selectedVulnerability })}
                        </div>
                    </div>
                ))}
            </div>

            {selectedVulnerability ? (
                <div className="selected-vulnerability-details">
                    <h2 className="vulnerability-information">{selectedVulnerability}</h2>
                    {vulnerabilityData.find((vulnerability) => vulnerability.name === selectedVulnerability)?.details}
                </div>
            ) : (
                <div className="details-placeholder">
                    <p>Please click a vulnerability icon to view details.</p>
                </div>
            )}

            <p className="note">
                Data source:{" "}
                <a href="https://climatejust.org.uk" target="_blank" rel="noreferrer">
                    A selection of vulnerability insight, by theme, from ClimateJust.
                </a>
            </p>
        </LoadingOverlay>
    );
}

export default PersonalSocialVulnerabilities;
