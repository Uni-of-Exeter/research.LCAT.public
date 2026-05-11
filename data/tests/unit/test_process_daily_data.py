import numpy as np
import pytest

from data.src.process_daily_data import ClimateDataProcessor

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def processor():
    """ClimateDataProcessor instance with minimal config (no network calls)."""
    config = {"chess_scape_netcdf_location": "/data/climate/"}
    return ClimateDataProcessor(config)


def make_data(n_time, n_y=3, n_x=3, fill=5.0):
    """Helper: uniform array of shape (n_time, n_y, n_x)."""
    return np.full((n_time, n_y, n_x), fill, dtype=float)


# =============================================================================
# calculate_threshold_days
# =============================================================================


class TestCalculateThresholdDays:
    def test_exact_periods_annual(self, processor):
        """10 complete annual periods (3600 days): mean = days_per_year meeting threshold."""
        # All 3600 days have value 5.0; threshold = 3.0 (gte) → all days meet it
        data = make_data(3600, fill=5.0)
        result = processor.calculate_threshold_days(
            data, threshold=3.0, comparison="gte", season="annual"
        )

        assert result.shape == (3, 3)
        # 3600 days / 10 periods = 360 days/period, all meeting threshold → mean = 360
        np.testing.assert_array_almost_equal(result, 360.0)

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

    def test_partial_period_excluded_warns(self, processor, capsys):
        """A partial period should print a WARNING message."""
        data = make_data(3630, fill=5.0)  # 3600 + 30 trailing days
        processor.calculate_threshold_days(data, threshold=3.0, season="annual")

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "30 trailing days excluded" in captured.out

    def test_no_warning_for_exact_periods(self, processor, capsys):
        """Exact periods should not print a WARNING."""
        data = make_data(3600, fill=5.0)
        processor.calculate_threshold_days(data, threshold=3.0, season="annual")

        captured = capsys.readouterr()
        assert "WARNING" not in captured.out

    def test_seasonal_normalization_summer(self, processor):
        """season='summer' uses 90 days/period."""
        # 10 complete summer periods = 900 days, all meeting threshold → mean = 90
        data = make_data(900, fill=5.0)
        result = processor.calculate_threshold_days(
            data, threshold=3.0, season="summer"
        )
        np.testing.assert_array_almost_equal(result, 90.0)

    def test_seasonal_normalization_winter(self, processor):
        """season='winter' uses 90 days/period."""
        data = make_data(900, fill=5.0)
        result = processor.calculate_threshold_days(
            data, threshold=3.0, season="winter"
        )
        np.testing.assert_array_almost_equal(result, 90.0)

    def test_comparison_lte(self, processor):
        """lte comparison: days with value <= threshold are counted."""
        # 360 days; value = 2.0, threshold = 3.0 → all days meet lte → mean = 360
        data = make_data(360, fill=2.0)
        result = processor.calculate_threshold_days(
            data, threshold=3.0, comparison="lte", season="annual"
        )
        np.testing.assert_array_almost_equal(result, 360.0)

    def test_comparison_gte_none_meet(self, processor):
        """No days meet threshold → mean = 0."""
        data = make_data(360, fill=1.0)
        result = processor.calculate_threshold_days(
            data, threshold=5.0, comparison="gte", season="annual"
        )
        np.testing.assert_array_almost_equal(result, 0.0)

    def test_invalid_comparison_raises(self, processor):
        data = make_data(360)
        with pytest.raises(ValueError, match="Invalid comparison"):
            processor.calculate_threshold_days(data, threshold=5.0, comparison="eq")

    def test_invalid_season_raises(self, processor):
        data = make_data(360)
        with pytest.raises(ValueError, match="Invalid season"):
            processor.calculate_threshold_days(data, threshold=5.0, season="spring")

    def test_convert_kelvin(self, processor):
        """convert_kelvin=True subtracts 273.15 before comparison."""
        # 293.15 K = 20 °C; threshold = 15 °C (gte) → all days meet it
        data = make_data(360, fill=293.15)
        result = processor.calculate_threshold_days(
            data, threshold=15.0, comparison="gte", convert_kelvin=True, season="annual"
        )
        np.testing.assert_array_almost_equal(result, 360.0)

    def test_convert_kelvin_threshold_not_met(self, processor):
        """convert_kelvin=True: days below threshold after conversion → 0."""
        # 283.15 K = 10 °C; threshold = 15 °C → no days meet it
        data = make_data(360, fill=283.15)
        result = processor.calculate_threshold_days(
            data, threshold=15.0, comparison="gte", convert_kelvin=True, season="annual"
        )
        np.testing.assert_array_almost_equal(result, 0.0)

    def test_convert_precip(self, processor):
        """convert_precip=True multiplies by 86400 before comparison."""
        # 1e-4 kg m-2 s-1 * 86400 = 8.64 mm/day; threshold = 5.0 mm/day (gte) → all meet
        data = make_data(360, fill=1e-4)
        result = processor.calculate_threshold_days(
            data, threshold=5.0, comparison="gte", convert_precip=True, season="annual"
        )
        np.testing.assert_array_almost_equal(result, 360.0)

    def test_output_shape(self, processor):
        """Output shape matches spatial dimensions of input."""
        data = make_data(360, n_y=5, n_x=7)
        result = processor.calculate_threshold_days(
            data, threshold=3.0, season="annual"
        )
        assert result.shape == (5, 7)

    def test_partial_period_trailing_all_meet_does_not_inflate(self, processor):
        """
        Regression test for the float-division bug:
        Adding a partial period where every trailing day meets the threshold
        must not inflate the mean above the value from exact periods.
        """
        # Half the days per period meet the threshold (180/360 = 0.5 per year)
        n_y, n_x = 2, 2
        rng = np.random.default_rng(42)

        # Build 3600 days: first 180 of each 360-day block meet threshold, rest don't
        blocks = []
        for _ in range(10):
            block = np.zeros((360, n_y, n_x))
            block[:180] = 10.0  # above threshold=5
            blocks.append(block)
        data_exact = np.concatenate(blocks, axis=0)

        # Add 30 trailing days all meeting threshold
        trailing = np.full((30, n_y, n_x), 10.0)
        data_partial = np.concatenate([data_exact, trailing], axis=0)

        result_exact = processor.calculate_threshold_days(
            data_exact, threshold=5.0, season="annual"
        )
        result_partial = processor.calculate_threshold_days(
            data_partial, threshold=5.0, season="annual"
        )

        np.testing.assert_array_almost_equal(result_partial, result_exact)
        np.testing.assert_array_almost_equal(result_exact, 180.0)
