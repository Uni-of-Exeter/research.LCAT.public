import pytest
import numpy as np
import pandas as pd
import xarray as xr
import tempfile
from unittest.mock import MagicMock, patch, call

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


def test_close_netcdf_file_calls_close(csal):
    """Should call .close() on the current NetCDF dataset"""

    mock_dataset = MagicMock()
    csal.current_netcdf_data = mock_dataset

    csal.close_netcdf_file()

    mock_dataset.close.assert_called_once()


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


@patch("data.src.chessscape_averages_loader.os.path.exists", return_value=False)
def test_load_netcdf_sets_current_data_to_none_if_file_missing(mock_exists, csal):
    """Should set current_netcdf_data to None when filepath does not exist"""

    # First simulate having old data loaded
    csal.current_netcdf_data = MagicMock()

    csal.load_netcdf(
        is_bias_corrected=True,
        season="annual",
        rcp=60,
        variable="tas",
    )

    assert csal.current_netcdf_data is None


# =============================================================================
# calculate_uk_averages_mean
# =============================================================================


def test_calculate_uk_averages_mean_returns_dataarray(csal, sample_annual_dataset):
    """Should return an xarray DataArray"""
    csal.season = "annual"
    csal.variable = "tas"

    result = csal.calculate_uk_averages_mean(sample_annual_dataset["tas"], 0, 10, 1)

    assert isinstance(result, xr.DataArray)


def test_calculate_uk_averages_mean_returns_scalar(csal, sample_annual_dataset):
    """Should return scalar value (DataArray with no dimensions)"""
    csal.season = "annual"
    csal.variable = "tas"

    result = csal.calculate_uk_averages_mean(sample_annual_dataset["tas"], 0, 10, 1)

    assert result.dims == ()


def test_calculate_uk_averages_mean_validates_winter_months(
    csal, sample_seasonal_dataset
):
    """Should validate that winter data contains only January"""
    csal.season = "winter"
    csal.variable = "tas"

    result = csal.calculate_uk_averages_mean(sample_seasonal_dataset["tas"], 0, 40, 4)
    assert result is not None


def test_calculate_uk_averages_mean_validates_summer_months(
    csal, sample_seasonal_dataset
):
    """Should validate that summer data contains only July"""
    csal.season = "summer"
    csal.variable = "tas"

    result = csal.calculate_uk_averages_mean(sample_seasonal_dataset["tas"], 2, 42, 4)
    assert result is not None


def test_calculate_uk_averages_mean_raises_for_wrong_winter_month(
    csal, sample_seasonal_dataset
):
    """Should raise ValueError if winter slice does not contain January months"""
    csal.season = "winter"
    csal.variable = "tas"

    with pytest.raises(ValueError, match="Different months"):
        csal.calculate_uk_averages_mean(
            sample_seasonal_dataset["tas"],
            lower_bound=1,
            higher_bound=41,
            step=4,
        )


# =============================================================================
# process_decade
# =============================================================================


def test_process_decade_annual_produces_expected_keys_and_stats(csal, sample_annual_dataset):
    """
    Annual:
    - produces 10 decades
    - decade tags match the current indexing scheme (1980..2070 step 10)
    - each decade has min/mean/max
    """
    csal.season = "annual"
    csal.variable = "tas"

    csal.process_decade(sample_annual_dataset)

    assert isinstance(csal.extracted_data, dict)

    expected_keys = list(range(1980, 2080, 10))  # 1980..2070
    assert sorted(csal.extracted_data.keys()) == expected_keys
    assert len(csal.extracted_data) == 10

    first_decade = csal.extracted_data[expected_keys[0]]
    assert isinstance(first_decade, xr.DataArray)


def test_process_decade_winter_seasonal_produces_expected_keys(csal, sample_seasonal_dataset):
    """
    Seasonal (winter):
    - produces 10 decades
    - decade tags match the current indexing scheme (1980..2070 step 10)
    """
    csal.season = "winter"
    csal.variable = "tas"

    csal.process_decade(sample_seasonal_dataset)

    expected_keys = list(range(1980, 2080, 10))
    assert sorted(csal.extracted_data.keys()) == expected_keys
    assert len(csal.extracted_data) == 10


def test_process_decade_summer_starts_at_index_2_and_uses_step_4(csal, sample_seasonal_dataset):
    """
    Seasonal (summer):
    prove the offset/step logic by checking the first call into
    calculate_uk_averages_min_mean_max uses lower=2, higher=42, step=4.
    """
    csal.season = "summer"
    csal.variable = "tas"

    dummy = xr.DataArray(0.0)

    with patch.object(
        ChessScapeAveragesLoader,
        "calculate_uk_averages_mean",
        return_value=dummy,
    ) as mock_calc:
        csal.process_decade(sample_seasonal_dataset)

    # First decade slice should be [2:42:4]
    first_call_args = mock_calc.call_args_list[0].args
    assert first_call_args[1] == 2
    assert first_call_args[2] == 42
    assert first_call_args[3] == 4

    assert mock_calc.call_count == 10


# =============================================================================
# transform_dataset
# =============================================================================


@pytest.mark.parametrize(
    "variable, data, expected, approx",
    [
        ("tas", xr.DataArray([300.0, 273.15, 283.15]), [26.85, 0.0, 10.0], True),
        ("tasmin", xr.DataArray([273.15, 283.15]), [0.0, 10.0], True),
        ("tasmax", xr.DataArray([293.15, 303.15]), [20.0, 30.0], True),
        ("pr", xr.DataArray([0.00001, 0.0001]), [0.864, 8.64], True),
        ("rsds", xr.DataArray([100.0, 200.0]), [100.0, 200.0], False),
        ("sfcWind", xr.DataArray([5.0, 10.0]), [5.0, 10.0], False),
    ],
)
def test_transform_dataset_parameterised(csal, variable, data, expected, approx):
    """transform_dataset should apply correct unit transforms depending on variable."""
    csal.variable = variable
    result = csal.transform_dataset(data)

    if approx:
        np.testing.assert_allclose(result.values, expected, rtol=1e-7, atol=1e-7)
    else:
        np.testing.assert_array_equal(result.values, expected)


# =============================================================================
# transform_data
# =============================================================================


def test_transform_data_transforms_all_decades(csal):
    """Should apply transforms to all decades in extracted_data"""
    csal.variable = "tas"
    csal.transform_performed = False

    csal.extracted_data = {
        1980: xr.DataArray(283.15),
        1990: xr.DataArray(284.15),
    }

    csal.transform_data()

    assert float(csal.extracted_data[1980].values) == pytest.approx(10.0)
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
        1980: xr.DataArray(283.15),
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
def test_insert_data_multiple_decades_calls_copy_from_with_expected_args(mock_psycopg2, csal):
    """Should call copy_from with expected table name and columns."""
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
        1980: xr.DataArray(15.0),
    }

    csal.insert_data_multiple_decades()

    mock_cur.copy_from.assert_called_once()

    args, kwargs = mock_cur.copy_from.call_args

    # Positional args: (file, table, ...)
    assert args[1] == csal.table_name

    # Keyword args: sep, columns
    assert kwargs["sep"] == ","
    assert kwargs["columns"] == [
        "row_id",
        "is_bias_corrected",
        "rcp",
        "season",
        "variable",
        "decade",
        "mean",
    ]

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
        1980: xr.DataArray(15.0),
        1990: xr.DataArray(16.0),
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
        1980: xr.DataArray(15.0),
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
        1980: xr.DataArray(15.0),
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


def test_process_all_variables_calls_methods_in_correct_order(csal):
    """Should call load -> process -> transform -> insert -> close in that order for each variable."""
    call_log = []

    def load_side_effect(is_bias_corrected, season, rcp, variable):
        # mimic the real method setting state so the log can include variable name
        csal.variable = variable
        call_log.append(("load", variable))

    def process_side_effect(_data):
        call_log.append(("process", csal.variable))

    def transform_side_effect():
        call_log.append(("transform", csal.variable))

    def insert_side_effect():
        call_log.append(("insert", csal.variable))

    def close_side_effect():
        call_log.append(("close", csal.variable))

    with patch.object(ChessScapeAveragesLoader, "load_netcdf", side_effect=load_side_effect), \
         patch.object(ChessScapeAveragesLoader, "process_decade", side_effect=process_side_effect), \
         patch.object(ChessScapeAveragesLoader, "transform_data", side_effect=transform_side_effect), \
         patch.object(ChessScapeAveragesLoader, "insert_data_multiple_decades", side_effect=insert_side_effect), \
         patch.object(ChessScapeAveragesLoader, "close_netcdf_file", side_effect=close_side_effect):

        # current_netcdf_data is accessed as an argument to process_decade
        # but our process_side_effect ignores it, so it can be anything
        csal.current_netcdf_data = MagicMock()

        csal.process_all_variables(season="annual", rcp=60, is_bias_corrected=True)

    expected_vars = ["pr", "rsds", "sfcWind", "tas", "tasmax", "tasmin"]

    expected_log = []
    for v in expected_vars:
        expected_log.extend(
            [("load", v), ("process", v), ("transform", v), ("insert", v), ("close", v)]
        )

    assert call_log == expected_log

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


def test_process_all_data_calls_drop_create_then_process_in_order(csal):
    """Should call drop_table -> create_table -> process_all_rcps(True) -> process_all_rcps(False) in order."""
    parent = MagicMock()

    with patch.object(ChessScapeAveragesLoader, "drop_table") as mock_drop, \
         patch.object(ChessScapeAveragesLoader, "create_table") as mock_create, \
         patch.object(ChessScapeAveragesLoader, "process_all_rcps") as mock_process:

        # Attach mocks to a parent so we can assert global ordering
        parent.attach_mock(mock_drop, "drop_table")
        parent.attach_mock(mock_create, "create_table")
        parent.attach_mock(mock_process, "process_all_rcps")

        csal.process_all_data()

        assert parent.mock_calls == [
            call.drop_table(),
            call.create_table(),
            call.process_all_rcps(True),
            call.process_all_rcps(False),
        ]
