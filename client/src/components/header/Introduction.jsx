/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

function Introduction() {
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
                <strong className="text-emphasis"> local decision makers.</strong> To provide feedback on the tool and
                aid us in the co-design process, please fill in our{" "}
                <a
                    href="https://forms.office.com/pages/responsepage.aspx?id=d10qkZj77k6vMhM02PBKUwt2iHj6sgtNt-F8e7EjD4hUNURIUFRZUTJHNVNKUTFNWVNNSzAxSDdFRS4u"
                    target="_blank"
                    rel="noreferrer"
                >
                    anonymous evaluation survey.
                </a>
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
                        Introduction to Local Climate Adaptation.
                    </a>
                </li>
                <li>
                    <a
                        href="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-USER-GUIDE_FINAL-Feb-24.pdf"
                        target="_blank"
                        rel="noreferrer"
                    >
                        LCAT User Guide.
                    </a>
                </li>
            </ul>

            <p>
                <strong className="text-emphasis">Data disclaimers:</strong>
            </p>

            <ul>
                <li>
                    Please be aware that climate predictions for the regions of Northern Ireland and the Isles of Scilly
                    are not bias corrected. This is due to limitations of the underlying climate datasets used in LCAT.
                    For further information on bias correction, please see{" "}
                    <a
                        href="https://www.metoffice.gov.uk/binaries/content/assets/metofficegovuk/pdf/research/ukcp/ukcp18-guidance---how-to-bias-correct.pdf"
                        target="_blank"
                        rel="noreferrer"
                    >
                        this article
                    </a>{" "}
                    by the Met Office.
                </li>
                <li>
                    Climate predictions for the Shetland Islands (bias and non bias-corrected) are not included in the
                    CHESS-SCAPE dataset. Please be aware that climate predictions displayed in LCAT for these regions
                    are approximated to the closest predictions available in the Orkney Islands.
                </li>
                <li>
                    Bias-corrected climate predictions for the Isle of Man have been added to LCAT. Select this region
                    via the dropdown below.
                </li>
            </ul>
        </div>
    );
}

export default Introduction;
