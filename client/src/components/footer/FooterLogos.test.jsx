import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import FooterLogos from "./FooterLogos";

describe("FooterLogos", () => {
    afterEach(cleanup);

    it("renders the partner logos image with descriptive alt text", () => {
        render(<FooterLogos />);
        expect(screen.getByRole("img", { name: /Partner logos: University of Exeter/i })).toBeInTheDocument();
    });

    it("renders the funder logos image with descriptive alt text", () => {
        render(<FooterLogos />);
        expect(screen.getByRole("img", { name: /Funder logos: Co-funded by the European Union/i })).toBeInTheDocument();
    });
});
