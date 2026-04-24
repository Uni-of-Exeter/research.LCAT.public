import { reportStyles as styles } from "./reportStyles";

const getTextStyle = (text) => {
    const baseStyle = styles.climateVariable;
    if (text.length > 40) {
        return { ...baseStyle, fontSize: 10 };
    } else if (text.length > 30) {
        return { ...baseStyle, fontSize: 10.5 };
    }
    return baseStyle;
};

const formatLineBreaks = (text) => {
    // Manually define break points
    const breakPoints = [
        { from: "Respiratory diseases", to: "Respiratory\ndiseases" },
        { from: "viruses, fungi", to: "viruses,\nfungi" },
        { from: "natural environment", to: "natural\nenvironment" },
        { from: "health conditions", to: "health\nconditions" },
        { from: "are socially", to: "are\nsocially" },
        { from: "low personal", to: "low\npersonal" },
        { from: "Temperature increases", to: "Temperature\nincreases" },
    ];

    let formattedText = text;

    for (const breakPoint of breakPoints) {
        if (formattedText.includes(breakPoint.from)) {
            formattedText = formattedText.replace(breakPoint.from, breakPoint.to);
        }
    }

    return formattedText;
};

export { formatLineBreaks, getTextStyle };
