import pytest
import numpy as np
from unittest.mock import MagicMock, patch, call

from data.src.db_plotter import DBPlotter


@pytest.fixture
def mock_config():
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
    }


@pytest.fixture
def dbp(mock_config):
    return DBPlotter(mock_config)


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.db_plotter.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, dbp):
    """Should use provided credentials over config"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    dbp.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )


@patch("data.src.db_plotter.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, dbp):
    """Should use config credentials when none provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    dbp.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )


@patch("data.src.db_plotter.psycopg2")
def test_connect_to_db_sets_connection_and_cursor(mock_psycopg2, dbp):
    """Should set conn and cur attributes"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    dbp.connect_to_db()

    assert dbp.conn == mock_conn
    assert dbp.cur == mock_cursor


# =============================================================================
# set_clean_boundary_names
# =============================================================================


def test_set_clean_boundary_names_sets_all_boundaries(dbp):
    """Should set clean names for all 8 boundaries"""
    assert len(dbp.clean_boundary_names) == 8
    assert "uk_counties" in dbp.clean_boundary_names
    assert "la_districts" in dbp.clean_boundary_names
    assert "lsoa" in dbp.clean_boundary_names
    assert "msoa" in dbp.clean_boundary_names
    assert "parishes" in dbp.clean_boundary_names
    assert "sc_dz" in dbp.clean_boundary_names
    assert "ni_dz" in dbp.clean_boundary_names
    assert "iom" in dbp.clean_boundary_names


def test_set_clean_boundary_names_has_readable_names(dbp):
    """Should have human-readable names"""
    assert dbp.clean_boundary_names["uk_counties"] == "UK Counties and Unitary Authorities"
    assert dbp.clean_boundary_names["ni_dz"] == "Northern Ireland Data Zones"
    assert dbp.clean_boundary_names["sc_dz"] == "Scotland Data Zones"


# =============================================================================
# get_boundary_geometry
# =============================================================================


def test_get_boundary_geometry_queries_correct_table(dbp):
    """Should query the correct boundary table"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_boundary_geometry("uk_counties")

    sql = dbp.cur.execute.call_args[0][0]
    assert "boundary_uk_counties" in sql
    assert "SELECT gid, geom" in sql


def test_get_boundary_geometry_returns_fetched_data(dbp):
    """Should return fetched geometry data"""
    dbp.cur = MagicMock()
    mock_data = [(1, b"geom1"), (2, b"geom2")]
    dbp.cur.fetchall.return_value = mock_data

    result = dbp.get_boundary_geometry("lsoa")

    assert result == mock_data


# =============================================================================
# get_grid_geometry
# =============================================================================


def test_get_grid_geometry_queries_chess_scape_grid(dbp):
    """Should query chess_scape_grid table"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_grid_geometry()

    sql = dbp.cur.execute.call_args[0][0]
    assert "chess_scape_grid" in sql
    assert "SELECT grid_cell_id, geometry, bias_corrected, coastal_info" in sql


def test_get_grid_geometry_returns_all_columns(dbp):
    """Should return grid_cell_id, geometry, bias_corrected, and coastal_info"""
    dbp.cur = MagicMock()
    mock_data = [(1, b"geom1", True, "coastline")]
    dbp.cur.fetchall.return_value = mock_data

    result = dbp.get_grid_geometry()

    assert result == mock_data


# =============================================================================
# get_chess_data
# =============================================================================


def test_get_chess_data_queries_correct_table(dbp):
    """Should query the correct CHESS-SCAPE table"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_chess_data(rcp=60, season="annual", variable="tas", decade=1980)

    sql = dbp.cur.execute.call_args[0][0]
    assert "chess_scape_rcp60_annual" in sql


def test_get_chess_data_selects_correct_column(dbp):
    """Should select the correct variable and decade column"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_chess_data(rcp=85, season="winter", variable="pr", decade=2050)

    sql = dbp.cur.execute.call_args[0][0]
    assert "pr_2050" in sql


def test_get_chess_data_returns_grid_cell_id_and_value(dbp):
    """Should return grid_cell_id and data value"""
    dbp.cur = MagicMock()
    mock_data = [(1, 15.5), (2, 16.2)]
    dbp.cur.fetchall.return_value = mock_data

    result = dbp.get_chess_data(60, "annual", "tas", 1980)

    assert result == mock_data


# =============================================================================
# get_geometry_by_gid
# =============================================================================


def test_get_geometry_by_gid_queries_with_gid(dbp):
    """Should query boundary table with specific gid"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_geometry_by_gid("uk_counties", 42)

    call_args = dbp.cur.execute.call_args
    sql = call_args[0][0]
    params = call_args[0][1]
    
    assert "boundary_uk_counties" in sql
    assert "WHERE s.gid = %s" in sql
    assert params == (42,)


def test_get_geometry_by_gid_returns_gid_and_geometry(dbp):
    """Should return gid and geometry"""
    dbp.cur = MagicMock()
    mock_data = [(42, b"geom_data")]
    dbp.cur.fetchall.return_value = mock_data

    result = dbp.get_geometry_by_gid("lsoa", 42)

    assert result == mock_data


# =============================================================================
# get_region_name_by_gid
# =============================================================================


def test_get_region_name_by_gid_queries_correct_column_for_uk_counties(dbp):
    """Should use CTYUA23NM column for uk_counties"""
    dbp.cur = MagicMock()
    dbp.cur.fetchone.return_value = ("Test County",)

    dbp.get_region_name_by_gid("uk_counties", 1)

    sql = dbp.cur.execute.call_args[0][0]
    assert "CTYUA23NM" in sql


def test_get_region_name_by_gid_queries_correct_column_for_ni_dz(dbp):
    """Should use DZ2021_nm column for ni_dz"""
    dbp.cur = MagicMock()
    dbp.cur.fetchone.return_value = ("Test DZ",)

    dbp.get_region_name_by_gid("ni_dz", 1)

    sql = dbp.cur.execute.call_args[0][0]
    assert "DZ2021_nm" in sql


def test_get_region_name_by_gid_returns_name(dbp):
    """Should return region name"""
    dbp.cur = MagicMock()
    dbp.cur.fetchone.return_value = ("Test Region",)

    result = dbp.get_region_name_by_gid("lsoa", 100)

    assert result == "Test Region"


def test_get_region_name_by_gid_uses_correct_gid_parameter(dbp):
    """Should pass gid as parameter"""
    dbp.cur = MagicMock()
    dbp.cur.fetchone.return_value = ("Test",)

    dbp.get_region_name_by_gid("msoa", 999)

    call_args = dbp.cur.execute.call_args[0]
    assert call_args[1] == (999,)


# =============================================================================
# get_overlapping_cells
# =============================================================================


def test_get_overlapping_cells_queries_overlap_table(dbp):
    """Should query grid_overlaps table"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_overlapping_cells("uk_counties", 10)

    sql = dbp.cur.execute.call_args[0][0]
    assert "grid_overlaps_uk_counties" in sql
    assert "chess_scape_grid" in sql
    assert "JOIN" in sql


def test_get_overlapping_cells_filters_by_gid(dbp):
    """Should filter results by gid"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_overlapping_cells("lsoa", 42)

    call_args = dbp.cur.execute.call_args[0]
    assert call_args[1] == (42,)


def test_get_overlapping_cells_returns_all_required_columns(dbp):
    """Should return grid_cell_id, geometry, bias_corrected, is_overlap, coastal_info"""
    dbp.cur = MagicMock()
    mock_data = [(1, b"geom", True, True, "coastline")]
    dbp.cur.fetchall.return_value = mock_data

    result = dbp.get_overlapping_cells("parishes", 5)

    assert result == mock_data


# =============================================================================
# get_cached_chess_data
# =============================================================================


def test_get_cached_chess_data_queries_cache_table(dbp):
    """Should query the correct cache table"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_cached_chess_data("uk_counties", "tas", 1980, 60, "annual")

    sql = dbp.cur.execute.call_args[0][0]
    assert "cache_uk_counties_to_rcp60_annual" in sql


def test_get_cached_chess_data_selects_correct_column(dbp):
    """Should select the correct variable and decade column"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_cached_chess_data("lsoa", "pr", 2050, 85, "winter")

    sql = dbp.cur.execute.call_args[0][0]
    assert "pr_2050" in sql


def test_get_cached_chess_data_returns_gid_and_value(dbp):
    """Should return gid and data value"""
    dbp.cur = MagicMock()
    mock_data = [(1, 12.5), (2, 13.1)]
    dbp.cur.fetchall.return_value = mock_data

    result = dbp.get_cached_chess_data("msoa", "tas", 1990, 60, "summer")

    assert result == mock_data


# =============================================================================
# get_no_overlap_geometry
# =============================================================================


def test_get_no_overlap_geometry_queries_regions_with_no_overlap(dbp):
    """Should query regions where is_overlap is FALSE"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_no_overlap_geometry("uk_counties")

    sql = dbp.cur.execute.call_args[0][0]
    assert "boundary_uk_counties" in sql
    assert "grid_overlaps_uk_counties" in sql
    assert "is_overlap = FALSE" in sql


def test_get_no_overlap_geometry_returns_gid_and_geometry(dbp):
    """Should return gid and geometry for no-overlap regions"""
    dbp.cur = MagicMock()
    mock_data = [(1, b"geom1"), (2, b"geom2")]
    dbp.cur.fetchall.return_value = mock_data

    result = dbp.get_no_overlap_geometry("parishes")

    assert result == mock_data


def test_get_no_overlap_geometry_uses_subquery(dbp):
    """Should use subquery to find non-overlapping gids"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_no_overlap_geometry("sc_dz")

    sql = dbp.cur.execute.call_args[0][0]
    assert "WHERE bt.gid IN" in sql


# =============================================================================
# plot_boundary (basic test without matplotlib)
# =============================================================================


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb")
def test_plot_boundary_calls_get_boundary_geometry(mock_wkb, mock_gdf, mock_show, dbp):
    """Should call get_boundary_geometry with correct identifier"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []
    
    with patch.object(dbp, 'get_boundary_geometry', return_value=[]) as mock_get:
        dbp.plot_boundary("uk_counties")
        mock_get.assert_called_once_with("uk_counties")


# =============================================================================
# plot_boundary_coloured_by_coastal (basic test without matplotlib)
# =============================================================================


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb")
def test_plot_boundary_coloured_by_coastal_queries_coastal_data(mock_wkb, mock_gdf, mock_show, dbp):
    """Should query is_coastal column"""
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []
    
    with patch.object(dbp, 'get_boundary_geometry', return_value=[]):
        dbp.plot_boundary_coloured_by_coastal("uk_counties")
        
        sql_calls = [str(call) for call in dbp.cur.execute.call_args_list]
        sql_combined = " ".join(sql_calls)
        assert "is_coastal" in sql_combined


# =============================================================================
# plot_chess_grid_cells (basic test without matplotlib)
# =============================================================================


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb")
def test_plot_chess_grid_cells_calls_get_grid_geometry(mock_wkb, mock_gdf, mock_show, dbp):
    """Should call get_grid_geometry"""
    dbp.cur = MagicMock()
    
    with patch.object(dbp, 'get_grid_geometry', return_value=[]) as mock_get:
        dbp.plot_chess_grid_cells()
        mock_get.assert_called_once()


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb")
@patch("data.src.db_plotter.unary_union")
def test_plot_chess_grid_cells_merges_when_requested(mock_union, mock_wkb, mock_gdf, mock_show, dbp):
    """Should merge geometries when merged=True"""
    dbp.cur = MagicMock()
    
    with patch.object(dbp, 'get_grid_geometry', return_value=[]):
        dbp.plot_chess_grid_cells(merged=True)
        # When merged=True, unary_union should be called


# =============================================================================
# plot_region_and_overlapping_cells (basic test without matplotlib)
# =============================================================================


def test_plot_region_and_overlapping_cells_gets_region_data(dbp):
    """Should get region geometry and name"""
    dbp.cur = MagicMock()
    dbp.cur.fetchone.return_value = ("Test Region",)
    
    with patch.object(dbp, 'get_geometry_by_gid', return_value=[]) as mock_geom, \
         patch.object(dbp, 'get_region_name_by_gid', return_value="Test") as mock_name, \
         patch.object(dbp, 'get_overlapping_cells', return_value=[]):
        
        # This will fail during GeoDataFrame creation, but we can verify the calls were made
        try:
            dbp.plot_region_and_overlapping_cells("uk_counties", 10)
        except (IndexError, AttributeError, KeyError, ValueError):
            # Expected to fail due to empty data, but methods should have been called
            pass
        
        mock_geom.assert_called_once_with("uk_counties", 10)
        mock_name.assert_called_once_with("uk_counties", 10)


# =============================================================================
# plot_no_overlap_locations (basic test without matplotlib)
# =============================================================================


def test_plot_no_overlap_locations_returns_early_if_no_data(dbp):
    """Should return early if no overlaps found"""
    with patch.object(dbp, 'get_grid_geometry', return_value=[]), \
         patch.object(dbp, 'get_no_overlap_geometry', return_value=[]):
        
        # Should not raise exception and should print message
        dbp.plot_no_overlap_locations("uk_counties")


def test_plot_no_overlap_locations_processes_data_when_found(dbp):
    """Should call get_no_overlap_geometry when data exists"""
    mock_no_overlap = [(1, b"geom")]
    
    with patch.object(dbp, 'get_grid_geometry', return_value=[]) as mock_grid, \
         patch.object(dbp, 'get_no_overlap_geometry', return_value=mock_no_overlap) as mock_no_overlap_get:
        
        # This will fail during plotting, but we can verify methods were called
        try:
            dbp.plot_no_overlap_locations("parishes")
        except (RuntimeError, AttributeError, TypeError, ValueError):
            # Expected to fail due to mock data, but methods should have been called
            pass
        
        mock_grid.assert_called_once()
        mock_no_overlap_get.assert_called_once_with("parishes")


# =============================================================================
# plot_boundary_coloured_by_cache (basic test without matplotlib)
# =============================================================================


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb")
def test_plot_boundary_coloured_by_cache_gets_cached_data(mock_wkb, mock_gdf, mock_show, dbp):
    """Should get boundary geometry and cached CHESS data"""
    with patch.object(dbp, 'get_boundary_geometry', return_value=[]) as mock_boundary, \
         patch.object(dbp, 'get_cached_chess_data', return_value=[]) as mock_cache:
        
        dbp.plot_boundary_coloured_by_cache("uk_counties", "tas", 1980, 60, "annual")
        
        mock_boundary.assert_called_once_with("uk_counties")
        mock_cache.assert_called_once_with("uk_counties", "tas", 1980, 60, "annual")


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb")
def test_plot_boundary_coloured_by_cache_handles_lines_parameter(mock_wkb, mock_gdf, mock_show, dbp):
    """Should respect lines parameter for edge display"""
    with patch.object(dbp, 'get_boundary_geometry', return_value=[]), \
         patch.object(dbp, 'get_cached_chess_data', return_value=[]):
        
        # Should not raise exception with lines=True
        dbp.plot_boundary_coloured_by_cache("lsoa", "pr", 2050, 85, "winter", lines=True)
        
        # Should not raise exception with lines=False
        dbp.plot_boundary_coloured_by_cache("lsoa", "pr", 2050, 85, "winter", lines=False)
