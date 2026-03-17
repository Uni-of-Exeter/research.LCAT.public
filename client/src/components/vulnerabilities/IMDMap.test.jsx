import { cleanup, render, screen } from "@testing-library/react";
import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { centreFromBbox, zoomFromBbox } from "./IMDMap.jsx";
import IMDMap from "./IMDMap.jsx";

vi.mock("react-collapsed", () => ({
    useCollapse: () => ({
        getCollapseProps: () => ({}),
        getToggleProps: () => ({}),
    }),
}));

vi.mock("./LinkOutIcon", () => ({
    default: () => null,
}));

describe("zoomFromBbox", () => {
    it("returns zoom 5 for very large span (> 8 degrees)", () => {
        expect(zoomFromBbox({ min_lat: 50, max_lat: 59, min_lon: -5, max_lon: 2 })).toBe(5);
    });

    it("returns zoom 6 for span > 4 degrees", () => {
        expect(zoomFromBbox({ min_lat: 50, max_lat: 55, min_lon: 0, max_lon: 1 })).toBe(6);
    });

    it("returns zoom 7 for span > 2 degrees", () => {
        expect(zoomFromBbox({ min_lat: 50, max_lat: 53, min_lon: 0, max_lon: 1 })).toBe(7);
    });

    it("returns zoom 8 for span > 1 degree", () => {
        expect(zoomFromBbox({ min_lat: 51, max_lat: 52.5, min_lon: 0, max_lon: 1 })).toBe(8);
    });

    it("returns zoom 9 for span > 0.5 degrees", () => {
        expect(zoomFromBbox({ min_lat: 51.0, max_lat: 51.6, min_lon: 0, max_lon: 0.1 })).toBe(9);
    });

    it("returns zoom 10 for span > 0.2 degrees", () => {
        expect(zoomFromBbox({ min_lat: 51.0, max_lat: 51.3, min_lon: 0, max_lon: 0.1 })).toBe(10);
    });

    it("returns zoom 11 for very small span (<= 0.2 degrees)", () => {
        expect(zoomFromBbox({ min_lat: 51.0, max_lat: 51.1, min_lon: 0, max_lon: 0.1 })).toBe(11);
    });

    it("uses the larger of lat/lon span", () => {
        // lat span = 0.1, lon span = 5 → should use lon span → zoom 6
        expect(zoomFromBbox({ min_lat: 51.0, max_lat: 51.1, min_lon: 0, max_lon: 5 })).toBe(6);
    });
});

describe("centreFromBbox", () => {
    it("returns the midpoint of lat and lon", () => {
        const result = centreFromBbox({ min_lat: 50, max_lat: 52, min_lon: -2, max_lon: 0 });
        expect(result).toEqual({ lat: 51, lon: -1 });
    });

    it("handles negative coordinates correctly", () => {
        const result = centreFromBbox({ min_lat: -10, max_lat: 10, min_lon: -20, max_lon: 20 });
        expect(result).toEqual({ lat: 0, lon: 0 });
    });

    it("handles non-integer midpoints", () => {
        const result = centreFromBbox({ min_lat: 51.0, max_lat: 51.5, min_lon: -1.5, max_lon: -1.0 });
        expect(result).toEqual({ lat: 51.25, lon: -1.25 });
    });
});

const ENGLAND = { id: 1, name: "Cornwall", country: "England" };
const SCOTLAND = { id: 2, name: "Glasgow", country: "Scotland" };
const WALES = { id: 3, name: "Cardiff", country: "Wales" };
const NI = { id: 4, name: "Belfast", country: "Northern Ireland" };

describe("IMDMap link rendering", () => {
    afterEach(cleanup);
    it("renders nothing when regions is empty", () => {
        const { container } = render(<IMDMap regions={[]} regionType="boundary_uk_counties" />);
        expect(container.firstChild).toBeNull();
    });

    it("shows England link and hides others for an English region", () => {
        render(<IMDMap regions={[ENGLAND]} regionType="boundary_uk_counties" />);
        expect(screen.getByRole("link", { name: /deprivation data for England/i })).toBeInTheDocument();
        expect(screen.queryByRole("link", { name: /deprivation data for Scotland/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Wales/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Northern Ireland/i })).toBeNull();
    });

    it("shows Scotland link and hides others for a Scottish region", () => {
        render(<IMDMap regions={[SCOTLAND]} regionType="boundary_uk_counties" />);
        expect(screen.getByRole("link", { name: /deprivation data for Scotland/i })).toBeInTheDocument();
        expect(screen.queryByRole("link", { name: /deprivation data for England/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Wales/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Northern Ireland/i })).toBeNull();
    });

    it("shows Wales link and hides others for a Welsh region", () => {
        render(<IMDMap regions={[WALES]} regionType="boundary_uk_counties" />);
        expect(screen.getByRole("link", { name: /deprivation data for Wales/i })).toBeInTheDocument();
        expect(screen.queryByRole("link", { name: /deprivation data for England/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Scotland/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Northern Ireland/i })).toBeNull();
    });

    it("shows Northern Ireland link and hides others for an NI region", () => {
        render(<IMDMap regions={[NI]} regionType="boundary_uk_counties" />);
        expect(screen.getByRole("link", { name: /deprivation data for Northern Ireland/i })).toBeInTheDocument();
        expect(screen.queryByRole("link", { name: /deprivation data for England/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Scotland/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Wales/i })).toBeNull();
    });

    it("shows England and Wales links for mixed regions", () => {
        render(<IMDMap regions={[ENGLAND, WALES]} regionType="boundary_uk_counties" />);
        expect(screen.getByRole("link", { name: /deprivation data for England/i })).toBeInTheDocument();
        expect(screen.getByRole("link", { name: /deprivation data for Wales/i })).toBeInTheDocument();
        expect(screen.queryByRole("link", { name: /deprivation data for Scotland/i })).toBeNull();
        expect(screen.queryByRole("link", { name: /deprivation data for Northern Ireland/i })).toBeNull();
    });

    it("England link uses hardcoded default coordinates when no bbox is fetched", () => {
        render(<IMDMap regions={[ENGLAND]} regionType="boundary_uk_counties" />);
        const link = screen.getByRole("link", { name: /deprivation data for England/i });
        expect(link.href).toContain("lat=52.5");
        expect(link.href).toContain("lon=-1.5");
        expect(link.href).toContain("zoom=8");
    });

    it("Scotland link uses hardcoded default coordinates when no bbox is fetched", () => {
        render(<IMDMap regions={[SCOTLAND]} regionType="boundary_uk_counties" />);
        const link = screen.getByRole("link", { name: /deprivation data for Scotland/i });
        expect(link.href).toContain("/8/");
        expect(link.href).toContain("/-4/");
        expect(link.href).toContain("/56.5/");
    });

    it("Wales link points to the correct static URL", () => {
        render(<IMDMap regions={[WALES]} regionType="boundary_uk_counties" />);
        const link = screen.getByRole("link", { name: /deprivation data for Wales/i });
        expect(link.href).toContain("datamap.gov.wales");
    });

    it("Northern Ireland link points to the correct static URL", () => {
        render(<IMDMap regions={[NI]} regionType="boundary_uk_counties" />);
        const link = screen.getByRole("link", { name: /deprivation data for Northern Ireland/i });
        expect(link.href).toContain("datavis.nisra.gov.uk");
    });
});
