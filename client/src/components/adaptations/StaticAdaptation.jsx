/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import "./StaticAdaptation.css";

import { useCollapse } from "react-collapsed";

import StaticReferences from "./StaticReferences";

const StaticAdaptation = (props) => {
    const { getCollapseProps, getToggleProps, isExpanded } = useCollapse();

    return (
        <div className="adaptation collapsible">
            <div className="adaptation header" {...getToggleProps()}>
                {props.adaptation.label}
                <div className={isExpanded ? "arrow down" : "arrow right"} />
            </div>
            <div {...getCollapseProps()}>
                <div className="content">
                    <b className="static-adaptation-emphasis">Description:</b>
                    <p>{props.adaptation.description}</p>
                    <p>This adaptation is also relevant to the following climate impact pathways:</p>
                    <ul>
                        {props.adaptation.aggregated_layers
                            .filter((item) => item !== props.selectedHazardName)
                            .map((item, index) => (
                                <li key={index}>{item}</li>
                            ))}
                    </ul>

                    <StaticReferences referenceIds={props.adaptation.reference_id} />
                </div>
            </div>
        </div>
    );
};

export default StaticAdaptation;
