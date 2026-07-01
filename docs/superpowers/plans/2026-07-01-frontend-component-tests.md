# Frontend Component Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add thorough, behaviour-focused Vitest + Testing Library tests for the untested React components in `client/src/components`, and rewrite the one bad legacy component test (`ClimateSummary.test.jsx`).

**Architecture:** These are **characterization tests over existing, unchanged components** — each test should PASS on first run (there is no red phase). Tests render the real component with small fixtures, query by role/label/text, and drive real user interactions. Only true boundaries (`localStorage`, `window` events, and two data-JSON imports) are mocked. Follow the canonical style of the existing `vulnerabilities/IMDMap.test.jsx` and `adaptations/Reference.test.jsx`.

**Tech Stack:** Vitest 4, `@testing-library/react`, `@testing-library/jest-dom` (loaded via `client/src/test-setup.js`), jsdom. Config in `client/vite.config.js` (svgr + react plugins apply in tests).

## Global Constraints

- All commands run from `client/` (e.g. `cd client && npx vitest run <path>`).
- Test files are co-located: `ComponentName.test.jsx` next to the component.
- Query priority: `getByRole` → `getByLabelText` → `getByText`. Avoid markup-regex and implementation-detail assertions.
- Mock ONLY: `localStorage` control (jsdom provides the API — clear it per test), `window` custom events, and the two Kumu JSON data imports (`processed_references.json`, `adaptation_data.json`). Do NOT mock CSS, `.jsx`/`.svg` icons, `react-collapsed`, or `react-loading-overlay-ts`.
- `gtag` is a bare global guarded by `typeof gtag !== "undefined"`; leave it undefined so analytics calls are skipped. Do NOT assert on analytics.
- Use `afterEach(cleanup)` in files that render repeatedly (matching the existing files); otherwise rely on Testing Library's default cleanup.
- Indentation: 4-space, double-quoted imports, matching `IMDMap.test.jsx` (the repo's Prettier/ESLint config governs — run `npm run lint` at the end).
- **If a test fails:** decide whether the test's expectation is wrong (fix the test) or the component has a genuine bug. Do NOT modify component source to make a test pass — if you suspect a real bug, stop and report it.
- Reference exact copy/URLs verbatim from the component source; this plan quotes them.

## File Structure

One new/rewritten `*.test.jsx` per target component:

```
client/src/components/
  footer/ContactUs.test.jsx            (new)
  footer/Handbook.test.jsx             (new)
  footer/AdaptationGuide.test.jsx      (new)
  footer/FooterText.test.jsx           (new)
  footer/FooterLogos.test.jsx          (new)
  footer/PageSelectionModal.test.jsx   (new)
  header/Introduction.test.jsx         (new)
  feedback/Feedback.test.jsx           (new)
  vulnerabilities/LinkOutIcon.test.jsx (new)
  cookies/PolicyModal.test.jsx         (new)
  cookies/ConsentBanner.test.jsx       (new)
  climatePrediction/ClimateSettings.test.jsx (new)
  climatePrediction/HelpPopover.test.jsx     (new)
  climateHazard/ClimateHazardRisk.test.jsx   (new)
  vulnerabilities/PersonalSocialVulnerabilities.test.jsx (new)
  climateImpacts/ClimateImpactSummary.test.jsx (new)
  adaptations/StaticReferences.test.jsx (new)
  adaptations/StaticAdaptation.test.jsx (new)
  adaptations/StaticAdaptations.test.jsx (new)
  climatePrediction/ClimateSummary.test.jsx (REWRITE)
```

Tasks are ordered simplest-first to establish patterns, then interactive, then data-coupled, then the rewrite.

---

### Task 1: Tier B footer statics (ContactUs, Handbook, AdaptationGuide, FooterText, FooterLogos)

**Files:**
- Create: `client/src/components/footer/ContactUs.test.jsx`
- Create: `client/src/components/footer/Handbook.test.jsx`
- Create: `client/src/components/footer/AdaptationGuide.test.jsx`
- Create: `client/src/components/footer/FooterText.test.jsx`
- Create: `client/src/components/footer/FooterLogos.test.jsx`

**Interfaces:**
- Consumes: `LCAT_HANDBOOK_URL`, `ADAPTATION_INTRO_PDF_URL` from `../../utils/constants`.
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Write `ContactUs.test.jsx`**

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ContactUs from "./ContactUs";

describe("ContactUs", () => {
    it("shows the contact heading", () => {
        render(<ContactUs />);
        expect(screen.getByRole("heading", { name: /need help\? contact us\./i })).toBeInTheDocument();
    });

    it("links to the LCAT email address", () => {
        render(<ContactUs />);
        const emailLink = screen.getByRole("link", { name: "lcat@exeter.ac.uk" });
        expect(emailLink).toHaveAttribute("href", "mailto:lcat@exeter.ac.uk");
    });
});
```

- [ ] **Step 2: Write `Handbook.test.jsx`**

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LCAT_HANDBOOK_URL } from "../../utils/constants";
import Handbook from "./Handbook";

describe("Handbook", () => {
    it("shows the handbook heading", () => {
        render(<Handbook />);
        expect(screen.getByText("Access our Handbook.")).toBeInTheDocument();
    });

    it("links to the handbook PDF", () => {
        render(<Handbook />);
        const link = screen.getByRole("link", { name: /LCAT Handbook \(at ecehh\.org\)/i });
        expect(link).toHaveAttribute("href", LCAT_HANDBOOK_URL);
        expect(link).toHaveAttribute("target", "_blank");
    });
});
```

- [ ] **Step 3: Write `AdaptationGuide.test.jsx`**

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ADAPTATION_INTRO_PDF_URL } from "../../utils/constants";
import AdaptationGuide from "./AdaptationGuide";

describe("AdaptationGuide", () => {
    it("shows the adaptation guide heading", () => {
        render(<AdaptationGuide />);
        expect(screen.getByText("Learn About Climate Adaptation.")).toBeInTheDocument();
    });

    it("links to the adaptation intro PDF", () => {
        render(<AdaptationGuide />);
        const link = screen.getByRole("link", { name: /Introduction to Local Climate Adaptation \(at ecehh\.org\)/i });
        expect(link).toHaveAttribute("href", ADAPTATION_INTRO_PDF_URL);
    });
});
```

- [ ] **Step 4: Write `FooterText.test.jsx`**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import FooterText from "./FooterText";

describe("FooterText", () => {
    it("names the lead developing organisation", () => {
        render(<FooterText />);
        expect(screen.getByText(/Local Climate Adaptation Tool has been developed/i)).toBeInTheDocument();
    });

    it("links to the open-source code repository", () => {
        render(<FooterText />);
        const link = screen.getByRole("link", { name: /Source code published/i });
        expect(link).toHaveAttribute("href", "https://github.com/Uni-of-Exeter/research.LCAT.public");
    });

    it("dispatches open_cookie_banner when 'Manage cookies' is clicked", () => {
        const handler = vi.fn();
        window.addEventListener("open_cookie_banner", handler);
        render(<FooterText />);

        fireEvent.click(screen.getByRole("button", { name: /manage cookies/i }));

        expect(handler).toHaveBeenCalledTimes(1);
        window.removeEventListener("open_cookie_banner", handler);
    });
});
```

- [ ] **Step 5: Write `FooterLogos.test.jsx`**

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import FooterLogos from "./FooterLogos";

describe("FooterLogos", () => {
    it("renders the partner logos image with descriptive alt text", () => {
        render(<FooterLogos />);
        expect(screen.getByRole("img", { name: /Partner logos: University of Exeter/i })).toBeInTheDocument();
    });

    it("renders the funder logos image with descriptive alt text", () => {
        render(<FooterLogos />);
        expect(screen.getByRole("img", { name: /Funder logos: Co-funded by the European Union/i })).toBeInTheDocument();
    });
});
```

- [ ] **Step 6: Run the footer tests — expect PASS**

Run: `cd client && npx vitest run src/components/footer/ContactUs.test.jsx src/components/footer/Handbook.test.jsx src/components/footer/AdaptationGuide.test.jsx src/components/footer/FooterText.test.jsx src/components/footer/FooterLogos.test.jsx`
Expected: 5 files, all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add client/src/components/footer/ContactUs.test.jsx client/src/components/footer/Handbook.test.jsx client/src/components/footer/AdaptationGuide.test.jsx client/src/components/footer/FooterText.test.jsx client/src/components/footer/FooterLogos.test.jsx
git commit -m "test: cover footer static components"
```

---

### Task 2: Tier B — Introduction, Feedback, LinkOutIcon

**Files:**
- Create: `client/src/components/header/Introduction.test.jsx`
- Create: `client/src/components/feedback/Feedback.test.jsx`
- Create: `client/src/components/vulnerabilities/LinkOutIcon.test.jsx`

**Interfaces:**
- Consumes: `LCAT_HANDBOOK_URL` from `../../utils/constants` (Introduction).
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Write `Introduction.test.jsx`**

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { LCAT_HANDBOOK_URL } from "../../utils/constants";
import Introduction from "./Introduction";

describe("Introduction", () => {
    it("summarises what the tool shows", () => {
        render(<Introduction />);
        expect(screen.getByText(/see what the scientific research is saying about/i)).toBeInTheDocument();
    });

    it("lists the LCAT Handbook as a helpful resource", () => {
        render(<Introduction />);
        const link = screen.getByRole("link", { name: "LCAT Handbook" });
        expect(link).toHaveAttribute("href", LCAT_HANDBOOK_URL);
    });

    it("links to the Met Office Local Authority Climate Service", () => {
        render(<Introduction />);
        const link = screen.getByRole("link", { name: /Met Office Local Authority Climate Service/i });
        expect(link).toHaveAttribute("href", "https://climatedataportal.metoffice.gov.uk/pages/lacs");
    });
});
```

- [ ] **Step 2: Write `Feedback.test.jsx`**

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Feedback from "./Feedback";

describe("Feedback", () => {
    it("shows the evaluation survey heading", () => {
        render(<Feedback />);
        expect(screen.getByRole("heading", { name: /evaluation survey/i })).toBeInTheDocument();
    });

    it("links to the survey in a new tab with an accessible name", () => {
        render(<Feedback />);
        const link = screen.getByRole("link", { name: /Access the evaluation survey in a new tab/i });
        expect(link).toHaveAttribute("href", expect.stringContaining("forms.office.com"));
        expect(link).toHaveAttribute("target", "_blank");
    });
});
```

- [ ] **Step 3: Write `LinkOutIcon.test.jsx`**

```jsx
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import LinkOutIcon from "./LinkOutIcon";

describe("LinkOutIcon", () => {
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
```

- [ ] **Step 4: Run — expect PASS**

Run: `cd client && npx vitest run src/components/header/Introduction.test.jsx src/components/feedback/Feedback.test.jsx src/components/vulnerabilities/LinkOutIcon.test.jsx`
Expected: 3 files, all PASS.

- [ ] **Step 5: Commit**

```bash
git add client/src/components/header/Introduction.test.jsx client/src/components/feedback/Feedback.test.jsx client/src/components/vulnerabilities/LinkOutIcon.test.jsx
git commit -m "test: cover Introduction, Feedback, and LinkOutIcon"
```

---

### Task 3: PolicyModal

**Files:**
- Create: `client/src/components/cookies/PolicyModal.test.jsx`

**Interfaces:**
- Component: `CookiePolicyModal({ open, onClose })` (default export). Renders `null` when `!open`; otherwise a `role="dialog"` with `aria-modal="true"`; a full-screen overlay `role="button"` `aria-label="Close cookie policy overlay"` that calls `onClose`; a `keydown` Escape listener on `window` that calls `onClose`.

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import CookiePolicyModal from "./PolicyModal";

describe("CookiePolicyModal", () => {
    afterEach(cleanup);

    it("renders nothing when closed", () => {
        const { container } = render(<CookiePolicyModal open={false} onClose={() => {}} />);
        expect(container.firstChild).toBeNull();
    });

    it("renders an accessible modal dialog when open", () => {
        render(<CookiePolicyModal open={true} onClose={() => {}} />);
        const dialog = screen.getByRole("dialog");
        expect(dialog).toHaveAttribute("aria-modal", "true");
    });

    it("calls onClose when the overlay is clicked", () => {
        const onClose = vi.fn();
        render(<CookiePolicyModal open={true} onClose={onClose} />);
        fireEvent.click(screen.getByRole("button", { name: /close cookie policy overlay/i }));
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("calls onClose when Escape is pressed", () => {
        const onClose = vi.fn();
        render(<CookiePolicyModal open={true} onClose={onClose} />);
        fireEvent.keyDown(window, { key: "Escape" });
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/cookies/PolicyModal.test.jsx`
Expected: 4 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/cookies/PolicyModal.test.jsx
git commit -m "test: cover CookiePolicyModal open/close behaviour"
```

---

### Task 4: ConsentBanner

**Files:**
- Create: `client/src/components/cookies/ConsentBanner.test.jsx`

**Interfaces:**
- Component: `CookieConsent()` (default export from `ConsentBanner.jsx`). On mount reads `localStorage.getItem("cookie_consent")`: `"true"` → hidden (loads GA), `"false"` → hidden, `null` → shown. Accept button (`"Accept all cookies"`) sets `"true"` and hides; Decline (`"Reject non-essential cookies"`) sets `"false"` and hides. A `"cookie policy"` button opens the nested `CookiePolicyModal` (`role="dialog"`). Listens for the `open_cookie_banner` window event to re-show.

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import CookieConsent from "./ConsentBanner";

describe("CookieConsent", () => {
    beforeEach(() => {
        localStorage.clear();
        delete window.gtag;
    });
    afterEach(cleanup);

    it("shows the banner when no consent choice is stored", () => {
        render(<CookieConsent />);
        expect(screen.getByText(/We use cookies to improve your experience/i)).toBeInTheDocument();
    });

    it("stays hidden when consent was already granted", () => {
        localStorage.setItem("cookie_consent", "true");
        render(<CookieConsent />);
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();
    });

    it("stores acceptance and hides the banner", () => {
        render(<CookieConsent />);
        fireEvent.click(screen.getByRole("button", { name: /accept all cookies/i }));
        expect(localStorage.getItem("cookie_consent")).toBe("true");
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();
    });

    it("stores rejection and hides the banner", () => {
        render(<CookieConsent />);
        fireEvent.click(screen.getByRole("button", { name: /reject non-essential cookies/i }));
        expect(localStorage.getItem("cookie_consent")).toBe("false");
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();
    });

    it("opens the cookie policy dialog from the banner", () => {
        render(<CookieConsent />);
        expect(screen.queryByRole("dialog")).toBeNull();
        fireEvent.click(screen.getByRole("button", { name: /cookie policy/i }));
        expect(screen.getByRole("dialog")).toBeInTheDocument();
    });

    it("re-shows the banner when the open_cookie_banner event fires", () => {
        localStorage.setItem("cookie_consent", "true");
        render(<CookieConsent />);
        expect(screen.queryByText(/We use cookies to improve your experience/i)).toBeNull();

        fireEvent(window, new Event("open_cookie_banner"));

        expect(screen.getByText(/We use cookies to improve your experience/i)).toBeInTheDocument();
    });
});
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/cookies/ConsentBanner.test.jsx`
Expected: 6 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/cookies/ConsentBanner.test.jsx
git commit -m "test: cover cookie consent banner behaviour"
```

---

### Task 5: PageSelectionModal

**Files:**
- Create: `client/src/components/footer/PageSelectionModal.test.jsx`

**Interfaces:**
- Component: `PageSelectionModal({ isOpen, onClose, onGenerate, availablePages })`. `availablePages`: `[{ id, title, defaultSelected }]`. Renders `null` when `!isOpen`. One checkbox per page, `aria-label={`Include ${title} in report`}`, initially checked per `defaultSelected`. Generate button label includes `({N} page(s))` and is disabled when 0 selected; on click calls `onGenerate(selectedIds)` then `onClose()`. Cancel button, Escape keydown, and clicking the overlay itself each call `onClose`.

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import PageSelectionModal from "./PageSelectionModal";

const PAGES = [
    { id: "intro", title: "Introduction", defaultSelected: true },
    { id: "hazards", title: "Hazards", defaultSelected: false },
];

const renderModal = (overrides = {}) =>
    render(
        <PageSelectionModal
            isOpen={true}
            onClose={overrides.onClose || (() => {})}
            onGenerate={overrides.onGenerate || (() => {})}
            availablePages={overrides.availablePages || PAGES}
        />,
    );

describe("PageSelectionModal", () => {
    afterEach(cleanup);

    it("renders nothing when closed", () => {
        const { container } = render(
            <PageSelectionModal isOpen={false} onClose={() => {}} onGenerate={() => {}} availablePages={PAGES} />,
        );
        expect(container.firstChild).toBeNull();
    });

    it("renders a checkbox per page with default selection", () => {
        renderModal();
        expect(screen.getByRole("checkbox", { name: /Include Introduction in report/i })).toBeChecked();
        expect(screen.getByRole("checkbox", { name: /Include Hazards in report/i })).not.toBeChecked();
    });

    it("updates the selected-page count when a checkbox is toggled", () => {
        renderModal();
        expect(screen.getByRole("button", { name: /Generate Report \(1 page\)/i })).toBeInTheDocument();
        fireEvent.click(screen.getByRole("checkbox", { name: /Include Hazards in report/i }));
        expect(screen.getByRole("button", { name: /Generate Report \(2 pages\)/i })).toBeInTheDocument();
    });

    it("disables Generate when no pages are selected", () => {
        renderModal();
        fireEvent.click(screen.getByRole("checkbox", { name: /Include Introduction in report/i }));
        expect(screen.getByRole("button", { name: /Generate Report \(0 pages\)/i })).toBeDisabled();
    });

    it("generates with the selected page ids then closes", () => {
        const onGenerate = vi.fn();
        const onClose = vi.fn();
        renderModal({ onGenerate, onClose });
        fireEvent.click(screen.getByRole("button", { name: /Generate Report \(1 page\)/i }));
        expect(onGenerate).toHaveBeenCalledWith(["intro"]);
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("closes on Cancel", () => {
        const onClose = vi.fn();
        renderModal({ onClose });
        fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
        expect(onClose).toHaveBeenCalledTimes(1);
    });

    it("closes on Escape", () => {
        const onClose = vi.fn();
        renderModal({ onClose });
        fireEvent.keyDown(screen.getByRole("button", { name: /Close modal/i }), { key: "Escape" });
        expect(onClose).toHaveBeenCalledTimes(1);
    });
});
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/footer/PageSelectionModal.test.jsx`
Expected: 7 tests PASS. (Note: the overlay itself is the element with accessible name "Close modal (click background or press Escape)".)

- [ ] **Step 3: Commit**

```bash
git add client/src/components/footer/PageSelectionModal.test.jsx
git commit -m "test: cover report page selection modal"
```

---

### Task 6: ClimateSettings

**Files:**
- Create: `client/src/components/climatePrediction/ClimateSettings.test.jsx`

**Interfaces:**
- Component: `ClimateSettings({ regions, rcp, season, setRcp, setSeason })`. Returns `null` when `regions.length === 0`. Renders region names joined by `andify`. First `<select>` = RCP (`rcp60`/`rcp85`) → `setRcp`; conditional text `(equivalent to global warming level of 2.0-3.7C which is RCP 6.0)` for rcp60. Second `<select>` = season (`annual`/`summer`/`winter`) → `setSeason`.

- [ ] **Step 1: Write the test**

```jsx
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
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/climatePrediction/ClimateSettings.test.jsx`
Expected: 5 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/climatePrediction/ClimateSettings.test.jsx
git commit -m "test: cover climate settings selectors"
```

---

### Task 7: HelpPopover

**Files:**
- Create: `client/src/components/climatePrediction/HelpPopover.test.jsx`

**Interfaces:**
- Component: `HelpPopover({ children, content })`. Returns `null` when `!content`. Renders a trigger `button` `aria-label="More information"` containing `children`. Popover content shown when open (click toggles) or hovered (`mouseEnter`); hidden on `mouseLeave` (when not click-opened); Escape closes; a `button` `aria-label="Close"` closes.

- [ ] **Step 1: Write the test**

```jsx
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
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/climatePrediction/HelpPopover.test.jsx`
Expected: 6 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/climatePrediction/HelpPopover.test.jsx
git commit -m "test: cover help popover open/close behaviour"
```

---

### Task 8: ClimateHazardRisk

**Files:**
- Create: `client/src/components/climateHazard/ClimateHazardRisk.test.jsx`

**Interfaces:**
- Component: `ClimateHazardRisk({ applyCoastalFilter })`. Renders one button per hazard (from `ClimateHazardData`): `Heatwaves`, `Wildfires`, `Air Quality`, `Flooding`, `Coastal Erosion`. Before a click, shows placeholder `Please click a climate hazard risk icon to view details.` Clicking a hazard shows an `h2` with its name and its details. When `applyCoastalFilter` is `true`, `Coastal Erosion` is removed.

- [ ] **Step 1: Write the test**

```jsx
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
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/climateHazard/ClimateHazardRisk.test.jsx`
Expected: 4 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/climateHazard/ClimateHazardRisk.test.jsx
git commit -m "test: cover climate hazard risk selection"
```

---

### Task 9: PersonalSocialVulnerabilities

**Files:**
- Create: `client/src/components/vulnerabilities/PersonalSocialVulnerabilities.test.jsx`

**Interfaces:**
- Component: `PersonalSocialVulnerabilities()` (no props). Renders one button per vulnerability (from `PersonalSocialVulnerabilitiesData`): includes `Older people`, `Under 5s`, `People on low incomes`, etc. Placeholder before selection: `Please click a vulnerability icon to view details.` Clicking shows an `h2` with the name and a ClimateJust data-source link (`https://climatejust.org.uk`).

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import PersonalSocialVulnerabilities from "./PersonalSocialVulnerabilities";

describe("PersonalSocialVulnerabilities", () => {
    afterEach(cleanup);

    it("renders a button for each vulnerability", () => {
        render(<PersonalSocialVulnerabilities />);
        expect(screen.getByRole("button", { name: /older people/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /people on low incomes/i })).toBeInTheDocument();
    });

    it("shows the placeholder prompt before a vulnerability is selected", () => {
        render(<PersonalSocialVulnerabilities />);
        expect(screen.getByText(/Please click a vulnerability icon to view details\./i)).toBeInTheDocument();
    });

    it("shows details and a ClimateJust source link once a vulnerability is clicked", () => {
        render(<PersonalSocialVulnerabilities />);
        fireEvent.click(screen.getByRole("button", { name: /older people/i }));
        expect(screen.getByRole("heading", { name: "Older people" })).toBeInTheDocument();
        const link = screen.getByRole("link", { name: /vulnerability insight, by theme, from ClimateJust/i });
        expect(link).toHaveAttribute("href", "https://climatejust.org.uk");
    });
});
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/vulnerabilities/PersonalSocialVulnerabilities.test.jsx`
Expected: 3 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/vulnerabilities/PersonalSocialVulnerabilities.test.jsx
git commit -m "test: cover personal and social vulnerabilities"
```

---

### Task 10: ClimateImpactSummary

**Files:**
- Create: `client/src/components/climateImpacts/ClimateImpactSummary.test.jsx`

**Interfaces:**
- Component: `ClimateImpactSummary({ loading, selectedImpactHazard, setSelectedImpactHazard, applyCoastalFilter })`. Wrapped in `LoadingOverlay` with text `Loading impact summaries`. Renders a pathway `<select>` (options: `Extreme Storms`, `Coastal Security`, `Flooding and Drought`, `Food and Personal Security`, `Marine Health Hazards`, `Temperature`). On mount and coastal-filter change it calls `setSelectedImpactHazard`. `selectedImpactHazard` MUST be a valid pathway name (used with `.find(...).id`), so pass `"Extreme Storms"`. Changing the select calls `setSelectedImpactHazard(value)`. With `applyCoastalFilter`, coastal pathways (`Coastal Security`, `Marine Health Hazards`) are removed.

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import ClimateImpactSummary from "./ClimateImpactSummary";

const baseProps = {
    loading: false,
    selectedImpactHazard: "Extreme Storms",
    setSelectedImpactHazard: () => {},
    applyCoastalFilter: false,
};

describe("ClimateImpactSummary", () => {
    afterEach(cleanup);

    it("renders the impact pathway options", () => {
        render(<ClimateImpactSummary {...baseProps} />);
        expect(screen.getByRole("option", { name: "Extreme Storms" })).toBeInTheDocument();
        expect(screen.getByRole("option", { name: "Temperature" })).toBeInTheDocument();
        expect(screen.getByRole("option", { name: "Coastal Security" })).toBeInTheDocument();
    });

    it("shows the loading overlay text while loading", () => {
        render(<ClimateImpactSummary {...baseProps} loading={true} />);
        expect(screen.getByText("Loading impact summaries")).toBeInTheDocument();
    });

    it("calls setSelectedImpactHazard when the pathway changes", () => {
        const setSelectedImpactHazard = vi.fn();
        render(<ClimateImpactSummary {...baseProps} setSelectedImpactHazard={setSelectedImpactHazard} />);
        fireEvent.change(screen.getByRole("combobox"), { target: { value: "Temperature" } });
        expect(setSelectedImpactHazard).toHaveBeenCalledWith("Temperature");
    });

    it("removes coastal pathways when the coastal filter is applied", () => {
        render(<ClimateImpactSummary {...baseProps} applyCoastalFilter={true} />);
        expect(screen.queryByRole("option", { name: "Coastal Security" })).toBeNull();
        expect(screen.queryByRole("option", { name: "Marine Health Hazards" })).toBeNull();
        expect(screen.getByRole("option", { name: "Extreme Storms" })).toBeInTheDocument();
    });
});
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/climateImpacts/ClimateImpactSummary.test.jsx`
Expected: 4 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/climateImpacts/ClimateImpactSummary.test.jsx
git commit -m "test: cover climate impact summary pathway selection"
```

---

### Task 11: StaticReferences

**Files:**
- Create: `client/src/components/adaptations/StaticReferences.test.jsx`

**Interfaces:**
- Component: `StaticReferences({ referenceIds })`. Looks each id up in `processed_references.json` (keyed by stringified id), returns `null` if none resolve. Groups resolved refs by `type`, rendering `References:` and a collapsible group header `"{type} ({count})"`. Each group starts collapsed; clicking the header reveals the `Reference` entries (which show their `title`). This task mocks the JSON import to supply deterministic fixtures.

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../../kumu/parsed/processed_references.json", () => ({
    default: {
        1: {
            article_id: "1",
            title: "Heat and health in cities",
            type: "Journal Article",
            link: "https://example.com/heat",
            authors: "Smith, J.",
            journal: "Climate & Health",
            issue: "12(3)",
            date: "2022",
        },
    },
}));

import StaticReferences from "./StaticReferences";

describe("StaticReferences", () => {
    afterEach(cleanup);

    it("renders nothing when no ids resolve to a reference", () => {
        const { container } = render(<StaticReferences referenceIds={[999]} />);
        expect(container.firstChild).toBeNull();
    });

    it("renders a collapsible group header with the type and count", () => {
        render(<StaticReferences referenceIds={[1]} />);
        expect(screen.getByText("References:")).toBeInTheDocument();
        expect(screen.getByText("Journal Article (1)")).toBeInTheDocument();
    });

    it("reveals the reference title when the group header is clicked", () => {
        render(<StaticReferences referenceIds={[1]} />);
        expect(screen.queryByText("Heat and health in cities")).toBeNull();
        fireEvent.click(screen.getByText("Journal Article (1)"));
        expect(screen.getByText("Heat and health in cities")).toBeInTheDocument();
    });
});
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/adaptations/StaticReferences.test.jsx`
Expected: 3 tests PASS. If the collapsed content is still queryable (react-collapsed keeps it mounted), change the third test to assert on visibility via `aria-expanded` on the header instead — but the `Reference` child itself starts collapsed and is absent from the tree, so `queryByText` should be null before the click.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/adaptations/StaticReferences.test.jsx
git commit -m "test: cover static references grouping and expansion"
```

---

### Task 12: StaticAdaptation

**Files:**
- Create: `client/src/components/adaptations/StaticAdaptation.test.jsx`

**Interfaces:**
- Component: `StaticAdaptation({ adaptation, selectedHazards })`. `adaptation.attributes`: `{ label, description, aggregated_layers: string[], reference_id: (string|number)[] }`. Header shows `attributes.label` and is a collapse toggle (starts collapsed). Expanded content shows `Description:` + the description, and — when `aggregated_layers` has entries not in `selectedHazards` — `Related impact pathways: {joined}`. Imports `processed_references.json` for case studies and passes `reference_id` to `StaticReferences`; mock it as `{}` so those stay empty/null.

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../../kumu/parsed/processed_references.json", () => ({ default: {} }));

import StaticAdaptation from "./StaticAdaptation";

const adaptation = {
    _id: "a1",
    attributes: {
        label: "Install green roofs",
        description: "Green roofs reduce urban heat and rainfall runoff.",
        aggregated_layers: ["Flooding", "Heatwaves"],
        reference_id: [],
    },
};

describe("StaticAdaptation", () => {
    afterEach(cleanup);

    it("renders the adaptation label", () => {
        render(<StaticAdaptation adaptation={adaptation} selectedHazards={[]} />);
        expect(screen.getByText("Install green roofs")).toBeInTheDocument();
    });

    it("reveals the description when the header is expanded", () => {
        render(<StaticAdaptation adaptation={adaptation} selectedHazards={[]} />);
        expect(screen.queryByText(/Green roofs reduce urban heat/i)).toBeNull();
        fireEvent.click(screen.getByText("Install green roofs"));
        expect(screen.getByText(/Green roofs reduce urban heat/i)).toBeInTheDocument();
    });

    it("lists related impact pathways not already selected", () => {
        render(<StaticAdaptation adaptation={adaptation} selectedHazards={[]} />);
        fireEvent.click(screen.getByText("Install green roofs"));
        expect(screen.getByText(/Related impact pathways:/i)).toHaveTextContent("Flooding, Heatwaves");
    });
});
```

> **Note for the implementer:** Vitest auto-hoists `vi.mock(...)` above imports, so the mock reliably applies to the `StaticAdaptation` import even though it is written between the import lines. Keep `vi` in the `vitest` import.

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/adaptations/StaticAdaptation.test.jsx`
Expected: 3 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/adaptations/StaticAdaptation.test.jsx
git commit -m "test: cover static adaptation expansion and pathways"
```

---

### Task 13: StaticAdaptations

**Files:**
- Create: `client/src/components/adaptations/StaticAdaptations.test.jsx`

**Interfaces:**
- Component: `StaticAdaptations({ selectedAdaptationHazards, setSelectedAdaptationHazards, applyCoastalFilter, filterName, setFilterName })`. Renders `Adaptations` heading and one pathway button per `pathways` entry (from `ClimateImpactSummaryData`: `Extreme Storms`, `Coastal Security`, `Flooding and Drought`, `Food and Personal Security`, `Marine Health Hazards`, `Temperature`). Clicking a pathway calls `setSelectedAdaptationHazards` (with an updater fn). A `Reset adaptation filters` button calls `setSelectedAdaptationHazards([])`. A theme `<select>` (options from `adaptationFilters` display names, default `No filter applied`) calls `setFilterName`. Filters `adaptation_data.json` by hazard/theme and shows `"{N} climate adaptation(s) was/were found"` plus one `StaticAdaptation` per match, else `No adaptations found`. A `Reference source information` toggle reveals data-source copy. Mock both JSON imports for determinism.

- [ ] **Step 1: Write the test**

```jsx
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../../kumu/parsed/processed_references.json", () => ({ default: {} }));
vi.mock("../../kumu/parsed/adaptation_data.json", () => ({
    default: [
        {
            _id: "a1",
            attributes: {
                label: "Adaptation One",
                description: "First adaptation",
                layer: ["flooding in full"],
                "ccc adaptation theme": ["Nature"],
                aggregated_layers: [],
                reference_id: [],
            },
        },
    ],
}));

import StaticAdaptations from "./StaticAdaptations";

const baseProps = {
    selectedAdaptationHazards: [],
    setSelectedAdaptationHazards: () => {},
    applyCoastalFilter: false,
    filterName: "No filter applied",
    setFilterName: () => {},
};

const renderAdaptations = (overrides = {}) => render(<StaticAdaptations {...baseProps} {...overrides} />);

describe("StaticAdaptations", () => {
    afterEach(cleanup);

    it("renders the heading and a pathway filter button per pathway", () => {
        renderAdaptations();
        expect(screen.getByRole("heading", { name: "Adaptations" })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /extreme storms/i })).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /temperature/i })).toBeInTheDocument();
    });

    it("shows the matching adaptation and found-count", () => {
        renderAdaptations();
        expect(screen.getByText(/1 climate adaptation was found/i)).toBeInTheDocument();
        expect(screen.getByText("Adaptation One")).toBeInTheDocument();
    });

    it("selects a hazard when its pathway button is clicked", () => {
        const setSelectedAdaptationHazards = vi.fn();
        renderAdaptations({ setSelectedAdaptationHazards });
        fireEvent.click(screen.getByRole("button", { name: /extreme storms/i }));
        expect(setSelectedAdaptationHazards).toHaveBeenCalled();
    });

    it("clears hazards when Reset adaptation filters is clicked", () => {
        const setSelectedAdaptationHazards = vi.fn();
        renderAdaptations({ setSelectedAdaptationHazards });
        fireEvent.click(screen.getByRole("button", { name: /reset adaptation filters/i }));
        expect(setSelectedAdaptationHazards).toHaveBeenCalledWith([]);
    });

    it("changes the theme filter via the dropdown", () => {
        const setFilterName = vi.fn();
        renderAdaptations({ setFilterName });
        fireEvent.change(screen.getByRole("combobox"), { target: { value: "Nature" } });
        expect(setFilterName).toHaveBeenCalledWith("Nature");
    });

    it("reveals the reference source information when expanded", () => {
        renderAdaptations();
        expect(screen.queryByText(/The adaptation data is based on published scientific literature/i)).toBeNull();
        fireEvent.click(screen.getByRole("button", { name: /reference source information/i }));
        expect(screen.getByText(/The adaptation data is based on published scientific literature/i)).toBeInTheDocument();
    });
});
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/adaptations/StaticAdaptations.test.jsx`
Expected: 6 tests PASS. (If `getByRole("combobox")` is ambiguous, scope it via `screen.getByRole("combobox")` still works because there is a single theme `<select>` in this component.)

- [ ] **Step 3: Commit**

```bash
git add client/src/components/adaptations/StaticAdaptations.test.jsx
git commit -m "test: cover static adaptations filtering and data source"
```

---

### Task 14: Rewrite ClimateSummary.test.jsx

**Files:**
- Modify (full rewrite): `client/src/components/climatePrediction/ClimateSummary.test.jsx`

**Interfaces:**
- Component: `ClimateSummary({ regions, loading, climatePrediction, year, season })`. Returns `null` when `regions.length === 0`. Renders four variable boxes (Temperature/Rainfall/Dry Days/Windiness) whose summary text comes from real `climateUtils.formatClimateData`. Each variable has a clickable icon button (class `climate-icon-button`); clicking `Temperature` shows a `temperature metrics` section with `Tropical Nights` and `Hot Heat Days`; clicking again returns to the placeholder `Please click a climate variable icon to view additional metrics.` Wrapped in `LoadingOverlay` text `Loading climate data`.
- Fixture derivation (real `climateChange` = `value_{year} - value_1980`, `formatClimateData` wording): with the fixture below and `year=2050`: Temperature `12-10=+2` → `Temperature increases by 2.00 °C`; Rainfall `1-2=-1` → `Rainfall decreases by 1.00 mm/day`; Dry Days `8-5=+3` (plural) → `Dry Days increase by 3.00 days/year`; Windiness `sfcWind 4-4=0` → `No change in Windiness`.

- [ ] **Step 1: Replace the file contents entirely**

```jsx
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
        expect(screen.getByText(/Dry Days increase by 3\.00 days\/year/i)).toBeInTheDocument();
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
```

- [ ] **Step 2: Run — expect PASS**

Run: `cd client && npx vitest run src/components/climatePrediction/ClimateSummary.test.jsx`
Expected: 6 tests PASS. If the "No change in" assertion is brittle because the name node is split across elements, replace it with `expect(screen.getByText(/No change in/i)).toBeInTheDocument()` and a separate `expect(screen.getByText("Windiness")).toBeInTheDocument()`.

- [ ] **Step 3: Commit**

```bash
git add client/src/components/climatePrediction/ClimateSummary.test.jsx
git commit -m "test: rewrite ClimateSummary test in canonical Testing Library style"
```

---

### Task 15: Full-suite verification

**Files:** none (verification only).

- [ ] **Step 1: Run the entire test suite**

Run: `cd client && npx vitest run`
Expected: all test files PASS (the 6 pre-existing files plus the ~19 new/rewritten ones).

- [ ] **Step 2: Lint the new test files**

Run: `cd client && npm run lint`
Expected: no errors. Fix any formatting/lint issues (e.g. import order via `eslint-plugin-simple-import-sort`) and re-run.

- [ ] **Step 3: Final commit if lint made changes**

```bash
git add -A client/src/components
git commit -m "style: satisfy lint for new frontend tests"
```

---

## Self-Review

**1. Spec coverage:**
- Tier A (11): PageSelectionModal (T5), PolicyModal (T3), ConsentBanner (T4), ClimateHazardRisk (T8), ClimateImpactSummary (T10), PersonalSocialVulnerabilities (T9), HelpPopover (T7), ClimateSettings (T6), StaticReferences (T11), StaticAdaptation (T12), StaticAdaptations (T13). ✅
- Tier B (8): Feedback (T2), ContactUs (T1), Handbook (T1), AdaptationGuide (T1), Introduction (T2), FooterText (T1), FooterLogos (T1), LinkOutIcon (T2). ✅ (`Header` optional — omitted, as the spec allows.)
- Legacy rewrite: ClimateSummary (T14). ✅
- Boundary handling: localStorage/`open_cookie_banner` (T4, T1), JSON data mocks (T11–T13), gtag left undefined (all). ✅
- Deferred set (Footer/maps/Plotly/Kumu/report/loaders) — not scheduled, as intended. ✅

**2. Placeholder scan:** No TBD/TODO. Every code step contains complete, runnable test code and each expected copy string/URL is quoted verbatim from source. ✅

**3. Type/name consistency:** Component prop names and exported names match source (`CookieConsent`, `CookiePolicyModal`, `PageSelectionModal` props, `setSelectedImpactHazard`, `setSelectedAdaptationHazards`, `setFilterName`). Data-module mock keys (`processed_references.json` string keys; `adaptation_data.json` `attributes.layer`/`ccc adaptation theme`) match consumer code. ✅

**Known risks flagged inline (with fallbacks):** react-collapsed collapsed-content queryability (T11), split-text node for "No change in Windiness" (T14), single-combobox assumption (T13).
