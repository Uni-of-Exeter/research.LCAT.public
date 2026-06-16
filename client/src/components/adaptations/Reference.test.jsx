import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import Reference from "./Reference";

// Render with the real react-collapsed so the test exercises the actual
// controlled-toggle behaviour that regressed in commit 721cd31.
const baseProps = {
    link: "https://www.example.com/research/heat-health-article-123",
    title: "Heat and health in cities",
    type: "journal-article",
    article_id: "abc-123",
    authors: "Smith, J., Doe, A., Brown, B., Green, C.",
    journal: "Climate & Health",
    issue: "12(3)",
    date: "2022",
};

const renderReference = (overrides = {}) => render(<Reference {...baseProps} {...overrides} />);

describe("Reference", () => {
    afterEach(cleanup);

    it("shows the reference title", () => {
        renderReference();
        expect(screen.getByText(baseProps.title)).toBeInTheDocument();
    });

    it("falls back to a truncated link when no title is given", () => {
        renderReference({ title: undefined });
        expect(screen.getByText(`${baseProps.link.slice(0, 40)}...`)).toBeInTheDocument();
    });

    it("starts collapsed with the details (and source link) hidden", () => {
        const { container } = renderReference();
        expect(container.querySelector(".reference-container")).toHaveAttribute("aria-expanded", "false");
        // Collapsed details are not in the accessibility tree, so the source link is not yet reachable.
        expect(screen.queryByRole("link")).toBeNull();
    });

    // This is the regression guard: dropping `onClick: handleToggle` from
    // getToggleProps (as in the bug fixed by 721cd31) makes the title click a
    // no-op because the collapse is controlled by `isExpanded`.
    it("expands when the title is clicked, and collapses on a second click", () => {
        const { container } = renderReference();
        const refContainer = container.querySelector(".reference-container");
        const title = screen.getByText(baseProps.title);

        fireEvent.click(title);
        expect(refContainer).toHaveAttribute("aria-expanded", "true");

        fireEvent.click(title);
        expect(refContainer).toHaveAttribute("aria-expanded", "false");
    });

    it("toggles with the keyboard (Enter) on the container", () => {
        const { container } = renderReference();
        const refContainer = container.querySelector(".reference-container");

        fireEvent.keyDown(refContainer, { key: "Enter" });
        expect(refContainer).toHaveAttribute("aria-expanded", "true");
    });

    it("reveals the source as a clickable external link once expanded", () => {
        renderReference();
        fireEvent.click(screen.getByText(baseProps.title));

        const link = screen.getByRole("link");
        expect(link).toHaveAttribute("href", baseProps.link);
        expect(link).toHaveAttribute("target", "_blank");
        expect(link).toHaveAttribute("rel", "noopener noreferrer");
    });
});
