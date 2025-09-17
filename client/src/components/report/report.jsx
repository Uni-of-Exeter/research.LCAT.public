import { Document, Image, Link, Page, Text, View } from '@react-pdf/renderer';

import LCATLogo from '../../images/logos/LCAT_Logo_Primary_RGB.png';
import FooterLogos from '../../images/logos/new-footer-logos.png';
import FunderLogos from '../../images/logos/new-funder-logos.png';
import { andify } from "../../utils/utils";
import AdaptationsPDF from './pages/Adaptations';
import ClimateSummaryPDF from './pages/ClimateSummary';
import HazardsPDF from './pages/Hazards';
import ImpactsPDF from './pages/Impacts';
import VulnerabilityPDF from './pages/Vulnerability';
import { reportStyles as styles } from './reportStyles';


const ReportFooter = () => {
    return (
        <View style={styles.footer} wrap={false}>
            <Text style={styles.footerText}>
                Please note that LCAT is updated regularly. The information contained in this summary was correct as of the date you downloaded the document. We suggest returning to the website for the most up to date information and data. If you would like to understand the sources for any of this summary, please visit the LCAT website. To reference this report, please reference University of Exeter and the date you downloaded the report.
            </Text>

            <View style={styles.footerLogosContainer}>
                <View style={styles.logoBlock}>
                    <Image
                        src={FooterLogos}
                        style={styles.footerPartnerLogos}
                    />
                </View>
                <View style={styles.logoBlock}>
                    <Image
                        src={FunderLogos}
                        style={styles.footerFunderLogos}
                    />
                </View>
            </View>
        </View>
    );
};

const ClimateReport = ({ regions, climatePrediction, selectedImpactHazard, selectedAdaptationHazards, filterName, rcp, season, applyCoastalFilter, selectedPages = ['climate'] }) => {
    const shouldIncludePage = (pageId) => selectedPages.includes(pageId);

    // Determine which is the last page to include the footer
    let lastPage = 'climate'; // Default

    if (shouldIncludePage('adaptations')) {
        lastPage = 'adaptations';
    } else if (shouldIncludePage('vulnerability') && regions && regions.length > 0) {
        lastPage = 'vulnerability';
    } else if ((shouldIncludePage('health-impacts') || shouldIncludePage('community-impacts')) && selectedImpactHazard) {
        lastPage = 'impacts';
    } else if (shouldIncludePage('hazards') && selectedImpactHazard) {
        lastPage = 'hazards';
    }

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
                    <Text style={styles.bodyText}>
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
                    <Text style={styles.bodyText}>
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
                    {lastPage === 'climate' && <ReportFooter />}
                </Page>
            )}

            {shouldIncludePage('hazards') && selectedImpactHazard && (
                <Page size="A4" style={styles.page}>
                    <HazardsPDF
                        applyCoastalFilter={applyCoastalFilter} />
                    {lastPage === 'hazards' && <ReportFooter />}
                </Page>
            )}

            {(shouldIncludePage('health-impacts') || shouldIncludePage('community-impacts')) && selectedImpactHazard && (
                <Page size="A4" style={styles.page}>
                    <ImpactsPDF
                        selectedImpactHazard={selectedImpactHazard}
                        includeHealthImpacts={shouldIncludePage('health-impacts')}
                        includeCommunityImpacts={shouldIncludePage('community-impacts')}
                    />
                    {lastPage === 'impacts' && <ReportFooter />}
                </Page>
            )}

            {shouldIncludePage('vulnerability') && regions && regions.length > 0 && (
                <Page size="A4" style={styles.page}>
                    <VulnerabilityPDF />
                    {lastPage === 'vulnerability' && <ReportFooter />}
                </Page>
            )}

            {shouldIncludePage('adaptations') && (
                <Page size="A4" style={styles.page}>
                    <AdaptationsPDF
                        selectedAdaptationHazards={selectedAdaptationHazards}
                        filterName={filterName}
                    />
                    {lastPage === 'adaptations' && <ReportFooter />}
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
        'health-impacts': 'Health Impacts',
        'community-impacts': 'Community Impacts',
        'adaptations': 'Adaptations',
        'vulnerability': 'Vulnerability Assessment'
    };
    return titles[pageId] || pageId;
};

export default ClimateReport;