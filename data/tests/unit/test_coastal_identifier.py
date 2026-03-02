import pytest
from unittest.mock import MagicMock, patch, call

import psycopg2

from data.src.coastal_identifier import CoastalIdentifier


@pytest.fixture
def mock_config():
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
    }


@pytest.fixture
def ci(mock_config):
    return CoastalIdentifier(mock_config)


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.coastal_identifier.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, ci):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    ci.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )
    mock_conn.cursor.assert_called_once()
    assert ci.conn is mock_conn
    assert ci.cur is mock_cursor


@patch("data.src.coastal_identifier.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, ci):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    ci.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )
    mock_conn.cursor.assert_called_once()
    assert ci.conn is mock_conn
    assert ci.cur is mock_cursor


# =============================================================================
# add_column
# =============================================================================


def test_add_column_executes_expected_query_and_commits(ci):
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.add_column("uk_counties", "is_coastal")

    ci.cur.execute.assert_called_once()
    sql = ci.cur.execute.call_args[0][0]

    assert 'ALTER TABLE "boundary_uk_counties"' in sql
    assert 'ADD COLUMN IF NOT EXISTS "is_coastal" BOOLEAN' in sql

    ci.conn.commit.assert_called_once()


def test_add_column_supports_custom_column_name(ci):
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.add_column("parishes", "custom_col")

    sql = ci.cur.execute.call_args[0][0]
    assert 'ALTER TABLE "boundary_parishes"' in sql
    assert 'ADD COLUMN IF NOT EXISTS "custom_col" BOOLEAN' in sql


# =============================================================================
# process_boundary
# =============================================================================


@patch.object(CoastalIdentifier, "add_column")
def test_process_boundary_calls_add_column(mock_add_column, ci):
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("uk_counties")

    mock_add_column.assert_called_once_with("uk_counties", "is_coastal")
    

def test_process_boundary_normal_boundary_updates_with_expected_sql_and_params(ci):
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("uk_counties")

    # Two commits expected: one from add_column, one from update
    assert ci.conn.commit.call_count == 2

    # Last execute should be the UPDATE
    update_sql, update_params = ci.cur.execute.call_args_list[-1][0]

    assert "UPDATE boundary_uk_counties b" in update_sql
    assert "SET is_coastal = EXISTS" in update_sql
    assert "FROM grid_overlaps_uk_counties o" in update_sql
    assert "JOIN chess_scape_grid g ON o.grid_cell_id = g.grid_cell_id" in update_sql
    assert "WHERE o.gid = b.gid AND g.coastal_info IN %s" in update_sql

    # Params should be a 1-tuple containing the coastal_values tuple
    assert update_params == (tuple(ci.coastal_values),)


def test_process_boundary_ni_marks_all_regions_coastal(ci):
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("ni_dz")

    assert ci.conn.commit.call_count == 2

    update_sql = ci.cur.execute.call_args_list[-1][0][0]
    assert "UPDATE boundary_ni_dz" in update_sql
    assert "SET is_coastal = TRUE" in update_sql


@patch.object(CoastalIdentifier, "add_column")
def test_process_boundary_rolls_back_on_update_error(mock_add_column, ci):
    """
    add_column happens outside the try/except in process_boundary, so to test rollback we:
    - stub out add_column to succeed
    - raise on the UPDATE execute
    """
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    # First execute would have been add_column, but we patched it out.
    ci.cur.execute.side_effect = psycopg2.Error("boom")

    ci.process_boundary("uk_counties")

    ci.conn.rollback.assert_called_once()
    # commit should not be called for the failed update; add_column is patched out too
    ci.conn.commit.assert_not_called()


def test_process_boundary_add_column_then_update_execute_order(ci):
    """
    Verifies the sequence is:
    1) ALTER TABLE ... (from add_column)
    2) UPDATE ... (from process_boundary)
    """
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("lsoa")

    assert ci.cur.execute.call_count == 2

    alter_sql = ci.cur.execute.call_args_list[0][0][0]
    update_sql = ci.cur.execute.call_args_list[1][0][0]

    assert alter_sql.startswith('ALTER TABLE "boundary_lsoa"')
    assert "UPDATE boundary_lsoa b" in update_sql


# =============================================================================
# process_all_boundaries
# =============================================================================


@patch.object(CoastalIdentifier, "process_boundary")
def test_process_all_boundaries_processes_expected_boundaries_in_order(mock_process_boundary, ci):
    ci.process_all_boundaries()

    expected = [
        "uk_counties",
        "la_districts",
        "lsoa",
        "msoa",
        "parishes",
        "sc_dz",
        "ni_dz",
        "iom"
    ]

    assert [c.args[0] for c in mock_process_boundary.call_args_list] == expected

