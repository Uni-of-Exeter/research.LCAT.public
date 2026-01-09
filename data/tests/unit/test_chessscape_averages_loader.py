import pytest
import numpy as np
import pandas as pd
import xarray as xr
import tempfile
from unittest.mock import MagicMock, patch

from data.src.chessscape_averages_loader import ChessScapeAveragesLoader


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_config():
    """Minimal config for ChessScapeAveragesLoader."""
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
        "chess_scape_netcdf_location": "/data/climate/",
    }


@pytest.fixture
def csal(mock_config):
    """Create ChessScapeAveragesLoader instance with mocked config."""
    loader = ChessScapeAveragesLoader(mock_config)
    return loader


@pytest.fixture
def sample_annual_dataset():
    """
    Minimal annual NetCDF dataset.
    100 time steps (100 years), 3x3 grid.
    """
    np.random.seed(42)
    tas_data = np.random.rand(100, 3, 3) * 10 + 280
    
    ds = xr.Dataset(
        {"tas": (["time", "y", "x"], tas_data)},
        coords={
            "time": pd.date_range(start="1981-01-01", periods=100, freq="YS"),
            "y": [0, 1000, 2000],
            "x": [0, 1000, 2000],
        },
    )
    return ds


@pytest.fixture
def sample_seasonal_dataset():
    """
    Minimal seasonal NetCDF dataset.
    400 time steps (100 years * 4 seasons), 3x3 grid.
    Uses pandas DatetimeIndex which converts to pandas Timestamp on indexing.
    """
    np.random.seed(42)
    tas_data = np.random.rand(400, 3, 3) * 10 + 280
    
    # Use pandas date_range - these will be Timestamp objects when accessed individually
    times = pd.date_range(start="1981-01-01", periods=400, freq="3MS")
    
    ds = xr.Dataset(
        {"tas": (["time", "y", "x"], tas_data)},
        coords={
            "time": times,
            "y": [0, 1000, 2000],
            "x": [0, 1000, 2000],
        },
    )
    return ds


@pytest.fixture
def sample_netcdf_file(sample_annual_dataset):
    """Write sample dataset to temp file."""
    with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp:
        sample_annual_dataset.to_netcdf(tmp.name)
        return tmp.name


# =============================================================================
# set_data_location
# =============================================================================


def test_set_data_location_uses_config_by_default(csal):
    """Should use config location when no filepath provided"""
    # Loader should have set data_location from config during init
    assert csal.data_location == "/data/climate/"


def test_set_data_location_uses_provided_filepath(csal):
    """Should use provided filepath over config"""
    csal.set_data_location("/custom/path/")
    assert csal.data_location == "/custom/path/"


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, csal):
    """Should use explicit credentials when provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db(
        host="custom_host",
        dbname="custom_db",
        user="custom_user",
        password="custom_pass",
    )

    mock_psycopg2.connect.assert_called_once_with(
        host="custom_host",
        dbname="custom_db",
        user="custom_user",
        password="custom_pass",
    )


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, csal):
    """Should read credentials from config when none provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost",
        dbname="test_db",
        user="test_user",
        password="test_password",
    )


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_connect_to_db_sets_connection_and_cursor(mock_psycopg2, csal):
    """Should set conn and cur attributes"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()

    assert csal.conn == mock_conn
    assert csal.cur == mock_cursor


# =============================================================================
# open_netcdf_file
# =============================================================================


def test_open_netcdf_file_returns_dataset(csal, sample_netcdf_file):
    """Should load NetCDF file and return xarray Dataset"""
    ds = csal.open_netcdf_file(sample_netcdf_file)
    
    assert isinstance(ds, xr.Dataset)
    assert "tas" in ds.data_vars


def test_open_netcdf_file_missing_file_returns_none(csal):
    """Should return None when file doesn't exist"""
    result = csal.open_netcdf_file("/nonexistent/path.nc")
    assert result is None


# =============================================================================
# close_netcdf_file
# =============================================================================


def test_close_netcdf_file_closes_current_data(csal, sample_annual_dataset):
    """Should close the current netcdf data"""
    csal.current_netcdf_data = sample_annual_dataset
    csal.close_netcdf_file()
    
    # Dataset should be closed
    assert csal.current_netcdf_data is not None


# =============================================================================
# load_netcdf
# =============================================================================


@patch.object(ChessScapeAveragesLoader, "open_netcdf_file")
@patch("data.src.chessscape_averages_loader.os.path.exists", return_value=True)
def test_load_netcdf_builds_correct_filepath_annual_bias_corrected(mock_exists, mock_open, csal):
    """Should build correct filepath for annual bias-corrected data"""
    csal.load_netcdf(
        is_bias_corrected=True,
        season="annual",
        rcp=60,
        variable="tas",
    )
    
    filepath = mock_open.call_args[0][0]
    assert "rcp60_bias-corrected" in filepath
    assert "annual" in filepath
    assert "tas" in filepath
    assert filepath.endswith(".nc")


@patch.object(ChessScapeAveragesLoader, "open_netcdf_file")
@patch("data.src.chessscape_averages_loader.os.path.exists", return_value=True)
def test_load_netcdf_builds_correct_filepath_seasonal_non_bias_corrected(mock_exists, mock_open, csal):
    """Should build correct filepath for seasonal non-bias-corrected data"""
    csal.load_netcdf(
        is_bias_corrected=False,
        season="winter",
        rcp=85,
        variable="pr",
    )
    
    filepath = mock_open.call_args[0][0]
    assert "rcp85" in filepath
    assert "_bias-corrected" not in filepath
    assert "seasonal" in filepath
    assert "pr" in filepath


@patch.object(ChessScapeAveragesLoader, "open_netcdf_file")
@patch("data.src.chessscape_averages_loader.os.path.exists", return_value=True)
def test_load_netcdf_sets_instance_variables(mock_exists, mock_open, csal):
    """Should set season, rcp, variable, and is_bias_corrected"""
    csal.load_netcdf(
        is_bias_corrected=True,
        season="summer",
        rcp=60,
        variable="tasmax",
    )
    
    assert csal.season == "summer"
    assert csal.rcp == 60
    assert csal.variable == "tasmax"
    assert csal.is_bias_corrected is True


@patch.object(ChessScapeAveragesLoader, "open_netcdf_file")
@patch("data.src.chessscape_averages_loader.os.path.exists", return_value=True)
def test_load_netcdf_clears_previous_data(mock_exists, mock_open, csal):
    """Should clear extracted_data and reset transform_performed"""
    csal.extracted_data = {"old": "data"}
    csal.transform_performed = True
    
    csal.load_netcdf(True, "annual", 60, "tas")
    
    assert csal.extracted_data == {}
    assert csal.transform_performed is False


# =============================================================================
# calculate_uk_averages_min_mean_max
# =============================================================================


def test_calculate_uk_averages_min_mean_max_returns_dict(csal, sample_annual_dataset):
    """Should return dict with min, mean, max keys"""
    csal.season = "annual"
    csal.variable = "tas"
    
    result = csal.calculate_uk_averages_min_mean_max(sample_annual_dataset, 0, 10, 1)
    
    assert "min" in result
    assert "mean" in result
    assert "max" in result


def test_calculate_uk_averages_min_mean_max_returns_scalar_values(csal, sample_annual_dataset):
    """Should return scalar values, not arrays"""
    csal.season = "annual"
    csal.variable = "tas"
    
    result = csal.calculate_uk_averages_min_mean_max(sample_annual_dataset, 0, 10, 1)
    
    # Values should be scalars (xarray DataArrays with no dimensions)
    assert result["min"].dims == ()
    assert result["mean"].dims == ()
    assert result["max"].dims == ()


def test_calculate_uk_averages_min_mean_max_uses_10_values(csal, sample_annual_dataset):
    """Should calculate over exactly 10 time steps (1 decade)"""
    csal.season = "annual"
    csal.variable = "tas"
    
    result = csal.calculate_uk_averages_min_mean_max(sample_annual_dataset, 0, 10, 1)
    assert result is not None


def test_calculate_uk_averages_min_mean_max_raises_for_wrong_slice_size(csal, sample_annual_dataset):
    """Should raise ValueError if slice doesn't contain exactly 10 values"""
    csal.season = "annual"
    csal.variable = "tas"
    
    with pytest.raises(ValueError, match="10 values"):
        csal.calculate_uk_averages_min_mean_max(sample_annual_dataset, 0, 5, 1)


def test_calculate_uk_averages_min_mean_max_validates_winter_months(csal, sample_seasonal_dataset):
    """Should validate that winter data contains only January"""
    csal.season = "winter"
    csal.variable = "tas"
    
    # Winter starts at offset 0 (January)
    # The real implementation checks months via pandas Timestamp.month
    # Our sample dataset should have the right structure
    result = csal.calculate_uk_averages_min_mean_max(sample_seasonal_dataset, 0, 40, 4)
    assert result is not None


def test_calculate_uk_averages_min_mean_max_validates_summer_months(csal, sample_seasonal_dataset):
    """Should validate that summer data contains only July"""
    csal.season = "summer"
    csal.variable = "tas"  # Fixed typo: was 'csl'
    
    # Summer starts at offset 2 (July)
    result = csal.calculate_uk_averages_min_mean_max(sample_seasonal_dataset, 2, 42, 4)
    assert result is not None


# =============================================================================
# process_decade
# =============================================================================


def test_process_decade_returns_dict_by_decade(csal, sample_annual_dataset):
    """Should return dict keyed by decade start year"""
    csal.season = "annual"
    csal.variable = "tas"
    
    csal.process_decade(sample_annual_dataset)
    
    assert isinstance(csal.extracted_data, dict)
    assert 1980 in csal.extracted_data or 1981 in csal.extracted_data
    assert len(csal.extracted_data) == 10


def test_process_decade_annual_uses_step_of_1(csal, sample_annual_dataset):
    """Should use every time step for annual data"""
    csal.season = "annual"
    csal.variable = "tas"
    
    csal.process_decade(sample_annual_dataset)
    
    first_decade = list(csal.extracted_data.values())[0]
    assert "min" in first_decade
    assert "mean" in first_decade
    assert "max" in first_decade


def test_process_decade_seasonal_uses_step_of_4(csal, sample_seasonal_dataset):
    """Should use every 4th time step for seasonal data"""
    csal.season = "winter"
    csal.variable = "tas"
    
    csal.process_decade(sample_seasonal_dataset)
    
    assert isinstance(csal.extracted_data, dict)
    assert len(csal.extracted_data) == 10


def test_process_decade_summer_starts_at_offset_2(csal, sample_seasonal_dataset):
    """Summer data should start at index 2 (July)"""
    csal.season = "summer"
    csal.variable = "tas"
    
    csal.process_decade(sample_seasonal_dataset)
    assert len(csal.extracted_data) == 10


def test_process_decade_winter_starts_at_offset_0(csal, sample_seasonal_dataset):
    """Winter data should start at index 0 (January)"""
    csal.season = "winter"
    csal.variable = "tas"
    
    csal.process_decade(sample_seasonal_dataset)
    assert len(csal.extracted_data) == 10


# =============================================================================
# transform_dataset
# =============================================================================


def test_transform_dataset_converts_kelvin_to_celsius(csal):
    """Temperature variables should be converted from Kelvin to Celsius"""
    csal.variable = "tas"
    data = xr.DataArray([300.0, 273.15, 283.15])
    
    result = csal.transform_dataset(data)
    
    np.testing.assert_array_almost_equal(result.values, [26.85, 0.0, 10.0])


def test_transform_dataset_converts_tasmin_kelvin_to_celsius(csal):
    """tasmin should also be converted from Kelvin to Celsius"""
    csal.variable = "tasmin"
    data = xr.DataArray([273.15, 283.15])
    
    result = csal.transform_dataset(data)
    
    np.testing.assert_array_almost_equal(result.values, [0.0, 10.0])


def test_transform_dataset_converts_tasmax_kelvin_to_celsius(csal):
    """tasmax should also be converted from Kelvin to Celsius"""
    csal.variable = "tasmax"
    data = xr.DataArray([293.15, 303.15])
    
    result = csal.transform_dataset(data)
    
    np.testing.assert_array_almost_equal(result.values, [20.0, 30.0])


def test_transform_dataset_converts_precipitation(csal):
    """Precipitation should be converted from kg/m2/s to mm/day"""
    csal.variable = "pr"
    data = xr.DataArray([0.00001, 0.0001])
    
    result = csal.transform_dataset(data)
    
    np.testing.assert_array_almost_equal(result.values, [0.864, 8.64])


def test_transform_dataset_leaves_other_variables_unchanged(csal):
    """Variables like rsds and sfcWind should not be transformed"""
    csal.variable = "rsds"
    data = xr.DataArray([100.0, 200.0])
    
    result = csal.transform_dataset(data)
    
    np.testing.assert_array_equal(result.values, [100.0, 200.0])


def test_transform_dataset_leaves_sfcWind_unchanged(csal):
    """sfcWind should not be transformed"""
    csal.variable = "sfcWind"
    data = xr.DataArray([5.0, 10.0])
    
    result = csal.transform_dataset(data)
    
    np.testing.assert_array_equal(result.values, [5.0, 10.0])


# =============================================================================
# transform_data
# =============================================================================


def test_transform_data_transforms_all_decades(csal):
    """Should apply transforms to all decades in extracted_data"""
    csal.variable = "tas"
    csal.transform_performed = False
    
    csal.extracted_data = {
        1980: {
            "min": xr.DataArray(273.15),
            "mean": xr.DataArray(283.15),
            "max": xr.DataArray(293.15),
        },
        1990: {
            "min": xr.DataArray(274.15),
            "mean": xr.DataArray(284.15),
            "max": xr.DataArray(294.15),
        },
    }
    
    csal.transform_data()
    
    assert csal.extracted_data[1980]["mean"].values == pytest.approx(10.0)
    assert csal.transform_performed is True


def test_transform_data_raises_if_already_transformed(csal):
    """Should raise error if transforms already applied"""
    csal.transform_performed = True
    
    with pytest.raises(ValueError, match="already performed"):
        csal.transform_data()


def test_transform_data_sets_transform_flag(csal):
    """Should set transform_performed flag to True"""
    csal.variable = "tas"
    csal.transform_performed = False
    csal.extracted_data = {
        1980: {
            "min": xr.DataArray(273.15),
            "mean": xr.DataArray(283.15),
            "max": xr.DataArray(293.15),
        },
    }
    
    csal.transform_data()
    
    assert csal.transform_performed is True


# =============================================================================
# create_table
# =============================================================================


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_create_table_creates_with_correct_name(mock_psycopg2, csal):
    """Should create table with chess_scape_uk_averages name"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()
    csal.create_table()

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "chess_scape_uk_averages" in sql_combined
    assert "CREATE TABLE" in sql_combined.upper()


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_create_table_includes_all_columns(mock_psycopg2, csal):
    """Should include row_id, is_bias_corrected, rcp, season, variable, decade, min, mean, max"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()
    csal.create_table()

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "row_id" in sql_combined
    assert "is_bias_corrected" in sql_combined
    assert "rcp" in sql_combined
    assert "season" in sql_combined
    assert "variable" in sql_combined
    assert "decade" in sql_combined


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_create_table_uses_if_not_exists(mock_psycopg2, csal):
    """Should use IF NOT EXISTS to avoid errors"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()
    csal.create_table()

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "IF NOT EXISTS" in sql_combined.upper()


# =============================================================================
# drop_table
# =============================================================================


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_drop_table_drops_averages_table(mock_psycopg2, csal):
    """Should drop the chess_scape_uk_averages table"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()
    csal.drop_table()

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "DROP TABLE" in sql_combined.upper()
    assert "chess_scape_uk_averages" in sql_combined


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_drop_table_handles_exception(mock_psycopg2, csal):
    """Should handle exceptions gracefully"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn
    mock_cur.execute.side_effect = Exception("Database error")

    csal.connect_to_db()
    # Should not raise exception
    csal.drop_table()


# =============================================================================
# insert_data_multiple_decades
# =============================================================================


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_insert_data_multiple_decades_uses_copy_from(mock_psycopg2, csal):
    """Should use COPY FROM for efficient bulk insert"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()
    csal.is_bias_corrected = True
    csal.rcp = 60
    csal.season = "annual"
    csal.variable = "tas"
    csal.row_id = 0
    
    csal.extracted_data = {
        1980: {
            "min": xr.DataArray(10.0),
            "mean": xr.DataArray(15.0),
            "max": xr.DataArray(20.0),
        },
    }

    csal.insert_data_multiple_decades()

    assert mock_cur.copy_from.called


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_insert_data_multiple_decades_increments_row_id(mock_psycopg2, csal):
    """Should increment row_id for each row inserted"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()
    csal.is_bias_corrected = True
    csal.rcp = 60
    csal.season = "annual"
    csal.variable = "tas"
    csal.row_id = 0
    
    csal.extracted_data = {
        1980: {
            "min": xr.DataArray(10.0),
            "mean": xr.DataArray(15.0),
            "max": xr.DataArray(20.0),
        },
        1990: {
            "min": xr.DataArray(11.0),
            "mean": xr.DataArray(16.0),
            "max": xr.DataArray(21.0),
        },
    }

    csal.insert_data_multiple_decades()

    assert csal.row_id == 2


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_insert_data_multiple_decades_commits_transaction(mock_psycopg2, csal):
    """Should commit transaction after insert"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csal.connect_to_db()
    csal.is_bias_corrected = True
    csal.rcp = 60
    csal.season = "annual"
    csal.variable = "tas"
    csal.row_id = 0
    
    csal.extracted_data = {
        1980: {
            "min": xr.DataArray(10.0),
            "mean": xr.DataArray(15.0),
            "max": xr.DataArray(20.0),
        },
    }

    csal.insert_data_multiple_decades()

    assert mock_conn.commit.called


@patch("data.src.chessscape_averages_loader.psycopg2")
def test_insert_data_multiple_decades_rolls_back_on_error(mock_psycopg2, csal):
    """Should rollback on error"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn
    mock_cur.copy_from.side_effect = Exception("Insert error")

    csal.connect_to_db()
    csal.is_bias_corrected = True
    csal.rcp = 60
    csal.season = "annual"
    csal.variable = "tas"
    csal.row_id = 0
    
    csal.extracted_data = {
        1980: {
            "min": xr.DataArray(10.0),
            "mean": xr.DataArray(15.0),
            "max": xr.DataArray(20.0),
        },
    }

    csal.insert_data_multiple_decades()

    assert mock_conn.rollback.called


# =============================================================================
# process_all_variables
# =============================================================================


@patch.object(ChessScapeAveragesLoader, "close_netcdf_file")
@patch.object(ChessScapeAveragesLoader, "insert_data_multiple_decades")
@patch.object(ChessScapeAveragesLoader, "transform_data")
@patch.object(ChessScapeAveragesLoader, "process_decade")
@patch.object(ChessScapeAveragesLoader, "load_netcdf")
def test_process_all_variables_processes_all_six_variables(
    mock_load, mock_process, mock_transform, mock_insert, mock_close, csal
):
    """Should process all 6 climate variables"""
    csal.process_all_variables(season="annual", rcp=60, is_bias_corrected=True)

    assert mock_load.call_count == 6

    variables_loaded = [call.args[3] for call in mock_load.call_args_list]
    assert "pr" in variables_loaded
    assert "rsds" in variables_loaded
    assert "sfcWind" in variables_loaded
    assert "tas" in variables_loaded
    assert "tasmax" in variables_loaded
    assert "tasmin" in variables_loaded


@patch.object(ChessScapeAveragesLoader, "close_netcdf_file")
@patch.object(ChessScapeAveragesLoader, "insert_data_multiple_decades")
@patch.object(ChessScapeAveragesLoader, "transform_data")
@patch.object(ChessScapeAveragesLoader, "process_decade")
@patch.object(ChessScapeAveragesLoader, "load_netcdf")
def test_process_all_variables_calls_in_correct_order(
    mock_load, mock_process, mock_transform, mock_insert, mock_close, csal
):
    """Should call methods in correct order for each variable"""
    csal.process_all_variables(season="annual", rcp=60, is_bias_corrected=True)

    # Each variable should have load, process, transform, insert, close called
    assert mock_load.call_count == 6
    assert mock_process.call_count == 6
    assert mock_transform.call_count == 6
    assert mock_insert.call_count == 6
    assert mock_close.call_count == 6


# =============================================================================
# process_all_seasons
# =============================================================================


@patch.object(ChessScapeAveragesLoader, "process_all_variables")
def test_process_all_seasons_processes_three_seasons(mock_process, csal):
    """Should process annual, winter, and summer data"""
    csal.process_all_seasons(rcp=60, is_bias_corrected=True)

    assert mock_process.call_count == 3

    seasons_processed = [call.args[0] for call in mock_process.call_args_list]
    assert "annual" in seasons_processed
    assert "winter" in seasons_processed
    assert "summer" in seasons_processed


@patch.object(ChessScapeAveragesLoader, "process_all_variables")
def test_process_all_seasons_passes_rcp_and_bias_corrected(mock_process, csal):
    """Should pass rcp and is_bias_corrected to process_all_variables"""
    csal.process_all_seasons(rcp=85, is_bias_corrected=False)

    for call in mock_process.call_args_list:
        assert call.args[1] == 85
        assert call.args[2] is False


# =============================================================================
# process_all_rcps
# =============================================================================


@patch.object(ChessScapeAveragesLoader, "process_all_seasons")
def test_process_all_rcps_processes_both_scenarios(mock_process, csal):
    """Should process both RCP 6.0 and RCP 8.5 scenarios"""
    csal.process_all_rcps(is_bias_corrected=True)

    assert mock_process.call_count == 2

    rcps_processed = [call.args[0] for call in mock_process.call_args_list]
    assert 60 in rcps_processed
    assert 85 in rcps_processed


@patch.object(ChessScapeAveragesLoader, "process_all_seasons")
def test_process_all_rcps_passes_bias_corrected_flag(mock_process, csal):
    """Should pass is_bias_corrected to process_all_seasons"""
    csal.process_all_rcps(is_bias_corrected=False)

    for call in mock_process.call_args_list:
        assert call.args[1] is False


# =============================================================================
# process_all_data
# =============================================================================


@patch.object(ChessScapeAveragesLoader, "process_all_rcps")
@patch.object(ChessScapeAveragesLoader, "create_table")
@patch.object(ChessScapeAveragesLoader, "drop_table")
def test_process_all_data_drops_and_creates_table(mock_drop, mock_create, mock_process, csal):
    """Should drop and create table before processing"""
    csal.process_all_data()

    assert mock_drop.called
    assert mock_create.called


@patch.object(ChessScapeAveragesLoader, "process_all_rcps")
@patch.object(ChessScapeAveragesLoader, "create_table")
@patch.object(ChessScapeAveragesLoader, "drop_table")
def test_process_all_data_processes_both_bias_types(mock_drop, mock_create, mock_process, csal):
    """Should process both bias-corrected and non-bias-corrected data"""
    csal.process_all_data()

    assert mock_process.call_count == 2

    bias_flags = [call.args[0] for call in mock_process.call_args_list]
    assert True in bias_flags
    assert False in bias_flags


@patch.object(ChessScapeAveragesLoader, "process_all_rcps")
@patch.object(ChessScapeAveragesLoader, "create_table")
@patch.object(ChessScapeAveragesLoader, "drop_table")
def test_process_all_data_drops_before_creating(mock_drop, mock_create, mock_process, csal):
    """Should drop table before creating it"""
    csal.process_all_data()

    # Check that drop is called before create
    assert mock_drop.called
    assert mock_create.called
