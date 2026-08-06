const basePrediction = [
    {
        tas_1980: 10,
        tas_2020: 11,
        tas_2050: 12,
        tas_2080: 13,
        tasmin_1_percentile_1980: 8,
        tasmin_1_percentile_2020: 9,
        tasmin_1_percentile_2050: 10,
        tasmin_1_percentile_2080: 11,
        tasmax_99_percentile_1980: 12,
        tasmax_99_percentile_2020: 13,
        tasmax_99_percentile_2050: 14,
        tasmax_99_percentile_2080: 15,
    },
];

const baseAverages = {
    1980: 9.5,
    2020: 10.5,
    2050: 11.5,
    2080: 12.5,
};

const createGraphProps = (overrides = {}) => ({
    regions: [{ name: "Cornwall" }],
    season: "annual",
    rcp: "rcp60",
    setSeason: () => {},
    setRcp: () => {},
    loading: false,
    climatePrediction: basePrediction,
    climateAverages: baseAverages,
    variable: "tas",
    setVariable: () => {},
    ...overrides,
});

export { baseAverages, basePrediction, createGraphProps };
