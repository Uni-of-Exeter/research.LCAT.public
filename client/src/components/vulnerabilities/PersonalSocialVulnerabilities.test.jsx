import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import PersonalSocialVulnerabilities from "./PersonalSocialVulnerabilities";

describe("PersonalSocialVulnerabilities", () => {
    afterEach(cleanup);

    it("renders a button for each vulnerability", () => {
        render(<PersonalSocialVulnerabilities />);
        expect(screen.getByRole("button", { name: /older people/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /people on low incomes/i })).toBeInTheDocument();
    });

    it("shows the placeholder prompt before a vulnerability is selected", () => {
        render(<PersonalSocialVulnerabilities />);
        expect(screen.getByText(/Please click a vulnerability icon to view details\./i)).toBeInTheDocument();
    });

    it("shows details and a ClimateJust source link once a vulnerability is clicked", () => {
        render(<PersonalSocialVulnerabilities />);
        fireEvent.click(screen.getByRole("button", { name: /older people/i }));
        expect(screen.getByRole("heading", { name: "Older people" })).toBeInTheDocument();
        const link = screen.getByRole("link", { name: /vulnerability insight, by theme, from ClimateJust/i });
        expect(link).toHaveAttribute("href", "https://climatejust.org.uk");
    });
});
