import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import ClimateSummary from "./ClimateSummary";

const prediction = [
    {
        tas_1980: "10",
        tas_2050: "12",
        pr_1980: "2",
        pr_2050: "1",
        dry_days_1980: "5",
        dry_days_2050: "8",
        sfcWind_1980: "4",
        sfcWind_2050: "4",
        tropical_nights_1980: "1",
        tropical_nights_2050: "3",
        hot_heat_days_1980: "0",
        hot_heat_days_2050: "2",
        heavy_rain_days_1980: "1",
        heavy_rain_days_2050: "2",
        rsds_1980: "100",
        rsds_2050: "110",
        windy_days_1980: "3",
        windy_days_2050: "5",
    },
];

const baseProps = {
    regions: [{ id: 1 }],
    loading: false,
    climatePrediction: prediction,
    year: 2050,
    season: "annual",
};

const clickIcon = (container, index) => {
    const iconButtons = container.querySelectorAll(".climate-icon-button");
    fireEvent.click(iconButtons[index]);
};

describe("ClimateSummary", () => {
    afterEach(cleanup);

    it("renders nothing when no regions are selected", () => {
        const { container } = render(<ClimateSummary {...baseProps} regions={[]} />);
        expect(container.firstChild).toBeNull();
    });

    it("summarises each main climate variable from the prediction data", () => {
        render(<ClimateSummary {...baseProps} />);
        expect(screen.getByText(/Temperature increases by 2\.00 °C/i)).toBeInTheDocument();
        expect(screen.getByText(/Rainfall decreases by 1\.00 mm\/day/i)).toBeInTheDocument();
        // Dry Days summary text is split across elements because the name has a HelpPopover;
        // use a custom function matcher on the parent summary-text div.
        expect(
            screen.getByText(
                (_, el) =>
                    el?.classList?.contains("summary-text") &&
                    /Dry Days/i.test(el.textContent) &&
                    /increase by 3\.00 days\/year/i.test(el.textContent),
            ),
        ).toBeInTheDocument();
        expect(screen.getByText(/No change in/i)).toHaveTextContent(/Windiness/i);
    });

    it("shows the placeholder prompt before a variable is selected", () => {
        render(<ClimateSummary {...baseProps} />);
        expect(
            screen.getByText(/Please click a climate variable icon to view additional metrics\./i),
        ).toBeInTheDocument();
    });

    it("reveals temperature detail metrics when the temperature icon is clicked", () => {
        const { container } = render(<ClimateSummary {...baseProps} />);
        clickIcon(container, 0); // first icon button = Temperature
        expect(screen.getByRole("heading", { name: /temperature metrics/i })).toBeInTheDocument();
        expect(screen.getByText(/Tropical Nights/i)).toBeInTheDocument();
        expect(screen.getByText(/Hot Heat Days/i)).toBeInTheDocument();
    });

    it("collapses the detail metrics back to the placeholder on a second click", () => {
        const { container } = render(<ClimateSummary {...baseProps} />);
        clickIcon(container, 0);
        clickIcon(container, 0);
        expect(
            screen.getByText(/Please click a climate variable icon to view additional metrics\./i),
        ).toBeInTheDocument();
    });

    it("shows the loading overlay text while loading", () => {
        render(<ClimateSummary {...baseProps} loading={true} />);
        expect(screen.getByText("Loading climate data")).toBeInTheDocument();
    });
});
