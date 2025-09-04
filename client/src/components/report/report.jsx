import { Document, Image, Link, Page, Text, View } from '@react-pdf/renderer';

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
import AdaptationMicroorganismsIcon from '../../images/impacts/community/AdaptationAndOrMutationOfMicroorganisms.png';
import BiodiversityDisruptionIcon from '../../images/impacts/community/Biodiversity and ecological balance disruption.png';
import BuildingDamageIcon from '../../images/impacts/community/Building and structural damage.png';
import BuildingPerformanceIcon from '../../images/impacts/community/Building performance.png';
import CoastalDefencesIcon from '../../images/impacts/community/Damage or loss of coastal defences.png';
import PossessionsHomeIcon from '../../images/impacts/community/Damage or loss of possessions or home.png';
import BuiltEnvironmentIcon from '../../images/impacts/community/Damage or loss of the built and natural environment.png';
import LocalEconomyIcon from '../../images/impacts/community/Damage to local economy.png';
import FoodSecurityIcon from '../../images/impacts/community/Food security.png';
import MarineBiodiversityIcon from '../../images/impacts/community/Marine and coastal biodiversity and ecological balance disruption.png';
import FishingIndustryIcon from '../../images/impacts/community/Negative impact on the fishing industry.png';
import AgriculturalProductionIcon from '../../images/impacts/community/Negative impacts on agricultural and livestock production.png';
import OutdoorAirQualityIcon from '../../images/impacts/community/Outdoor air quality.png';
import PeopleRequiringCareIcon from '../../images/impacts/community/People requiring care.png';
import PublicTransportIcon from '../../images/impacts/community/Public transport disruption.png';
import WaterQualityIcon from '../../images/impacts/community/Reduction in water quality.png';
import TransportDisruptionIcon from '../../images/impacts/community/Transport disruption.png';
import UrbanHeatIslandIcon from '../../images/impacts/community/Urban heat island effect.png';
import UnhealthyDietIcon from '../../images/impacts/general/Adverse health outcomes and malnutrition associated with an unhealthy diet.png';
import ChemicalExposureIcon from '../../images/impacts/general/Adverse health outcomes associated with exposure to chemicals heavy metals and microplastics.png';
import FertilityIcon from '../../images/impacts/general/Adverse pregnancy outcomes.png';
import AntimicrobialResistanceIcon from '../../images/impacts/general/Antimicrobial resistance.png';
import CardiovascularDiseasesIcon from '../../images/impacts/general/Cardiovascular diseases.png';
import FloodAccidentsIcon from '../../images/impacts/general/Drowning or flood related accidents.png';
import DampMortalityIcon from '../../images/impacts/general/Illness and mortality due to damp building fabrics.png';
import MarineToxinsIcon from '../../images/impacts/general/Illness from biological contaminants.png';
import InfectionIcon from '../../images/impacts/general/Infections caused by pathogenic organisms.png';
import InjuryIcon from '../../images/impacts/general/injuries.png';
import RespiratoryDiseasesIcon from '../../images/impacts/general/Respiratory diseases.png';
import VectorBorneDiseasesIcon from '../../images/impacts/general/Vector-borne diseases.png';
import LCATLogo from '../../images/logos/LCAT_Logo_Primary_RGB.png';
import HealthConditionsIcon from '../../images/vulnerabilities/healthConditions.png';
import LowIncomesIcon from '../../images/vulnerabilities/lowIncomes.png';
import LowLocalKnowledgeIcon from '../../images/vulnerabilities/lowLocalKnowledge.png';
import LowMobilityIcon from '../../images/vulnerabilities/lowMobility.png';
import OlderPeopleIcon from '../../images/vulnerabilities/olderPeople.png';
import PrivateSocialHousingIcon from '../../images/vulnerabilities/privateSocialHousing.png';
import SociallyIsolatedIcon from '../../images/vulnerabilities/sociallyIsolated.png';
import UnderFivesIcon from '../../images/vulnerabilities/underFives.png';
import adaptationData from '../../kumu/parsed/adaptation_data.json';
import { climateVariables, formatClimateData } from '../../utils/climateUtils';
import { andify } from "../../utils/utils";
import { defaultFilterName } from '../adaptations/AdaptationCategories';
import { adaptationFilters } from '../adaptations/AdaptationCategories';
import { climateHazardsData } from '../climateHazard/ClimateHazardData';
import { communityImpacts, impacts, pathways } from '../climateImpacts/ClimateImpactSummaryData';
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
    switch (arrow) {
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

const vulnerabilityIconMap = {
    'Older people': OlderPeopleIcon,
    'Under 5s': UnderFivesIcon,
    'People with health conditions': HealthConditionsIcon,
    'People on low incomes': LowIncomesIcon,
    'Tenants in private or social housing': PrivateSocialHousingIcon,
    'People living in area for a short time': LowLocalKnowledgeIcon,
    'People who are socially isolated': SociallyIsolatedIcon,
    'People with low personal mobility': LowMobilityIcon,
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

const ClimateHazardsPDF = ({ applyCoastalFilter }) => {
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
    )
};

const ClimateImpactsPDF = ({ selectedImpactHazard, includeHealthImpacts = true, includeCommunityImpacts = true }) => {
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
                                <View key={index} style={styles.climateItem}>
                                    <View style={styles.iconContainer}>
                                        <Image src={iconSrc} style={styles.icon} />
                                    </View>
                                    <Text style={styles.climateVariable}>{impact.name}</Text>
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
                                <View key={index} style={styles.climateItem}>
                                    <View style={styles.iconContainer}>
                                        <Image src={iconSrc} style={styles.icon} />
                                    </View>
                                    <Text style={styles.climateVariable}>{impact.name}</Text>
                                </View>
                            );
                        })}
                    </View>
                </>
            )}
        </View>
    );
};

const VulnerabilityPDF = () => {
    return (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>Personal and social vulnerabilities</Text>
            <Text style={styles.bodyText}>
                Below is a summary of some of the key vulnerable groups for the UK.{'\n\n'}
                It is important to consider vulnerability because not everyone is affected equally by climate change.
                This impacts people&apos;s ability to cope with, adapt to and recover from climate events and extreme weather.
                Those experiencing multiple vulnerabilities are more vulnerable to climate impacts.
            </Text>

            <View style={styles.climateContainer}>
                {Object.entries(vulnerabilityIconMap).map(([vulnerabilityName, iconSrc], index) => {
                    return (
                        <View key={index} style={styles.climateItem}>
                            <View style={styles.iconContainer}>
                                <Image src={iconSrc} style={styles.icon} />
                            </View>
                            <Text style={styles.climateVariable}>{vulnerabilityName}</Text>
                        </View>
                    );
                })}
            </View>

            <Text style={styles.text}>
                To access localised data on these vulnerabilities, visit LCAT and click on each vulnerability icon.
            </Text>
        </View>
    );
};

const AdaptationsPDF = ({ selectedAdaptationHazards, filterName }) => {
    const hazardText = selectedAdaptationHazards && selectedAdaptationHazards.length > 0
        ? selectedAdaptationHazards.join(", ")
        : "no specific hazards";

    const isDefaultFilter = filterName === defaultFilterName;

    // Find the filter category for the current filterName
    const selectedFilter = adaptationFilters.find(filter => filter.filterName === filterName);
    const filterCategory = selectedFilter ? selectedFilter.category : adaptationFilters[0].category;

    // Filter adaptations (same logic as StaticAdaptations)
    const filteredAdaptations = adaptationData.filter((adaptation) => {
        const layers = adaptation.attributes.layer.map((layer) => layer.toLowerCase());
        const adaptationCategories = adaptation.attributes[filterCategory] || [];

        const matchesAllHazards = selectedAdaptationHazards && selectedAdaptationHazards.length > 0
            ? selectedAdaptationHazards.every((hazard) =>
                layers.some((layer) => layer.includes(hazard.toLowerCase() + " in full"))
            )
            : false;

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
                Want to learn more about climate adaptation? Read our <Link src="https://www.ecehh.org/wp/wp-content/uploads/2021/09/LCAT-Introduction-to-Local-Climate-Adaptation-May-2024.pdf">Introduction to Climate Adaptation</Link>.</Text>
        </View>
    );
};

const ClimateReport = ({ regions, climatePrediction, selectedImpactHazard, selectedAdaptationHazards, filterName, rcp, season, applyCoastalFilter, selectedPages = ['climate'] }) => {
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

            {shouldIncludePage('hazards') && selectedImpactHazard && (
                <Page size="A4" style={styles.page}>
                    <ClimateHazardsPDF
                        applyCoastalFilter={applyCoastalFilter} />
                </Page>
            )}

            {(shouldIncludePage('health-impacts') || shouldIncludePage('community-impacts')) && selectedImpactHazard && (
                <Page size="A4" style={styles.page}>
                    <ClimateImpactsPDF
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