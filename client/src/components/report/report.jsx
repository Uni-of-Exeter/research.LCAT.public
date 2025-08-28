import { Document, Image,Link,Page, Text, View } from '@react-pdf/renderer';

import DecreaseArrow from '../../images/buttons/decrease.png';
import IncreaseArrow from '../../images/buttons/increase.png';
import CloudIcon from '../../images/climate/Cloud Cover.png';
import RainIcon from '../../images/climate/Rain.png';
import TemperatureIcon from '../../images/climate/Temperature.png';
import WindIcon from '../../images/climate/Wind Speed.png';
import AirPollutionIcon from '../../images/hazards/Air Pollution.png';
import CoastalErosionIcon from '../../images/hazards/Coastal Erosion.png';
import FloodingIcon from '../../images/hazards/Flood.png';
import HeatwaveIcon from '../../images/hazards/Heatwave.png';
import WildfireIcon from '../../images/hazards/Wildfires.png';
import LCATLogo from '../../images/logos/LCAT_Logo_Primary_RGB.png';
import { climateVariables, formatClimateData } from '../../utils/climateUtils';
import { andify } from "../../utils/utils";
import { climateHazardsData } from '../climateHazard/ClimateHazardData';
import { reportStyles as styles } from './reportStyles';


const getClimateIcon = (variable) => {
    const iconMap = {
        'tas': TemperatureIcon,
        'pr': RainIcon,
        'rsds': CloudIcon,
        'sfcWind': WindIcon,
    };
    return iconMap[variable] || TemperatureIcon;
};

const getArrowIcon = (arrow) => {
    switch(arrow) {
        case 'up': return IncreaseArrow;
        case 'down': return DecreaseArrow;
        case 'none': return null;
        default: return null;
    }
};

const getHazardIcon = (hazardName) => {
    const iconMap = {
        'Heatwaves': HeatwaveIcon,
        'Wildfires': WildfireIcon,
        'Air Quality': AirPollutionIcon,
        'Flooding': FloodingIcon,
        'Coastal Erosion': CoastalErosionIcon,
    };
    return iconMap[hazardName] || HeatwaveIcon;
};

// Climate Summary Component for PDF
const ClimateSummaryPDF = ({ climatePrediction, regions, rcp, season }) => {
    if (!climatePrediction || climatePrediction.length === 0) {
        return (
            <View style={styles.section}>
                <Text style={styles.subtitle}>Climate Summary</Text>
                <Text style={styles.text}>No climate data available for this region.</Text>
            </View>
        );
    }

    return (
        <View style={styles.section}>
            <Text style={styles.subtitle}>EXPLORE YOUR LOCAL CLIMATE</Text>
            {regions && regions.length > 0 && rcp && season && (
                <>
                    <Text style={styles.text}>
                        For {andify(regions.map(region => region.name))} under the 
                        {rcp === 'rcp60' ? ' existing global policies ' : ' worst case scenario '} 
                        (equivalent to global warming level of {rcp === 'rcp60' ? '2.0-3.7C which is RCP 6.0' : '3.2-5.4C which is RCP 8.5'}) 
                        the {season} average climate change for 2070 compared with local records for the 1980s is expected to be:
                    </Text>
                </>
            )}

            <View style={styles.climateContainer}>
                {climateVariables.map((item, index) => {
                    const climateData = formatClimateData(climatePrediction, item.variable, item.name, item.units, 2070);
                    const iconSrc = getClimateIcon(item.variable);
                    const arrowSrc = getArrowIcon(climateData.arrow);
                    
                    return (
                        <View key={index} style={styles.climateItem}>
                            <View style={styles.iconContainer}>
                                {arrowSrc && (
                                    <Image src={arrowSrc} style={styles.arrow} />
                                )}
                                <Image src={iconSrc} style={styles.icon} />
                            </View>
                            <Text style={styles.climateVariable}>{item.name}</Text>
                            <Text style={styles.climateValue}>{climateData.change}</Text>
                        </View>
                    );
                })}
            </View>
            
            <Text style={styles.text}>
                Note: Yearly average climate change does not always reflect the extremes of summer and winter.
            </Text>
        </View>
    );
};

const ClimateHazardsPDF = ({applyCoastalFilter}) => {
    const filteredHazards = applyCoastalFilter 
        ? climateHazardsData.filter((hazard) => hazard.name !== "Coastal Erosion")
        : climateHazardsData;
    return (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>Climate Hazard Risk</Text>
            <Text style={styles.bodyText}>
                Below is a summary of some of the key climate hazards for the UK.  
            </Text>

            <View style={styles.climateContainer}>
                {filteredHazards.map((hazard, index) => {
                    const iconSrc = getHazardIcon(hazard.name);
                    
                    return (
                        <View key={index} style={styles.climateItem}>
                            <View style={styles.iconContainer}>
                                <Image src={iconSrc} style={styles.icon} />
                            </View>
                            <Text style={styles.climateVariable}>{hazard.name}</Text>
                        </View>
                    );
                })}
            </View>
            
            <Text style={styles.text}>
                To access localised data on these risks, visit LCAT and click on each hazard.              
            </Text>
        </View>
    )};

    const ClimateReport = ({ regions, climatePrediction, selectedHazardName, rcp, season, applyCoastalFilter, selectedPages = ['climate'] }) => {
    const shouldIncludePage = (pageId) => selectedPages.includes(pageId);

    return (
        <Document>
            <Page size="A4" style={styles.page}>
                {/* Header with text logo and PNG logo */}
                <View style={styles.header}>
                    <View style={styles.headerLeft}>
                        {regions && regions.length > 0 && (
                            <>
                                <Text style={styles.title}>
                                    Summary Report for {andify(regions.map(region => region.name))}
                                </Text>
                            </>
                        )}
                    </View>
                    <View style={styles.headerRight}>
                        <Image src={LCATLogo} style={styles.logo} />
                    </View>
                </View>

                <View style={styles.section}>                    
                    <Text style={styles.intro}>
                        The Local Climate Adaptation Tool (LCAT) offers you data and evidence to understand and plan for current and future climate impacts. 
                        This includes how local climates will change, likely UK hazards, community and health impacts, who is vulnerable and what adaptations to consider. 
                        LCAT is evidence-based and designed with and for local decision makers.
                    </Text>
                    <Text style={styles.text}>
                        Benefits of adaptation include:
                    </Text>
                    <View style={styles.bulletList}>
                        {[
                            'Making communities stronger in the face of change',
                            'Making the places we live more resilient, healthier, safer and greener',
                            'Strengthening our systems and services & reducing damage',
                            'Saving money by investing in adapting now'
                        ].map((benefit, index) => (
                            <Text key={index} style={styles.bulletItem}>
                                • {benefit}
                            </Text>
                        ))}
                    </View>
                    <Text style={styles.text}>
                        The following information was taken from LCAT on {new Date().toLocaleDateString()} and is a summary based on your unique search selection. <Link src="https://lcat.uk/">Visit LCAT</Link> for more information, including for different locations, impacts or adaptation topic areas.  
                    </Text>
                </View>
                {/* Summary of selected pages */}
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Report Contents</Text>
                    {selectedPages.map(pageId => (
                        <Text key={pageId} style={styles.contentItem}>
                            • {getPageTitle(pageId)}
                        </Text>
                    ))}
                </View>
            </Page>

            {/* Conditionally include pages based on selection */}
            {shouldIncludePage('climate') && (
                <Page size="A4" style={styles.page}>
                    <ClimateSummaryPDF 
                        climatePrediction={climatePrediction} 
                        regions={regions}
                        rcp={rcp}
                        season={season}
                    />
                </Page>
            )}

            {shouldIncludePage('hazards') && selectedHazardName && (
                <Page size="A4" style={styles.page}>
                    <ClimateHazardsPDF 
                        applyCoastalFilter={applyCoastalFilter}/>
                </Page>
            )}

            {shouldIncludePage('adaptations') && (
                <Page size="A4" style={styles.page}>
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Adaptation Options</Text>
                        <Text style={styles.bodyText}>
                            Recommended adaptation strategies and actions.
                        </Text>
                        {/* Add your adaptations content here */}
                    </View>
                </Page>
            )}

            {shouldIncludePage('vulnerability') && regions && regions.length > 0 && (
                <Page size="A4" style={styles.page}>
                    <View style={styles.section}>
                        <Text style={styles.sectionTitle}>Vulnerability Assessment</Text>
                        <Text style={styles.bodyText}>
                            Community vulnerability factors for {regions.map(r => r.name).join(", ")}
                        </Text>
                        {/* Add your vulnerability content here */}
                    </View>
                </Page>
            )}
        </Document>
    );
};

// Add helper function to get page titles
const getPageTitle = (pageId) => {
    const titles = {
        'climate': 'Climate Summary',
        'hazards': 'Climate Hazards',
        'adaptations': 'Adaptation Options',
        'vulnerability': 'Vulnerability Assessment'
    };
    return titles[pageId] || pageId;
};

export default ClimateReport;