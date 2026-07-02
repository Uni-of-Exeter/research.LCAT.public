import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../../kumu/parsed/processed_references.json", () => ({ default: {} }));
vi.mock("../../kumu/parsed/adaptation_data.json", () => ({
    default: [
        {
            _id: "a1",
            attributes: {
                label: "Adaptation One",
                description: "First adaptation",
                layer: ["flooding in full"],
                "ccc adaptation theme": ["Nature"],
                aggregated_layers: [],
                reference_id: [],
            },
        },
    ],
}));

import StaticAdaptations from "./StaticAdaptations";

const baseProps = {
    selectedAdaptationHazards: [],
    setSelectedAdaptationHazards: () => {},
    applyCoastalFilter: false,
    filterName: "No filter applied",
    setFilterName: () => {},
};

const renderAdaptations = (overrides = {}) => render(<StaticAdaptations {...baseProps} {...overrides} />);

describe("StaticAdaptations", () => {
    afterEach(cleanup);

    it("renders the heading and a pathway filter button per pathway", () => {
        renderAdaptations();
        expect(screen.getByRole("heading", { name: "Adaptations" })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /extreme storms/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /temperature/i })).toBeInTheDocument();
    });

    it("shows the matching adaptation and found-count", () => {
        renderAdaptations();
        expect(screen.getByText(/1 climate adaptation was found/i)).toBeInTheDocument();
        expect(screen.getByText("Adaptation One")).toBeInTheDocument();
    });

    it("selects a hazard when its pathway button is clicked", () => {
        const setSelectedAdaptationHazards = vi.fn();
        renderAdaptations({ setSelectedAdaptationHazards });
        fireEvent.click(screen.getByRole("button", { name: /extreme storms/i }));
        expect(setSelectedAdaptationHazards).toHaveBeenCalled();
    });

    it("clears hazards when Reset adaptation filters is clicked", () => {
        const setSelectedAdaptationHazards = vi.fn();
        renderAdaptations({ setSelectedAdaptationHazards });
        fireEvent.click(screen.getByRole("button", { name: /reset adaptation filters/i }));
        expect(setSelectedAdaptationHazards).toHaveBeenCalledWith([]);
    });

    it("changes the theme filter via the dropdown", () => {
        const setFilterName = vi.fn();
        renderAdaptations({ setFilterName });
        fireEvent.change(screen.getByRole("combobox"), { target: { value: "Nature" } });
        expect(setFilterName).toHaveBeenCalledWith("Nature");
    });

    it("reveals the reference source information when expanded", () => {
        renderAdaptations();
        expect(screen.queryByText(/The adaptation data is based on published scientific literature/i)).toBeNull();
        fireEvent.click(screen.getByRole("button", { name: /reference source information/i }));
        expect(screen.getByText(/The adaptation data is based on published scientific literature/i)).toBeInTheDocument();
    });
});
