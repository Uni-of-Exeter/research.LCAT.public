import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";

import ClimateMap from "./ClimateMap";

vi.mock("@tanstack/react-virtual", () => ({
    useVirtualizer: () => ({
        getTotalSize: () => 0,
        getVirtualItems: () => [],
    }),
}));

vi.mock("react-leaflet", () => ({
    MapContainer: ({ children }) => <div data-testid="map-container">{children}</div>,
    GeoJSON: () => <div data-testid="geojson-layer" />,
    TileLayer: () => <div data-testid="tile-layer" />,
}));

vi.mock("./GeoJSONLoader.jsx", () => ({
    default: () => null,
}));

describe("ClimateMap accessibility", () => {
    it("has no detectable accessibility violations in its default state", async () => {
        const { container } = render(
            <ClimateMap
                regions={[]}
                setRegions={() => { }}
                allRegions={[]}
                regionType="boundary_uk_counties"
                setRegionType={() => { }}
            />,
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
        expect(screen.getByRole("heading", { name: /select your area/i })).toBeInTheDocument();
        expect(screen.getByRole("combobox", { name: /boundary type/i })).toBeInTheDocument();
    });
});
