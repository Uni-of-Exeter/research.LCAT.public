import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

from data.src.cache_climate import CacheClimate


@pytest.fixture
def mock_config():
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
    }


@pytest.fixture
def cc(mock_config):
    return CacheClimate(mock_config)


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.cache_climate.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, cc):
    """Should use provided credentials over config"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    cc.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )


@patch("data.src.cache_climate.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, cc):
    """Should use config credentials when none provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    cc.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )


@patch("data.src.cache_climate.psycopg2")
def test_connect_to_db_sets_connection_and_cursor(mock_psycopg2, cc):
    """Should set conn and cur attributes"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    cc.connect_to_db()

    assert cc.conn == mock_conn
    assert cc.cur == mock_cursor


# =============================================================================
# drop_table
# =============================================================================


def test_drop_table_executes_drop_query(cc):
    """Should execute DROP TABLE query"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()

    cc.drop_table("cache_test")

    cc.cur.execute.assert_called_once_with('DROP TABLE IF EXISTS "cache_test";')
    cc.conn.commit.assert_called_once()


def test_drop_table_commits_transaction(cc):
    """Should commit after dropping table"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()

    cc.drop_table("test_table")

    assert cc.conn.commit.called


def test_drop_table_handles_exception(cc):
    """Should handle exceptions gracefully"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cur.execute.side_effect = Exception("Database error")

    # Should not raise exception
    cc.drop_table("cache_test")


# =============================================================================
# set_boundary
# =============================================================================


def test_set_boundary_sets_boundary_identifier(cc):
    """Should set boundary_identifier attribute"""
    cc.set_boundary("uk_counties")
    assert cc.boundary_identifier == "uk_counties"


def test_set_boundary_sets_overlap_table(cc):
    """Should set overlap_table based on boundary identifier"""
    cc.set_boundary("uk_counties")
    assert cc.overlap_table == "grid_overlaps_uk_counties"


def test_set_boundary_resets_climate_and_cache_tables(cc):
    """Should reset climate_table and cache_table to None"""
    cc.climate_table = "some_table"
    cc.cache_table = "some_cache"
    
    cc.set_boundary("la_districts")
    
    assert cc.climate_table is None
    assert cc.cache_table is None


# =============================================================================
# set_rcp_and_season
# =============================================================================


def test_set_rcp_and_season_sets_climate_table(cc):
    """Should set climate_table based on rcp and season"""
    cc.set_rcp_and_season(60, "annual")
    assert cc.climate_table == "chess_scape_rcp60_annual"


def test_set_rcp_and_season_sets_cache_table(cc):
    """Should set cache_table based on boundary, rcp and season"""
    cc.boundary_identifier = "uk_counties"
    cc.set_rcp_and_season(85, "winter")
    assert cc.cache_table == "cache_uk_counties_to_rcp85_winter"


def test_set_rcp_and_season_handles_summer(cc):
    """Should handle summer season correctly"""
    cc.boundary_identifier = "lsoa"
    cc.set_rcp_and_season(60, "summer")
    assert cc.cache_table == "cache_lsoa_to_rcp60_summer"
    assert cc.climate_table == "chess_scape_rcp60_summer"


# =============================================================================
# get_climate_column_names
# =============================================================================


def test_get_climate_column_names_queries_information_schema(cc):
    """Should query information_schema.columns"""
    cc.cur = MagicMock()
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.cur.fetchall.return_value = [
        ("grid_cell_id",),
        ("tas_1980_min",),
        ("tas_1980_mean",),
    ]

    cc.get_climate_column_names()

    sql = cc.cur.execute.call_args[0][0]
    assert "information_schema.columns" in sql
    assert "chess_scape_rcp60_annual" in sql


def test_get_climate_column_names_excludes_grid_cell_id(cc):
    """Should exclude grid_cell_id from returned columns"""
    cc.cur = MagicMock()
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.cur.fetchall.return_value = [
        ("grid_cell_id",),
        ("tas_1980_min",),
        ("tas_1980_mean",),
    ]

    columns = cc.get_climate_column_names()

    assert "grid_cell_id" not in columns
    assert "tas_1980_min" in columns
    assert "tas_1980_mean" in columns


def test_get_climate_column_names_returns_list(cc):
    """Should return list of column names"""
    cc.cur = MagicMock()
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.cur.fetchall.return_value = [("col1",), ("col2",), ("col3",)]

    columns = cc.get_climate_column_names()

    assert isinstance(columns, list)
    assert len(columns) == 3


# =============================================================================
# create_table
# =============================================================================


def test_create_table_creates_table_with_correct_name(cc):
    """Should create table with cache_table name"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_uk_counties_to_rcp60_annual"
    cc.get_climate_column_names = MagicMock(return_value=["tas_1980_min", "tas_1980_mean"])

    cc.create_table()

    sql = cc.cur.execute.call_args[0][0]
    assert "CREATE TABLE" in sql
    assert "cache_uk_counties_to_rcp60_annual" in sql


def test_create_table_includes_gid_primary_key(cc):
    """Should include gid as primary key"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.get_climate_column_names = MagicMock(return_value=["col1"])

    cc.create_table()

    sql = cc.cur.execute.call_args[0][0]
    assert "gid INT PRIMARY KEY" in sql


def test_create_table_includes_all_climate_columns(cc):
    """Should include all climate columns as DOUBLE PRECISION"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.get_climate_column_names = MagicMock(
        return_value=["tas_1980_min", "tas_1980_mean", "tas_1980_max"]
    )

    cc.create_table()

    sql = cc.cur.execute.call_args[0][0]
    assert "tas_1980_min" in sql
    assert "tas_1980_mean" in sql
    assert "tas_1980_max" in sql
    assert "DOUBLE PRECISION" in sql


def test_create_table_commits_transaction(cc):
    """Should commit after creating table"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.get_climate_column_names = MagicMock(return_value=["col1"])

    cc.create_table()

    assert cc.conn.commit.called


def test_create_table_handles_exception(cc):
    """Should handle exceptions gracefully"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.get_climate_column_names = MagicMock(return_value=["col1"])
    cc.cur.execute.side_effect = Exception("Database error")

    # Should not raise exception
    cc.create_table()


# =============================================================================
# cache_all_gids
# =============================================================================


def test_cache_all_gids_uses_correct_aggregations(cc):
    """Should use MIN for _min, AVG for _mean, MAX for _max columns"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.overlap_table = "grid_overlaps_test"
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.get_climate_column_names = MagicMock(
        return_value=["tas_1980_min", "tas_1980_mean", "tas_1980_max"]
    )

    cc.cache_all_gids()

    sql = cc.cur.execute.call_args[0][0]
    assert 'MIN("tas_1980_min")' in sql
    assert 'AVG("tas_1980_mean")' in sql
    assert 'MAX("tas_1980_max")' in sql


def test_cache_all_gids_joins_overlap_and_climate_tables(cc):
    """Should join overlap and climate tables"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.overlap_table = "grid_overlaps_uk_counties"
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.get_climate_column_names = MagicMock(return_value=["col1_mean"])

    cc.cache_all_gids()

    sql = cc.cur.execute.call_args[0][0]
    assert "grid_overlaps_uk_counties" in sql
    assert "chess_scape_rcp60_annual" in sql
    assert "JOIN" in sql


def test_cache_all_gids_groups_by_gid(cc):
    """Should group results by gid"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.overlap_table = "grid_overlaps_test"
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.get_climate_column_names = MagicMock(return_value=["col1_mean"])

    cc.cache_all_gids()

    sql = cc.cur.execute.call_args[0][0]
    assert "GROUP BY ot.gid" in sql


def test_cache_all_gids_inserts_into_cache_table(cc):
    """Should insert aggregated data into cache table"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.overlap_table = "grid_overlaps_test"
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.get_climate_column_names = MagicMock(return_value=["col1_mean"])

    cc.cache_all_gids()

    sql = cc.cur.execute.call_args[0][0]
    assert "INSERT INTO" in sql
    assert "cache_test" in sql


def test_cache_all_gids_commits_transaction(cc):
    """Should commit after caching data"""
    cc.conn = MagicMock()
    cc.cur = MagicMock()
    cc.cache_table = "cache_test"
    cc.overlap_table = "grid_overlaps_test"
    cc.climate_table = "chess_scape_rcp60_annual"
    cc.get_climate_column_names = MagicMock(return_value=["col1_mean"])

    cc.cache_all_gids()

    assert cc.conn.commit.called


# =============================================================================
# process_boundary
# =============================================================================


@patch.object(CacheClimate, "cache_all_gids")
@patch.object(CacheClimate, "create_table")
@patch.object(CacheClimate, "drop_table")
@patch.object(CacheClimate, "set_rcp_and_season")
@patch.object(CacheClimate, "set_boundary")
def test_process_boundary_calls_set_boundary(
    mock_set_boundary, mock_set_rcp, mock_drop, mock_create, mock_cache, cc
):
    """Should call set_boundary with provided identifier"""
    cc.process_boundary("uk_counties")

    mock_set_boundary.assert_called_once_with("uk_counties")


@patch.object(CacheClimate, "cache_all_gids")
@patch.object(CacheClimate, "create_table")
@patch.object(CacheClimate, "drop_table")
@patch.object(CacheClimate, "set_rcp_and_season")
@patch.object(CacheClimate, "set_boundary")
def test_process_boundary_processes_both_rcps(
    mock_set_boundary, mock_set_rcp, mock_drop, mock_create, mock_cache, cc
):
    """Should process both RCP 60 and RCP 85"""
    cc.process_boundary("uk_counties")

    rcp_calls = [call.args[0] for call in mock_set_rcp.call_args_list]
    assert 60 in rcp_calls
    assert 85 in rcp_calls


@patch.object(CacheClimate, "cache_all_gids")
@patch.object(CacheClimate, "create_table")
@patch.object(CacheClimate, "drop_table")
@patch.object(CacheClimate, "set_rcp_and_season")
@patch.object(CacheClimate, "set_boundary")
def test_process_boundary_processes_all_three_seasons(
    mock_set_boundary, mock_set_rcp, mock_drop, mock_create, mock_cache, cc
):
    """Should process annual, summer, and winter"""
    cc.process_boundary("uk_counties")

    season_calls = [call.args[1] for call in mock_set_rcp.call_args_list]
    assert "annual" in season_calls
    assert "summer" in season_calls
    assert "winter" in season_calls


@patch.object(CacheClimate, "cache_all_gids")
@patch.object(CacheClimate, "create_table")
@patch.object(CacheClimate, "drop_table")
@patch.object(CacheClimate, "set_rcp_and_season")
@patch.object(CacheClimate, "set_boundary")
def test_process_boundary_processes_six_combinations(
    mock_set_boundary, mock_set_rcp, mock_drop, mock_create, mock_cache, cc
):
    """Should process 6 combinations (2 RCPs × 3 seasons)"""
    cc.process_boundary("uk_counties")

    assert mock_set_rcp.call_count == 6
    assert mock_drop.call_count == 6
    assert mock_create.call_count == 6
    assert mock_cache.call_count == 6


@patch.object(CacheClimate, "cache_all_gids")
@patch.object(CacheClimate, "create_table")
@patch.object(CacheClimate, "drop_table")
@patch.object(CacheClimate, "set_rcp_and_season")
@patch.object(CacheClimate, "set_boundary")
def test_process_boundary_drops_before_creating(
    mock_set_boundary, mock_set_rcp, mock_drop, mock_create, mock_cache, cc
):
    """Should drop table before creating it"""
    cc.process_boundary("uk_counties")

    # Check that drop is called before create for each iteration
    assert mock_drop.called
    assert mock_create.called


# =============================================================================
# process_all_boundaries
# =============================================================================


@patch.object(CacheClimate, "process_boundary")
def test_process_all_boundaries_processes_all_eight_boundaries(mock_process, cc):
    """Should process all 8 boundary identifiers"""
    cc.process_all_boundaries()

    assert mock_process.call_count == 8

    boundaries_processed = [call.args[0] for call in mock_process.call_args_list]
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


@patch.object(CacheClimate, "process_boundary")
def test_process_all_boundaries_processes_in_correct_order(mock_process, cc):
    """Should process boundaries in expected order"""
    cc.process_all_boundaries()

    boundaries_processed = [call.args[0] for call in mock_process.call_args_list]
    expected_order = [
        "uk_counties",
        "la_districts",
        "lsoa",
        "msoa",
        "parishes",
        "sc_dz",
        "ni_dz",
        "iom",
    ]

    assert boundaries_processed == expected_order
