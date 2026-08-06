import { Image, Text, View } from "@react-pdf/renderer";

import AirPollutionIcon from "../../../images/hazards/AirPollution.png";
import CoastalErosionIcon from "../../../images/hazards/CoastalErosion.png";
import FloodingIcon from "../../../images/hazards/Flood.png";
import HeatwaveIcon from "../../../images/hazards/Heatwave.png";
import WildfireIcon from "../../../images/hazards/Wildfires.png";
import { climateHazardsData } from "../../climateHazard/ClimateHazardData";
import { reportStyles as styles } from "../reportStyles";

const getHazardIcon = (hazardName) => {
    const iconMap = {
        Heatwaves: HeatwaveIcon,
        Wildfires: WildfireIcon,
        "Air Quality": AirPollutionIcon,
        Flooding: FloodingIcon,
        "Coastal Erosion": CoastalErosionIcon,
    };
    return iconMap[hazardName] || HeatwaveIcon;
};

const HazardsPDF = ({ applyCoastalFilter }) => {
    const filteredHazards = applyCoastalFilter
        ? climateHazardsData.filter((hazard) => hazard.name !== "Coastal Erosion")
        : climateHazardsData;
    return (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>Climate Hazard Risk</Text>
            <Text style={styles.bodyText}>Below is a summary of some of the key climate hazards for the UK.</Text>

            <View style={styles.climateContainer}>
                {filteredHazards.map((hazard, index) => {
                    const iconSrc = getHazardIcon(hazard.name);

                    return (
                        <View key={index} style={[styles.climateItem, { width: "19%", padding: 4 }]}>
                            <View style={styles.iconContainer}>
                                <Image src={iconSrc} style={styles.icon} />
                            </View>
                            <Text style={styles.climateVariable}>{hazard.name}</Text>
                        </View>
                    );
                })}
            </View>

            <Text style={styles.bodyText}>
                To access localised data on these risks, visit LCAT and click on each hazard.
            </Text>
        </View>
    );
};

export default HazardsPDF;
