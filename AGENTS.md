# LCAT Agent Guide

Use this file as the default operating guide for this repository.
Keep changes focused, test the module you touched, and avoid broad refactors.

## 1) Repo map and ownership

- `client/`: React + Vite front end (port 3001 in dev).
- `server/`: Express API + static serving (port 3000).
- `data/`: offline Python data processing and DB build pipeline.
- `docs/`: setup and data/build documentation.

If a task is mostly in one module, stay in that module unless wiring requires cross-module edits.

When working inside `client/` or `data/`, read that folder's local `AGENTS.md` first and follow it as the primary guide for module-specific work.

## 2) Task routing (decision table)

| Task type | Primary module | First command |
| --- | --- | --- |
| UI rendering, interactions, component behavior | `client/` | `cd client && npm run test` |
| API route logic, DB query plumbing, server startup | `server/` | `cd server && npm run lint` |
| Climate preprocessing, loaders, cached table generation | `data/` | `cd data && poetry run pytest` |

## 3) Required workflow for code changes

1. Identify target module first (`client`, `server`, or `data`).
2. Make the smallest change that satisfies the task.
3. Run the narrowest relevant checks.
4. If checks fail, fix before expanding scope.
5. Summarize what changed, why, and what was run.

## 4) Testing expectations

- Client: test visible behavior and interactions; avoid over-testing implementation details.
- Data: test deterministic transformations, edge cases, and explicit failure paths.
- Server: lint at minimum; if route behavior changes, validate by running server and hitting affected endpoint.

When adding logic, add or update tests in the same module whenever practical.

## 5) "Do / Don’t" pairs

- Do: prefer module-local fixes and module-local tests.
- Don’t: edit unrelated modules "for cleanup" in the same change.

- Do: use existing patterns from neighboring files.
- Don’t: introduce new frameworks or patterns without need.

- Do: pair each warning with a concrete action.
- Don’t: leave vague notes like "needs refactor" without a scoped follow-up.

- Do: keep docs concise and actionable.
- Don’t: add long architecture narratives in task-focused edits.

## 6) Writing style and British English

- Always write in British English in all code comments, documentation, docstrings, and communication.
- Use British spelling conventions (e.g., "colour", "organise", "favour", "realise", "centre", "analyse", "recognised").
- Use British conventions for terminology (e.g., "car boot" not "trunk", "flat" not "apartment").
- This applies to: commit messages, pull request descriptions, code review feedback, documentation, and generated content.

## 7) Module-specific guidance

- Use `client/AGENTS.md` for frontend commands, test patterns, and canonical examples.
- Use `data/AGENTS.md` for offline data-processing commands, test patterns, and canonical examples.
- For server-only tasks, use `server/package.json` scripts and local route patterns in `server/routes/api.js`.

Follow local module style before introducing a new pattern.

## 8) References (load only when needed)

- Installation and run flow: `docs/3-install.md`.
- Data module usage and tests: `data/README.md`.
- Frontend testing conventions skill: `.github/skills/frontend-testing/SKILL.md`.
- Data testing conventions skill: `.github/skills/python-data-processing-testing/SKILL.md`.

Scoped guides:

- `client/AGENTS.md` (frontend-specific workflow and testing guidance).
- `data/AGENTS.md` (offline data-processing workflow and testing guidance).

Only open additional docs when the current task requires them.

## 9) External infra repository (optional, on-demand)

- Primary source for infra context: sibling repo at `../research.LCAT`.
- Secondary reference only: `https://github.com/Uni-of-Exeter/research.LCAT`.
- Use infra repo only for deployment, CI/CD, environment variables, container/runtime config, reverse proxy, or production wiring tasks.
- Do not consult infra repo for module-local app logic changes in `client/`, `server/`, or `data/` unless there is a clear infra dependency.

Decision table:

| Situation | Action |
| --- | --- |
| App code change only | Stay in this repo |
| Build/deploy mismatch | Check `../research.LCAT` workflows and runtime config |
| Env mismatch between local and deployed | Check `../research.LCAT` env/config definitions |

If `../research.LCAT` is missing or unreadable and infra context is required, stop and ask the user before continuing.