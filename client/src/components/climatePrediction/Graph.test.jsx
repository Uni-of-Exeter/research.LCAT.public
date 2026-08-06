import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Graph from "./Graph";
import { createGraphProps } from "./Graph.test-fixtures";

vi.mock("react-plotly.js", () => ({
    default: () => <div aria-label="Climate graph" role="img" />,
}));

describe("Graph", () => {
    afterEach(() => {
        cleanup();
        vi.clearAllMocks();
    });

    it("keeps the data table hidden by default and reveals it with the toggle", () => {
        render(<Graph {...createGraphProps()} />);

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
        render(<Graph {...createGraphProps()} />);

        fireEvent.click(screen.getByText(/explore climate details/i));
        fireEvent.change(screen.getByRole("combobox", { name: /displayed area/i }), {
            target: { value: "1" },
        });
        fireEvent.click(screen.getByRole("button", { name: /show data table/i }));

        expect(screen.getByRole("columnheader", { name: /uk average/i })).toBeInTheDocument();
        expect(screen.getByText("9.50")).toBeInTheDocument();
    });
});
