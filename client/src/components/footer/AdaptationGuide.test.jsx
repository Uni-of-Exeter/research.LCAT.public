import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { ADAPTATION_INTRO_PDF_URL } from "../../utils/constants";
import AdaptationGuide from "./AdaptationGuide";

describe("AdaptationGuide", () => {
    afterEach(cleanup);

    it("shows the adaptation guide heading", () => {
        render(<AdaptationGuide />);
        expect(screen.getByText("Learn About Climate Adaptation.")).toBeInTheDocument();
    });

    it("links to the adaptation intro PDF", () => {
        render(<AdaptationGuide />);
        const link = screen.getByRole("link", { name: /Introduction to Local Climate Adaptation \(at ecehh\.org\)/i });
        expect(link).toHaveAttribute("href", ADAPTATION_INTRO_PDF_URL);
    });
});
