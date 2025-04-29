/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

// General impact icons for impacts data structure
import SvgAdaptationAndOrMutationOfMicroorganisms from "../../images/impacts/community/AdaptationAndOrMutationOfMicroorganisms";
// Community impact icons for communityImpacts data structure
import SvgBiodiversityAndEcologicalBalanceDisruption from "../../images/impacts/community/BiodiversityAndEcologicalBalanceDisruption";
import SvgBuildingAndStructuralDamage from "../../images/impacts/community/BuildingAndStructuralDamage";
import SvgBuildingPerformance from "../../images/impacts/community/BuildingPerformance";
import SvgDamageOrLossOfCoastalDefences from "../../images/impacts/community/DamageOrLossOfCoastalDefences";
import SvgDamageOrLossOfPossessionsOrHome from "../../images/impacts/community/DamageOrLossOfPossessionsOrHome";
import SvgDamageOrLossOfTheBuiltAndNaturalEnvironment from "../../images/impacts/community/DamageOrLossOfTheBuiltAndNaturalEnvironment";
import SvgDamageToLocalEconomy from "../../images/impacts/community/DamageToLocalEconomy";
import SvgFoodSecurity from "../../images/impacts/community/FoodSecurity";
import SvgMarineAndCoastalBiodiversityAndEcologicalBalanceDisruption from "../../images/impacts/community/MarineAndCoastalBiodiversityAndEcologicalBalanceDisruption";
import SvgNegativeImpactOnTheFishingIndustry from "../../images/impacts/community/NegativeImpactOnTheFishingIndustry";
import SvgNegativeImpactsOnAgriculturalAndLivestockProduction from "../../images/impacts/community/NegativeImpactsOnAgriculturalAndLivestockProduction";
import SvgOutdoorAirQuality from "../../images/impacts/community/OutdoorAirQuality";
import SvgPeopleRequiringCare from "../../images/impacts/community/PeopleRequiringCare";
import SvgPublicTransportDisruption from "../../images/impacts/community/PublicTransportDisruption";
import SvgReductionInWaterQuality from "../../images/impacts/community/ReductionInWaterQuality";
import SvgTransportDisruption from "../../images/impacts/community/TransportDisruption";
import SvgUrbanHeatIslandEffect from "../../images/impacts/community/UrbanHeatIslandEffect";
import SvgAdverseHealthOutcomesAndMalnutritionAssociatedWithAnUnhealthyDiet from "../../images/impacts/general/AdverseHealthOutcomesAndMalnutritionAssociatedWithAnUnhealthyDiet";
import SvgAdverseHealthOutcomesAssociatedWithExposureToChemicalsHeavyMetalsAndMicroplastics from "../../images/impacts/general/AdverseHealthOutcomesAssociatedWithExposureToChemicalsHeavyMetalsAndMicroplastics";
import SvgAdversePregnancyOutcomes from "../../images/impacts/general/AdversePregnancyOutcomes";
import SvgAntimicrobialResistance from "../../images/impacts/general/AntimicrobialResistance";
import SvgCardiovascularDiseases from "../../images/impacts/general/CardiovascularDiseases";
import SvgDrowningOrFloodRelatedAccidents from "../../images/impacts/general/DrowningOrFloodRelatedAccidents";
import SvgIllnessAndMortalityDueToDampBuildingFabrics from "../../images/impacts/general/IllnessAndMortalityDueToDampBuildingFabrics";
import SvgIllnessFromBiologicalContaminants from "../../images/impacts/general/IllnessFromBiologicalContaminants";
import SvgInfectionsCausedByPathogenicOrganisms from "../../images/impacts/general/InfectionsCausedByPathogenicOrganisms";
import SvgInjuries from "../../images/impacts/general/Injuries";
import SvgRespiratoryDiseases from "../../images/impacts/general/RespiratoryDiseases";
import SvgVectorBorneDiseases from "../../images/impacts/general/VectorBorneDiseases";

// Impact pathway names, pathway IDs used in inPathway field, and Kumu map iframe embeds
export const pathways = [
    {
        id: 0,
        name: "Extreme Storms",
        isCoastal: false,
        emoji: "\u26c8\ufe0f",
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Extreme Storms"
                src="https://embed.kumu.io/e836987dc7d7100b341e3ba2a941ea7b"
                style={{
                    border: "none",
                }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Extreme Storms"
                src="https://embed.kumu.io/0e652cde907f0103070b2c79a7e47b13"
                style={{
                    border: "none",
                }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Extreme Storms"
                src="https://embed.kumu.io/aae27fd92a6152720a9b9219cfdfa830"
                style={{
                    border: "none",
                }}
            />
        ),
    },
    {
        id: 1,
        name: "Coastal Security",
        isCoastal: true,
        emoji: "\ud83c\udf0a",
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Coastal Security"
                src="https://embed.kumu.io/56732326c1bf93d40f6a009d1a92e9fd"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Coastal Security"
                src="https://embed.kumu.io/05e181382a51350528021c4cc7b34983"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Coastal Security"
                src="https://embed.kumu.io/a3b585c75a63c0943f97f0be09ea932a"
                style={{
                    border: "none",
                }}
            />
        ),
    },
    {
        id: 2,
        name: "Flooding and Drought",
        isCoastal: false,
        emoji: "\ud83d\udca7\ud83c\udf35",
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Flooding and Drought"
                src="https://embed.kumu.io/d26e21b394b69d37ea143b209b4e6934"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Flooding and Drought"
                src="https://embed.kumu.io/948cbc16742ef8c2f1aa357bba6558b8"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Flooding and Drought"
                src="https://embed.kumu.io/33e6bd9d90e0e9a10a3e18d91ff8e83f"
                style={{
                    border: "none",
                }}
            />
        ),
    },
    {
        id: 3,
        name: "Food and Personal Security",
        isCoastal: false,
        emoji: "\ud83c\udf3d",
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Food and Personal Security"
                src="https://embed.kumu.io/ada31d266a03a003fe425951394987cc"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Food and Personal Security"
                src="https://embed.kumu.io/c886a2f88045e20382b2891769c51aed"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Food and Personal Security"
                src="https://embed.kumu.io/fe873f39b6a280b944d9cb13b6de8ab5"
                style={{
                    border: "none",
                }}
            />
        ),
    },
    {
        id: 4,
        name: "Marine Health Hazards",
        emoji: "\ud83e\udeb8",
        isCoastal: true,
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Marine Health Hazards"
                src="https://embed.kumu.io/b98a88bb34cc4f0cbf0d2315f7adb5e9"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Marine Health Hazards"
                src="https://embed.kumu.io/e0f8b44984fb5985fe3023d68638ac27"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Marine Health Hazards"
                src="https://embed.kumu.io/de2ec4681a20dcbd6def8ace6eed135c"
                style={{
                    border: "none",
                }}
            />
        ),
    },
    {
        id: 5,
        name: "Temperature",
        isCoastal: false,
        emoji: "\ud83c\udf21\ufe0f",
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Temperature"
                src="https://embed.kumu.io/00665b674dab2da306070a26b93918df"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Temperature"
                src="https://embed.kumu.io/557f050f3d6c05ed38c65d4c954b5e1c"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Temperature"
                src="https://embed.kumu.io/7546cae6da000e5490b0bf1fc1424a5e"
                style={{
                    border: "none",
                }}
            />
        ),
    },
];

export const impacts = [
    {
        id: 0,
        name: "Respiratory diseases",
        inPathway: [0, 2, 3, 4, 5],
        icon: <SvgRespiratoryDiseases className="impact-img" />,
    },
    {
        id: 1,
        name: "Injury",
        inPathway: [0, 1, 5],
        icon: <SvgInjuries className="impact-img" />,
    },
    {
        id: 2,
        name: "Infections caused by bacteria, viruses, fungi, and worms",
        inPathway: [0, 2, 3, 4, 5],
        icon: <SvgInfectionsCausedByPathogenicOrganisms className="impact-img" />,
    },
    {
        id: 3,
        name: "Illness or injury caused by exposure to chemicals, heavy metals, and microplastics",
        inPathway: [0, 1, 2],
        icon: (
            <SvgAdverseHealthOutcomesAssociatedWithExposureToChemicalsHeavyMetalsAndMicroplastics className="impact-img" />
        ),
    },
    {
        id: 4,
        name: "Illness and mortality due to damp",
        inPathway: [1],
        icon: <SvgIllnessAndMortalityDueToDampBuildingFabrics className="impact-img" />,
    },
    {
        id: 5,
        name: "Vector-borne diseases",
        inPathway: [1, 3, 5],
        icon: <SvgVectorBorneDiseases className="impact-img" />,
    },
    {
        id: 6,
        name: "Drowning or flood-related accidents",
        inPathway: [2],
        icon: <SvgDrowningOrFloodRelatedAccidents className="impact-img" />,
    },
    {
        id: 7,
        name: "Adverse health outcomes and malnutrition associated with an unhealthy diet",
        inPathway: [3],
        icon: <SvgAdverseHealthOutcomesAndMalnutritionAssociatedWithAnUnhealthyDiet className="impact-img" />,
    },
    {
        id: 8,
        name: "Antimicrobial resistance",
        inPathway: [4],
        icon: <SvgAntimicrobialResistance className="impact-img" />,
    },
    {
        id: 9,
        name: "Adverse health outcomes associated with naturally produced toxins in marine environments",
        inPathway: [4],
        icon: <SvgIllnessFromBiologicalContaminants className="impact=img" />,
    },
    {
        id: 10,
        name: "Fertility and endocrine function",
        inPathway: [4],
        icon: <SvgAdversePregnancyOutcomes className="impact-img" />,
    },
    {
        id: 11,
        name: "Cardiovascular diseases",
        inPathway: [5],
        icon: <SvgCardiovascularDiseases className="impact-img" />,
    },
];

export const communityImpacts = [
    {
        id: 0,
        name: "Damage or loss of possessions and/or home",
        inPathway: [0],
        icon: <SvgDamageOrLossOfPossessionsOrHome className="impact-img" />,
    },
    {
        id: 1,
        name: "Damage or loss of coastal defences",
        inPathway: [0, 1],
        icon: <SvgDamageOrLossOfCoastalDefences className="impact-img" />,
    },
    {
        id: 2,
        name: "Damage or loss of the built and natural environment",
        inPathway: [0, 1],
        icon: <SvgDamageOrLossOfTheBuiltAndNaturalEnvironment className="impact-img" />,
    },
    {
        id: 3,
        name: "People requiring care to maintain wellbeing",
        inPathway: [0],
        icon: <SvgPeopleRequiringCare className="impact-img" />,
    },
    {
        id: 4,
        name: "Marine and coastal biodiversity and ecological balance disruption",
        inPathway: [1, 4],
        icon: <SvgMarineAndCoastalBiodiversityAndEcologicalBalanceDisruption className="impact-img" />,
    },
    {
        id: 5,
        name: "Damage to local economy",
        inPathway: [1, 4],
        icon: <SvgDamageToLocalEconomy className="impact-img" />,
    },
    {
        id: 6,
        name: "Reduction in water availability and quality",
        inPathway: [2, 3, 4],
        icon: <SvgReductionInWaterQuality className="impact-img" />,
    },
    {
        id: 7,
        name: "Transport disruption",
        inPathway: [2],
        icon: <SvgTransportDisruption className="impact-img" />,
    },
    {
        id: 8,
        name: "Building and structural damage",
        inPathway: [2],
        icon: <SvgBuildingAndStructuralDamage className="impact-img" />,
    },
    {
        id: 9,
        name: "Biodiversity and ecological balance disruption",
        inPathway: [2],
        icon: <SvgBiodiversityAndEcologicalBalanceDisruption className="impact-img" />,
    },
    {
        id: 10,
        name: "Food security",
        inPathway: [3],
        icon: <SvgFoodSecurity className="impact-img" />,
    },
    {
        id: 11,
        name: "Negative impacts on agricultural and livestock production",
        inPathway: [3],
        icon: <SvgNegativeImpactsOnAgriculturalAndLivestockProduction className="impact-img" />,
    },
    {
        id: 12,
        name: "Negative impacts on the fishing industry",
        inPathway: [3],
        icon: <SvgNegativeImpactOnTheFishingIndustry className="impact-img" />,
    },
    {
        id: 13,
        name: "Adaptation and/or mutation of microorganisms to antibiotics, chemicals and environmental stressors",
        inPathway: [4],
        icon: <SvgAdaptationAndOrMutationOfMicroorganisms className="impact-img" />,
    },
    {
        id: 14,
        name: "Public transport disruption",
        inPathway: [5],
        icon: <SvgPublicTransportDisruption className="impact-img" />,
    },
    {
        id: 15,
        name: "Urban Heat Island effect",
        inPathway: [5],
        icon: <SvgUrbanHeatIslandEffect className="impact-img" />,
    },
    {
        id: 16,
        name: "Building performance",
        inPathway: [5],
        icon: <SvgBuildingPerformance className="impact-img" />,
    },
    {
        id: 17,
        name: "Outdoor air quality",
        inPathway: [5],
        icon: <SvgOutdoorAirQuality className="impact-img" />,
    },
];
