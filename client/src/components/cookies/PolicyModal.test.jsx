import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import CookiePolicyModal from "./PolicyModal";

describe("CookiePolicyModal", () => {
    afterEach(cleanup);

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
        fireEvent.click(screen.getByRole("button", { name: /close cookie policy overlay/i }));
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("calls onClose when Escape is pressed", () => {
        const onClose = vi.fn();
        render(<CookiePolicyModal open={true} onClose={onClose} />);
        fireEvent.keyDown(window, { key: "Escape" });
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});
