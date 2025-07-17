import React from 'react';
import { Document, Page, StyleSheet, Text, View, Svg, Path, Circle, G, Image } from '@react-pdf/renderer';

import { climateVariables, formatClimateData } from '../../utils/climateUtils';

// SVG Components for PDF - recreated from the original SVG files
const TemperatureIcon = ({ style }) => (
    <Svg style={style} viewBox="0 0 30.858 30.858" width={40} height={40}>
        <G transform="translate(-2.052 -277.791)">
            <Circle
                cx={17.481}
                cy={293.22}
                r={15.429}
                fill="#115158"
                fillOpacity={1}
            />
            <G fill="#fff">
                <Path
                    d="M32 61.5a11.5 11.5 0 0 1-6.5-21V9a6.5 6.5 0 0 1 13 0v31.52a11.5 11.5 0 0 1-6.5 21zm0-56A3.5 3.5 0 0 0 28.5 9v33.21l-.75.44a8.5 8.5 0 1 0 8.5 0l-.75-.44V9A3.5 3.5 0 0 0 32 5.5Z"
                    fill="#fff"
                    transform="matrix(.40335 0 0 .40335 4.574 279.907)"
                />
                <Path
                    d="M35.5 43.94a3 3 0 0 1-1.5-2.59V18h-4v23.35a3 3 0 0 1-1.5 2.59 7 7 0 1 0 7 0z"
                    fill="#fff"
                    transform="matrix(.40335 0 0 .40335 4.574 279.907)"
                />
            </G>
        </G>
    </Svg>
);

const RainIcon = ({ style }) => (
    <Svg style={style} viewBox="0 0 30.858 30.858" width={40} height={40}>
        <G transform="translate(-159.86 -43.52)">
            <Circle
                cx={175.29}
                cy={58.949}
                r={15.429}
                fill="#115158"
                fillOpacity={1}
            />
            <G fill="#fff">
                <Path
                    d="M45.488 18.014C43.702 11.038 37.371 6 30 6c-8.822 0-16 7.178-16 16-4.411 0-8 3.589-8 8s3.589 8 8 8h32c5.514 0 10-4.486 10-10 0-5.684-4.787-10.301-10.512-9.986ZM46 34H14c-2.206 0-4-1.794-4-4s1.794-4 4-4c.506 0 1.005.097 1.482.288a1.998 1.998 0 0 0 2.712-2.202A12.006 12.006 0 0 1 18 22c0-6.617 5.383-12 12-12 6.052 0 11.168 4.528 11.9 10.534a2.002 2.002 0 0 0 2.513 1.687C48.37 21.139 52 24.174 52 28c0 3.309-2.691 6-6 6zM32 42a2 2 0 0 0-2 2v10a2 2 0 0 0 4 0V44a2 2 0 0 0-2-2zM24 42a2 2 0 0 0-2 2v10a2 2 0 0 0 4 0V44a2 2 0 0 0-2-2zM16 42a2 2 0 0 0-2 2v10a2 2 0 0 0 4 0V44a2 2 0 0 0-2-2zM40 42a2 2 0 0 0-2 2v10a2 2 0 0 0 4 0V44a2 2 0 0 0-2-2zM48 42a2 2 0 0 0-2 2v10a2 2 0 0 0 4 0V44a2 2 0 0 0-2-2z"
                    fill="#fff"
                    transform="matrix(.38638 0 0 .38638 163.24 46.512)"
                />
            </G>
        </G>
    </Svg>
);

const CloudIcon = ({ style }) => (
    <Svg style={style} viewBox="0 0 30.858 30.858" width={40} height={40}>
        <Circle
            cx={15.429}
            cy={15.429}
            r={15.429}
            fill="#115158"
            fillOpacity={1}
        />
        <Path
            d="M24.424 11.837h-.043a3.465 3.465 0 0 0-4.5-2.437 3.925 3.925 0 0 0-3.499-2.11 3.934 3.934 0 0 0-3.935 3.808c-.809-.536-1.962-.77-3.115-.554-1.522.285-3.147 1.461-3.147 3.907 0 .216.017.431.052.642-1.786.172-3.187 1.674-3.187 3.495 0 1.937 1.583 3.513 3.53 3.513h11.587a3.525 3.525 0 0 0 3.516-3.24h2.741c1.946 0 3.53-1.575 3.53-3.512s-1.584-3.512-3.53-3.512zm-6.257 9.037H6.579a2.294 2.294 0 0 1-2.297-2.286c0-1.26 1.03-2.285 2.297-2.285h.463a.617.617 0 0 0 .51-.27.61.61 0 0 0 .061-.573 2.67 2.67 0 0 1-.196-1.01c0-2.075 1.499-2.58 2.143-2.7.753-.142 1.546-.009 2.088.295a3.516 3.516 0 0 0-2.342 3.304c0 1.937 1.584 3.512 3.53 3.512h7.61a2.295 2.295 0 0 1-2.28 2.013zm6.257-3.24H12.836a2.293 2.293 0 0 1-2.296-2.285c0-1.26 1.03-2.285 2.296-2.285h.463a.617.617 0 0 0 .511-.27.61.61 0 0 0 .06-.573 2.67 2.67 0 0 1-.196-1.01 2.705 2.705 0 0 1 2.709-2.695c1.192 0 2.231.76 2.586 1.892a.615.615 0 0 0 .907.343 2.224 2.224 0 0 1 3.363 1.742.615.615 0 0 0 .615.57h.57a2.293 2.293 0 0 1 2.297 2.286c0 1.26-1.03 2.286-2.297 2.286z"
            fill="#fff"
        />
    </Svg>
);

const WindIcon = ({ style }) => (
    <Svg style={style} viewBox="0 0 30.858 30.858" width={40} height={40}>
        <G transform="translate(-146.345 -130.38)">
            <Circle
                cx={161.774}
                cy={145.81}
                r={15.429}
                fill="#115158"
                fillOpacity={1}
            />
            <G fill="#fff">
                <Path
                    d="M42 24c6.627 0 12-5.373 12-12S48.627 0 42 0 30 5.373 30 12a2 2 0 1 0 4 0 8 8 0 1 1 8 8H4a2 2 0 1 0 0 4z"
                    fill="#fff"
                    transform="matrix(.36048 0 0 .36048 151.23 138.183)"
                />
                <Path
                    d="M20 17a7 7 0 1 0-6.441-9.744 2 2 0 0 0 3.68 1.57A3.001 3.001 0 1 1 20 13H2a2 2 0 0 0 0 4zM38 31a6 6 0 1 1-6 6 2 2 0 0 0-4 0c0 5.523 4.477 10 10 10s10-4.477 10-10-4.477-10-10-10H7a2 2 0 1 0 0 4z"
                    fill="#fff"
                    transform="matrix(.36048 0 0 .36048 151.23 138.183)"
                />
            </G>
        </G>
    </Svg>
);

const IncreaseArrow = ({ style }) => (
    <Svg style={style} viewBox="0 0 7.938 5.292" width={15} height={12}>
        <Path
            d="m27.781 45.646-3.968 5.292h7.937Z"
            fill="#f5821f"
            fillOpacity={0.94117647}
            transform="translate(-23.813 -45.646)"
        />
    </Svg>
);

const DecreaseArrow = ({ style }) => (
    <Svg style={style} viewBox="0 0 7.938 5.292" width={15} height={12}>
        <Path
            d="m27.781 50.938-3.968-5.292h7.937Z"
            fill="#f5821f"
            fillOpacity={0.94117647}
            transform="translate(-23.813 -45.646)"
        />
    </Svg>
);

const getClimateIcon = (variable) => {
    const iconMap = {
        'tas': TemperatureIcon,
        'pr': RainIcon,
        'rsds': CloudIcon,
        'sfcWind': WindIcon,
    };
    return iconMap[variable] || TemperatureIcon;
};

const getArrowComponent = (arrow) => {
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
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 30,
        paddingBottom: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#ddd',
    },
    logoContainer: {
        alignItems: 'center',
    },
    logo: {
        width: 200,
        height: 60,
        marginBottom: 10,
    },
    logoText: {
        fontSize: 36,
        fontWeight: 'bold',
        color: '#005157',
        textAlign: 'center',
        letterSpacing: 2,
    },
    logoSubtext: {
        fontSize: 14,
        color: '#666',
        textAlign: 'center',
    },
    title: {
        fontSize: 24,
        marginBottom: 20,
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
        marginBottom: 4,
    },
    arrow: {
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
});

// Climate Summary Component for PDF
const ClimateSummaryPDF = ({ climatePrediction, year = 2050 }) => {
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
            <Text style={styles.subtitle}>Climate Summary (Projected for {year})</Text>
            
            {/* Visual climate summary matching the web version */}
            <View style={styles.climateContainer}>
                {climateVariables.map((item, index) => {
                    const climateData = formatClimateData(climatePrediction, item.variable, item.name, item.units, year);
                    const IconComponent = getClimateIcon(item.variable);
                    const ArrowComponent = getArrowComponent(climateData.arrow);
                    
                    return (
                        <View key={index} style={styles.climateItem}>
                            <View style={styles.iconContainer}>
                                {ArrowComponent && (
                                    <ArrowComponent style={styles.arrow} />
                                )}
                                <IconComponent style={styles.icon} />
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
                    const climateData = formatClimateData(climatePrediction, item.variable, item.name, item.units, year);
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
const ClimateReport = ({ regions = [], climatePrediction = null, selectedHazardName = null, year = 2050 }) => {
    return (
        <Document>
            <Page size="A4" style={styles.page}>
                {/* Header with simple text logo */}
                <View style={styles.header}>
                    <View style={styles.logoContainer}>
                        <Text style={styles.logoText}>LCAT</Text>
                        <Text style={styles.logoSubtext}>Local Climate Adaptation Tool</Text>
                    </View>
                </View>

                <View style={styles.section}>
                    <Text style={styles.title}>Climate Risk Assessment Report</Text>
                    
                    {regions && regions.length > 0 && (
                        <>
                            <Text style={styles.subtitle}>Selected Regions</Text>
                            <Text style={styles.text}>
                                {regions.map(region => region.name).join(', ')}
                            </Text>
                        </>
                    )}
                    
                    <Text style={styles.subtitle}>Executive Summary</Text>
                    <Text style={styles.text}>
                        This report provides an analysis of climate risks and adaptation strategies 
                        for the selected regions based on the LCAT (Local Climate Adaptation Tool) assessment.
                    </Text>
                </View>
            </Page>
            
            <Page size="A4" style={styles.page}>
                <ClimateSummaryPDF 
                    climatePrediction={climatePrediction} 
                    year={year} 
                />
                
                <View style={styles.section}>
                    <Text style={styles.subtitle}>Climate Projections Methodology</Text>
                    <Text style={styles.text}>
                        The climate projections are based on ensemble climate models and represent 
                        the change from the 1980 baseline period to the projected future period ({year}).
                    </Text>

                    <Text style={styles.subtitle}>Risk Assessment</Text>
                    <Text style={styles.text}>
                        Climate hazards have been evaluated for their potential impact on various 
                        sectors including agriculture, infrastructure, and public health.
                    </Text>

                    {selectedHazardName && (
                        <>
                            <Text style={styles.subtitle}>Primary Climate Hazard</Text>
                            <Text style={styles.text}>
                                Focus area: {selectedHazardName}
                            </Text>
                        </>
                    )}

                    <Text style={styles.subtitle}>Adaptation Recommendations</Text>
                    <Text style={styles.text}>
                        Based on the risk assessment, specific adaptation measures have been 
                        identified to reduce vulnerability and enhance resilience.
                    </Text>

                    <Text style={styles.text}>
                        Generated on: {new Date().toLocaleDateString()}
                    </Text>
                </View>
            </Page>
        </Document>
    );
};

export default ClimateReport;