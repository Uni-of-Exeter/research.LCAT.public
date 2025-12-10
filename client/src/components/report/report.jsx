import { Document, Page } from '@react-pdf/renderer';

import AdaptationsPDF from './pages/Adaptations';
import ClimateSummaryPDF from './pages/ClimateSummary';
import HazardsPDF from './pages/Hazards';
import ImpactsPDF from './pages/Impacts';
import IntroPDF from './pages/Intro';
import VulnerabilityPDF from './pages/Vulnerability';
import { reportStyles as styles } from './reportStyles';

const ClimateReport = ({ regions, climatePrediction, selectedImpactHazard, selectedAdaptationHazards, filterName, rcp, season, applyCoastalFilter, selectedPages = ['climate'] }) => {
    const shouldIncludePage = (pageId) => selectedPages.includes(pageId);

    return (
        <Document>
            <IntroPDF
                regions={regions}
                selectedPages={selectedPages}
            />

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

            {shouldIncludePage('hazards') && selectedImpactHazard && (
                <Page size="A4" style={styles.page}>
                    <HazardsPDF
                        applyCoastalFilter={applyCoastalFilter} />
                </Page>
            )}

            {(shouldIncludePage('health-impacts') || shouldIncludePage('community-impacts')) && selectedImpactHazard && (
                <Page size="A4" style={styles.page}>
                    <ImpactsPDF
                        selectedImpactHazard={selectedImpactHazard}
                        includeHealthImpacts={shouldIncludePage('health-impacts')}
                        includeCommunityImpacts={shouldIncludePage('community-impacts')}
                    />
                </Page>
            )}

            {shouldIncludePage('vulnerability') && regions && regions.length > 0 && (
                <Page size="A4" style={styles.page}>
                    <VulnerabilityPDF />
                </Page>
            )}

            {shouldIncludePage('adaptations') && (
                <Page size="A4" style={styles.page}>
                    <AdaptationsPDF
                        selectedAdaptationHazards={selectedAdaptationHazards}
                        filterName={filterName}
                    />
                </Page>
            )}
        </Document>
    );
};

export default ClimateReport;