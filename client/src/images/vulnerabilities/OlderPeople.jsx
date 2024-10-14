import React, { useState } from "react";

const SvgOlderPeople = (props) => {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width={116.629}
            height={116.629}
            viewBox="0 0 30.858 30.858"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            {...props}
        >
            <g transform="translate(0 -266.142)">
                <g
                    style={{
                        fill: "#fff",
                    }}
                >
                    <path
                        d="M274.8 274.8v18.8h-37.5v-18.8c0-10.3 8.4-18.8 18.8-18.8s18.7 8.4 18.7 18.8"
                        style={{
                            fill: "#fff",
                        }}
                        transform="translate(2.251 267.803)scale(.05168)"
                    />
                    <path
                        d="m256 68.5-93.7 65.6V68.5h-37.5v91.9l-56.2 39.4H106v243.7h300V199.8h37.5zm56.3 318.7H199.8c-10.4 0-18.8-8.4-18.8-18.8v-75h18.8v-15.7c0-30.5 22.9-57.7 53.3-59.3 32.5-1.6 59.2 24.1 59.2 56.2v18.8H331v75c0 10.5-8.4 18.8-18.7 18.8"
                        style={{
                            fill: "#fff",
                        }}
                        transform="translate(2.251 267.803)scale(.05168)"
                    />
                </g>
                <circle
                    cx={15.429}
                    cy={281.571}
                    r={15.429}
                    style={{
                        opacity: 1,
                        fill: "#031d44",
                        fillOpacity: 1,
                        stroke: "none",
                        strokeWidth: 0.5,
                        strokeMiterlimit: 4,
                        strokeDasharray: "none",
                        strokeOpacity: 1,
                    }}
                />
                <g
                    style={{
                        strokeWidth: 7.57722664,
                    }}
                >
                    <g
                        style={{
                            strokeWidth: 53.97331238,
                        }}
                    >
                        <g
                            style={{
                                strokeWidth: 59.44264603,
                            }}
                        >
                            <path
                                d="M401.65 121.64c-14.219-15.109-37.918-15.809-53.09-1.652-15.18 14.145-16.016 37.973-1.953 53.227.14.156 4.652 5.136 10.793 14l-77.227 70.598c-5.977 5.465-8.379 13.34-7.164 20.766-15.758 8.226-26.578 24.707-26.578 43.695v222.75c0 6.86 5.566 12.414 12.414 12.414 6.867 0 12.414-5.555 12.414-12.414l.008-222.75c0-13.395 10.84-24.281 24.188-24.422.101 0 .183.023.281.023.102 0 .184-.023.281-.023 13.352.156 24.164 11.039 24.164 24.422 0 6.86 5.563 12.414 12.414 12.414 6.867 0 12.414-5.555 12.414-12.414 0-17.137-8.785-32.238-22.098-41.07l56.957-52.074c7.504 18.777 13.328 41.352 13.328 66.55v226.61c0 20.833 16.891 37.712 37.715 37.712 20.828 0 37.703-16.883 37.703-37.711V295.68c0-101.78-64.238-171.14-66.965-174.04zm-25.61-67.16c0 30.09-24.391 54.484-54.48 54.484s-54.484-24.395-54.484-54.484C267.076 24.394 291.471 0 321.56 0s54.48 24.395 54.48 54.48"
                                style={{
                                    fill:
                                        props.selectedVulnerability === "Older people"
                                            ? "#FFD667"
                                            : isHovered
                                              ? "#FFD667"
                                              : "#fff",
                                    strokeWidth: 59.44264603,
                                }}
                                transform="translate(-.138 268.552)scale(.04497)"
                            />
                        </g>
                    </g>
                </g>
            </g>
        </svg>
    );
};
export default SvgOlderPeople;
