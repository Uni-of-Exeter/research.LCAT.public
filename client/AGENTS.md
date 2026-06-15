# Client Agent Guide

Use this file when the task is primarily in `client/`.
Prefer behavior-focused fixes and tests.

## 1) Scope and boundaries

-   Owns React UI, rendering logic, and user interactions.
-   Treat `server/` and `data/` as external dependencies unless wiring requires changes.

If the task is purely UI behavior, stay in `client/`.

## 2) First commands

From repo root:

```bash
cd client
npm install
npm run lint
npm run format
npm test -- --run
```

If formatting needs fixing:

```bash
cd client
npm run format:fix
```

For active development:

```bash
cd client
npm run dev
```

## 3) Implementation rules

-   Keep changes local to the touched feature/component.
-   Prefer existing component and utility patterns over new abstractions.
-   Do not refactor unrelated components in the same change.

## 4) Testing rules

-   Use Vitest + Testing Library.
-   Test visible behavior and interactions, not component internals.
-   Prefer role-based queries (`getByRole`) and accessible names.
-   Add or update tests with logic changes whenever practical.

Decision table:

| Situation                           | Action                                          |
| ----------------------------------- | ----------------------------------------------- |
| New UI state/branch                 | Add a focused render-state test                 |
| Click/toggle changes UI             | Add an interaction test                         |
| Helper function has branching logic | Add unit tests for branch thresholds/edge cases |

## 5) Canonical examples

-   Behavior and link rendering tests: `src/components/vulnerabilities/IMDMap.test.jsx`.
-   Utility and state defaults: `src/utils/defaultState.js`, `src/utils/utils.js`.

## 6) Useful references

-   Frontend testing skill: `../.github/skills/frontend-testing/SKILL.md`.
-   Repo-level defaults: `../AGENTS.md`.

Use references on demand; avoid broad doc exploration for small UI changes.
