import React, { useState } from "react";

const SvgHeatwave = (props) => {
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
                    d="M6.622 272.142h3.595a.3.3 0 0 1 .3.3V283.6a3.58 3.58 0 0 1 1.497 2.92 3.6 3.6 0 0 1-3.594 3.595 3.6 3.6 0 0 1-3.595-3.595c0-1.165.557-2.244 1.498-2.92v-11.159a.3.3 0 0 1 .3-.3m11.351 2.176c1.293.974 1.984 2.149 1.959 3.327-.035 1.623-1.347 3.093-2.203 4.532-.816 1.372-1.266 2.815-.711 4.168.332.813 1.03 1.59 2.02 2.247l-1.007.398c-1.108-.737-1.886-1.6-2.258-2.51-.62-1.513-.11-3.063.74-4.492.888-1.494 2.117-2.907 2.147-4.35.023-1.042-.596-2.092-1.74-2.954zm3.586 0c1.292.974 1.984 2.149 1.959 3.327-.035 1.623-1.347 3.093-2.203 4.532-.816 1.372-1.266 2.815-.712 4.168.333.813 1.031 1.59 2.02 2.247l-1.006.398c-1.108-.737-1.886-1.6-2.258-2.51-.62-1.513-.11-3.063.74-4.492.888-1.494 2.116-2.907 2.147-4.35.022-1.042-.596-2.092-1.74-2.954zm3.755 0c1.293.974 1.984 2.149 1.959 3.327-.035 1.623-1.348 3.093-2.203 4.532-.816 1.372-1.266 2.815-.712 4.168.333.813 1.031 1.59 2.02 2.247l-1.006.398c-1.108-.737-1.885-1.6-2.258-2.51-.62-1.513-.11-3.063.74-4.492.888-1.494 2.116-2.907 2.147-4.35.022-1.042-.596-2.092-1.739-2.954z"
                    style={{
                        opacity: 1,
                        fill: props.selectedHazard === "Heatwaves" ? "#FFD667" : isHovered ? "#FFD667" : "#fff",
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
                    d="M6.922 272.741v11.017a.3.3 0 0 1-.136.252 2.99 2.99 0 0 0-1.362 2.51 3 3 0 0 0 2.996 2.996 3 3 0 0 0 2.995-2.996 2.98 2.98 0 0 0-1.362-2.51.3.3 0 0 1-.136-.252v-.533H8.72v1.222a2.1 2.1 0 0 1 1.798 2.074 2.1 2.1 0 0 1-2.097 2.096 2.1 2.1 0 0 1-2.097-2.096c0-1.055.782-1.928 1.797-2.074v-9.01a.3.3 0 0 1 .6 0v1.198h1.197v-.899h-.599a.3.3 0 1 1 0-.599h.6v-.898H8.42a.3.3 0 0 1 0-.6h1.497v-.898z"
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
                    d="M8.72 277.234v2.397h1.197v-.9h-.599a.3.3 0 0 1 0-.599h.6v-.898zm0 2.996v2.396h1.197v-.898h-.599a.3.3 0 1 1 0-.6h.6v-.898zm-.3 4.792a1.5 1.5 0 0 0-1.498 1.498 1.5 1.5 0 0 0 1.498 1.498 1.5 1.5 0 0 0 1.497-1.498 1.5 1.5 0 0 0-1.497-1.498"
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
        </svg>
    );
};
export default SvgHeatwave;
