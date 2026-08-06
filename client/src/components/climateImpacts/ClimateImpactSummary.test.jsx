import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import ClimateImpactSummary from "./ClimateImpactSummary";

const baseProps = {
    loading: false,
    selectedImpactHazard: "Extreme Storms",
    setSelectedImpactHazard: () => {},
    applyCoastalFilter: false,
};

describe("ClimateImpactSummary", () => {
    afterEach(cleanup);

    it("renders the impact pathway options", () => {
        render(<ClimateImpactSummary {...baseProps} />);
        expect(screen.getByRole("option", { name: "Extreme Storms" })).toBeInTheDocument();
        expect(screen.getByRole("option", { name: "Temperature" })).toBeInTheDocument();
        expect(screen.getByRole("option", { name: "Coastal Security" })).toBeInTheDocument();
    });

    it("shows the loading overlay text while loading", () => {
        render(<ClimateImpactSummary {...baseProps} loading={true} />);
        expect(screen.getByText("Loading impact summaries")).toBeInTheDocument();
    });

    it("calls setSelectedImpactHazard when the pathway changes", () => {
        const setSelectedImpactHazard = vi.fn();
        render(<ClimateImpactSummary {...baseProps} setSelectedImpactHazard={setSelectedImpactHazard} />);
        fireEvent.change(screen.getByRole("combobox"), { target: { value: "Temperature" } });
        expect(setSelectedImpactHazard).toHaveBeenCalledWith("Temperature");
    });

    it("removes coastal pathways when the coastal filter is applied", () => {
        render(<ClimateImpactSummary {...baseProps} applyCoastalFilter={true} />);
        expect(screen.queryByRole("option", { name: "Coastal Security" })).toBeNull();
        expect(screen.queryByRole("option", { name: "Marine Health Hazards" })).toBeNull();
        expect(screen.getByRole("option", { name: "Extreme Storms" })).toBeInTheDocument();
    });
});
