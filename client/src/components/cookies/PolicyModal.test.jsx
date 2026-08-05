import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import CookiePolicyModal from "./PolicyModal";

window.scrollTo = vi.fn();

describe("CookiePolicyModal", () => {
    afterEach(() => {
        cleanup();
        document.body.style.position = "";
        document.body.style.top = "";
        document.body.style.width = "";
    });

    it("renders nothing when closed", () => {
        const { container } = render(<CookiePolicyModal open={false} onClose={() => {}} />);
        expect(container.firstChild).toBeNull();
    });

    it("renders an accessible modal dialog when open", () => {
        render(<CookiePolicyModal open={true} onClose={() => {}} />);
        const dialog = screen.getByRole("dialog");
        expect(dialog).toHaveAttribute("aria-modal", "true");
    });

    it("calls onClose when the overlay is clicked", () => {
        const onClose = vi.fn();
        render(<CookiePolicyModal open={true} onClose={onClose} />);
        const dialog = screen.getByRole("dialog", { name: /cookie policy/i });
        const overlay = dialog.firstElementChild;
        expect(overlay).not.toBeNull();

        fireEvent.click(overlay);
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("calls onClose when Escape is pressed", () => {
        const onClose = vi.fn();
        render(<CookiePolicyModal open={true} onClose={onClose} />);
        fireEvent.keyDown(window, { key: "Escape" });
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("restores pre-existing inline body styles when it closes", () => {
        document.body.style.position = "relative";
        document.body.style.top = "12px";
        document.body.style.width = "80%";

        const { rerender } = render(<CookiePolicyModal open={true} onClose={() => {}} />);

        expect(document.body.style.position).toBe("fixed");
        expect(document.body.style.top).toBe("0px");
        expect(document.body.style.width).toBe("100%");

        rerender(<CookiePolicyModal open={false} onClose={() => {}} />);

        expect(document.body.style.position).toBe("relative");
        expect(document.body.style.top).toBe("12px");
        expect(document.body.style.width).toBe("80%");
    });

    it("keeps focus trapped in the modal and restores prior focus on close", () => {
        const onClose = vi.fn();

        const { rerender } = render(
            <>
                <button type="button">Before modal</button>
                <CookiePolicyModal open={false} onClose={onClose} />
            </>,
        );

        const beforeButton = screen.getByRole("button", { name: "Before modal" });
        beforeButton.focus();

        rerender(
            <>
                <button type="button">Before modal</button>
                <CookiePolicyModal open={true} onClose={onClose} />
            </>,
        );

        const closeButton = screen.getByRole("button", { name: /close cookie policy/i });
        const policyLink = screen.getByRole("link", { name: /google's cookie policy/i });

        closeButton.focus();
        fireEvent.keyDown(window, { key: "Tab", shiftKey: true });
        expect(policyLink).toHaveFocus();

        policyLink.focus();
        fireEvent.keyDown(window, { key: "Tab" });
        expect(closeButton).toHaveFocus();

        rerender(
            <>
                <button type="button">Before modal</button>
                <CookiePolicyModal open={false} onClose={onClose} />
            </>,
        );

        expect(beforeButton).toHaveFocus();
    });
});
