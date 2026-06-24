---
name: frontend-testing
description: "Use when writing or expanding React frontend tests in this repo, especially readable Vitest and Testing Library coverage for display, accessibility, and interactions."
user-invocable: true
---

# Frontend Testing

Use this skill when adding or improving tests for the client app in `client/`.

## Goal

Write tests that protect user-facing behaviour without becoming brittle or over-specified. Prefer a small number of clear tests that show what the component renders and how it responds to user actions.

## What To Test

- What the user can see: text, links, buttons, headings, labels, and empty states.
- What the user can do: click, expand, collapse, submit, navigate, and select.
- What changes after interaction: new content appears, state toggles, a link points somewhere else, or a fetch-driven result is shown.
- Boundary states: no data, partial data, loading, and failed requests where those states matter.

## How To Write The Tests

- Start from the public behaviour of the component, not its internals.
- Prefer `screen.getByRole`, `getByLabelText`, and `getByText` over querying implementation details.
- Give tests short, descriptive names that read like the behaviour being checked.
- Keep each test focused on one visible outcome or one interaction path.
- Use small fixtures that are easy to understand at a glance.
- Mock only external boundaries such as network calls, browser APIs, or heavy third-party widgets.
- Avoid snapshot tests unless the output is genuinely hard to express as assertions.

## Repo Conventions

- The test stack is Vitest plus Testing Library.
- Jest DOM matchers are already available through `client/src/test-setup.js`.
- Favour `afterEach(cleanup)` only when the file needs it explicitly; let Testing Library do the default cleanup when possible.
- When testing a collapsible or fetch-on-open component, render the component, trigger the user action, then assert the visible result.

## Good Coverage Patterns

- Render nothing when the component has no usable input.
- Render the correct controls and links for each supported case.
- Verify accessible names on interactive elements.
- Verify that a click or toggle changes what the user sees.
- Verify default values when data has not yet been fetched.
- Verify that mixed inputs still show the right subset of UI.

## Keep It Readable

- Use one arrange-act-assert flow per test.
- Use helper fixtures instead of repeating large object literals.
- If a test needs a lot of setup, extract the setup into a small local helper.
- If the test starts asserting too many unrelated things, split it.
- Prefer the simplest mock that makes the behaviour testable.

## Example Approach

Use a concrete pattern like this from `IMDMap.test.jsx`:

```jsx
it("renders nothing when regions is empty", () => {
	const { container } = render(<IMDMap regions={[]} regionType="boundary_uk_counties" />);
	expect(container.firstChild).toBeNull();
});

it("shows England link and hides others for an English region", () => {
	render(<IMDMap regions={[ENGLAND]} regionType="boundary_uk_counties" />);
	expect(screen.getByRole("link", { name: /deprivation data for England/i })).toBeInTheDocument();
	expect(screen.queryByRole("link", { name: /deprivation data for Scotland/i })).toBeNull();
	expect(screen.queryByRole("link", { name: /deprivation data for Wales/i })).toBeNull();
	expect(screen.queryByRole("link", { name: /deprivation data for Northern Ireland/i })).toBeNull();
});
```

This is usually enough. Do not test implementation details unless they are part of the public behaviour.