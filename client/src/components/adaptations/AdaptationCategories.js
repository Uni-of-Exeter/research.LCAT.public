/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

// Adaptation categories are indexed by key in adaptation_data.json
export const adaptationBodyKeys = {
    CCC: "ccc adaptation theme",
    IPCC: "ipcc adaptation category",
};

export const CCCAdaptationThemes = [
    "Nature",
    "Working lands and seas",
    "Towns and cities",
    "Community preparedness and response",
    "Health",
    "Energy",
    "Transport",
    "Buildings",
    "Food security",
    "Telecoms & ICT",
    "Business",
    "Finance",
    "Water supply",
    "All",
];

export const IPCCCategories = [
    "Engineered and built environment",
    "Educational",
    "Technological ",
    "Ecosystem-based",
    "Services",
    "Laws and regulations",
    "Government policies and programs",
    "Economic",
    "Behavioural",
    "Informational",
];

// This array contains aggregated filter names and categories
export const adaptationFilters = [
    { filterName: "No filter applied", category: "", displayName: "No filter applied" },
    { filterName: "Nature", category: "ccc adaptation theme", displayName: "Nature" },
    { filterName: "Working lands and seas", category: "ccc adaptation theme", displayName: "Working lands and seas" },
    { filterName: "Towns and cities", category: "ccc adaptation theme", displayName: "Towns and cities" },
    {
        filterName: "Community preparedness and response",
        category: "ccc adaptation theme",
        displayName: "Community preparedness and response",
    },
    { filterName: "Health", category: "ccc adaptation theme", displayName: "Health" },
    { filterName: "Energy", category: "ccc adaptation theme", displayName: "Energy" },
    { filterName: "Transport", category: "ccc adaptation theme", displayName: "Transport" },
    { filterName: "Buildings", category: "ccc adaptation theme", displayName: "Buildings" },
    { filterName: "Food security", category: "ccc adaptation theme", displayName: "Food security" },
    { filterName: "Telecoms & ICT", category: "ccc adaptation theme", displayName: "Telecoms & ICT" },
    { filterName: "Business", category: "ccc adaptation theme", displayName: "Business" },
    { filterName: "Finance", category: "ccc adaptation theme", displayName: "Finance" },
    { filterName: "Water supply", category: "ccc adaptation theme", displayName: "Water supply" },
    {
        filterName: "Government policies and programs",
        category: "ipcc adaptation category",
        displayName: "Monitoring and management programmes",
    },
];
