/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

const Introduction = () => {
    return (
        <div className="grey-section">
            <p>Use this tool to see what the scientific research is saying about:</p>
            <ul>
                <li>
                    <strong className="text-emphasis">How</strong> local climates will change
                </li>
                <li>
                    <strong className="text-emphasis">What</strong> health and community impacts may occur as a result
                </li>
                <li>
                    <strong className="text-emphasis">Who</strong> will be most vulnerable and why
                </li>
                <li>
                    <strong className="text-emphasis">Which</strong> adaptations to consider
                </li>
            </ul>
            <p>
                LCAT is <strong className="text-emphasis">evidence-based</strong> and designed with and for{" "}
                <strong className="text-emphasis"> local decision makers.</strong>
            </p>

            <p>
                <strong className="text-emphasis">Helpful resources:</strong>
            </p>

            <ul>
                <li>
                    <a
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-Introduction-to-Local-Climate-Adaptation-May-2024.pdf"
                        target="_blank"
                        rel="noreferrer"
                    >
                        Introduction to Local Climate Adaptation
                    </a>
                </li>
                <li>
                    <a
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE_FINAL-Autumn-24.pdf"
                        target="_blank"
                        rel="noreferrer"
                    >
                        LCAT User Guide
                    </a>
                </li>
                <li>
                    <a href="https://climatedataportal.metoffice.gov.uk/pages/lacs" target="_blank" rel="noreferrer">
                        Met Office Local Authority Climate Service
                    </a>
                </li>
            </ul>
        </div>
    );
};

export default Introduction;
