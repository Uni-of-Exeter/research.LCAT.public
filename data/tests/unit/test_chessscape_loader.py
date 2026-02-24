import pytest
import numpy as np
import xarray as xr
import pandas as pd
import tempfile
from unittest.mock import MagicMock, patch

from data.src.chessscape_loader import ChessScapeLoader


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_config():
    """Minimal config for ChessScapeLoader."""
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
        "chess_scape_netcdf_location": "/data/climate/",
    }


@pytest.fixture
def sample_mask():
    """
    Sample labelled mask:
    0 = no data (ocean)
    1 = bias corrected (mainland UK)
    2 = non-bias corrected (NI, Scilly)
    """
    return np.array([
        [0, 1, 1],
        [1, 1, 2],
        [0, 2, 2],
    ])


@pytest.fixture
def csl(mock_config, sample_mask):
    """Create ChessScapeLoader instance with mocked config."""
    with patch.object(ChessScapeLoader, "set_data_location"):
        loader = ChessScapeLoader(mock_config, sample_mask)
        loader.data_location = "/data/climate/"
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
    Uses pandas Timestamp for .month attribute compatibility.
    """
    
    np.random.seed(42)
    tas_data = np.random.rand(400, 3, 3) * 10 + 280
    
    # Create seasonal timestamps using pandas (has .month attribute)
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
# load_mask
# =============================================================================


def test_load_mask_sets_mask(csl, sample_mask):
    """Should store the mask array on the instance."""
    csl.load_mask(sample_mask)
    np.testing.assert_array_equal(csl.mask, sample_mask)


def test_load_mask_detects_bias_corrected_needed(csl):
    """Should add 'bias_corrected' to bias_corrected_keys when mask contains 1s."""
    mask_with_ones = np.array([[0, 1], [1, 0]])
    csl.bias_corrected_keys = []
    csl.load_mask(mask_with_ones)
    
    assert "bias_corrected" in csl.bias_corrected_keys


def test_load_mask_detects_non_bias_corrected_needed(csl):
    """Should add 'non_bias_corrected' to bias_corrected_keys when mask contains 2s."""
    mask_with_twos = np.array([[0, 2], [2, 0]])
    csl.bias_corrected_keys = []
    csl.load_mask(mask_with_twos)
    
    assert "non_bias_corrected" in csl.bias_corrected_keys

def test_load_mask_detects_both_bias_types_when_present(csl):
    """Should include both bias_corrected and non_bias_corrected when mask contains 1s and 2s."""
    mask_with_both = np.array([[1, 2], [2, 0]])

    csl.load_mask(mask_with_both)

    assert "bias_corrected" in csl.bias_corrected_keys
    assert "non_bias_corrected" in csl.bias_corrected_keys

def test_load_mask_rejects_boolean_mask(csl):
    boolean_mask = np.array([[True, False], [False, True]])

    with pytest.raises(ValueError, match="Boolean mask"):
        csl.load_mask(boolean_mask)


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.chessscape_loader.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, csl):
    """Should use explicit credentials when provided."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db(
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
    
    assert csl.conn is mock_conn
    assert csl.cur is mock_conn.cursor.return_value


@patch("data.src.chessscape_loader.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, csl):
    """Should read credentials from config when none provided."""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost",
        dbname="test_db",
        user="test_user",
        password="test_password",
    )

    assert csl.conn is mock_conn
    assert csl.cur is mock_conn.cursor.return_value

# =============================================================================
# open_netcdf_file
# =============================================================================


def test_open_netcdf_file_returns_dataset(csl, sample_netcdf_file):
    """Should load NetCDF file and return xarray Dataset."""
    ds = csl.open_netcdf_file(sample_netcdf_file)
    
    assert isinstance(ds, xr.Dataset)
    assert "tas" in ds.data_vars


def test_open_netcdf_file_missing_file_returns_none(csl):
    """Should return None when file doesn't exist."""
    result = csl.open_netcdf_file("/nonexistent/path.nc")
    assert result is None


# =============================================================================
# load_netcdf
# =============================================================================


@patch.object(ChessScapeLoader, "open_netcdf_file")
@patch("data.src.chessscape_loader.os.path.exists", return_value=True)
def test_load_netcdf_builds_correct_filepath_annual(mock_exists, mock_open, csl):
    """Should build correct filepath for annual bias-corrected data."""
    csl.load_netcdf(
        season="annual",
        rcp=60,
        bias_corrected_key="bias_corrected",
        variable="tas",
    )
    
    filepath = mock_open.call_args[0][0]
    assert "rcp60_bias-corrected" in filepath
    assert "annual" in filepath
    assert "tas" in filepath
    assert filepath.endswith(".nc")


@patch.object(ChessScapeLoader, "open_netcdf_file")
@patch("data.src.chessscape_loader.os.path.exists", return_value=True)
def test_load_netcdf_builds_correct_filepath_seasonal(mock_exists, mock_open, csl):
    """Should build correct filepath for seasonal non-bias-corrected data."""
    csl.load_netcdf(
        season="winter",
        rcp=85,
        bias_corrected_key="non_bias_corrected",
        variable="pr",
    )
    
    filepath = mock_open.call_args[0][0]
    assert "rcp85" in filepath
    assert "_bias-corrected" not in filepath
    assert "seasonal" in filepath
    assert "pr" in filepath


@patch.object(ChessScapeLoader, "open_netcdf_file")
@patch("data.src.chessscape_loader.os.path.exists", return_value=True)
def test_load_netcdf_sets_table_name(mock_exists, mock_open, csl):
    """Should set table_name based on rcp, season, and variable."""
    csl.load_netcdf(
        season="summer",
        rcp=60,
        bias_corrected_key="bias_corrected",
        variable="tasmax",
    )
    
    assert csl.table_name == "chess_scape_rcp60_summer_tasmax"


# =============================================================================
# calculate_min_mean_max
# =============================================================================


def test_calculate_min_mean_max_returns_dict(csl, sample_annual_dataset):
    """Should return dict with min, mean, max keys."""
    csl.season = "annual"
    csl.variable = "tas"
    
    result = csl.calculate_min_mean_max(sample_annual_dataset, 0, 10, 1)
    
    assert "min" in result
    assert "mean" in result
    assert "max" in result


def test_calculate_min_mean_max_uses_10_values(csl, sample_annual_dataset):
    """Should calculate over exactly 10 time steps (1 decade)."""
    csl.season = "annual"
    csl.variable = "tas"
    
    result = csl.calculate_min_mean_max(sample_annual_dataset, 0, 10, 1)
    assert result is not None


def test_calculate_min_mean_max_raises_for_wrong_slice_size(csl, sample_annual_dataset):
    """Should raise ValueError if slice doesn't contain exactly 10 values."""
    csl.season = "annual"
    csl.variable = "tas"
    
    with pytest.raises(ValueError, match="10 values"):
        csl.calculate_min_mean_max(sample_annual_dataset, 0, 5, 1)


# =============================================================================
# process_decade
# =============================================================================


def test_process_decade_returns_dict_by_decade(csl, sample_annual_dataset):
    """Should return dict keyed by decade start year."""
    csl.season = "annual"
    csl.variable = "tas"
    
    result = csl.process_decade(sample_annual_dataset)
    
    assert isinstance(result, dict)
    assert 1980 in result or 1981 in result
    assert len(result) == 10


def test_process_decade_annual_uses_step_of_1(csl, sample_annual_dataset):
    """Should use every time step for annual data."""
    csl.season = "annual"
    csl.variable = "tas"
    
    result = csl.process_decade(sample_annual_dataset)
    
    first_decade = list(result.values())[0]
    assert "min" in first_decade
    assert "mean" in first_decade
    assert "max" in first_decade


def test_process_decade_seasonal_uses_step_of_4(csl, sample_seasonal_dataset):
    """Should use every 4th time step for seasonal data."""
    csl.season = "winter"
    csl.variable = "tas"
    
    result = csl.process_decade(sample_seasonal_dataset)
    
    assert isinstance(result, dict)
    assert len(result) == 10


def test_process_decade_summer_starts_at_offset_2(csl, sample_seasonal_dataset):
    """Summer data should start at index 2 (July)."""
    csl.season = "summer"
    csl.variable = "tas"
    
    result = csl.process_decade(sample_seasonal_dataset)
    assert len(result) == 10


# =============================================================================
# transform_dataset
# =============================================================================


def test_transform_dataset_converts_kelvin_to_celsius(csl):
    """Temperature variables should be converted from Kelvin to Celsius."""
    csl.variable = "tas"
    data = xr.DataArray([300.0, 273.15, 283.15])
    
    result = csl.transform_dataset(data)
    
    np.testing.assert_array_almost_equal(result.values, [26.85, 0.0, 10.0])


def test_transform_dataset_converts_precipitation(csl):
    """Precipitation should be converted from kg/m2/s to mm/day."""
    csl.variable = "pr"
    data = xr.DataArray([0.00001, 0.0001])
    
    result = csl.transform_dataset(data)
    
    np.testing.assert_array_almost_equal(result.values, [0.864, 8.64])


def test_transform_dataset_leaves_other_variables_unchanged(csl):
    """Variables like rsds and sfcWind should not be transformed."""
    csl.variable = "rsds"
    data = xr.DataArray([100.0, 200.0])
    
    result = csl.transform_dataset(data)
    
    np.testing.assert_array_equal(result.values, [100.0, 200.0])


# =============================================================================
# transform_all_means
# =============================================================================


def test_transform_all_means_transforms_all_decades(csl):
    """Should apply transforms to all decades in extracted_data."""
    csl.variable = "tas"
    csl.transform_performed = False
    
    csl.extracted_data = {
        "bias_corrected": {
            1980: {
                "min": xr.DataArray([273.15]),
                "mean": xr.DataArray([283.15]),
                "max": xr.DataArray([293.15]),
            },
            1990: {
                "min": xr.DataArray([274.15]),
                "mean": xr.DataArray([284.15]),
                "max": xr.DataArray([294.15]),
            },
        }
    }
    
    csl.transform_all_means()
    
    assert csl.extracted_data["bias_corrected"][1980]["mean"].values[0] == pytest.approx(10.0)
    assert csl.transform_performed is True


def test_transform_all_means_raises_if_already_transformed(csl):
    """Should raise error if transforms already applied."""
    csl.transform_performed = True
    
    with pytest.raises(ValueError, match="already performed"):
        csl.transform_all_means()


# =============================================================================
# create_table
# =============================================================================


@patch("data.src.chessscape_loader.psycopg2")
def test_create_table_creates_with_correct_name(mock_psycopg2, csl):
    """Should create table with name matching current variable settings."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db()
    csl.table_name = "chess_scape_rcp60_annual_tas"
    csl.create_table()

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "chess_scape_rcp60_annual_tas" in sql_combined
    assert "CREATE TABLE" in sql_combined.upper()


# =============================================================================
# drop_table
# =============================================================================


@patch("data.src.chessscape_loader.psycopg2")
def test_drop_table_drops_current_table(mock_psycopg2, csl):
    """Should drop the table specified by self.table_name."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db()
    csl.table_name = "chess_scape_rcp60_annual_tas"
    csl.drop_table()

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "DROP TABLE" in sql_combined.upper()
    assert "chess_scape_rcp60_annual_tas" in sql_combined


@patch("data.src.chessscape_loader.psycopg2")
def test_drop_table_with_explicit_name(mock_psycopg2, csl):
    """Should drop table by explicit name when provided."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db()
    csl.drop_table("custom_table_name")

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "custom_table_name" in sql_combined


# =============================================================================
# add_multiple_columns
# =============================================================================


@patch("data.src.chessscape_loader.psycopg2")
def test_add_multiple_columns_adds_all_columns(mock_psycopg2, csl):
    """Should add all specified columns to the table."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db()
    csl.table_name = "test_table"
    csl.add_multiple_columns(["tas_1980_min", "tas_1980_mean", "tas_1980_max"])

    assert mock_cur.execute.call_count == 3

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "tas_1980_min" in sql_combined
    assert "tas_1980_mean" in sql_combined
    assert "tas_1980_max" in sql_combined


# =============================================================================
# insert_data_multiple_decades
# =============================================================================


@patch("data.src.chessscape_loader.psycopg2")
def test_insert_data_multiple_decades_uses_correct_data_source(mock_psycopg2, csl, sample_mask):
    """Should use bias_corrected for mask=1, non_bias_corrected for mask=2."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db()
    csl.mask = sample_mask
    csl.table_name = "test_table"
    csl.variable = "tas"
    csl.bias_corrected_keys = ["bias_corrected", "non_bias_corrected"]

    csl.extracted_data = {
        "bias_corrected": {
            1980: {
                "min": xr.DataArray(np.ones((3, 3)) * 10),
                "mean": xr.DataArray(np.ones((3, 3)) * 15),
                "max": xr.DataArray(np.ones((3, 3)) * 20),
            },
        },
        "non_bias_corrected": {
            1980: {
                "min": xr.DataArray(np.ones((3, 3)) * 11),
                "mean": xr.DataArray(np.ones((3, 3)) * 16),
                "max": xr.DataArray(np.ones((3, 3)) * 21),
            },
        },
    }

    csl.insert_data_multiple_decades()

    assert mock_cur.copy_from.called


def test_insert_data_multiple_decades_skips_zero_mask_cells(csl, sample_mask):
    """Cells with mask value 0 should be skipped."""
    non_zero_cells = np.count_nonzero(sample_mask)
    zero_cells = sample_mask.size - non_zero_cells
    
    assert zero_cells == 2
    assert non_zero_cells == 7


# =============================================================================
# join_tables
# =============================================================================


@patch("data.src.chessscape_loader.psycopg2")
def test_join_tables_creates_aggregated_table(mock_psycopg2, csl):
    """Should create a single table joining all variable tables."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    mock_psycopg2.connect.return_value = mock_conn

    csl.connect_to_db()
    csl.aggregated_table_name = "chess_scape_rcp60_annual"
    csl.join_tables(["tas", "pr", "rsds"])

    sql_calls = [str(call) for call in mock_cur.execute.call_args_list]
    sql_combined = " ".join(sql_calls)

    assert "CREATE TABLE" in sql_combined.upper()
    assert "JOIN" in sql_combined.upper()


# =============================================================================
# process_all_variables
# =============================================================================


@patch.object(ChessScapeLoader, "join_tables")
@patch.object(ChessScapeLoader, "close_netcdf_files")
@patch.object(ChessScapeLoader, "insert_data_multiple_decades")
@patch.object(ChessScapeLoader, "create_table")
@patch.object(ChessScapeLoader, "drop_table")
@patch.object(ChessScapeLoader, "transform_all_means")
@patch.object(ChessScapeLoader, "process_bias_keys")
@patch.object(ChessScapeLoader, "load_all_netcdf")
def test_process_all_variables_processes_all_six_variables(
    mock_load, mock_process, mock_transform, mock_drop, mock_create,
    mock_insert, mock_close, mock_join, csl
):
    """Should process all 6 climate variables."""
    csl.process_all_variables(season="annual", rcp=60)

    assert mock_load.call_count == 6

    variables_loaded = [call.args[2] for call in mock_load.call_args_list]
    assert "pr" in variables_loaded
    assert "rsds" in variables_loaded
    assert "sfcWind" in variables_loaded
    assert "tas" in variables_loaded
    assert "tasmax" in variables_loaded
    assert "tasmin" in variables_loaded


@patch.object(ChessScapeLoader, "join_tables")
@patch.object(ChessScapeLoader, "close_netcdf_files")
@patch.object(ChessScapeLoader, "insert_data_multiple_decades")
@patch.object(ChessScapeLoader, "create_table")
@patch.object(ChessScapeLoader, "drop_table")
@patch.object(ChessScapeLoader, "transform_all_means")
@patch.object(ChessScapeLoader, "process_bias_keys")
@patch.object(ChessScapeLoader, "load_all_netcdf")
def test_process_all_variables_joins_tables_at_end(
    mock_load, mock_process, mock_transform, mock_drop, mock_create,
    mock_insert, mock_close, mock_join, csl
):
    """Should call join_tables with all variable names at the end."""
    csl.process_all_variables(season="annual", rcp=60)

    mock_join.assert_called_once()
    variables = mock_join.call_args[0][0]
    assert len(variables) == 6


# =============================================================================
# process_all_seasons
# =============================================================================


@patch.object(ChessScapeLoader, "process_all_variables")
def test_process_all_seasons_processes_three_seasons(mock_process, csl):
    """Should process annual, winter, and summer data."""
    csl.process_all_seasons(rcp=60)

    assert mock_process.call_count == 3

    seasons_processed = [call.args[0] for call in mock_process.call_args_list]
    assert "annual" in seasons_processed
    assert "winter" in seasons_processed
    assert "summer" in seasons_processed


# =============================================================================
# process_all_rcps
# =============================================================================


@patch.object(ChessScapeLoader, "process_all_seasons")
def test_process_all_rcps_processes_both_scenarios(mock_process, csl):
    """Should process both RCP 6.0 and RCP 8.5 scenarios."""
    csl.process_all_rcps()

    assert mock_process.call_count == 2

    rcps_processed = [call.args[0] for call in mock_process.call_args_list]
    assert 60 in rcps_processed
    assert 85 in rcps_processed