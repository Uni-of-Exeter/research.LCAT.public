import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import ContactUs from "./ContactUs";

describe("ContactUs", () => {
    afterEach(cleanup);

    it("shows the contact heading", () => {
        render(<ContactUs />);
        expect(screen.getByRole("heading", { name: /need help\? contact us\./i })).toBeInTheDocument();
    });

    it("links to the LCAT email address", () => {
        render(<ContactUs />);
        const emailLink = screen.getByRole("link", { name: "lcat@exeter.ac.uk" });
        expect(emailLink).toHaveAttribute("href", "mailto:lcat@exeter.ac.uk");
    });
});
