/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import { ReactComponent as LCATLogoSvg } from "../../images/logos/LCAT_Logo_Primary_RGB.svg";

function LCATHeader() {
    return (
        <div className="white-section">
            <header className="App-header">
                <LCATLogoSvg width={300} />
            </header>
        </div>
    );
}

export default LCATHeader;
