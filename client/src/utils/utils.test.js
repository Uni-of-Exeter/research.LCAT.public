import { describe, expect, it } from "vitest";

import { andify } from "./utils";

describe("andify", () => {
    it("returns single item", () => {
        expect(andify(["apple"])).toBe("apple");
    });

    it('joins two items with "and"', () => {
        expect(andify(["apple", "banana"])).toBe("apple and banana");
    });

    it('joins multiple items with commas and "and"', () => {
        expect(andify(["apple", "banana", "orange"])).toBe("apple, banana and orange");
    });

    it("handles empty array", () => {
        expect(andify([])).toBeUndefined();
    });
});
