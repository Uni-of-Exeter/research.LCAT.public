import "@testing-library/jest-dom/vitest";
import { beforeAll } from "vitest";

// Patch localStorage to add missing methods if needed
beforeAll(() => {
    // Check if localStorage is broken (missing standard methods)
    if (typeof localStorage !== "undefined" && typeof localStorage.getItem !== "function") {
        // Recreate Storage interface
        const storage = {};

        Object.defineProperty(window, "localStorage", {
            value: {
                length: 0,
                getItem(key) {
                    return storage[key] || null;
                },
                setItem(key, value) {
                    storage[key] = String(value);
                    this.length = Object.keys(storage).length;
                },
                removeItem(key) {
                    delete storage[key];
                    this.length = Object.keys(storage).length;
                },
                clear() {
                    Object.keys(storage).forEach(key => {
                        delete storage[key];
                    });
                    this.length = 0;
                },
                key(index) {
                    return Object.keys(storage)[index] || null;
                },
            },
            writable: true,
            configurable: true,
        });
    }
});
