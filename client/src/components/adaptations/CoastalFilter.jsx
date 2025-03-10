/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import { useEffect } from "react";

const CoastalFilter = ({ regions, setApplyCoastalFilter }) => {
    // Every time regions changes, check whether coastal filter should be true or false
    useEffect(() => {
        const areAnyRegionsCoastal = regions.some((region) => region.isCoastal);
        setApplyCoastalFilter(!areAnyRegionsCoastal);
    }, [regions, setApplyCoastalFilter]);

    return null;
};

export default CoastalFilter;
