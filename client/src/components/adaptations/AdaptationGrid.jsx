import { DataGrid } from "@mui/x-data-grid";
import * as React from "react";

const AdaptationGrid = ({ adaptationData, pathways }) => {
    // Extract unique aggregated_layers
    const uniqueLayers = Array.from(new Set(adaptationData.flatMap((item) => item.attributes.aggregated_layers || [])));

    // Define columns for DataGrid
    const columns = [
        { field: "label", headerName: "Label", flex: 2 },
        ...pathways.map((pathway) => ({
            field: pathway.name,
            type: "boolean",
            headerName: pathway.name,
        })),
    ];

    // Transform adaptationData into rows
    const rows = adaptationData.map((item, index) => {
        const row = {
            id: index,
            label: item.attributes.label,
        };
        uniqueLayers.forEach((layer) => {
            row[layer] = item.attributes.aggregated_layers?.includes(layer) ? true : false;
        });
        return row;
    });

    return (
        <div style={{ height: "auto", width: "100%" }}>
            <DataGrid
                rows={rows}
                columns={columns}
                getRowClassName={(params) => (params.indexRelativeToCurrentPage % 2 === 0 ? "odd-row" : "even-row")}
                sx={{
                    "& .even-row": {
                        backgroundColor: "#ffffff",
                    },
                    "& .odd-row": {
                        backgroundColor: "#f5f5f5",
                    },
                }}
                initialState={{
                    pagination: {
                        paginationModel: {
                            pageSize: 8,
                        },
                    },
                }}
                disableRowSelectionOnClick
            />
        </div>
    );
};

export default AdaptationGrid;
