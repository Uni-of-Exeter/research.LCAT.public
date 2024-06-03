import React from "react";

const AdaptationGuide = () => {
    return (
        <div className="footer-flex-container">
            <div className="footer-heading">Learn About Climate Adaptation.</div>
            <div className="footer-flex-content">
                <p>
                    <a
                        className="dummy-resource-button"
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-Introduction-to-Local-Climate-Adaptation-May-2024.pdf"
                        target="_blank"
                        rel="noreferrer"
                    ></a>
                </p>
                <p>
                    Read our&nbsp;
                    <a
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-Introduction-to-Local-Climate-Adaptation-May-2024.pdf"
                        target="_blank"
                        rel="noreferrer"
                    >
                        Introduction to Local Climate Adaptation (at ecehh.org)
                    </a>
                </p>
            </div>
        </div>
    );
};

export default AdaptationGuide;
