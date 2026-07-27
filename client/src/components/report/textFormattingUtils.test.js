import { describe, expect, it, vi } from "vitest";

vi.mock("./reportStyles", () => ({
    reportStyles: {
        climateVariable: { fontSize: 14, fontWeight: "bold" },
    },
}));

import { formatLineBreaks, getTextStyle } from "./textFormattingUtils";

describe("getTextStyle", () => {
    it("returns base style for short text", () => {
        const result = getTextStyle("Short label");
        expect(result).toEqual({ fontSize: 14, fontWeight: "bold" });
    });

    it("returns 10.5 font size for text over 30 chars", () => {
        const result = getTextStyle("This is a label that is over thirty");
        expect(result).toEqual({ fontSize: 10.5, fontWeight: "bold" });
    });

    it("returns 10 font size for text over 40 chars", () => {
        const result = getTextStyle("This label is definitely over forty characters long");
        expect(result).toEqual({ fontSize: 10, fontWeight: "bold" });
    });
});

describe("formatLineBreaks", () => {
    it("replaces known breakpoints with line breaks", () => {
        const input = "Respiratory diseases and viruses, fungi";
        const result = formatLineBreaks(input);
        expect(result).toBe("Respiratory\ndiseases and viruses,\nfungi");
    });

    it("leaves text unchanged when no breakpoints match", () => {
        const input = "Unmatched text stays the same";
        const result = formatLineBreaks(input);
        expect(result).toBe(input);
    });

    it("applies multiple replacements in the same string", () => {
        const input = "Temperature increases impact the natural environment";
        const result = formatLineBreaks(input);
        expect(result).toBe("Temperature\nincreases impact the natural\nenvironment");
    });
});
