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

function ModelLoader(props) {
    useEffect(() => {
        // don't bother loading if we have no regions yet
        if (props.regions.length > 0) {
            try {
                let prepend = "";
                if (process.env.NODE_ENV === "development") {
                    prepend = "http://localhost:3000";
                }

                var url =
                    prepend +
                    "/api/hadgem_rpc85?" +
                    new URLSearchParams({
                        table: props.table,
                        regionType: props.regionType,
                    }) +
                    "&" +
                    // clumsy, fixme
                    new URLSearchParams(props.regions.map((v) => ["locations", v.id]));

                fetch(url).then((response) => {
                    response.json().then((v) => {
                        props.callback(v);
                    });
                });
            } catch (error) {
                console.error(error);
            }
        }
    }, [props.regions, props.table, props.regionType]);

    return null;
}

export default ModelLoader;
