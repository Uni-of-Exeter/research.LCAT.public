import React from 'react';
import { Document, Page, StyleSheet, Text, View, Image } from '@react-pdf/renderer';
import { climateVariables, formatClimateData } from '../../utils/climateUtils';

// PDF styles
const styles = StyleSheet.create({
    page: {
        flexDirection: 'column',
        backgroundColor: '#ffffff',
        padding: 30,
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
    imageContainer: {
        alignItems: 'center',
        marginBottom: 20,
    },
    climateSummaryImage: {
        maxWidth: '100%',
        maxHeight: 300,
    },
});

// Climate Summary Component for PDF
const ClimateSummaryPDF = ({ climatePrediction, year = 2050, climateSummaryImage }) => {
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
            
            {/* Use captured image if available, otherwise fallback to table */}
            {climateSummaryImage ? (
                <View style={styles.imageContainer}>
                    <Image 
                        src={climateSummaryImage} 
                        style={styles.climateSummaryImage}
                    />
                </View>
            ) : (
                <View style={styles.climateContainer}>
                    <Text style={styles.text}>
                        Climate summary visualization not available. See table below for details.
                    </Text>
                </View>
            )}

            {/* Always include the detailed table */}
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

// PDF Document component
const ClimateReport = ({ regions = [], climatePrediction = null, selectedHazardName = null, year = 2050, climateSummaryImage = null }) => (
    <Document>
        <Page size="A4" style={styles.page}>
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
                climateSummaryImage={climateSummaryImage}
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

export default ClimateReport;