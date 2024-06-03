import React from "react";

const UserGuide = () => {
    return (
        <div className="footer-flex-container">
            <div className="footer-heading">Access our User Guide</div>
            <div className="footer-flex-content">
                <p>
                    <a
                        className="user-guide-button"
                        href="https://www.ecehh.org/research/local-climate-adaptation-tool/"
                        target="_blank"
                        rel="noreferrer"
                    ></a>
                </p>
                <p>
                    Find the&nbsp;
                    <a
                        href="https://www.ecehh.org/research/local-climate-adaptation-tool/"
                        target="_blank"
                        rel="noreferrer"
                    >
                        LCAT User Guide at: ecehh.org
                    </a>
                </p>
            </div>
        </div>
    );
};

export default UserGuide;
