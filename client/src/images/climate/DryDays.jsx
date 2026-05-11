import React, { useState } from "react";

const SvgDryDays = ({ selected, isAnnual, ...rest }) => {
    const [isHovered, setIsHovered] = useState(false);

    const isActive = isHovered || selected;

    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            xmlnsXlink="http://www.w3.org/1999/xlink"
            width={116.629}
            height={116.629}
            viewBox="0 0 30.858395 30.858396"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            {...rest}
        >
            <defs>
                <linearGradient id="swatch1">
                    <stop
                        style={{ stopColor: "#115158", stopOpacity: 1 }}
                        offset="0"
                    />
                </linearGradient>
                <linearGradient
                    xlinkHref="#swatch1"
                    id="linearGradient1"
                    x1="24.114841"
                    y1="296.80731"
                    x2="25.660345"
                    y2="296.80731"
                    gradientUnits="userSpaceOnUse"
                    gradientTransform="matrix(1.6711766,-1.2204183,2.1986608,2.7640433,-678.03957,-508.7767)"
                />
            </defs>
            <g transform="translate(-2.3950532e-6,-266.14159)">
                {/* Outer circle stays teal */}
                <circle
                    style={{
                        fill: "#115158",
                        fillOpacity: 1,
                        strokeWidth: 0.465,
                    }}
                    cx={15.429199}
                    cy={281.5708}
                    r={15.429199}
                />

                {/* Droplet shape that changes color */}
                <path
                    style={{
                        fill: isActive ? "#FFD667" : "#fff",
                        strokeWidth: 0.456767,
                    }}
                    d="m 15.648754,272.9839 c -10.2023636,13.36108 -2.000008,15.85393 -0.433341,15.93673 2.524143,0.13352 10.300944,-2.30011 0.433341,-15.93673 z"
                />

                {/* Diagonal line through droplet that changes color */}
                <path
                    d="m 10.18403,273.76253 c -0.7128528,0.52058 -0.5302398,1.89995 0.407609,3.07901 l 8.495097,10.6796 c 0.937865,1.17902 2.277578,1.7134 2.990434,1.19284 0.712853,-0.52058 0.530242,-1.89998 -0.407625,-3.07901 L 13.17445,274.95535 c -0.937851,-1.179 -2.277563,-1.7134 -2.99042,-1.19282 z"
                    style={{
                        fill: isActive ? "#FFD667" : "#fff",
                        stroke: "url(#linearGradient1)",
                        strokeWidth: 0.714987,
                    }}
                />
            </g>
        </svg>
    );
};

export default SvgDryDays;
