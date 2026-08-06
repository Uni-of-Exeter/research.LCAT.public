import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import ClimateSettings from "./ClimateSettings";

const baseProps = {
    regions: [{ name: "Cornwall" }, { name: "Devon" }],
    rcp: "rcp60",
    season: "annual",
    setRcp: () => {},
    setSeason: () => {},
};

describe("ClimateSettings", () => {
    afterEach(cleanup);

    it("renders nothing when no regions are selected", () => {
        const { container } = render(<ClimateSettings {...baseProps} regions={[]} />);
        expect(container.firstChild).toBeNull();
    });

    it("lists the selected region names", () => {
        render(<ClimateSettings {...baseProps} />);
        expect(screen.getByText("Cornwall and Devon")).toBeInTheDocument();
    });

    it("shows the RCP 6.0 explanation for rcp60", () => {
        render(<ClimateSettings {...baseProps} rcp="rcp60" />);
        expect(screen.getByText(/global warming level of 2\.0-3\.7C which is RCP 6\.0/i)).toBeInTheDocument();
    });

    it("calls setRcp when the RCP dropdown changes", () => {
        const setRcp = vi.fn();
        render(<ClimateSettings {...baseProps} setRcp={setRcp} />);
        const rcpSelect = screen.getAllByRole("combobox")[0];
        fireEvent.change(rcpSelect, { target: { value: "rcp85" } });
        expect(setRcp).toHaveBeenCalledWith("rcp85");
    });

    it("calls setSeason when the season dropdown changes", () => {
        const setSeason = vi.fn();
        render(<ClimateSettings {...baseProps} setSeason={setSeason} />);
        const seasonSelect = screen.getAllByRole("combobox")[1];
        fireEvent.change(seasonSelect, { target: { value: "summer" } });
        expect(setSeason).toHaveBeenCalledWith("summer");
    });
});
