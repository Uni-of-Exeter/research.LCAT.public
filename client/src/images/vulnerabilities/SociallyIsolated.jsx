import React, { useState } from "react";

const SvgSociallyIsolated = ({ selectedVulnerability, ...rest }) => {
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
                                strokeWidth: 364.55151367,
                            }}
                        >
                            <g
                                style={{
                                    strokeWidth: 352.73236084,
                                }}
                            >
                                <path
                                    d="M342.7 282.21a20.78 20.78 0 0 0-20.78 20.78 20.8 20.8 0 0 0 6.085 14.7 20.8 20.8 0 0 0 14.695 6.086 20.8 20.8 0 0 0 14.699-6.086 20.8 20.8 0 0 0 6.086-14.7 20.8 20.8 0 0 0-6.086-14.694 20.8 20.8 0 0 0-14.699-6.086"
                                    style={{
                                        fill:
                                            selectedVulnerability === "People who are socially isolated"
                                                ? "#FFD667"
                                                : isHovered
                                                  ? "#FFD667"
                                                  : "#fff",
                                        strokeWidth: 352.73236084,
                                    }}
                                    transform="translate(-3.028 263.786)scale(.05398)"
                                />
                                <path
                                    d="M552.31 292.59 348.41 90.55a8.11 8.11 0 0 0-11.41 0L133.09 292.59a8.1 8.1 0 0 0-2.402 5.719 8.1 8.1 0 0 0 2.347 5.742l34.375 34.695h-.004q.494.389 1.04.695v158.98a9.754 9.754 0 0 0 9.757 9.754h329a9.77 9.77 0 0 0 6.899-2.855 9.77 9.77 0 0 0 2.855-6.899v-158.98a7.5 7.5 0 0 0 1.04-.695l34.374-34.695a8.106 8.106 0 0 0-.054-11.461zM338.02 439.83h9.352l7.933 48.828H330.09zm42.262 48.828-10.363-63.809v-65.676c.59.469 1.172.941 1.734 1.465a39.4 39.4 0 0 1 10.652 30.062c0 5.535 4.485 10.023 10.02 10.023 5.536 0 10.023-4.488 10.023-10.023 0-19.133-5.726-34.18-17.02-44.72h-.004a62.18 62.18 0 0 0-42.629-14.94 62.27 62.27 0 0 0-42.629 14.94c-11.297 10.54-17.02 25.587-17.02 44.72 0 5.535 4.485 10.023 10.02 10.023 5.536 0 10.023-4.488 10.023-10.023a39.47 39.47 0 0 1 10.543-29.961 30 30 0 0 1 1.844-1.574v65.68l-10.367 63.812H187.96v-158.87L337 182.107a8.11 8.11 0 0 1 11.41 0l149.03 147.67v158.87z"
                                    style={{
                                        fill:
                                            selectedVulnerability === "People who are socially isolated"
                                                ? "#FFD667"
                                                : isHovered
                                                  ? "#FFD667"
                                                  : "#fff",
                                        strokeWidth: 352.73236084,
                                    }}
                                    transform="translate(-3.028 263.786)scale(.05398)"
                                />
                            </g>
                        </g>
                    </g>
                </g>
            </g>
        </svg>
    );
};

export default SvgSociallyIsolated;
