import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";

import CookiePolicyModal from "./PolicyModal";

describe("CookiePolicyModal accessibility", () => {
    it("has no detectable accessibility violations when open", async () => {
        const { container } = render(<CookiePolicyModal open={true} onClose={() => {}} />);

        const results = await axe(container);
        expect(results).toHaveNoViolations();
        expect(screen.getByRole("dialog", { name: /cookie policy/i })).toHaveAttribute("aria-modal", "true");
    });
});
