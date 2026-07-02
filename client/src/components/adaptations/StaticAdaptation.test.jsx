import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../../kumu/parsed/processed_references.json", () => ({ default: {} }));

import StaticAdaptation from "./StaticAdaptation";

const adaptation = {
    _id: "a1",
    attributes: {
        label: "Install green roofs",
        description: "Green roofs reduce urban heat and rainfall runoff.",
        aggregated_layers: ["Flooding", "Heatwaves"],
        reference_id: [],
    },
};

describe("StaticAdaptation", () => {
    afterEach(cleanup);

    it("renders the adaptation label", () => {
        render(<StaticAdaptation adaptation={adaptation} selectedHazards={[]} />);
        expect(screen.getByText("Install green roofs")).toBeInTheDocument();
    });

    it("reveals the description when the header is expanded", () => {
        const { container } = render(<StaticAdaptation adaptation={adaptation} selectedHazards={[]} />);
        // react-collapsed keeps content mounted, so check aria-expanded instead
        const toggleElement = container.querySelector("[aria-expanded]");
        expect(toggleElement?.getAttribute("aria-expanded")).toBe("false");
        fireEvent.click(screen.getByText("Install green roofs"));
        expect(toggleElement?.getAttribute("aria-expanded")).toBe("true");
        expect(screen.getByText(/Green roofs reduce urban heat/i)).toBeInTheDocument();
    });

    it("lists related impact pathways not already selected", () => {
        render(<StaticAdaptation adaptation={adaptation} selectedHazards={[]} />);
        fireEvent.click(screen.getByText("Install green roofs"));
        const pathwaysElement = screen.getByText(/Related impact pathways:/i).closest("p");
        expect(pathwaysElement).toHaveTextContent("Related impact pathways: Flooding, Heatwaves");
    });
});
