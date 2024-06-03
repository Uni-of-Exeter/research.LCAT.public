import React from "react";

const UserGuide = () => {
    return (
        <div className="footer-flex-container">
            <div className="footer-heading">Access our User Guide.</div>
            <div className="footer-flex-content">
                <p>
                    <a
                        className="user-guide-button"
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE_FINAL-Feb-24.pdf"
                        target="_blank"
                        rel="noreferrer"
                    ></a>
                </p>
                <p>
                    Read the&nbsp;
                    <a
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE_FINAL-Feb-24.pdf"
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
