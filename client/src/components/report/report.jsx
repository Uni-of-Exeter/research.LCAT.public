import { Circle, Document, G, Image,Link,Page, Path, StyleSheet, Svg, Text, View } from '@react-pdf/renderer';
import React from 'react';

import DecreaseArrow from '../../images/buttons/decrease.png';
import IncreaseArrow from '../../images/buttons/increase.png';
import CloudIcon from '../../images/climate/Cloud Cover.png';
import RainIcon from '../../images/climate/Rain.png';
import TemperatureIcon from '../../images/climate/Temperature.png';
import WindIcon from '../../images/climate/Wind Speed.png';
import LCATLogo from '../../images/logos/LCAT_Logo_Primary_RGB.png';
import { climateVariables, formatClimateData } from '../../utils/climateUtils';
import { andify } from "../../utils/utils";


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

// PDF styles
const styles = StyleSheet.create({
    page: {
        flexDirection: 'column',
        backgroundColor: '#ffffff',
        padding: 30,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
        paddingBottom: 10,
        borderBottomWidth: 1,
        borderBottomColor: '#ddd',
    },
    headerLeft: {
        flex: 1,
        paddingRight: 10,
    },
    headerRight: {
        alignItems: 'flex-end',
    },
    logoContainer: {
        alignItems: 'flex-start',
    },
    logo: {
        width: 120,
        height: 120,
    },
    title: {
        fontSize: 22,
        marginBottom: 10,
        textAlign: 'center',
        fontWeight: 'bold',
    },
    section: {
        margin: 10,
        padding: 10,
        flexGrow: 1,
    },
    text: {
        fontSize: 12,
        lineHeight: 1.5,
    },
    intro: {
        fontSize: 12,
        marginBottom: 10,
        fontWeight: 'bold',
    },
    subtitle: {
        fontSize: 16,
        marginBottom: 10,
        fontWeight: 'bold',
    },
    climateContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 20,
        padding: 15,
        border: '1px solid #ddd',
        borderRadius: 8,
        backgroundColor: '#f9f9f9',
    },
    climateItem: {
        alignItems: 'center',
        width: '23%',
        padding: 10,
        backgroundColor: '#ffffff',
        borderRadius: 8,
        border: '1px solid #e0e0e0',
    },
    climateVariable: {
        fontSize: 14,
        fontWeight: 'bold',
        marginBottom: 8,
        textAlign: 'center',
        color: '#333333',
    },
    climateValue: {
        fontSize: 11,
        textAlign: 'center',
        lineHeight: 1.4,
        color: '#666666',
    },
    iconContainer: {
        alignItems: 'center',
        marginBottom: 8,
        flexDirection: 'column',
    },
    icon: {
        width: 40,
        height: 40,
        marginBottom: 4,
    },
    arrow: {
        width: 15,
        height: 12,
        marginBottom: 4,
    },
    table: {
        display: 'table',
        width: '100%',
        borderStyle: 'solid',
        borderWidth: 1,
        borderColor: '#ddd',
        marginBottom: 10,
    },
    tableRow: {
        flexDirection: 'row',
        borderBottomWidth: 1,
        borderBottomColor: '#ddd',
    },
    tableCell: {
        width: '50%',
        padding: 5,
        fontSize: 11,
    },
    tableHeader: {
        backgroundColor: '#f5f5f5',
        fontWeight: 'bold',
    },
    bulletList: {
        marginLeft: 10,
        marginTop: 5,
        marginBottom: 15,
    },
    bulletItem: {
        fontSize: 12,
        lineHeight: 1.5,
        marginBottom: 3,
    },
});

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

            {/* Detailed table for additional information */}
            <View style={styles.table}>
                <View style={[styles.tableRow, styles.tableHeader]}>
                    <Text style={styles.tableCell}>Climate Variable</Text>
                    <Text style={styles.tableCell}>Projected Change</Text>
                </View>
                {climateVariables.map((item, index) => {
                    const climateData = formatClimateData(climatePrediction, item.variable, item.name, item.units, 2070);
                    return (
                        <View key={index} style={styles.tableRow}>
                            <Text style={styles.tableCell}>{item.name}</Text>
                            <Text style={styles.tableCell}>{climateData.change}</Text>
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

// PDF Document component (no hooks allowed)
const ClimateReport = ({ regions = [], climatePrediction = null, selectedHazardName = null, rcp, season }) => {
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
                        The following information was taken from LCAT on {new Date().toLocaleDateString()} 
                        and is a summary based on your unique search selection. <Link src="https://lcat.uk/">Visit LCAT</Link> 
                        for more information, including for different locations, impacts or adaptation topic areas.  
                    </Text>
                </View>
            </Page>
            
            <Page size="A4" style={styles.page}>
                <ClimateSummaryPDF 
                    climatePrediction={climatePrediction} 
                    regions={regions}
                    rcp={rcp}
                    season={season}
                />
            </Page>
        </Document>
    );
};

export default ClimateReport;