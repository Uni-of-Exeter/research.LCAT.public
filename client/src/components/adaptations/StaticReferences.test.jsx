import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../../kumu/parsed/processed_references.json", () => ({
    default: {
        1: {
            article_id: "1",
            title: "Heat and health in cities",
            type: "Journal Article",
            link: "https://example.com/heat",
            authors: "Smith, J.",
            journal: "Climate & Health",
            issue: "12(3)",
            date: "2022",
        },
    },
}));

import StaticReferences from "./StaticReferences";

describe("StaticReferences", () => {
    afterEach(cleanup);

    it("renders nothing when no ids resolve to a reference", () => {
        const { container } = render(<StaticReferences referenceIds={[999]} />);
        expect(container.firstChild).toBeNull();
    });

    it("renders a collapsible group header with the type and count", () => {
        render(<StaticReferences referenceIds={[1]} />);
        expect(screen.getByText("References:")).toBeInTheDocument();
        expect(screen.getByText("Journal Article (1)")).toBeInTheDocument();
    });

    it("reveals the reference title when the group header is clicked", () => {
        render(<StaticReferences referenceIds={[1]} />);
        const headerSpan = screen.getByText("Journal Article (1)");
        const header = headerSpan.closest(".reference-group-header");
        expect(header).toHaveAttribute("aria-expanded", "false");
        fireEvent.click(header);
        expect(header).toHaveAttribute("aria-expanded", "true");
    });
});
