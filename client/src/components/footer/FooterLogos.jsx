/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

const FooterLogos = () => {
    return (
        <div className="footer">
            <div className="logo-block">
                <img
                    className="logos"
                    alt="Partner logos: University of Exeter, European Centre for Environment for Environment and Human Health, Cornwall Council"
                />
            </div>

            <div className="logo-block">
                <img
                    className="funder-logos"
                    alt="Funder logos: Co-funded by the European Union, UK Research and Innovation, and BlueAdapt"
                />
            </div>
        </div>
    );
};

export default FooterLogos;
