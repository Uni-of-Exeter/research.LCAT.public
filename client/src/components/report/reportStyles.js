import { StyleSheet } from '@react-pdf/renderer';

// React PDF cannot use regular CSS, so we define styles here
export const reportStyles = StyleSheet.create({
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
        margin: 5,
        padding: 5,
        flexGrow: 1,
    },
    contentItem: {
        fontSize: 12,
        marginBottom: 4,
        color: '#333',
    },
    twoColumnList: {
        flexDirection: 'row',
        width: '70%',
    },
    column: {
        width: '50%',
    },
    contentItemColumn: {
        fontSize: 12,
        marginBottom: 4,
        color: '#333',
    },
    headerText: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
    },
    subHeaderText: {
        fontSize: 16,
        color: '#666',
        marginBottom: 8,
    },
    dateText: {
        fontSize: 12,
        color: '#888',
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 12,
        color: '#333',
    },
    bodyText: {
        fontSize: 12,
        lineHeight: 1.5,
        color: '#333',
    },
    italic: {
        fontStyle: 'italic',
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
        justifyContent: 'space-around',
        flexWrap: 'wrap',
        marginBottom: 20,
        padding: 10,
        border: '1px solid #ddd',
        borderRadius: 8,
        backgroundColor: '#f9f9f9',
        gap: 2,
    },
    climateItem: {
        alignItems: 'center',
        padding: 2,
        backgroundColor: '#ffffff',
        borderRadius: 8,
        border: '1px solid #e0e0e0',
        marginBottom: 2,
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
    footer: {
        marginTop: 'auto',
        padding: '10pt',
        borderTop: '1pt solid #f0f0f0',
        backgroundColor: '#f7f7f7',
        },
    footerText: {
        fontSize: 8,
        marginBottom: 8,
        color: '#444444',
        textAlign: 'center',
        },
    footerLogosContainer: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginTop: 5,
        marginBottom: 5,
        },
    footerPartnerLogos: {
        width: 300,
        marginBottom: 10,
        },
    footerFunderLogos: {
        width: 300,
        },
    logoBlock: {
        marginBottom: 10,
        alignItems: 'center',
        },
});
