import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import ClimateHazardRisk from "./ClimateHazardRisk";

describe("ClimateHazardRisk", () => {
    afterEach(cleanup);

    it("renders a button for each climate hazard", () => {
        render(<ClimateHazardRisk applyCoastalFilter={false} />);
        expect(screen.getByRole("button", { name: /heatwaves/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /flooding/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /coastal erosion/i })).toBeInTheDocument();
    });

    it("shows the placeholder prompt before a hazard is selected", () => {
        render(<ClimateHazardRisk applyCoastalFilter={false} />);
        expect(screen.getByText(/Please click a climate hazard risk icon to view details\./i)).toBeInTheDocument();
    });

    it("shows details for the clicked hazard", () => {
        render(<ClimateHazardRisk applyCoastalFilter={false} />);
        fireEvent.click(screen.getByRole("button", { name: /heatwaves/i }));
        expect(screen.getByRole("heading", { name: "Heatwaves" })).toBeInTheDocument();
        expect(screen.queryByText(/Please click a climate hazard risk icon/i)).toBeNull();
    });

    it("hides Coastal Erosion when the coastal filter is applied", () => {
        render(<ClimateHazardRisk applyCoastalFilter={true} />);
        expect(screen.queryByRole("button", { name: /coastal erosion/i })).toBeNull();
        expect(screen.getByRole("button", { name: /heatwaves/i })).toBeInTheDocument();
    });
});
