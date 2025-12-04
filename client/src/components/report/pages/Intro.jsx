import { Image, Link, Page, Text, View } from '@react-pdf/renderer';

import LCATLogo from '../../../images/logos/LCAT_Logo_Primary_RGB.png';
import FooterLogos from '../../../images/logos/new-footer-logos.png';
import FunderLogos from '../../../images/logos/new-funder-logos.png';
import { andify } from "../../../utils/utils";
import { reportStyles as styles } from '../reportStyles';

// Helper function to get page titles
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

const IntroPDF = ({ regions, selectedPages }) => {
    return (
        <Page size="A4" style={styles.page}>
            {/* Header with logo */}
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
                <Text style={styles.bodyText}>
                    To reference this report, please cite <Text style={styles.italic}>&quot;University of Exeter ({new Date().getFullYear()}) Local Climate Adaptation Tool, available from lcat.uk. Accessed on {new Date().toLocaleDateString()}.&quot;</Text>
                </Text>
            </View>
            {/* Summary of selected pages */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Report Contents</Text>
                <View style={styles.twoColumnList}>
                    <View style={styles.column}>
                        {selectedPages.slice(0, Math.min(3, selectedPages.length)).map(pageId => (
                            <Text key={pageId} style={styles.contentItemColumn}>
                                • {getPageTitle(pageId)}
                            </Text>
                        ))}
                    </View>
                    {selectedPages.length > 3 && (
                        <View style={styles.column}>
                            {selectedPages.slice(3).map(pageId => (
                                <Text key={pageId} style={styles.contentItemColumn}>
                                    • {getPageTitle(pageId)}
                                </Text>
                            ))}
                        </View>
                    )}
                </View>
            </View>
            {/* Footer with logos and disclaimer */}
            <View style={styles.footer} wrap={false}>
                <Text style={styles.footerText}>
                    Please note that LCAT is updated regularly. The information contained in this summary was correct as of the date you downloaded the document. We suggest returning to the website for the most up to date information and data. If you would like to understand the sources for any of this summary, please visit the LCAT website.
                    {'\n\n'}
                    The LCAT project team and their agents, take no responsibility for decisions taken as a result of the use of this tool. While every effort has been made to ensure data represented in the tool are accurate, no liability is accepted for any inaccuracies in the dataset or for any actions taken based on the use of this tool. The views expressed in this tool do not reflect the views of the organisations or the funding bodies. There is no guarantee that the tool will be updated to reflect changes in the source information.
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
        </Page>
    );
}

export default IntroPDF;