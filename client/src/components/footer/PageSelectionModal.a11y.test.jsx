import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";

import PageSelectionModal from "./PageSelectionModal";

const PAGES = [
    { id: "intro", title: "Introduction", defaultSelected: true },
    { id: "hazards", title: "Hazards", defaultSelected: false },
];

describe("PageSelectionModal accessibility", () => {
    it("has no detectable accessibility violations when open", async () => {
        const { container } = render(
            <PageSelectionModal isOpen={true} onClose={() => { }} onGenerate={() => { }} availablePages={PAGES} />,
        );

        const results = await axe(container);
        expect(results).toHaveNoViolations();
        expect(screen.getByRole("dialog", { name: /select report pages/i })).toHaveAttribute("aria-modal", "true");
    });
});
