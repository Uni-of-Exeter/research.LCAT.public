import { render, screen, cleanup } from "@testing-library/react";
import { describe, expect, it, afterEach } from "vitest";

import Feedback from "./Feedback";

describe("Feedback", () => {
    afterEach(cleanup);

    it("shows the evaluation survey heading", () => {
        render(<Feedback />);
        expect(screen.getByRole("heading", { name: /evaluation survey/i })).toBeInTheDocument();
    });

    it("links to the survey in a new tab with an accessible name", () => {
        render(<Feedback />);
        const link = screen.getByRole("link", { name: /Access the evaluation survey in a new tab/i });
        expect(link).toHaveAttribute("href", expect.stringContaining("forms.office.com"));
        expect(link).toHaveAttribute("target", "_blank");
    });
});
