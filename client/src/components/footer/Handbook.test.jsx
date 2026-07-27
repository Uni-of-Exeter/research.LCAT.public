import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { LCAT_HANDBOOK_URL } from "../../utils/constants";
import Handbook from "./Handbook";

describe("Handbook", () => {
    afterEach(cleanup);

    it("shows the handbook heading", () => {
        render(<Handbook />);
        expect(screen.getByText("Access our Handbook.")).toBeInTheDocument();
    });

    it("links to the handbook PDF", () => {
        render(<Handbook />);
        const link = screen.getByRole("link", { name: /LCAT Handbook \(at ecehh\.org\)/i });
        expect(link).toHaveAttribute("href", LCAT_HANDBOOK_URL);
        expect(link).toHaveAttribute("target", "_blank");
    });
});
