import React, { useState } from "react";

const SvgWildfires = ({ selectedHazard, ...rest }) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            xmlSpace="preserve"
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
                <path
                    d="M15.429 266.142A15.43 15.43 0 0 0 0 281.571a15.43 15.43 0 0 0 15.429 15.43 15.43 15.43 0 0 0 15.43-15.43 15.43 15.43 0 0 0-15.43-15.429"
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
                <path
                    d="m16.249 289.673 3.38 3.482-1.289.004v2.449h-4.206v-2.435l-1.202.004zM9.929 287.507l3.38 3.483-1.289.004v2.448H7.814v-2.434l-1.202.004zM6.878 270.998l.974 3.528 2.79 2.446-2.42-.63.124.28 2.247 2.262-2.038-.245 2.608 2.957-2.12-.286 2.715 3.22-3.841-.545v3.654H6.31v-3.713l-3.849 1.004 2.348-3.436-1.75.436 2.26-3.165-1.69.374 2.114-2.627-2.157.733 2.57-2.607zM21.138 269.396c.735.887-.33 3.6-.437 5.635.365-.698 1.853-1.63 2.475-2.195-.37 2.363-.993 3.95-.467 5.177.164-.762.84-.993 1.526-1.414-.217 1.574-.075 2.862.422 4.437l1.047-.915c.544 4.783-.49 8.066-4.5 8.1 1.42-1.185 3.184-2.677 2.788-3.661-.317.424-1.04.58-1.405.87.488-1.386.713-3.26.17-4.445-.12 1.666-.177 1.4-.973 2.642.308-1.642-.136-2.15-.707-2.972.083 1.075-.393 2.057-1.024 3.132-.715-1.575.607-5.516-1.576-6.354.536 2.565-.387 4.134-.079 6.168-.66-.325-1.3-1.063-1.511-1.99-.217.938.247 2.046.483 2.849l-1.084-.677c-.047 2.05 1.731 3.345 3.45 4.508-4.479.052-6.557-2.168-5.978-6.256.203.518.508 1.113.901 1.297-.635-2.582-.823-4.754.155-6.125q.1.974.681 1.346c-.107-2.203.762-6.489 1.935-7.958-.143.928-.179 4.142.257 4.732-.097-2.464 3.4-4.063 3.45-5.931"
                    style={{
                        opacity: 1,
                        fill: selectedHazard === "Wildfires" ? "#FFD667" : isHovered ? "#FFD667" : "#fff",
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
        </svg>
    );
};
export default SvgWildfires;
