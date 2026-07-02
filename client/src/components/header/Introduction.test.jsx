import { cleanup,render, screen } from "@testing-library/react";
import { afterEach,describe, expect, it } from "vitest";

import { LCAT_HANDBOOK_URL } from "../../utils/constants";
import Introduction from "./Introduction";

describe("Introduction", () => {
    afterEach(cleanup);

    it("summarises what the tool shows", () => {
        render(<Introduction />);
        expect(screen.getByText(/see what the scientific research is saying about/i)).toBeInTheDocument();
    });

    it("lists the LCAT Handbook as a helpful resource", () => {
        render(<Introduction />);
        const link = screen.getByRole("link", { name: "LCAT Handbook" });
        expect(link).toHaveAttribute("href", LCAT_HANDBOOK_URL);
    });

    it("links to the Met Office Local Authority Climate Service", () => {
        render(<Introduction />);
        const link = screen.getByRole("link", { name: /Met Office Local Authority Climate Service/i });
        expect(link).toHaveAttribute("href", "https://climatedataportal.metoffice.gov.uk/pages/lacs");
    });
});
