/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

const FooterText = () => {
    return (
        <div className="footer">
            <p>
                The Local Climate Adaptation Tool has been developed by the{" "}
                <a href="https://www.ecehh.org/" target="_blank" rel="noreferrer">
                    University of Exeter’s European Centre for Human Health
                </a>
                ,{" "}
                <a href="https://www.cornwall.gov.uk/" target="_blank" rel="noreferrer">
                    Cornwall Council
                </a>
                ,{" "}
                <a href="https://thentrythis.org" target="_blank" rel="noreferrer">
                    Then Try This
                </a>{" "}
                and{" "}
                <a href="https://www.turing.ac.uk/" target="_blank" rel="noreferrer">
                    The Alan Turing Institute
                </a>{" "}
                with co-design partners from Local Government, the National Health Service, emergency services, and
                voluntary and private sectors. Funding for the project has been provided by Research England’s
                Collaboration Fund, Strategic Priorities Fund and Policy Support Fund, as part of the Policy@Exeter
                initiative, The Schroder Foundation, and the Net Zero Innovation Programme; a UCL and Local Government
                Association Initiative. This work was also supported by Wave 1 of The UKRI Strategic Priorities Fund
                under the EPSRC Grant EP/W006022/1, delivered through the “Environment and Sustainability” theme within
                The Alan Turing Institute.
            </p>

            <p>
                This has been co-funded through the BlueAdapt project. BlueAdapt has received funding from the European
                Union’s Horizon Europe research and innovation programme under grant agreement No 101057764 and by the
                UKRI/HM Government.
            </p>

            <p>
                The LCAT project team (University of Exeter, Then Try This, Cornwall Council and The Alan Turing
                Institute) and their agents, take no responsibility for decisions taken as a result of the use of this
                tool. While every effort has been made to ensure data represented in the tool are accurate, no liability
                is accepted for any inaccuracies in the dataset or for any actions taken based on the use of this tool.
                The views expressed in this tool do not reflect the views of the organisations or the funding bodies.
                There is no guarantee that the tool will be updated to reflect changes in the source information.
            </p>

            <p>
                <a href="https://github.com/Uni-of-Exeter/research.LCAT.public" target="_blank" rel="noreferrer">
                    Source code published
                </a>{" "}
                open source under the{" "}
                <a href="http://www.cgpl.org/" target="_blank" rel="noreferrer">
                    Common Good Public Licence Beta 1.0
                </a>
            </p>

            <p>
                Boundary data sourced from the Office for National Statistics, and licensed under the Open Government
                Licence v.3.0
                <br />
                Contains OS data © Crown copyright and database right 2024
            </p>

            <p>
                Development before 2024 Copyright © Then Try This & University of Exeter
                <br />
                Development from 2024 Copyright © University of Exeter
            </p>

            <p>
                <button
                    type="button"
                    style={{ background: "none", border: "none", color: "#115158ff", textDecoration: "underline", cursor: "pointer", padding: 0, font: "inherit" }}
                    onClick={() => window.dispatchEvent(new Event('open_cookie_banner'))}
                >
                    Manage cookies
                </button>
            </p>
        </div>
    );
};

export default FooterText;
