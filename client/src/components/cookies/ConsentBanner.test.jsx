import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import CookieConsent from "./ConsentBanner";

describe("CookieConsent", () => {
    beforeEach(() => {
        localStorage.clear();
        delete window.gtag;
    });
    afterEach(cleanup);

    it("shows the banner when no consent choice is stored", () => {
        render(<CookieConsent />);
        expect(screen.getByText(/We use cookies to improve your experience/i)).toBeInTheDocument();
    });

    it("stays hidden when consent was already granted", () => {
        localStorage.setItem("cookie_consent", "true");
        render(<CookieConsent />);
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();
    });

    it("stores acceptance and hides the banner", () => {
        render(<CookieConsent />);
        fireEvent.click(screen.getByRole("button", { name: /accept all cookies/i }));
        expect(localStorage.getItem("cookie_consent")).toBe("true");
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();
    });

    it("stores rejection and hides the banner", () => {
        render(<CookieConsent />);
        fireEvent.click(screen.getByRole("button", { name: /reject non-essential cookies/i }));
        expect(localStorage.getItem("cookie_consent")).toBe("false");
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();
    });

    it("opens the cookie policy dialog from the banner", () => {
        render(<CookieConsent />);
        expect(screen.queryByRole("dialog")).toBeNull();
        fireEvent.click(screen.getByRole("button", { name: /cookie policy/i }));
        expect(screen.getByRole("dialog")).toBeInTheDocument();
    });

    it("re-shows the banner when the open_cookie_banner event fires", () => {
        localStorage.setItem("cookie_consent", "true");
        render(<CookieConsent />);
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();

        fireEvent(window, new Event("open_cookie_banner"));

        expect(screen.getByText(/We use cookies to improve your experience/i)).toBeInTheDocument();
    });
});
