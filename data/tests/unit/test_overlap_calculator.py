import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from data.src.overlap_calculator import OverlapCalculator


@pytest.fixture
def mock_config():
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
    }


@pytest.fixture
def oc(mock_config):
    return OverlapCalculator(mock_config)


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.overlap_calculator.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, oc):
    """Should use provided credentials over config"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    oc.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )


@patch("data.src.overlap_calculator.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, oc):
    """Should use config credentials when none provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    oc.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )


@patch("data.src.overlap_calculator.psycopg2")
def test_connect_to_db_sets_connection_and_cursor(mock_psycopg2, oc):
    """Should set conn and cur attributes"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    oc.connect_to_db()

    assert oc.conn == mock_conn
    assert oc.cur == mock_cursor


# =============================================================================
# set_boundary_table
# =============================================================================


def test_set_boundary_table_sets_boundary_identifier(oc):
    """Should set boundary_identifier attribute"""
    oc.set_boundary_table("uk_counties")
    assert oc.boundary_identifier == "uk_counties"


def test_set_boundary_table_sets_boundary_table_name(oc):
    """Should set boundary_table_name based on identifier"""
    oc.set_boundary_table("lsoa")
    assert oc.boundary_table_name == "boundary_lsoa"


def test_set_boundary_table_sets_new_table_name(oc):
    """Should set new_table_name (overlap table) based on identifier"""
    oc.set_boundary_table("msoa")
    assert oc.new_table_name == "grid_overlaps_msoa"


def test_set_boundary_table_resets_no_overlap_dicts(oc):
    """Should reset no_overlap tracking dictionaries"""
    oc.no_overlap_regions = {"old": "data"}
    oc.no_overlap_closest_cells = {"old": "data"}
    
    oc.set_boundary_table("parishes")
    
    assert oc.no_overlap_regions == {}
    assert oc.no_overlap_closest_cells == {}


# =============================================================================
# drop_table
# =============================================================================


def test_drop_table_executes_drop_query(oc):
    """Should execute DROP TABLE query"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()

    oc.drop_table("test_table")

    oc.cur.execute.assert_called_once_with('DROP TABLE IF EXISTS "test_table";')
    oc.conn.commit.assert_called_once()


def test_drop_table_commits_transaction(oc):
    """Should commit after dropping table"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()

    oc.drop_table("overlap_test")

    assert oc.conn.commit.called


def test_drop_table_handles_exception(oc):
    """Should handle exceptions gracefully"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.cur.execute.side_effect = Exception("Database error")

    # Should not raise exception
    oc.drop_table("test_table")


# =============================================================================
# create_overlap_table
# =============================================================================


def test_create_overlap_table_creates_with_correct_name(oc):
    """Should create overlap table with correct naming"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.new_table_name = "grid_overlaps_uk_counties"
    oc.boundary_table_name = "boundary_uk_counties"

    oc.create_overlap_table()

    sql = oc.cur.execute.call_args[0][0]
    assert "CREATE TABLE" in sql
    assert "grid_overlaps_uk_counties" in sql


def test_create_overlap_table_includes_required_columns(oc):
    """Should include gid, grid_cell_id, is_overlap, bias_corrected columns"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.new_table_name = "grid_overlaps_test"
    oc.boundary_table_name = "boundary_test"

    oc.create_overlap_table()

    sql = oc.cur.execute.call_args[0][0]
    assert "gid" in sql.lower()
    assert "grid_cell_id" in sql
    assert "is_overlap" in sql
    assert "bias_corrected" in sql


def test_create_overlap_table_commits_transaction(oc):
    """Should commit after creating table"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.new_table_name = "grid_overlaps_test"
    oc.boundary_table_name = "boundary_test"

    oc.create_overlap_table()

    assert oc.conn.commit.called


def test_create_overlap_table_raises_without_boundary_set(oc):
    """Should raise ValueError if boundary_table_name not set"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = None

    with pytest.raises(ValueError, match="boundary identifier"):
        oc.create_overlap_table()


# =============================================================================
# ensure_spatial_index
# =============================================================================


def test_ensure_spatial_index_creates_gist_index(oc):
    """Should create GIST spatial index on geometry column"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()

    oc.ensure_spatial_index("chess_scape_grid", "geometry")

    sql = oc.cur.execute.call_args[0][0]
    assert "CREATE INDEX" in sql.upper()
    assert "GIST" in sql.upper()
    assert "geometry" in sql


def test_ensure_spatial_index_commits_transaction(oc):
    """Should commit after creating index"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()

    oc.ensure_spatial_index("test_table", "geom")

    assert oc.conn.commit.called


# =============================================================================
# insert_overlaps_optimised
# =============================================================================


def test_insert_overlaps_optimised_uses_st_intersects(oc):
    """Should use ST_Intersects to find overlapping geometries"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_uk_counties"
    oc.new_table_name = "grid_overlaps_uk_counties"
    oc.grid_table_name = "chess_scape_grid"

    oc.insert_overlaps_optimised()

    sql = oc.cur.execute.call_args[0][0]
    assert "ST_Intersects" in sql


def test_insert_overlaps_optimised_inserts_into_overlap_table(oc):
    """Should insert results into overlap table"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_lsoa"
    oc.new_table_name = "grid_overlaps_lsoa"
    oc.grid_table_name = "chess_scape_grid"

    oc.insert_overlaps_optimised()

    sql = oc.cur.execute.call_args[0][0]
    assert "INSERT INTO" in sql
    assert "grid_overlaps_lsoa" in sql


def test_insert_overlaps_optimised_commits_transaction(oc):
    """Should commit after calculating overlaps"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_test"
    oc.new_table_name = "grid_overlaps_test"
    oc.grid_table_name = "chess_scape_grid"

    oc.insert_overlaps_optimised()

    assert oc.conn.commit.called


def test_insert_overlaps_optimised_sets_is_overlap_true(oc):
    """Should set is_overlap to TRUE for overlapping cells"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_test"
    oc.new_table_name = "grid_overlaps_test"
    oc.grid_table_name = "chess_scape_grid"

    oc.insert_overlaps_optimised()

    sql = oc.cur.execute.call_args[0][0]
    assert "TRUE" in sql


# =============================================================================
# find_no_overlap_regions
# =============================================================================


def test_find_no_overlap_regions_finds_gids_without_overlaps(oc):
    """Should find gids not present in overlap table"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_uk_counties"
    oc.new_table_name = "grid_overlaps_uk_counties"
    oc.cur.fetchall.return_value = [(1,), (5,), (10,)]

    result = oc.find_no_overlap_regions()

    assert result == [1, 5, 10]


def test_find_no_overlap_regions_returns_empty_list_when_all_overlap(oc):
    """Should return empty list when all regions have overlaps"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_test"
    oc.new_table_name = "grid_overlaps_test"
    oc.cur.fetchall.return_value = []

    result = oc.find_no_overlap_regions()

    assert result == []


# =============================================================================
# process_no_overlap_regions
# =============================================================================


@patch.object(OverlapCalculator, "insert_closest_cell")
@patch.object(OverlapCalculator, "find_closest_cell")
@patch.object(OverlapCalculator, "find_no_overlap_regions")
def test_process_no_overlap_regions_finds_and_processes_regions(mock_find_regions, mock_find_cell, mock_insert, oc):
    """Should find no-overlap regions and process each one"""
    mock_find_regions.return_value = [1, 2, 3]
    mock_find_cell.return_value = (100, 1.5, True)

    oc.process_no_overlap_regions()

    assert mock_find_cell.call_count == 3
    assert mock_insert.call_count == 3


@patch.object(OverlapCalculator, "find_no_overlap_regions")
def test_process_no_overlap_regions_handles_no_regions(mock_find_regions, oc):
    """Should handle case when no regions lack overlaps"""
    mock_find_regions.return_value = []

    oc.process_no_overlap_regions()

    # Should not raise exception


# =============================================================================
# process_all_boundary_overlaps
# =============================================================================


@patch.object(OverlapCalculator, "process_no_overlap_regions")
@patch.object(OverlapCalculator, "insert_overlaps_optimised")
@patch.object(OverlapCalculator, "ensure_spatial_index")
@patch.object(OverlapCalculator, "create_overlap_table")
@patch.object(OverlapCalculator, "drop_table")
@patch.object(OverlapCalculator, "set_boundary_table")
def test_process_all_boundary_overlaps_processes_all_eight_boundaries(
    mock_set, mock_drop, mock_create, mock_index, mock_insert, mock_no_overlap, oc
):
    """Should process all 8 boundary identifiers"""
    oc.process_all_boundary_overlaps(process_no_overlaps=False)

    assert mock_set.call_count == 8

    boundaries_processed = [call.args[0] for call in mock_set.call_args_list]
    expected_boundaries = [
        "uk_counties",
        "la_districts",
        "lsoa",
        "msoa",
        "parishes",
        "sc_dz",
        "ni_dz",
        "iom",
    ]

    for boundary in expected_boundaries:
        assert boundary in boundaries_processed


@patch.object(OverlapCalculator, "process_no_overlap_regions")
@patch.object(OverlapCalculator, "insert_overlaps_optimised")
@patch.object(OverlapCalculator, "ensure_spatial_index")
@patch.object(OverlapCalculator, "create_overlap_table")
@patch.object(OverlapCalculator, "drop_table")
@patch.object(OverlapCalculator, "set_boundary_table")
def test_process_all_boundary_overlaps_processes_no_overlaps_when_requested(
    mock_set, mock_drop, mock_create, mock_index, mock_insert, mock_no_overlap, oc
):
    """Should process no-overlap regions when process_no_overlaps=True"""
    oc.process_all_boundary_overlaps(process_no_overlaps=True)

    assert mock_no_overlap.call_count == 8


@patch.object(OverlapCalculator, "process_no_overlap_regions")
@patch.object(OverlapCalculator, "insert_overlaps_optimised")
@patch.object(OverlapCalculator, "ensure_spatial_index")
@patch.object(OverlapCalculator, "create_overlap_table")
@patch.object(OverlapCalculator, "drop_table")
@patch.object(OverlapCalculator, "set_boundary_table")
def test_process_all_boundary_overlaps_skips_no_overlaps_by_default(
    mock_set, mock_drop, mock_create, mock_index, mock_insert, mock_no_overlap, oc
):
    """Should not process no-overlap regions by default"""
    oc.process_all_boundary_overlaps(process_no_overlaps=False)

    assert mock_no_overlap.call_count == 0


@patch.object(OverlapCalculator, "process_no_overlap_regions")
@patch.object(OverlapCalculator, "insert_overlaps_optimised")
@patch.object(OverlapCalculator, "ensure_spatial_index")
@patch.object(OverlapCalculator, "create_overlap_table")
@patch.object(OverlapCalculator, "drop_table")
@patch.object(OverlapCalculator, "set_boundary_table")
def test_process_all_boundary_overlaps_drops_before_creating(
    mock_set, mock_drop, mock_create, mock_index, mock_insert, mock_no_overlap, oc
):
    """Should drop table before creating new one"""
    oc.process_all_boundary_overlaps()

    assert mock_drop.called
    assert mock_create.called


@patch.object(OverlapCalculator, "process_no_overlap_regions")
@patch.object(OverlapCalculator, "insert_overlaps_optimised")
@patch.object(OverlapCalculator, "ensure_spatial_index")
@patch.object(OverlapCalculator, "create_overlap_table")
@patch.object(OverlapCalculator, "drop_table")
@patch.object(OverlapCalculator, "set_boundary_table")
def test_process_all_boundary_overlaps_creates_spatial_indexes(
    mock_set, mock_drop, mock_create, mock_index, mock_insert, mock_no_overlap, oc
):
    """Should create spatial indexes on geometry columns"""
    oc.process_all_boundary_overlaps()

    # Should create indexes for both grid and boundary tables (2 per boundary * 8 boundaries)
    assert mock_index.call_count == 16


# =============================================================================
# Query helper methods
# =============================================================================


def test_get_region_geometry_queries_by_gid(oc):
    """Should query region geometry by gid"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_uk_counties"
    oc.cur.fetchone.return_value = (b"geometry_data",)

    result = oc.get_region_geometry(42)

    assert result == b"geometry_data"
    call_args = oc.cur.execute.call_args[0]
    assert call_args[1] == (42,)


def test_get_region_name_uses_correct_column_for_boundary(oc):
    """Should use correct name column for each boundary type"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_identifier = "uk_counties"
    oc.boundary_table_name = "boundary_uk_counties"
    oc.cur.fetchone.return_value = ("Test County",)

    result = oc.get_region_name(1)

    sql = oc.cur.execute.call_args[0][0]
    assert "CTYUA23NM" in sql
    assert result == "Test County"


def test_get_grid_cell_geometry_returns_geometry(oc):
    """Should return grid cell geometry by grid_cell_id"""
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.grid_table_name = "chess_scape_grid"
    oc.cur.fetchone.return_value = (b"cell_geometry",)

    result = oc.get_grid_cell_geometry(123)

    assert result == b"cell_geometry"
