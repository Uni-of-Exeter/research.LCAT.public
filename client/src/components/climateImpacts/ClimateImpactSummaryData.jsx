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
import SvgCoastalSecurity from "../../images/adaptations/CoastalSecurity.jsx";
import SvgFloodingAndDrought from "../../images/adaptations/FloodingAndDrought.jsx";
import SvgFoodAndPersonalSecurity from "../../images/adaptations/FoodAndPersonalSecurity.jsx";
import SvgMarineHealth from "../../images/adaptations/MarineHealth.jsx";
import SvgStorm from "../../images/adaptations/Storm.jsx";
import SvgTemperature from "../../images/adaptations/Temperature.jsx";
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
        icon: <SvgStorm className="icon" />,
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Extreme Storms"
                src="https://embed.kumu.io/ef98489198fe11581b90afcf6349f3cd"
                style={{
                    border: "none",
                }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Extreme Storms"
                src="https://embed.kumu.io/64953b0a74bd4dda4e7fd95125402199"
                style={{
                    border: "none",
                }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Extreme Storms"
                src="https://embed.kumu.io/8fe28d3cdb47759db954f6bce9f07ae2"
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
        icon: <SvgCoastalSecurity className="icon" />,
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Coastal Security"
                src="https://embed.kumu.io/c99b396b7de63cdb87a90e6ba74c29fb"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Coastal Security"
                src="https://embed.kumu.io/91759ac279021a06331a1dbe08ffb140"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Coastal Security"
                src="https://embed.kumu.io/d74ba2d15fe5f1d3c74ceb7aadc3738a"
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
        icon: <SvgFloodingAndDrought className="icon" />,
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Flooding and Drought"
                src="https://embed.kumu.io/6973a74e077675d71964f2ee365af128"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Flooding and Drought"
                src="https://embed.kumu.io/b935abed99c325a33a1abbf175fb6047"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Flooding and Drought"
                src="https://embed.kumu.io/371cf9d1ca638f1945ce4901fa516271"
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
        icon: <SvgFoodAndPersonalSecurity className="icon" />,
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Food and Personal Security"
                src="https://embed.kumu.io/b55c2f7e03206be0ff25bec82d08c1dc"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Food and Personal Security"
                src="https://embed.kumu.io/3712758edb597188b8dbcee8f87ec98c"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Food and Personal Security"
                src="https://embed.kumu.io/ba93b5fa867efa564e2fef89e9b96bc7"
                style={{
                    border: "none",
                }}
            />
        ),
    },
    {
        id: 4,
        name: "Marine Health Hazards",
        icon: <SvgMarineHealth className="icon" />,
        isCoastal: true,
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Marine Health Hazards"
                src="https://embed.kumu.io/eb55bf712cf99237f19dcfaed02d8dad"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Marine Health Hazards"
                src="https://embed.kumu.io/87c3e4de4ef200995c12265c490db586"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Marine Health Hazards"
                src="https://embed.kumu.io/66848de2b33dd70ab8db9335cf0ea6a3"
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
        icon: <SvgTemperature className="icon" />,
        summaryPathwayMap: (
            <iframe
                title="Summary Pathway Map for Temperature"
                src="https://embed.kumu.io/a1ad882db9a0df16eaa3442aef1221c8"
                style={{ border: "none" }}
            />
        ),
        completePathwayMap: (
            <iframe
                title="Complete Pathway Map for Temperature"
                src="https://embed.kumu.io/5a093dde7284f2d5c53a1f8d88e5718b"
                style={{ border: "none" }}
            />
        ),
        completePathwayMapWithAdaptations: (
            <iframe
                title="Complete Pathway Map (with adaptations) for Temperature"
                src="https://embed.kumu.io/00167af91fc2fb2148310103bf1e95bd"
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
        icon: <SvgRespiratoryDiseases className="icon" />,
    },
    {
        id: 1,
        name: "Injury",
        inPathway: [0, 1, 5],
        icon: <SvgInjuries className="icon" />,
    },
    {
        id: 2,
        name: "Infections caused by bacteria, viruses, fungi, and worms",
        inPathway: [0, 2, 3, 4, 5],
        icon: <SvgInfectionsCausedByPathogenicOrganisms className="icon" />,
    },
    {
        id: 3,
        name: "Illness or injury caused by exposure to chemicals, heavy metals, and microplastics",
        inPathway: [0, 1, 2],
        icon: <SvgAdverseHealthOutcomesAssociatedWithExposureToChemicalsHeavyMetalsAndMicroplastics className="icon" />,
    },
    {
        id: 4,
        name: "Illness and mortality due to damp",
        inPathway: [1],
        icon: <SvgIllnessAndMortalityDueToDampBuildingFabrics className="icon" />,
    },
    {
        id: 5,
        name: "Vector-borne diseases",
        inPathway: [1, 3, 5],
        icon: <SvgVectorBorneDiseases className="icon" />,
    },
    {
        id: 6,
        name: "Drowning or flood-related accidents",
        inPathway: [2],
        icon: <SvgDrowningOrFloodRelatedAccidents className="icon" />,
    },
    {
        id: 7,
        name: "Adverse health outcomes and malnutrition associated with an unhealthy diet",
        inPathway: [3],
        icon: <SvgAdverseHealthOutcomesAndMalnutritionAssociatedWithAnUnhealthyDiet className="icon" />,
    },
    {
        id: 8,
        name: "Antimicrobial resistance",
        inPathway: [4],
        icon: <SvgAntimicrobialResistance className="icon" />,
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
        icon: <SvgAdversePregnancyOutcomes className="icon" />,
    },
    {
        id: 11,
        name: "Cardiovascular diseases",
        inPathway: [5],
        icon: <SvgCardiovascularDiseases className="icon" />,
    },
];

export const communityImpacts = [
    {
        id: 0,
        name: "Damage or loss of possessions and/or home",
        inPathway: [0],
        icon: <SvgDamageOrLossOfPossessionsOrHome className="icon" />,
    },
    {
        id: 1,
        name: "Damage or loss of coastal defences",
        inPathway: [0, 1],
        icon: <SvgDamageOrLossOfCoastalDefences className="icon" />,
    },
    {
        id: 2,
        name: "Damage or loss of the built and natural environment",
        inPathway: [0, 1],
        icon: <SvgDamageOrLossOfTheBuiltAndNaturalEnvironment className="icon" />,
    },
    {
        id: 3,
        name: "People requiring care to maintain wellbeing",
        inPathway: [0],
        icon: <SvgPeopleRequiringCare className="icon" />,
    },
    {
        id: 4,
        name: "Marine and coastal biodiversity and ecological balance disruption",
        inPathway: [1, 4],
        icon: <SvgMarineAndCoastalBiodiversityAndEcologicalBalanceDisruption className="icon" />,
    },
    {
        id: 5,
        name: "Damage to local economy",
        inPathway: [1, 4],
        icon: <SvgDamageToLocalEconomy className="icon" />,
    },
    {
        id: 6,
        name: "Reduction in water availability and quality",
        inPathway: [2, 3, 4],
        icon: <SvgReductionInWaterQuality className="icon" />,
    },
    {
        id: 7,
        name: "Transport disruption",
        inPathway: [2],
        icon: <SvgTransportDisruption className="icon" />,
    },
    {
        id: 8,
        name: "Building and structural damage",
        inPathway: [2],
        icon: <SvgBuildingAndStructuralDamage className="icon" />,
    },
    {
        id: 9,
        name: "Biodiversity and ecological balance disruption",
        inPathway: [2],
        icon: <SvgBiodiversityAndEcologicalBalanceDisruption className="icon" />,
    },
    {
        id: 10,
        name: "Food security",
        inPathway: [3],
        icon: <SvgFoodSecurity className="icon" />,
    },
    {
        id: 11,
        name: "Negative impacts on agricultural and livestock production",
        inPathway: [3],
        icon: <SvgNegativeImpactsOnAgriculturalAndLivestockProduction className="icon" />,
    },
    {
        id: 12,
        name: "Negative impacts on the fishing industry",
        inPathway: [3],
        icon: <SvgNegativeImpactOnTheFishingIndustry className="icon" />,
    },
    {
        id: 13,
        name: "Adaptation and/or mutation of microorganisms to antibiotics, chemicals and environmental stressors",
        inPathway: [4],
        icon: <SvgAdaptationAndOrMutationOfMicroorganisms className="icon" />,
    },
    {
        id: 14,
        name: "Public transport disruption",
        inPathway: [5],
        icon: <SvgPublicTransportDisruption className="icon" />,
    },
    {
        id: 15,
        name: "Urban Heat Island effect",
        inPathway: [5],
        icon: <SvgUrbanHeatIslandEffect className="icon" />,
    },
    {
        id: 16,
        name: "Building performance",
        inPathway: [5],
        icon: <SvgBuildingPerformance className="icon" />,
    },
    {
        id: 17,
        name: "Outdoor air quality",
        inPathway: [5],
        icon: <SvgOutdoorAirQuality className="icon" />,
    },
];
