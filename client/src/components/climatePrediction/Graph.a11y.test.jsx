import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { afterEach, describe, expect, it, vi } from "vitest";

import Graph from "./Graph";
import { createGraphProps } from "./Graph.test-fixtures";

vi.mock("react-plotly.js", () => ({
    default: () => <div aria-label="Climate graph" role="img" />,
}));

describe("Graph accessibility", () => {
    afterEach(cleanup);

    it("has no detectable accessibility violations in its default collapsed state", async () => {
        const { container } = render(<Graph {...createGraphProps()} />);

        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });

    it("has no detectable accessibility violations when expanded and showing the data table", async () => {
        const { container } = render(<Graph {...createGraphProps()} />);

        fireEvent.click(screen.getByText(/explore climate details/i));
        fireEvent.click(screen.getByRole("button", { name: /show data table/i }));

        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });
});
