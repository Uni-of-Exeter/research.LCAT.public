import React, { useState } from "react";

const SvgHealthConditions = (props) => {
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
                            fill: props.selectedVulnerability === "People with health conditions" ? "#FFD667" : isHovered ? "#f5821fff" : "#fff",
                        }}
                        transform="translate(2.251 267.803)scale(.05168)"
                    />
                    <path
                        d="m256 68.5-93.7 65.6V68.5h-37.5v91.9l-56.2 39.4H106v243.7h300V199.8h37.5zm56.3 318.7H199.8c-10.4 0-18.8-8.4-18.8-18.8v-75h18.8v-15.7c0-30.5 22.9-57.7 53.3-59.3 32.5-1.6 59.2 24.1 59.2 56.2v18.8H331v75c0 10.5-8.4 18.8-18.7 18.8"
                        style={{
                            fill: props.selectedVulnerability === "People with health conditions" ? "#FFD667" : isHovered ? "#f5821fff" : "#fff",
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
                <path
                    d="M23.983 274.79c-1.188-1.297-2.778-2.014-4.464-2.014-1.46 0-2.847.533-3.96 1.522a5.92 5.92 0 0 0-3.958-1.522c-1.686 0-3.277.717-4.465 2.013-1.837 2.013-2.307 5.022-1.283 7.54h4.56l2.533-3.787a.68.68 0 0 1 .675-.3.68.68 0 0 1 .546.498l1.659 6.06 1.897-2.846a.68.68 0 0 1 .567-.307h3.413c.375 0 .682.307.682.682a.684.684 0 0 1-.682.682h-3.045l-2.533 3.787a.67.67 0 0 1-.566.307c-.034 0-.075 0-.11-.006a.68.68 0 0 1-.545-.498l-1.659-6.059-1.897 2.845a.68.68 0 0 1-.567.307H6.658l8.397 9.328c.13.143.307.225.505.225a.68.68 0 0 0 .505-.225l7.918-8.652c2.41-2.64 2.41-6.94 0-9.58"
                    style={{
                        fill: props.selectedVulnerability === "People with health conditions" ? "#FFD667" : isHovered ? "#f5821fff" : "#fff",
                        strokeWidth: 0.35277778,
                    }}
                />
            </g>
        </svg>
    );
};
export default SvgHealthConditions;
