import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import FooterText from "./FooterText";

describe("FooterText", () => {
    afterEach(cleanup);

    it("names the lead developing organisation", () => {
        render(<FooterText />);
        expect(screen.getByText(/Local Climate Adaptation Tool has been developed/i)).toBeInTheDocument();
    });

    it("links to the open-source code repository", () => {
        render(<FooterText />);
        const link = screen.getByRole("link", { name: /Source code published/i });
        expect(link).toHaveAttribute("href", "https://github.com/Uni-of-Exeter/research.LCAT.public");
    });

    it("dispatches open_cookie_banner when 'Manage cookies' is clicked", () => {
        const handler = vi.fn();
        window.addEventListener("open_cookie_banner", handler);
        render(<FooterText />);

        fireEvent.click(screen.getByRole("button", { name: /manage cookies/i }));

        expect(handler).toHaveBeenCalledTimes(1);
        window.removeEventListener("open_cookie_banner", handler);
    });
});
