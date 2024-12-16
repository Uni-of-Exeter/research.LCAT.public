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

const Feedback = () => {
    return (
        <div className="white-section">
            <h1>Evaluation Survey</h1>
            <div>
                <p>
                    Have you 5 minutes to tell us about your experience today? If so, please complete our evaluation
                    survey. It's completely anonymous, and helps us to improve this tool.{" "}
                    <a
                        href="https://forms.office.com/pages/responsepage.aspx?id=d10qkZj77k6vMhM02PBKUwt2iHj6sgtNt-F8e7EjD4hUNURIUFRZUTJHNVNKUTFNWVNNSzAxSDdFRS4u"
                        target="_blank"
                        rel="noreferrer"
                        aria-label="Access the evaluation survey in a new tab"
                    >
                        Please access the survey here.
                    </a>
                </p>
            </div>
        </div>
    );
};

export default Feedback;
