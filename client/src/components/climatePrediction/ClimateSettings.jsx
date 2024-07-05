/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import React, { useEffect, useState } from "react";

import { andify } from "../../utils/utils";

function ClimateSettings(props) {
    const [rcp, setRcp] = useState("rcp60");
    const [season, setSeason] = useState("annual");

    // change when graph changes
    useEffect(() => {
        setRcp(props.rcp);
    }, [props.rcp]);
    useEffect(() => {
        setSeason(props.season);
    }, [props.season]);

    if (props.regions.length === 0) {
        return null;
    }

    return (
        <div>
            <h1>Explore your local climate</h1>
            <p>
                For&nbsp;
                <span className={"projected-regions"}>{andify(props.regions.map((e) => e.name))}</span>
                &nbsp;under the&nbsp;
                <select
                    value={rcp}
                    onChange={(e) => {
                        props.rcpCallback(e.target.value);
                    }}
                >
                    <option value="rcp60">existing global policies</option>
                    <option value="rcp85">worst case scenario</option>
                </select>
                &nbsp;
                {rcp === "rcp60" && <span>(equivalent to global warming level of 2.0-3.7C which is RCP 6.0)</span>}
                {rcp === "rcp85" && <span>(equivalent to global warming level of 3.2-5.4C which is RCP 8.5)</span>}
                &nbsp;the&nbsp;
                <select
                    value={season}
                    onChange={(e) => {
                        props.seasonCallback(e.target.value);
                    }}
                >
                    <option value="annual">yearly</option>
                    <option value="summer">summer</option>
                    <option value="winter">winter</option>
                </select>
                &nbsp;average climate change for 2070
                {/*
            <select defaultValue="2070" onChange={(e) => { props.yearCallback(e.target.value); }}>                  
              <option value="2030">2030</option>
              <option value="2040">2040</option>
              <option value="2050">2050</option>
              <option value="2060">2060</option>
              <option value="2070">2070</option>
            </select>
            */}
                &nbsp;compared with local records for the 1980s is expected to be:
            </p>
        </div>
    );
}

export default ClimateSettings;
