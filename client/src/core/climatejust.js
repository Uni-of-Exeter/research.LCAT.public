// Development before 2024 Copyright (C) Then Try This and University of Exeter
// Development from 2024 Copyright (C) University of Exeter
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the Common Good Public License Beta 1.0 as
// published at http://www.cgpl.org
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// Common Good Public License Beta 1.0 for more details.

const nfviColumns = {
    // AGE	"Age composite Indicator"
    // HEALTH	"Health composite Indicator"
    // INCOME	"Income composite Indicator"
    // INFO	Information use composite Indicator
    // LOC_KNOW	Local knowledge composite Indicator
    // TENURE	Property tenure composite Indicator
    // MOBILITY	Mobility composite Indicator
    // CRIME	Crime composite Indicator
    // HOUSE_TYP	Housing characteristics composite Indicator
    // FLOOD_EXP	Flood experience composite Indicator
    // SERVICE	Service availability composite Indicator
    // SOC_NET	Social networks composite Indicator

    a1: {
        name: "Young children (% people under 5 years)",
        units: "percent",
        direction: "greater-than",
        average: 6.0680407487598553,
        deciles: [8.85122, 7.69741, 6.94098, 6.33214, 5.8, 5.30344, 4.81523, 4.30622, 3.64683],
    },
    a2: {
        name: "Older people (% people over 75 years)",
        units: "percent",
        direction: "greater-than",
        average: 7.8977026019842316,
        deciles: [13.1527, 10.9386, 9.55556, 8.41727, 7.42202, 6.45995, 5.45836, 4.38001, 3.10078],
    },
    h1: {
        name: "Disability / people in ill- health (% people whose day- to-day activities are limited)",
        units: "percent",
        direction: "greater-than",
        average: 18.3847966464569005,
        deciles: [26.0694, 23.0769, 21.0757, 19.4203, 17.9365, 16.5344, 15.0909, 13.4824, 11.3987],
    },
    h2: {
        name: "% households with at least one person with long term limiting illness",
        units: "percent",
        direction: "greater-than",
        average: 27.3258376869802775,
        deciles: [37.1078, 33.0391, 30.4281, 28.3784, 26.6154, 24.9581, 23.2053, 21.2585, 18.5259],
    },
    i1: {
        name: "Unemployed (% unemployed)",
        units: "percent",
        direction: "greater-than",
        average: 4.4616382746051906,
        deciles: [8.02348, 6.38528, 5.26316, 4.42238, 3.74823, 3.23034, 2.79028, 2.3888, 1.95412],
    },
    i2: {
        name: "Long-term unemployed (% who are LTU or who have never worked)",
        units: "percent",
        direction: "greater-than",
        average: 5.4768049245129287,
        deciles: [11.4574, 8.23009, 6.2709, 4.90654, 3.93574, 3.21324, 2.6455, 2.17186, 1.69972],
    },
    i3: {
        name: "Low income occupations (% in routine or semi- routine occupations)",
        units: "percent",
        direction: "greater-than",
        average: 26.1556301787725563,
        deciles: [41.0151, 36.1274, 31.9521, 28.4985, 25.3465, 22.4265, 19.5261, 16.4484, 12.7576],
    },
    i4: {
        name: "Households with dependent children and no adults in employment (%)",
        units: "percent",
        direction: "greater-than",
        average: 4.1739971166095521,
        deciles: [9.49285, 6.65796, 4.94071, 3.72671, 2.85714, 2.22222, 1.73797, 1.32827, 0.917431],
    },
    i5: {
        name: "People income deprived (%)",
        units: "percent",
        direction: "greater-than",
        average: 0.49851894528749311031,
        deciles: [0.900012, 0.79561, 0.699214, 0.599044, 0.496316, 0.397637, 0.29765, 0.200037, 0.0996834],
    },
    f1: {
        name: "Recent arrivals to UK (% people with <1 yr residency coming from outside UK)",
        units: "percent",
        direction: "greater-than",
        average: 0.99672459692779601716,
        deciles: [2.7027, 1.36054, 0.764951, 0.488102, 0.326584, 0.217077, 0.136054, 0.0682594, 0],
    },
    f2: {
        name: "Level of proficiency in English",
        units: "percent",
        direction: "greater-than",
        average: 1.4975662879723933,
        deciles: [3.89755, 2.00501, 1.27688, 0.880282, 0.60698, 0.416667, 0.276625, 0.162602, 0.0693962],
    },
    k1: {
        name: "New migrants from outside the local area",
        units: "percent",
        direction: "greater-than",
        average: 5.3172674935176975,
        deciles: [9.2569, 6.92592, 5.8372, 5.02513, 4.40222, 3.79747, 3.22657, 2.63987, 2.04808],
    },
    t1: {
        name: "Private renters (% Households)",
        units: "percent",
        direction: "greater-than",
        average: 15.3633258510867742,
        deciles: [31.4565, 22.1687, 16.9725, 13.7542, 11.5385, 9.79228, 8.29103, 6.87398, 5.2506],
    },
    t2: {
        name: "Social renters (% Households renting from Social or Council landlords)",
        units: "percent",
        direction: "greater-than",
        average: 18.3203755282177862,
        deciles: [45.5426, 32.6338, 23.756, 16.9492, 11.9912, 8.34951, 5.41935, 3.05556, 1.41176],
    },
    m1: {
        name: "High levels of disability (% of population who are disabled)",
        units: "percent",
        direction: "greater-than",
        average: 8.7672377574348774,
        deciles: [13.9248, 11.7161, 10.2497, 9.12698, 8.18444, 7.30689, 6.45768, 5.55556, 4.41008],
    },
    m2: {
        name: "% people living in medical and care establishments",
        units: "percent",
        direction: "greater-than",
        average: 0.75154989639579189532,
        deciles: [2.71862, 1.19792, 0.316656, 0, 0, 0, 0, 0, 0],
    },
    m3: {
        name: "Lack of private transport (% households with no car or van)",
        units: "percent",
        direction: "greater-than",
        average: 25.5717231685159002,
        deciles: [50.1672, 39.9582, 32.8341, 27.0085, 21.8289, 17.4004, 13.4831, 10.1124, 7.03911],
    },
    c1: {
        name: "High levels of crime",
        units: "metric",
        direction: "less-than",
        average: 0.50028658999354885092,
        deciles: [0.899525, 0.800207, 0.700231, 0.600353, 0.500786, 0.400621, 0.300681, 0.200463, 0.100231],
    },
    l1: {
        name: "% caravan or other mobile or temporary structures in all households",
        units: "percent",
        direction: "greater-than",
        average: 0.36432017650315128568,
        deciles: [0.446429, 0.162338, 0, 0, 0, 0, 0, 0, 0],
    },
    /*    e1: {
        name: "% number of properties within historical flood boundary",
        units: "percent",
        direction: "greater-than",
        average: 2.5641400464904503E-8,
        deciles: [
        -0.0974916000000,
        -0.0974916000000,
        -0.117275000000,
        -0.117275000000,
        -0.117275000000,
        -0.117275000000,
        -0.117275000000,
        -0.117275000000,
        -0.117275000000,
        ],
    },*/
    n1: {
        name: "% single-pensioner households",
        units: "percent",
        direction: "greater-than",
        average: 12.3792068202928419,
        deciles: [18.931, 16.3082, 14.5631, 13.2166, 12.0063, 10.8309, 9.60699, 8.13953, 6.18847],
    },
    n2: {
        name: "% lone-parent households with dependent children",
        units: "percent",
        direction: "greater-than",
        average: 7.1356034396462892,
        deciles: [13.0258, 10.1587, 8.45528, 7.14286, 6.10278, 5.20059, 4.39815, 3.63224, 2.8021],
    },
    n3: {
        name: "% children of primary school age (4-11) in the population",
        units: "percent",
        direction: "greater-than",
        average: 8.9017782415442498,
        deciles: [12.0468, 10.7672, 9.95792, 9.33398, 8.78735, 8.26347, 7.68725, 7.0028, 5.98007],
    },
    /*    s1: {
        name: "% of emergency services exposed to flooding",
        units: "percent",
        direction: "greater-than",
        average: 4.6896084965611445,
        deciles: [
        13.3333000000,
        7.05882000000,
        4.44444000000,
        2.90323000000,
        2.03390000000,
        1.25000000000,
        0,
        0,
        0,
        ],    
    },
    s2: {
        name: "% no. of care homes exposed to flooding",
        units: "percent",
        direction: "greater-than",
        average: 2.0140889716983393,
        deciles: [
        4.85714000000,
        2.81690000000,
        2.07921000000,
        1.66667000000,
        1.29412000000,
        0.952381000000,
        0.625000000000,
        0.400000000000,
        0,
        ],
   },
    s3: {
        name: "% no. of GP surgeries exposed to flooding",
        units: "percent",
        direction: "greater-than",
        average: 2.8433722671523401,
        deciles: [
        6.15385000000,
        3.97059000000,
        3.03030000000,
        2.38411000000,
        1.89474000000,
        1.44928000000,
        1.06195000000,
        0.675676000000,
        0,
        ],
    },
    s4: {
        name: "% no. of schools exposed to flooding",
        units: "percent",
        direction: "greater-than",
        average: 3.0325930304584342,
        deciles: [
        5.60000000000,
        4.00000000000,
        3.12500000000,
        2.64151000000,
        2.29508000000,
        2.00000000000,
        1.70213000000,
        1.50943000000,
        0.862069000000,
        ],    
        },
    imd_rank: {
        name: "IMD Rank",
        units: "rank",
        direction: "greater-than"
    },*/
    imd_decile: {
        name: "IMD Decile",
        units: "percent",
        direction: "greater-than",
        average: null,
        deciles: [],
    },
};

export { nfviColumns };
