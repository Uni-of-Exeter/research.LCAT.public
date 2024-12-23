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

import { andify } from "../../utils/utils";

const ClimateSettings = ({ regions, rcp, season, setRcp, setSeason }) => {
    if (regions.length === 0) {
        return null;
    }

    return (
        <div>
            <h1>Explore your local climate</h1>
            <p>
                For&nbsp;
                <span className="projected-regions">{andify(regions.map((e) => e.name))}</span>
                &nbsp;under the&nbsp;
                <select value={rcp} onChange={(e) => setRcp(e.target.value)}>
                    <option value="rcp60">existing global policies</option>
                    <option value="rcp85">worst case scenario</option>
                </select>
                &nbsp;
                {rcp === "rcp60" && <span>(equivalent to global warming level of 2.0-3.7C which is RCP 6.0)</span>}
                {rcp === "rcp85" && <span>(equivalent to global warming level of 3.2-5.4C which is RCP 8.5)</span>}
                &nbsp;the&nbsp;
                <select value={season} onChange={(e) => setSeason(e.target.value)}>
                    <option value="annual">yearly</option>
                    <option value="summer">summer</option>
                    <option value="winter">winter</option>
                </select>
                &nbsp;average climate change for 2070 compared with local records for the 1980s is expected to be:
            </p>
        </div>
    );
};

export default ClimateSettings;
