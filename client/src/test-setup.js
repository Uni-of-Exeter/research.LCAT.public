import "@testing-library/jest-dom/vitest";
import { beforeAll } from "vitest";

// Node 25 ships an experimental global `localStorage` that is present but non-functional:
// it requires `--localstorage-file` and prints a warning; `getItem`/`clear`/etc. are not
// functions. This shadows jsdom's own implementation, breaking any test that uses
// localStorage. The guard below (`typeof localStorage.getItem !== "function"`) installs a
// minimal in-memory replacement ONLY when the broken Node global is detected, making it a
// no-op in environments where the real Storage API is available.
beforeAll(() => {
    if (typeof localStorage !== "undefined" && typeof localStorage.getItem !== "function") {
        const storage = {};

        Object.defineProperty(window, "localStorage", {
            value: {
                length: 0,
                getItem(key) {
                    return Object.prototype.hasOwnProperty.call(storage, key) ? storage[key] : null;
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
