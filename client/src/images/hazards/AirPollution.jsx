import React, { useState } from "react";

const SvgAirPollution = ({ selectedHazard, ...rest }) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width={116.629}
            height={116.629}
            viewBox="0 0 30.858 30.858"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            {...rest}
        >
            <g
                style={{
                    display: "inline",
                }}
            >
                <circle
                    cx={15.429}
                    cy={281.571}
                    r={15.429}
                    style={{
                        opacity: 1,
                        fill: "#b95b09",
                        fillOpacity: 1,
                        stroke: "none",
                        strokeWidth: 0.5,
                        strokeMiterlimit: 4,
                        strokeDasharray: "none",
                        strokeOpacity: 1,
                    }}
                    transform="translate(0 -266.142)"
                />
            </g>
            <g
                style={{
                    display: "inline",
                }}
            >
                <path
                    d="M21.03 8.491a4.95 4.95 0 0 0-4.947-4.947 4.9 4.9 0 0 0-2.707.812 3.534 3.534 0 0 0-4.361 3.018 3.533 3.533 0 0 0-.707 6.065 3.534 3.534 0 1 0 6.05 3.534 3.534 3.534 0 0 0 3.139-3.534 2 2 0 0 0 0-.205 4.95 4.95 0 0 0 3.534-4.743zm5.655 1.414a4.95 4.95 0 0 0-4.128-4.877.716.716 0 1 0-.226 1.414 3.534 3.534 0 0 1 .431 6.849 3.4 3.4 0 0 0-.502-.757.707.707 0 1 0-1.046.905 2 2 0 0 1 .431.799q.09.3.092.615a2.12 2.12 0 0 1-2.12 2.12h-.127a.71.71 0 0 0-.707.53 2.12 2.12 0 0 1-1.993 1.59 2 2 0 0 1-.516-.063.707.707 0 0 0-.382 1.357q.44.126.898.12a3.53 3.53 0 0 0 3.237-2.12 3.534 3.534 0 0 0 3.124-3.534v-.212a4.95 4.95 0 0 0 3.534-4.736M12.549 19.8H6.187a.707.707 0 0 0-.706.707v3.534a.707.707 0 0 0 .706.707h7.069v-4.241a.707.707 0 0 0-.707-.707m11.309 3.534h-3.534v1.414h3.534a.707.707 0 0 0 0-1.414m-5.655-2.12H14.67v3.534h4.241V21.92a.707.707 0 0 0-.707-.707"
                    style={{
                        strokeWidth: 0.35277778,
                        fill: selectedHazard === "Air Quality" ? "#FFD667" : isHovered ? "#FFD667" : "#fff",
                    }}
                />
            </g>
        </svg>
    );
};
export default SvgAirPollution;
