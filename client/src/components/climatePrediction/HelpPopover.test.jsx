import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import HelpPopover from "./HelpPopover";

describe("HelpPopover", () => {
    afterEach(cleanup);

    it("renders nothing when there is no content", () => {
        const { container } = render(<HelpPopover content={null}>trigger</HelpPopover>);
        expect(container.firstChild).toBeNull();
    });

    it("renders the trigger with its children", () => {
        render(<HelpPopover content="Helpful details">Temperature</HelpPopover>);
        const trigger = screen.getByRole("button", { name: /more information/i });
        expect(trigger).toHaveTextContent("Temperature");
    });

    it("keeps the content hidden until the trigger is clicked", () => {
        render(<HelpPopover content="Helpful details">Temperature</HelpPopover>);
        expect(screen.queryByText("Helpful details")).toBeNull();
        fireEvent.click(screen.getByRole("button", { name: /more information/i }));
        expect(screen.getByText("Helpful details")).toBeInTheDocument();
    });

    it("toggles the content off on a second click", () => {
        render(<HelpPopover content="Helpful details">Temperature</HelpPopover>);
        const trigger = screen.getByRole("button", { name: /more information/i });
        fireEvent.click(trigger);
        fireEvent.click(trigger);
        expect(screen.queryByText("Helpful details")).toBeNull();
    });

    it("shows the content on hover", () => {
        render(<HelpPopover content="Helpful details">Temperature</HelpPopover>);
        fireEvent.mouseEnter(screen.getByRole("button", { name: /more information/i }));
        expect(screen.getByText("Helpful details")).toBeInTheDocument();
    });

    it("closes on Escape after being opened", () => {
        render(<HelpPopover content="Helpful details">Temperature</HelpPopover>);
        fireEvent.click(screen.getByRole("button", { name: /more information/i }));
        fireEvent.keyDown(document, { key: "Escape" });
        expect(screen.queryByText("Helpful details")).toBeNull();
    });
});
