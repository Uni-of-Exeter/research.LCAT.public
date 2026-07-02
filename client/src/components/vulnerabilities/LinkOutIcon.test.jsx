import { render, cleanup } from "@testing-library/react";
import { describe, expect, it, afterEach } from "vitest";

import LinkOutIcon from "./LinkOutIcon";

describe("LinkOutIcon", () => {
    afterEach(cleanup);

    it("renders an svg with default size", () => {
        const { container } = render(<LinkOutIcon />);
        const svg = container.querySelector("svg");
        expect(svg).toBeInTheDocument();
        expect(svg).toHaveAttribute("width", "1em");
    });

    it("respects the size and colour props", () => {
        const { container } = render(<LinkOutIcon size="2em" colour="red" />);
        const svg = container.querySelector("svg");
        expect(svg).toHaveAttribute("width", "2em");
        expect(svg.querySelector("path")).toHaveAttribute("stroke", "red");
    });
});
