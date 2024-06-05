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

const ContactUs = () => {
    return (
        <div className="footer-flex-container">
            <h1>Need help? Contact us.</h1>
            <div className="footer-flex-content">
                <p>
                    <a className="email-button" href="mailto:lcat@exeter.ac.uk" target="_blank" rel="noreferrer"></a>
                </p>
                <p>
                    Email us at:&nbsp;
                    <a href="mailto:lcat@exeter.ac.uk" target="_blank" rel="noreferrer">
                        lcat@exeter.ac.uk
                    </a>
                </p>
            </div>
        </div>
    );
};

export default ContactUs;
