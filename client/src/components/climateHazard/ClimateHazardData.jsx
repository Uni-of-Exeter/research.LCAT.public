/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import HeatwaveSvg from "../../images/hazards/Heatwave.jsx";
import WildfiresSvg from "../../images/hazards/Wildfires.jsx";
import FloodSvg from "../../images/hazards/Flood.jsx";
import AirPollutionSvg from "../../images/hazards/AirPollution.jsx";
import CoastalErosionSvg from "../../images/hazards/CoastalErosion.jsx";

// This map contains the rendered content in the ClimateHazardRisk component
export const climateHazardsData = [
    {
        name: "Heatwaves",
        icon: <HeatwaveSvg className="hazard-img" />,
        details: (
            <div>
                <p>
                    The UK's climate is warming. Our warmest years on record have occurred in the last 10 years. One
                    consequence of this is an increase in <strong className="text-emphasis">frequency</strong> and{" "}
                    <strong className="text-emphasis">intensity</strong> of heatwaves.
                </p>
                <p>
                    As warming continues in the future, UK summers are predicted to become hotter and drier on average
                    with regional variations existing. As a result, heatwaves will become:
                </p>
                <ul>
                    <li>More severe.</li>
                    <li>More frequent.</li>
                    <li>Longer.</li>
                </ul>

                <p>
                    Urban environments (e.g. cities) are likely to experience even greater heatwave intensity due to the
                    <strong className="text-emphasis"> urban heat island effect</strong>. Urban heat island effect
                    describes urban areas being a lot warmer than the rural areas around them because of denser
                    populations and infrastructure.
                </p>

                <p className="climate-hazard-emphasis">Where can I find localised heatwave risk data?</p>

                <p>
                    Heatwave data is within the climate indicator category of{" "}
                    <strong className="text-emphasis">Temperature extremes</strong>:{"  "}
                    <a href="https://uk-cri.org/" target="_blank" rel="noreferrer">
                        Climate Risk Indicators | uk-cri.org
                    </a>
                </p>
            </div>
        ),
    },
    {
        name: "Wildfires",
        icon: <WildfiresSvg className="hazard-img" />,
        details: (
            <div>
                <p>
                    Globally, hotter, drier weather in many regions has increased the frequency, intensity, and scale of
                    wildfires. This includes in the UK.
                </p>
                <p>Climate change increases the risk of wildfires through a combination of factors including:</p>
                <ul>
                    <li>Low humidity and low rainfall making it drier.</li>
                    <li>
                        <strong className="text-emphasis">Higher temperatures.</strong>
                    </li>
                    <li>Higher wind speeds.</li>
                </ul>
                <p className="climate-hazard-emphasis">Where can I find localised wildfire risk data?</p>
                <p>
                    Wildfire risk data is within the climate indicator category of{" "}
                    <strong className="text-emphasis">Wildfire</strong>:{"  "}
                    <a href="https://uk-cri.org/" target="_blank" rel="noreferrer">
                        Climate Risk Indicators | uk-cri.org
                    </a>
                </p>
            </div>
        ),
    },
    {
        name: "Air Quality",
        icon: <AirPollutionSvg className="hazard-img" />,
        details: (
            <div>
                <p>Indoor and outdoor air quality in the UK are affected by climate change.</p>
                <p>Indoor air quality is dependent on:</p>
                <ul>
                    <li>
                        Individual <strong className="text-emphasis">building performance.</strong>
                    </li>
                    <li>Emissions from indoor sources like air fresheners and cookers.</li>
                    <li>
                        <strong className="text-emphasis">Damp and mould.</strong>
                    </li>
                    <li>External air quality.</li>
                </ul>
                <p>Outdoor air quality is impacted by:</p>
                <ul>
                    <li>
                        <strong className="text-emphasis">Higher temperatures</strong> which can exacerbate the build-up
                        of <strong className="text-emphasis">air pollution.</strong>
                    </li>
                    <li>Drought can increase the amount of dust particles.</li>
                    <li>
                        <strong className="text-emphasis">Wildfire smoke.</strong>
                    </li>
                    <li>Thunderstorms and windstorms can increase allergens like pollen and fungal spores.</li>
                </ul>

                <p className="climate-hazard-emphasis">Where can I find localised outdoor air quality data?</p>

                <p>
                    Future air quality cannot be modelled yet. However, the first link below provides historical air
                    pollutant data for your area over time and the second link provides a five-day air pollution
                    forecast for your area.
                </p>

                <ul>
                    <li>
                        <a href="https://uk-air.defra.gov.uk/data/gis-mapping/" target="_blank" rel="noreferrer">
                            DEFRA Ambient Air Quality
                        </a>
                        {" - "}Find out the ambient air quality for your area.
                    </li>
                    <li>
                        <a href="https://uk-air.defra.gov.uk/forecasting/" target="_blank" rel="noreferrer">
                            DEFRA Air Pollution Forecast
                        </a>
                        {" - "}Explore your local air pollution forecast.
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "Flooding",
        icon: <FloodSvg className="hazard-img" />,
        details: (
            <div>
                <p>
                    The UK has become wetter over the recent decades, with an increase in frequency and intensity of
                    rainfall and flooding. Flooding is affected by:
                </p>

                <ul>
                    <li>The landscape.</li>
                    <li>
                        <strong className="text-emphasis">Flood management practices.</strong>
                    </li>
                    <li>Local soil type.</li>
                    <li>River flow rates.</li>
                    <li>
                        <strong className="text-emphasis">Building in flood risk locations.</strong>
                    </li>
                    <li>Urban development and its impact on natural drainage.</li>
                </ul>

                <p>
                    Warmer and wetter winters are projected in the future, with increased potential for flooding. The UK
                    is expected to experience drier summers, although the rain that does fall is also likely to be more
                    intense, also impacting flood risk.
                </p>

                <p className="climate-hazard-emphasis">Where can I find localised flood data?</p>

                <p>
                    Future flood risk datasets are not yet comprehensive or standardised across the UK, however a future
                    flood risk dataset can be found for your local area here:
                </p>

                <ul>
                    <li>
                        England{" - "}
                        <a href="https://www.gov.uk/check-long-term-flood-risk" target="_blank" rel="noreferrer">
                            Long Term Flood Risk
                        </a>
                    </li>
                    <li>
                        Scotland{" - "}
                        <a
                            href="https://scottishepa.maps.arcgis.com/apps/webappviewer/index.html?id=3098bbef089c4dd79e5344a0e1e7c91c&showLayers=FloodMapsBasic_2743;FloodMapsBasic_2743_1;FloodMapsBasic_2743_2;FloodMapsBasic_2743_3;FloodMapsBasic_2743_5;FloodMapsBasic_2743_6;FloodMapsBasic_2743_7;FloodMapsBasic_2743_9;FloodMapsBasic_2743_10;FloodMapsBasic_2743_11;FloodMapsBasic_2743_12;FloodMapsBasic_2743_13;FloodMapsBasic_2743;FloodMapsBasic_2743_1;FloodMapsBasic_2743_2;FloodMapsBasic_2743_3;FloodMapsBasic_2743_5;FloodMapsBasic_2743_6;FloodMapsBasic_2743_7;FloodMapsBasic_2743_9;FloodMapsBasic_2743_10;FloodMapsBasic_2743_11;FloodMapsBasic_2743_12;FloodMapsBasic_2743_14"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Current and Future Flood Risk
                        </a>
                    </li>
                    <li>
                        Wales{" - "}
                        <a
                            href="https://flood-map-for-planning.naturalresources.wales/"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Basic and Detailed Future Flood Risk
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
    {
        name: "Coastal Erosion",
        icon: <CoastalErosionSvg className="hazard-img" />,
        details: (
            <div>
                <p>Coastal erosion is increasing across the UK due to several interacting issues:</p>

                <ul>
                    <li>
                        <strong className="text-emphasis"> Sea level rise.</strong>
                    </li>
                    <li>Increase storm activity and severity.</li>
                    <li>Heavier rainfall.</li>
                    <li>
                        <strong className="text-emphasis">Human activity</strong> such as alteration of natural coastal
                        environments due to urbanisation.
                    </li>
                </ul>

                <p>
                    Increased coastal erosion risks leads to the damage and loss of natural or built coastal
                    infrastructure and defences, further increasing the risk to people and the environment in those
                    areas from climate change impacts.
                </p>

                <p className="climate-hazard-emphasis">Where can I find localised coastal erosion data?</p>

                <p>
                    Future coastal erosion risk datasets are not yet comprehensive or standardised across the UK,
                    however a future coastal erosion risk dataset can be found for your local area here:
                </p>
                <ul>
                    <li>
                        England{" - "}
                        <a
                            href="https://environment.maps.arcgis.com/apps/webappviewer/index.html?id=9cef4a084bbb4954b970cd35b099d94c&marker=583422.9849116375%2C343036.013226925%2C27700%2C%2C%2C&markertemplate=%7B%22title%22%3A%22%22%2C%22x%22%3A583422.9849116375%2C%22y%22%3A343036.013226925%2C%22wkid%22%3A27700%2C%22isIncludeShareUrl%22%3Atrue%7D&level=14"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Future coastal erosion risk and shoreline management plans
                        </a>
                    </li>
                    <li>
                        Scotland{" - "}
                        <a
                            href="https://snh.maps.arcgis.com/apps/webappviewer/index.html?id=78047dbef80f4a74acc192ac21c9d4e0"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Present and future coastal erosion risk
                        </a>
                    </li>
                    <li>
                        Wales{" - "}
                        <a
                            href="https://flood-risk-maps.naturalresources.wales/?locale=en"
                            target="_blank"
                            rel="noreferrer"
                        >
                            Future coastal erosion risk and shoreline management plans
                        </a>
                    </li>
                </ul>
            </div>
        ),
    },
];
