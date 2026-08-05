/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import { useEffect, useState } from "react";

export default function AccessibilityStatement() {
    const [isActive, setIsActive] = useState(() =>
        typeof window !== "undefined" ? window.location.hash === "#accessibility-statement" : false,
    );

    useEffect(() => {
        const updateRoute = () => setIsActive(window.location.hash === "#accessibility-statement");

        updateRoute();
        window.addEventListener("hashchange", updateRoute);

        return () => window.removeEventListener("hashchange", updateRoute);
    }, []);

    if (!isActive) return null;

    return (
        <div id="accessibility-statement-page" style={{ padding: "2rem 1.5rem 3rem" }}>
            <button
                id="accessibility-statement-back"
                className="accessibility-statement-back"
                type="button"
                onClick={() => {
                    window.location.hash = "";
                }}
            >
                Back to the tool
            </button>
            <div className="accessibility-statement-content">
                <h1 id="accessibility-statement-title" style={{ marginTop: 0 }}>
                    Accessibility statement
                </h1>

                <p>
                    The University of Exeter&apos;s European Centre for Human Health is committed to making its websites
                    accessible, in accordance with the Public Sector Bodies (Websites and Mobile Applications) (No. 2)
                    Accessibility Regulations 2018. <br />
                    <br />
                    This accessibility statement applies to{" "}
                    <a href="https://lcat.uk/" target="_blank" rel="noopener noreferrer">
                        https://lcat.uk/
                    </a>
                    .
                </p>

                <h2>Compliance status</h2>

                <p>
                    This website is partially compliant with the Web Content Accessibility Guidelines version 2.2 AA
                    standard, due to the non-compliances listed below.
                </p>

                <h2>Non-accessible content</h2>
                <h3>(a) non-compliance with the accessibility regulations</h3>
                <h4>Interactive climate data chart</h4>
                <p>
                    The website includes an interactive line chart (built with Plotly.js) showing projected climate
                    data. This chart:
                </p>
                <ul>
                    <li>
                        is not fully accessible to screen reader users, as some chart elements do not have accessible
                        names or roles conveyed to assistive technology (fails WCAG 4.1.2 Name, Role, Value)
                    </li>
                    <li>
                        cannot currently be fully operated using a keyboard, and elements within do not consistently
                        show a visible focus indicator when navigated to (fails WCAG 2.4.7 Focus Visible and 2.1.1
                        Keyboard)
                    </li>
                </ul>
                <p>
                    We have provided a figure caption containing a summary of the chart&apos;s content and an accessible
                    HTML data table immediately below the chart, containing the same data in full, which can be shown or
                    hidden using a standard button control. The chart remains available as a visual aid with mouse-hover
                    functionality (for example, to see exact values at a point).
                </p>
                <h4>Interactive map for selecting areas</h4>
                <p>
                    The map used to select areas is not fully accessible to all users, particularly those using keyboard
                    navigation or assistive technology (fails WCAG 2.1.1 Keyboard and 4.1.2 Name, Role, Value). We have
                    provided a form-based interface for selecting areas as an alternative to interacting with the map
                    directly.
                </p>
                <h4>PDF documents</h4>
                <p>
                    The website generates a PDF version of the site content. This PDF is not yet guaranteed to meet the
                    accessibility requirements and may not be fully accessible to all users.
                </p>

                <h2>Preparation of this accessibility statement</h2>

                <p>
                    This statement was prepared on 3rd August 2026.
                    <br />
                    <br />
                    The statement was last reviewed on 3rd August 2026.
                </p>

                <h2>Feedback and contact information</h2>
                <p>
                    If you find any problems not listed on this page or think we&apos;re not meeting accessibility
                    requirements, contact the LCAT team at&nbsp;
                    <a href="mailto:lcat@exeter.ac.uk" target="_blank" rel="noreferrer">
                        lcat@exeter.ac.uk
                    </a>
                    .
                </p>

                <h2>Enforcement procedure</h2>

                <p>
                    The Equality and Human Rights Commission (EHRC) is responsible for enforcing the Public Sector
                    Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018 (the
                    &quot;accessibility regulations&quot;).
                    <br />
                    <br />
                    If you are not happy with how we respond to your complaint,{" "}
                    <a href="https://www.equalityadvisoryservice.com/" target="_blank" rel="noopener noreferrer">
                        contact the Equality Advisory and Support Service (EASS)
                    </a>
                    .
                </p>
            </div>
        </div>
    );
}
