import { describe, expect, it } from "vitest";

import { climateChange, climateVariables, formatClimateData } from "./climateUtils";

const buildPrediction = (overrides = {}) => [
    {
        tas_1980: "10",
        tas_2050: "12.5",
        pr_1980: "1",
        pr_2050: "2",
        rsds_1980: "10",
        rsds_2050: "12",
        sfcWind_1980: "5",
        sfcWind_2050: "3",
        ...overrides,
    },
];

describe("climateChange", () => {
    it("returns the difference between baseline and prediction", () => {
        const prediction = buildPrediction();
        expect(climateChange(prediction, "tas", 2050)).toBe(2.5);
    });

    it("returns null when prediction is empty", () => {
        expect(climateChange([], "tas", 2050)).toBeNull();
    });
});

describe("formatClimateData", () => {
    it("returns a no-data message when value is null", () => {
        const result = formatClimateData([], "tas", "Temperature", "°C", 2050);

        expect(result).toEqual({
            name: "Temperature",
            value: null,
            change: "No data yet for this area, coming soon.",
            arrow: null,
            direction: null,
        });
    });

    it("formats positive changes with an up arrow", () => {
        const prediction = buildPrediction({
            pr_1980: "1",
            pr_2050: "2",
        });
        const result = formatClimateData(prediction, "pr", "Rainfall", "mm/day", 2050);

        expect(result).toMatchObject({
            name: "Rainfall",
            value: 1,
            change: "Rainfall increases by 1.00 mm/day",
            arrow: "up",
            direction: "increases",
            absoluteValue: "1.00",
            units: "mm/day",
        });
    });

    it("formats negative changes with a down arrow", () => {
        const prediction = buildPrediction({
            sfcWind_1980: "5",
            sfcWind_2050: "3",
        });
        const result = formatClimateData(prediction, "sfcWind", "Windiness", "m/sec", 2050);

        expect(result).toMatchObject({
            name: "Windiness",
            value: -2,
            change: "Windiness decreases by 2.00 m/sec",
            arrow: "down",
            direction: "decreases",
            absoluteValue: "2.00",
            units: "m/sec",
        });
    });

    it("formats zero change without arrows", () => {
        const prediction = buildPrediction({
            tas_1980: "4",
            tas_2050: "4",
        });
        const result = formatClimateData(prediction, "tas", "Temperature", "°C", 2050);

        expect(result).toMatchObject({
            name: "Temperature",
            value: 0,
            change: "No change in Temperature",
            arrow: "none",
            direction: "No change in",
        });
    });

    it("uses plural direction for day-based variables", () => {
        const prediction = buildPrediction({
            dry_days_1980: "10",
            dry_days_2050: "15",
        });
        const result = formatClimateData(prediction, "dry_days", "Dry Days", "days", 2050);

        expect(result).toMatchObject({
            arrow: "up",
            direction: "increase",
            change: "Dry Days increase by 5.00 days",
        });
    });
});

describe("climateVariables", () => {
    it("defines the available climate variables", () => {
        expect(climateVariables).toEqual(
            expect.arrayContaining([
                expect.objectContaining({ variable: "tas", name: "Temperature", units: "°C" }),
                expect.objectContaining({ variable: "pr", name: "Rainfall", units: "mm/day" }),
                expect.objectContaining({ variable: "sfcWind", name: "Windiness", units: "m/sec" }),
                expect.objectContaining({ variable: "rsds", name: "Radiation", units: "Watts/m²" }),
            ]),
        );
    });
});
