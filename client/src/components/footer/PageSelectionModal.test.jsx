import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import PageSelectionModal from "./PageSelectionModal";

const PAGES = [
    { id: "intro", title: "Introduction", defaultSelected: true },
    { id: "hazards", title: "Hazards", defaultSelected: false },
];

const renderModal = (overrides = {}) =>
    render(
        <PageSelectionModal
            isOpen={true}
            onClose={overrides.onClose || (() => {})}
            onGenerate={overrides.onGenerate || (() => {})}
            availablePages={overrides.availablePages || PAGES}
        />,
    );

describe("PageSelectionModal", () => {
    afterEach(cleanup);

    it("renders nothing when closed", () => {
        const { container } = render(
            <PageSelectionModal isOpen={false} onClose={() => {}} onGenerate={() => {}} availablePages={PAGES} />,
        );
        expect(container.firstChild).toBeNull();
    });

    it("renders a checkbox per page with default selection", () => {
        renderModal();
        expect(screen.getByRole("checkbox", { name: /Include Introduction in report/i })).toBeChecked();
        expect(screen.getByRole("checkbox", { name: /Include Hazards in report/i })).not.toBeChecked();
    });

    it("updates the selected-page count when a checkbox is toggled", () => {
        renderModal();
        expect(screen.getByRole("button", { name: /Generate Report \(1 page\)/i })).toBeInTheDocument();
        fireEvent.click(screen.getByRole("checkbox", { name: /Include Hazards in report/i }));
        expect(screen.getByRole("button", { name: /Generate Report \(2 pages\)/i })).toBeInTheDocument();
    });

    it("disables Generate when no pages are selected", () => {
        renderModal();
        fireEvent.click(screen.getByRole("checkbox", { name: /Include Introduction in report/i }));
        expect(screen.getByRole("button", { name: /Generate Report \(0 pages\)/i })).toBeDisabled();
    });

    it("generates with the selected page ids then closes", () => {
        const onGenerate = vi.fn();
        const onClose = vi.fn();
        renderModal({ onGenerate, onClose });
        fireEvent.click(screen.getByRole("button", { name: /Generate Report \(1 page\)/i }));
        expect(onGenerate).toHaveBeenCalledWith(["intro"]);
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("closes on Cancel", () => {
        const onClose = vi.fn();
        renderModal({ onClose });
        fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("closes on Escape", () => {
        const onClose = vi.fn();
        renderModal({ onClose });
        fireEvent.keyDown(window, {
            key: "Escape",
        });
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("closes when the overlay itself is clicked", () => {
        const onClose = vi.fn();
        renderModal({ onClose });
        const dialog = screen.getByRole("dialog", { name: /select report pages/i });
        const overlay = dialog.parentElement;
        expect(overlay).not.toBeNull();

        fireEvent.click(overlay);
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});
