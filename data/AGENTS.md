# Data Agent Guide

Use this file when the task is primarily in `data/`.
This module is an offline pipeline (not app runtime request handling).

## 1) Scope and boundaries

- Owns data ingestion, transformation, and database build/cache routines.
- Primary code lives in `src/`; tests in `tests/unit/`.
- Do not edit `client/` or `server/` unless output contracts or wiring require it.

## 2) First commands

From repo root:

```bash
cd data
poetry install
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
```

If formatting needs fixing:

```bash
cd data
poetry run ruff format .
```

For targeted work, run narrow tests first:

```bash
cd data
poetry run pytest tests/unit/test_process_daily_data.py
```

## 3) Implementation rules

- Prefer deterministic transformations and explicit failure behavior.
- Keep function signatures and output schema stable unless task requires change.
- Avoid broad pipeline refactors in task-focused fixes.

## 4) Testing rules

- Use pytest unit tests with small, explicit fixtures.
- Test normal path + edge case + failure/guardrail when relevant.
- Mock external boundaries (DB, filesystem, network/scraping), not pure transforms.
- Assert output shape/values/contracts directly.

Decision table:

| Situation | Action |
| --- | --- |
| Numeric transform logic changed | Add exact-value assertions (`numpy`/`pandas` helpers as needed) |
| New parameter branch | Add parameterized branch tests |
| Expected exception/warning path | Assert message and trigger condition |

## 5) Canonical examples

- Threshold and regression tests: `tests/unit/test_process_daily_data.py`.
- Mocked file-IO transformation tests: `tests/unit/test_process_kumu.py`.
- Mocked DB interaction tests: `tests/unit/test_cache_climate.py`.

## 6) Useful references

- Data testing skill: `../.github/skills/python-data-processing-testing/SKILL.md`.
- Module setup and test notes: `README.md`.
- Repo-level defaults: `../AGENTS.md`.

Use references on demand; keep context lean and task-specific.
