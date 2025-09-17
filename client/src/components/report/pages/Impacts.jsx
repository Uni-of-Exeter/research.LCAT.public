import { Image, Text, View } from '@react-pdf/renderer';

import AdaptationMicroorganismsIcon from '../../../images/impacts/community/AdaptationAndOrMutationOfMicroorganisms.png';
import BiodiversityDisruptionIcon from '../../../images/impacts/community/Biodiversity and ecological balance disruption.png';
import BuildingDamageIcon from '../../../images/impacts/community/Building and structural damage.png';
import BuildingPerformanceIcon from '../../../images/impacts/community/Building performance.png';
import CoastalDefencesIcon from '../../../images/impacts/community/Damage or loss of coastal defences.png';
import PossessionsHomeIcon from '../../../images/impacts/community/Damage or loss of possessions or home.png';
import BuiltEnvironmentIcon from '../../../images/impacts/community/Damage or loss of the built and natural environment.png';
import LocalEconomyIcon from '../../../images/impacts/community/Damage to local economy.png';
import FoodSecurityIcon from '../../../images/impacts/community/Food security.png';
import MarineBiodiversityIcon from '../../../images/impacts/community/Marine and coastal biodiversity and ecological balance disruption.png';
import FishingIndustryIcon from '../../../images/impacts/community/Negative impact on the fishing industry.png';
import AgriculturalProductionIcon from '../../../images/impacts/community/Negative impacts on agricultural and livestock production.png';
import OutdoorAirQualityIcon from '../../../images/impacts/community/Outdoor air quality.png';
import PeopleRequiringCareIcon from '../../../images/impacts/community/People requiring care.png';
import PublicTransportIcon from '../../../images/impacts/community/Public transport disruption.png';
import WaterQualityIcon from '../../../images/impacts/community/Reduction in water quality.png';
import TransportDisruptionIcon from '../../../images/impacts/community/Transport disruption.png';
import UrbanHeatIslandIcon from '../../../images/impacts/community/Urban heat island effect.png';
import UnhealthyDietIcon from '../../../images/impacts/general/Adverse health outcomes and malnutrition associated with an unhealthy diet.png';
import ChemicalExposureIcon from '../../../images/impacts/general/Adverse health outcomes associated with exposure to chemicals heavy metals and microplastics.png';
import FertilityIcon from '../../../images/impacts/general/Adverse pregnancy outcomes.png';
import AntimicrobialResistanceIcon from '../../../images/impacts/general/Antimicrobial resistance.png';
import CardiovascularDiseasesIcon from '../../../images/impacts/general/Cardiovascular diseases.png';
import FloodAccidentsIcon from '../../../images/impacts/general/Drowning or flood related accidents.png';
import DampMortalityIcon from '../../../images/impacts/general/Illness and mortality due to damp building fabrics.png';
import MarineToxinsIcon from '../../../images/impacts/general/Illness from biological contaminants.png';
import InfectionIcon from '../../../images/impacts/general/Infections caused by pathogenic organisms.png';
import InjuryIcon from '../../../images/impacts/general/injuries.png';
import RespiratoryDiseasesIcon from '../../../images/impacts/general/Respiratory diseases.png';
import VectorBorneDiseasesIcon from '../../../images/impacts/general/Vector-borne diseases.png';
import { communityImpacts, impacts, pathways } from '../../climateImpacts/ClimateImpactSummaryData';
import { reportStyles as styles } from '../reportStyles';
import { formatLineBreaks, getTextStyle } from '../textFormattingUtils';

const getImpactIcon = (impactName) => {
    const iconMap = {
        'Respiratory diseases': RespiratoryDiseasesIcon,
        'Injury': InjuryIcon,
        'Infections caused by bacteria, viruses, fungi, and worms': InfectionIcon,
        'Illness or injury caused by exposure to chemicals, heavy metals, and microplastics': ChemicalExposureIcon,
        'Illness and mortality due to damp': DampMortalityIcon,
        'Vector-borne diseases': VectorBorneDiseasesIcon,
        'Drowning or flood-related accidents': FloodAccidentsIcon,
        'Adverse health outcomes and malnutrition associated with an unhealthy diet': UnhealthyDietIcon,
        'Antimicrobial resistance': AntimicrobialResistanceIcon,
        'Adverse health outcomes associated with naturally produced toxins in marine environments': MarineToxinsIcon,
        'Fertility and endocrine function': FertilityIcon,
        'Cardiovascular diseases': CardiovascularDiseasesIcon,
    };
    return iconMap[impactName] || RespiratoryDiseasesIcon;
};

const getCommunityImpactIcon = (impactName) => {
    const iconMap = {
        'Damage or loss of possessions and/or home': PossessionsHomeIcon,
        'Damage or loss of coastal defences': CoastalDefencesIcon,
        'Damage or loss of the built and natural environment': BuiltEnvironmentIcon,
        'Damage to local economy': LocalEconomyIcon,
        'Food security': FoodSecurityIcon,
        'Marine and coastal biodiversity and ecological balance disruption': MarineBiodiversityIcon,
        'Negative impacts on the fishing industry': FishingIndustryIcon,
        'Negative impacts on agricultural and livestock production': AgriculturalProductionIcon,
        'Outdoor air quality': OutdoorAirQualityIcon,
        'People requiring care to maintain wellbeing': PeopleRequiringCareIcon,
        'Public transport disruption': PublicTransportIcon,
        'Reduction in water availability and quality': WaterQualityIcon,
        'Transport disruption': TransportDisruptionIcon,
        'Urban Heat Island effect': UrbanHeatIslandIcon,
        'Building performance': BuildingPerformanceIcon,
        'Building and structural damage': BuildingDamageIcon,
        'Biodiversity and ecological balance disruption': BiodiversityDisruptionIcon,
        'Adaptation and/or mutation of microorganisms to antibiotics, chemicals and environmental stressors': AdaptationMicroorganismsIcon,
    };
    return iconMap[impactName] || PossessionsHomeIcon;
};

const ImpactsPDF = ({ selectedImpactHazard, includeHealthImpacts = true, includeCommunityImpacts = true }) => {
    const hazardId = pathways.find((pathway) => pathway.name === selectedImpactHazard)?.id;

    if (!hazardId && hazardId !== 0) {
        return (
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Climate Impact Summary</Text>
                <Text style={styles.bodyText}>No impact data available for {selectedImpactHazard}.</Text>
            </View>
        );
    }

    const filteredImpacts = impacts.filter((item) => item.inPathway.includes(hazardId));
    const filteredCommunityImpacts = communityImpacts.filter((item) => item.inPathway.includes(hazardId));

    return (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>Climate Impact Summary</Text>
            <Text style={styles.bodyText}>
                Below is a summary of the climate impacts expected in the UK from{' '}
                <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>{selectedImpactHazard}</Text>
                . These impacts will vary by local area.
            </Text>

            {includeHealthImpacts && (
                <>
                    <Text style={styles.sectionTitle}>Health Impacts</Text>
                    <Text style={styles.bodyText}>
                        Climate change will have an overall{' '}
                        <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>negative impact</Text>
                        {' '}on health, including{' '}
                        <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>mental health disorders, wellbeing, and chronic health conditions.</Text>
                        {' '}See below for additional health impacts for each pathway.
                    </Text>
                    <View style={styles.climateContainer}>
                        {filteredImpacts.map((impact, index) => {
                            const iconSrc = getImpactIcon(impact.name);
                            return (
                                <View key={index} style={[styles.climateItem, { width: '24%' }]}>
                                    <View style={styles.iconContainer}>
                                        <Image src={iconSrc} style={styles.icon} />
                                    </View>
                                    <Text style={getTextStyle(impact.name)}>{formatLineBreaks(impact.name)}</Text>
                                </View>
                            );
                        })}
                    </View>
                </>
            )}

            {includeCommunityImpacts && (
                <>
                    <Text style={styles.sectionTitle}>Community Impacts</Text>
                    <Text style={styles.bodyText}>
                        Climate change will have a{' '}
                        <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>negative impact</Text>
                        {' '}on essential community infrastructures and services like{' '}
                        <Text style={[styles.bodyText, { fontWeight: 'bold' }]}>systems failures of hospitals, transport, water, and energy.</Text>
                        {' '}See below for additional community impacts for each pathway.
                    </Text>
                    <View style={styles.climateContainer}>
                        {filteredCommunityImpacts.map((impact, index) => {
                            const iconSrc = getCommunityImpactIcon(impact.name);
                            return (
                                <View key={index} style={[styles.climateItem, { width: '24%' }]}>
                                    <View style={styles.iconContainer}>
                                        <Image src={iconSrc} style={styles.icon} />
                                    </View>
                                    <Text style={getTextStyle(impact.name)}>{formatLineBreaks(impact.name)}</Text>
                                </View>
                            );
                        })}
                    </View>
                </>
            )}
        </View>
    );
};

export default ImpactsPDF;