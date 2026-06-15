---
name: python-data-processing-testing
description: "Use when writing or expanding Python unit tests for offline data-processing modules in data/src, with readable pytest patterns and pragmatic fixture/mocking choices."
user-invocable: true
---

# Python Data Processing Testing

Use this skill when adding or improving tests for the offline data-processing pipeline in `data/src/`.

## Scope

These functions are not part of the live app request path. They are used before runtime to build, transform, validate, and cache data.

Focus on deterministic unit tests that validate transformation logic, edge cases, and failure handling.

## Goal

Write tests that are readable, stable, and specific to behavior that matters for data quality and reproducibility.

Prefer a small number of clear tests over large, brittle tests that over-specify implementation details.

## What To Test

- Normal behavior on representative arrays, frames, and records.
- Edge cases: empty input, partial periods, invalid parameter values, and shape mismatches.
- Conversion and normalization paths (unit conversions, naming cleanup, filtering rules).
- Failure paths and guardrails: expected `ValueError`, skipped processing, and warning output.
- Output contracts: returned shape, key fields, schema expectations, and invariant values.

## How To Write The Tests

- Follow existing style in `data/tests/unit/` before introducing new patterns.
- Use small fixtures and helper builders to keep setup obvious.
- Prefer explicit assertions over snapshots.
- Use `pytest.mark.parametrize` for compact coverage of input/output permutations.
- Mock only external boundaries (database, file I/O, network, third-party scraping).
- Keep one behavior focus per test; split tests that assert unrelated outcomes.

## Repo Conventions

- Unit tests live in `data/tests/unit/`.
- Aim for one test module per source module in `data/src/`.
- Run tests from `data/` with Poetry:

```bash
cd data
poetry install
poetry run pytest
```

- Coverage output is enabled via `data/pytest.ini`.

## Good Coverage Patterns

- Validate exact outputs for deterministic numeric transformations.
- Add regression tests for known bugs (for example trailing-partial-period handling).
- Assert specific exception messages where they communicate contract guarantees.
- Check that optional flags actually affect behavior (`convert_kelvin`, `convert_precip`, etc.).
- Verify output shape and dtype expectations for array-based processors.

## Keep It Readable

- Use arrange-act-assert structure.
- Keep test names explicit and behavior-focused.
- Use helper functions like `make_data(...)` for repeated input generation.
- Keep mocks local to the test unless they are reused broadly.
- Avoid over-randomized fixtures; prefer deterministic values.

## Example Approach

Use a concrete pattern like this from `data/tests/unit/test_process_daily_data.py`:

```python
def test_partial_period_excluded(self, processor):
    """Trailing 30 days (one incomplete period) must not change the result."""
    # 10 complete annual periods = 3600 days, all meeting threshold
    data_exact = make_data(3600, fill=5.0)
    result_exact = processor.calculate_threshold_days(
        data_exact, threshold=3.0, season="annual"
    )

    # Add 30 trailing days that ALL meet the threshold — old float division
    # would inflate the mean; new code should give identical result
    trailing = make_data(30, fill=5.0)
    data_partial = np.concatenate([data_exact, trailing], axis=0)
    result_partial = processor.calculate_threshold_days(
        data_partial, threshold=3.0, season="annual"
    )

    np.testing.assert_array_almost_equal(result_partial, result_exact)


def test_zero_periods_raises_annual(self, processor):
    """Fewer days than one annual period must raise ValueError, not silently produce inf."""
    data = make_data(30)  # 30 < 360 days/annual period
    with pytest.raises(
        ValueError, match="Not enough data for even one complete annual period"
    ):
        processor.calculate_threshold_days(data, threshold=3.0, season="annual")
```

This is usually enough for one function: one normal-path test, one edge-case/regression test, and one contract/exception test.