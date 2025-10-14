// Function to parse the float values from the prediction

export const climateChange = (prediction, variable, year) => {
    if (prediction.length > 0) {
        const baseline = parseFloat(prediction[0][`${variable}_1980_mean`]);
        const predict = parseFloat(prediction[0][`${variable}_${year}_mean`]);
        return baseline != null && predict != null ? predict - baseline : null;
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
    
    // Invert value for rsds (more radiation = less cloud)
    const adjustedValue = variable === "rsds" ? -value : value;
    const absoluteValue = Math.abs(adjustedValue).toFixed(2);
    const direction = adjustedValue === 0 ? "No change in" : adjustedValue > 0 ? "increases" : "decreases";
    
    return {
        name,
        value: adjustedValue,
        change: adjustedValue === 0 ? `${direction} ${name}` : `${name} ${direction} by ${absoluteValue} ${units}`,
        arrow: adjustedValue === 0 ? 'none' : adjustedValue > 0 ? 'up' : 'down',
        direction,
        absoluteValue,
        units,
    };
};

// Climate variables configuration
export const climateVariables = [
    { variable: 'tas', name: 'Temperature', units: '°C' },
    { variable: 'pr', name: 'Rainfall', units: 'mm/day' },
    { variable: 'rsds', name: 'Cloudiness', units: 'Watts/m²' },
    { variable: 'sfcWind', name: 'Windiness', units: 'm/sec' },
];

// Get all climate data formatted
export const getAllClimateData = (climatePrediction, year = 2050) => {
    return climateVariables.map(({ variable, name, units }) => 
        formatClimateData(climatePrediction, variable, name, units, year)
    );
};
