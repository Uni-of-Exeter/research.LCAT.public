/* Development before 2024 Copyright (C) Then Try This and University of Exeter
Development from 2024 Copyright (C) University of Exeter

This program is free software: you can redistribute it and/or modify
it under the terms of the Common Good Public License Beta 1.0 as
published at http://www.cgpl.org

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Common Good Public License Beta 1.0 for more details. */

import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";

import AccessibilityStatement from "./AccessibilityStatement";

describe("AccessibilityStatement", () => {
    it("renders the standalone page when the accessibility statement hash is active", async () => {
        window.location.hash = "#accessibility-statement";

        const { container } = render(<AccessibilityStatement />);

        const headings = screen.getAllByRole("heading", { name: /accessibility statement/i });
        expect(headings.length).toBeGreaterThan(0);
        expect(screen.getByRole("heading", { name: /non-accessible content/i })).toBeInTheDocument();

        const results = await axe(container);
        expect(results).toHaveNoViolations();
    });
});
