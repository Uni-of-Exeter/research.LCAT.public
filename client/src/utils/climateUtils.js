// Function to parse the float values from the prediction
export const climateChange = (prediction, variable, year) => {
    if (prediction.length > 0) {
        const baseline = parseFloat(prediction[0][`${variable}_1980`]);
        const predict = parseFloat(prediction[0][`${variable}_${year}`]);
        return Number.isFinite(baseline) && Number.isFinite(predict) ? predict - baseline : null;
    }
    return null;
};

const FULL_SERIES_DECADES = [1980, 2030, 2040, 2050, 2060, 2070];

// Function to format climate data for display
export const formatClimateData = (prediction, variable, name, units, year = 2050) => {
    const value = climateChange(prediction, variable, year);
    if (value == null) {
        return {
            name,
            value: null,
            change: 'No data yet for this area, coming soon.',
            arrow: null,
            direction: null,
        };
    }
    
    const absoluteValue = Math.abs(value).toFixed(2);
    const direction = value === 0 ? "No change in" : value > 0 ? "increases" : "decreases";
    
    return {
        name,
        value: value,
        change: value === 0 ? `${direction} ${name}` : `${name} ${direction} by ${absoluteValue} ${units}`,
        arrow: value === 0 ? 'none' : value > 0 ? 'up' : 'down',
        direction,
        absoluteValue,
        units,
    };
};

// Climate variables configuration
export const climateVariables = [
    { variable: 'tas', name: 'Temperature', units: '°C', graphLabel: 'temperature', graphDecades: FULL_SERIES_DECADES },
    { variable: 'pr', name: 'Rainfall', units: 'mm/day', graphLabel: 'rain', graphDecades: FULL_SERIES_DECADES },
    { variable: 'sfcWind', name: 'Windiness', units: 'm/sec', graphLabel: 'wind', graphDecades: FULL_SERIES_DECADES },
    { variable: 'rsds', name: 'Radiation', units: 'Watts/m²', graphLabel: 'radiation', graphDecades: FULL_SERIES_DECADES },
    { variable: 'tropical_nights', name: 'Tropical Nights', units: 'days', graphLabel: 'tropical nights', graphDecades: FULL_SERIES_DECADES },
    { variable: 'hot_heat_days', name: 'Hot Heat Days', units: 'days', graphLabel: 'hot heat days', graphDecades: FULL_SERIES_DECADES },
    { variable: 'heavy_rain_days', name: 'Heavy Rain Days', units: 'days', graphLabel: 'heavy rain days', graphDecades: FULL_SERIES_DECADES },
    { variable: 'dry_days', name: 'Dry Days', units: 'days', graphLabel: 'dry days', graphDecades: FULL_SERIES_DECADES },
    { variable: 'windy_days', name: 'Windy Days', units: 'days', graphLabel: 'windy days', graphDecades: FULL_SERIES_DECADES },
];

export const getClimateVariableByKey = (variable) =>
    climateVariables.find((item) => item.variable === variable);

export const getGraphDecadesForVariable = (variable) =>
    getClimateVariableByKey(variable)?.graphDecades || FULL_SERIES_DECADES;

export const graphSelectableClimateVariables = climateVariables.filter((item) => item.graphLabel);

// Get all climate data formatted
export const getAllClimateData = (climatePrediction, year = 2050) => {
    return climateVariables.map(({ variable, name, units }) => 
        formatClimateData(climatePrediction, variable, name, units, year)
    );
};
