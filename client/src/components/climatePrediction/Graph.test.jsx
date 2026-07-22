import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Graph from "./Graph";

vi.mock("react-plotly.js", () => ({
    default: () => <div aria-label="Climate graph" role="img" />,
}));

class ResizeObserverMock {
    observe() { }

    disconnect() { }
}

window.ResizeObserver = ResizeObserverMock;

const basePrediction = [
    {
        tas_1980: 10,
        tas_2020: 11,
        tas_2050: 12,
        tas_2080: 13,
        tasmin_1_percentile_1980: 8,
        tasmin_1_percentile_2020: 9,
        tasmin_1_percentile_2050: 10,
        tasmin_1_percentile_2080: 11,
        tasmax_99_percentile_1980: 12,
        tasmax_99_percentile_2020: 13,
        tasmax_99_percentile_2050: 14,
        tasmax_99_percentile_2080: 15,
    },
];

const baseAverages = {
    1980: 9.5,
    2020: 10.5,
    2050: 11.5,
    2080: 12.5,
};

const baseProps = {
    regions: [{ name: "Cornwall" }],
    season: "annual",
    rcp: "rcp60",
    setSeason: vi.fn(),
    setRcp: vi.fn(),
    loading: false,
    climatePrediction: basePrediction,
    climateAverages: baseAverages,
    variable: "tas",
    setVariable: vi.fn(),
};

describe("Graph", () => {
    afterEach(() => {
        cleanup();
        vi.clearAllMocks();
    });

    it("keeps the data table hidden by default and reveals it with the toggle", () => {
        render(<Graph {...baseProps} />);

        fireEvent.click(screen.getByText(/explore climate details/i));

        const toggle = screen.getByRole("button", { name: /show data table/i });
        expect(toggle).toHaveAttribute("aria-expanded", "false");
        expect(screen.queryByRole("table")).toBeNull();

        fireEvent.click(toggle);

        expect(screen.getByRole("button", { name: /hide data table/i })).toHaveAttribute("aria-expanded", "true");
        expect(screen.getByRole("table")).toBeInTheDocument();
        expect(screen.getByText(/data table alternative for the climate graph/i)).toBeInTheDocument();
        expect(screen.getByRole("rowheader", { name: /1980 baseline/i })).toBeInTheDocument();
        expect(screen.getByRole("columnheader", { name: /your areas \(min\)/i })).toBeInTheDocument();
        expect(screen.queryByRole("columnheader", { name: /uk average/i })).toBeNull();
    });

    it("adds UK average values to the data table when comparison is selected", () => {
        render(<Graph {...baseProps} />);

        fireEvent.click(screen.getByText(/explore climate details/i));
        fireEvent.change(screen.getByRole("combobox", { name: /displayed area/i }), {
            target: { value: "1" },
        });
        fireEvent.click(screen.getByRole("button", { name: /show data table/i }));

        expect(screen.getByRole("columnheader", { name: /uk average/i })).toBeInTheDocument();
        expect(screen.getByText("9.50")).toBeInTheDocument();
    });
});
