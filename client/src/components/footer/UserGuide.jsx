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

const UserGuide = () => {
    return (
        <div className="footer-flex-container">
            <div className="footer-heading">Access our User Guide.</div>
            <div className="footer-flex-content">
                <p>
                    <a
                        className="user-guide-button"
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE_FINAL-Autumn-24.pdf"
                        target="_blank"
                        rel="noreferrer"
                        aria-label="Read the LCAT User Guide PDF"
                    ></a>
                </p>
                <p>
                    Read the&nbsp;
                    <a
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE_FINAL-Autumn-24.pdf"
                        target="_blank"
                        rel="noreferrer"
                    >
                        LCAT User Guide (at ecehh.org)
                    </a>
                </p>
            </div>
        </div>
    );
};

export default UserGuide;
