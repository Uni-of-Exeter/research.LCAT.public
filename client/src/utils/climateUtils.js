// Function to parse the float values from the prediction
export const climateChange = (prediction, variable, year) => {
    if (prediction.length > 0) {
        const baseline = parseFloat(prediction[0][`${variable}_1980`]);
        const predict = parseFloat(prediction[0][`${variable}_${year}`]);
        return Number.isFinite(baseline) && Number.isFinite(predict) ? predict - baseline : null;
    }
    return null;
};

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
    { variable: 'tas', name: 'Temperature', units: '°C' },
    { variable: 'pr', name: 'Rainfall', units: 'mm/day' },
    { variable: 'rsds', name: 'Radiation', units: 'Watts/m²' },
    { variable: 'sfcWind', name: 'Windiness', units: 'm/sec' },
];

// Get all climate data formatted
export const getAllClimateData = (climatePrediction, year = 2050) => {
    return climateVariables.map(({ variable, name, units }) => 
        formatClimateData(climatePrediction, variable, name, units, year)
    );
};
