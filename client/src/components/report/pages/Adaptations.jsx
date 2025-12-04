import { Link, Text, View } from '@react-pdf/renderer';

import adaptationData from '../../../kumu/parsed/adaptation_data.json';
import { ADAPTATION_INTRO_PDF_URL } from '../../../utils/constants';
import { adaptationFilters, defaultFilterName } from '../../adaptations/AdaptationCategories';
import { reportStyles as styles } from '../reportStyles';

const AdaptationsPDF = ({ selectedAdaptationHazards, filterName }) => {
    const hazardText = selectedAdaptationHazards && selectedAdaptationHazards.length > 0
        ? selectedAdaptationHazards.join(", ")
        : "no specific hazards";

    const isDefaultFilter = filterName === defaultFilterName;

    // Find the filter category for the current filterName
    const selectedFilter = adaptationFilters.find(filter => filter.filterName === filterName);
    const filterCategory = selectedFilter ? selectedFilter.category : adaptationFilters[0].category;

    // Filter adaptations
    const filteredAdaptations = adaptationData.filter((adaptation) => {
        const layers = adaptation.attributes.layer.map((layer) => layer.toLowerCase());
        const adaptationCategories = adaptation.attributes[filterCategory] || [];

        // If no hazards are selected, show all adaptations (just apply category filter)
        if (!selectedAdaptationHazards || selectedAdaptationHazards.length === 0) {
            if (filterName === defaultFilterName) {
                return true; // Show all adaptations
            } else {
                return adaptationCategories.includes(filterName); // Filter by category only
            }
        }

        // If hazards are selected, filter by both hazards and category
        const matchesAllHazards = selectedAdaptationHazards.every((hazard) =>
            layers.some((layer) => layer.includes(hazard.toLowerCase() + " in full"))
        );

        if (filterName === defaultFilterName) {
            return matchesAllHazards;
        } else {
            return matchesAllHazards && adaptationCategories.includes(filterName);
        }
    });

    // Limit to 20 adaptations
    const limitedAdaptations = filteredAdaptations.slice(0, 20);

    return (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>Adaptations</Text>
            <Text style={styles.bodyText}>
                Based on the expected climate change and resulting impacts in the UK, the following adaptations should be considered.
                These adaptations were identified to reduce risk to humans and the environment while providing co-benefits where possible.
                {'\n\n'}
                You have chosen adaptations related to{' '}
                <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>{hazardText}</Text>
                {!isDefaultFilter && (
                    <>
                        {' '}and have filtered the list by{' '}
                        <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>{filterName}</Text>
                    </>
                )}.{'\n\n'}
            </Text>

            {limitedAdaptations.length > 0 && (
                <>
                    <Text style={styles.bodyText}>
                        {filteredAdaptations.length > 20
                            ? `Showing the first 20 of ${filteredAdaptations.length} adaptations:`
                            : `${filteredAdaptations.length} adaptation${filteredAdaptations.length === 1 ? '' : 's'} found:`
                        }
                    </Text>

                    <View style={styles.bulletList}>
                        {limitedAdaptations.map((adaptation, index) => (
                            <Text key={index} style={styles.bulletItem}>
                                • {adaptation.attributes.label}
                            </Text>
                        ))}
                    </View>
                </>
            )}

            {limitedAdaptations.length === 0 && (
                <Text style={styles.bodyText}>
                    No adaptations found for the selected criteria.
                </Text>
            )}
            <Text style={styles.bodyText}>To access more detail on each adaptation, visit LCAT and click on each adaptation.{'\n'}
                Want to learn more about climate adaptation? Read our <Link src={ADAPTATION_INTRO_PDF_URL}>Introduction to Climate Adaptation</Link>.</Text>
        </View>
    );
};

export default AdaptationsPDF;