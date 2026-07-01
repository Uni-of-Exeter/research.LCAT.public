# Frontend component test suite expansion — design

Date: 2026-07-01
Branch: `react-tests`
Skill followed: `.github/skills/frontend-testing/SKILL.md`

## Goal

Add thorough, behaviour-focused tests for the untested React components in
`client/src/components`, protecting user-facing behaviour without becoming
brittle. Cover components that render cleanly under Testing Library (no heavy
third-party mocking), and rewrite the one bad legacy component test
(`ClimateSummary.test.jsx`) in the same style. Defer wrappers around Leaflet,
Plotly, Kumu, react-pdf, and fetch to a later pass.

## Current state

- Test stack: Vitest + Testing Library, jsdom, jest-dom matchers via
  `client/src/test-setup.js`. Config in `client/vite.config.js` (svgr + react
  plugins apply in tests).
- Freshly-written, canonical Testing-Library style (keep as-is — the model to
  follow): `vulnerabilities/IMDMap.test.jsx`,
  `adaptations/Reference.test.jsx`.
- Legacy tests brought over from `first-frontend-tests` (commit `6f1df8d`):
  - `climatePrediction/ClimateSummary.test.jsx` — **bad; to be rewritten**
    (see "Legacy rewrite" below). Uses `renderToStaticMarkup` and mocks every
    icon/CSS/child/util, asserting on raw markup regex — brittle and against
    the SKILL.
  - `utils/climateUtils.test.js`, `utils/utils.test.js`,
    `report/textFormattingUtils.test.js` — acceptable pure-function tests;
    left as-is this pass.

## Verified technical assumptions

Confirmed empirically before writing this spec:

1. CSS imports, `react-collapsed`, and `react-loading-overlay-ts` render in the
   test env unmocked (the existing `IMDMap`/`Reference` tests prove this).
2. Icon components imported as `.jsx` (e.g. `images/hazards/AirPollution.jsx`)
   are plain React components — no mocking needed.
3. svgr `.svg` `ReactComponent` imports transform correctly under Vitest
   (probed by rendering `Header`, which imports the LCAT logo `.svg`). The svg
   mocks in the old `ClimateSummary` test were defensive and unnecessary.

Consequence: the only boundaries that need mocking/control are `localStorage`,
`window` custom events, and (optionally) the `gtag` analytics global.

## Approach

Follow the canonical style from the SKILL and `IMDMap`/`Reference`:

- Co-located `ComponentName.test.jsx` next to each component.
- Real rendering via `render` / `screen`; query by role, label, then text.
- One arrange-act-assert flow per test; short behaviour-describing names.
- Small local fixtures; extract a local `renderX` helper only when a file
  repeats large prop literals (as `Reference.test.jsx` does).
- Mock only true boundaries. Do NOT mock CSS, `.jsx`/`.svg` icons,
  `react-collapsed`, or `react-loading-overlay-ts`.
- Use `afterEach(cleanup)` only where a file renders repeatedly and needs it
  (matching existing files); otherwise rely on Testing Library's default.
- No shared test-utils module — the components differ enough that local helpers
  are clearer than a shared abstraction (YAGNI).

Rejected alternatives:

- Heavy-mock / `renderToStaticMarkup` style (old `ClimateSummary` test): the
  SKILL discourages it and it is unnecessary given the verified assumptions.
- A shared render/fixtures utility module: premature abstraction across
  dissimilar components.

## Boundary handling

- `localStorage`: provided by jsdom. `ConsentBanner` reads/writes it; clear it
  in `beforeEach` and reset `window.gtag` where the accept path defines it.
- `window` events: `ConsentBanner` listens for `open_cookie_banner`; drive it
  with `window.dispatchEvent(new Event("open_cookie_banner"))`.
- `gtag`: a bare global guarded by `typeof gtag !== "undefined"`. Left
  undefined in tests, the analytics calls are skipped. Analytics firing is an
  implementation detail, not user-facing behaviour, so tests do not assert on
  it (per the SKILL).

## Scope — target components

### Tier A — interactive behaviour (11)

| Component | Behaviour to cover |
|---|---|
| `footer/PageSelectionModal` | null when `isOpen` false; checkbox toggles selection; live "(N pages)" count; Generate disabled at 0 selected; Cancel, Escape, and overlay click call `onClose`; Generate calls `onGenerate` with selected ids then closes |
| `cookies/PolicyModal` | null when `open` false; `dialog` role + `aria-modal`; Escape and overlay click call `onClose`; renders policy content when open |
| `cookies/ConsentBanner` | hidden when `cookie_consent` stored; shown when unset; Accept writes `"true"` + hides; Decline writes `"false"` + hides; "cookie policy" button opens `PolicyModal`; `open_cookie_banner` event reshows the banner |
| `climateHazard/ClimateHazardRisk` | renders a button per hazard; placeholder text before selection; clicking a hazard shows its heading/details; coastal filter removes "Coastal Erosion" |
| `climateImpacts/ClimateImpactSummary` | renders pathway `<select>`; changing it swaps the impacts shown; loading overlay text present; coastal filter removes coastal pathways |
| `vulnerabilities/PersonalSocialVulnerabilities` | renders a button per vulnerability; placeholder before selection; clicking shows details + external link |
| `climatePrediction/HelpPopover` | renders trigger children; click toggles the popover (content shown/hidden); hover shows; Escape and click-outside close |
| `climatePrediction/ClimateSettings` | null when `regions` empty; renders region names via `andify`; rcp `<select>` change calls `setRcp` and swaps the RCP explanation text; season `<select>` change calls `setSeason` |
| `adaptations/StaticReferences` | renders reference entries from data; collapse toggle reveals/hides; filters references by selected hazard |
| `adaptations/StaticAdaptation` | renders adaptation title; collapse toggle reveals details/nested references |
| `adaptations/StaticAdaptations` | renders filter buttons; clicking a hazard filter toggles it in/out of the selected set; data-source toggle shows/hides source |

### Tier B — static display (8)

Assert headings, key text, and that links have the correct `href` and
accessible names.

| Component | Behaviour to cover |
|---|---|
| `feedback/Feedback` | heading; survey link with correct `href`, `target="_blank"`, and aria-label |
| `footer/ContactUs` | heading/text; contact link(s) resolve correctly |
| `footer/Handbook` | link points to `LCAT_HANDBOOK_URL` |
| `footer/AdaptationGuide` | link points to `ADAPTATION_INTRO_PDF_URL` |
| `header/Introduction` | intro text; handbook link points to `LCAT_HANDBOOK_URL` |
| `footer/FooterText` | key static text present |
| `footer/FooterLogos` | renders the expected logos/links |
| `vulnerabilities/LinkOutIcon` | renders an svg; respects `size`/`colour` props |

`header/Header` (renders only the logo) is optional — a single render smoke
test if cheap; skip if it adds no meaningful coverage.

### Legacy rewrite — `climatePrediction/ClimateSummary.test.jsx`

Replace the existing brittle test wholesale with a canonical Testing-Library
version. `ClimateSummary` is a rich interactive component, not a static block,
so drive it with real `climateUtils` and a small fixture `climatePrediction`
(rows keyed like `tas_1980` / `tas_2050`); do NOT mock icons, CSS, `HelpPopover`
or the util functions. Cover:

- Returns null when `regions` is empty.
- Renders the four main variables (Temperature, Rainfall, Dry Days, Windiness)
  with summary text derived from the fixture (increase / decrease / "No change
  in").
- Clicking a variable's icon button reveals its detail metrics (e.g. clicking
  Temperature shows the "temperature metrics" heading with Tropical Nights and
  Hot Heat Days); clicking again returns to the placeholder.
- Shows the placeholder prompt before any selection.
- Surfaces the loading overlay text ("Loading climate data") when `loading`.
- Season affects derived units where visible (annual vs seasonal wording), if
  cheaply assertable.

Query by role/heading/text throughout; no markup-regex assertions.

## Deferred (out of scope this pass — heavy deps)

`footer/Footer` (react-pdf `usePDF`), `climateMap/ClimateMap` &
`GeoJSONLoader` (Leaflet), `climatePrediction/Graph` (Plotly),
`climateImpacts/KumuImpactPathway` (iframe), `report/*` (react-pdf),
`loaders/*` (fetch-driven).

## Execution & verification

- Implement in small batches (roughly by directory), running
  `npx vitest run` after each batch; every test green before continuing.
- Final gate: full `npx vitest run` green and `npm run lint` clean on new
  files (`eslint . --ext .js,.jsx`).
- All commits land on the `react-tests` branch.

## Out of scope

- The three acceptable legacy util-style tests (`utils/utils.test.js`,
  `utils/climateUtils.test.js`, `report/textFormattingUtils.test.js`) are left
  as-is; only `ClimateSummary.test.jsx` is rewritten.
- Testing pure data modules (`*Data.jsx`) directly — covered indirectly via the
  components that consume them.
- Analytics (`gtag`) assertions.
