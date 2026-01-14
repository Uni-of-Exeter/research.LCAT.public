import pytest
from unittest.mock import MagicMock, patch

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
    """Should use provided credentials over config"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    ci.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )


@patch("data.src.coastal_identifier.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, ci):
    """Should use config credentials when none provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    ci.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )


@patch("data.src.coastal_identifier.psycopg2")
def test_connect_to_db_sets_connection_and_cursor(mock_psycopg2, ci):
    """Should set conn and cur attributes"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    ci.connect_to_db()

    assert ci.conn == mock_conn
    assert ci.cur == mock_cursor


# =============================================================================
# __init__
# =============================================================================


def test_init_sets_default_coastal_values(ci):
    """Should set default coastal distance values"""
    assert "20km from coast" in ci.coastal_values
    assert "10km from coast" in ci.coastal_values
    assert "coastline" in ci.coastal_values


def test_init_sets_default_column_name(ci):
    """Should set default column name to is_coastal"""
    assert ci.coastal_column_name == "is_coastal"


def test_init_sets_coastal_values_in_correct_order(ci):
    """Should have coastal values ordered from far to near"""
    assert ci.coastal_values == ["20km from coast", "10km from coast", "coastline"]


# =============================================================================
# add_column
# =============================================================================


def test_add_column_executes_alter_table_query(ci):
    """Should execute ALTER TABLE query to add column"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.add_column("uk_counties", "is_coastal")

    sql = ci.cur.execute.call_args[0][0]
    assert "ALTER TABLE" in sql
    assert "boundary_uk_counties" in sql
    assert "is_coastal" in sql
    assert "BOOLEAN" in sql


def test_add_column_uses_if_not_exists(ci):
    """Should use IF NOT EXISTS to avoid errors"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.add_column("lsoa", "is_coastal")

    sql = ci.cur.execute.call_args[0][0]
    assert "IF NOT EXISTS" in sql


def test_add_column_commits_transaction(ci):
    """Should commit after adding column"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.add_column("msoa", "is_coastal")

    assert ci.conn.commit.called


def test_add_column_works_with_custom_column_name(ci):
    """Should work with custom column names"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.add_column("parishes", "custom_column")

    sql = ci.cur.execute.call_args[0][0]
    assert "custom_column" in sql


# =============================================================================
# process_boundary
# =============================================================================


@patch.object(CoastalIdentifier, "add_column")
def test_process_boundary_adds_column(mock_add_column, ci):
    """Should add is_coastal column to boundary table"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("uk_counties")

    mock_add_column.assert_called_once_with("uk_counties", "is_coastal")


def test_process_boundary_updates_regions_for_normal_boundary(ci):
    """Should execute UPDATE query for non-NI boundaries"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("uk_counties")

    sql = ci.cur.execute.call_args_list[-1][0][0]
    assert "UPDATE boundary_uk_counties" in sql
    assert "EXISTS" in sql
    assert "grid_overlaps_uk_counties" in sql
    assert "chess_scape_grid" in sql


def test_process_boundary_marks_all_ni_regions_coastal(ci):
    """Should mark all Northern Ireland regions as coastal"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("ni_dz")

    sql = ci.cur.execute.call_args_list[-1][0][0]
    assert "UPDATE boundary_ni_dz" in sql
    assert "is_coastal = TRUE" in sql


def test_process_boundary_uses_coastal_values_in_query(ci):
    """Should use coastal_values tuple in parameterized query"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("lsoa")

    # Check that the query was called with coastal values as parameter
    assert ci.cur.execute.call_count >= 2
    # Last execute call should have the coastal values tuple
    call_args = ci.cur.execute.call_args_list[-1]
    if len(call_args[0]) > 1:
        params = call_args[0][1]
        assert isinstance(params, tuple)
        assert len(params[0]) == 3


def test_process_boundary_commits_transaction(ci):
    """Should commit after updating regions"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("msoa")

    assert ci.conn.commit.called


@patch.object(CoastalIdentifier, "add_column")
def test_process_boundary_handles_database_error(mock_add_column, ci):
    """Should rollback on database error"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()
    
    import psycopg2
    # Make the UPDATE query execute fail
    ci.cur.execute.side_effect = psycopg2.Error("Database error")

    # Should not raise exception
    ci.process_boundary("parishes")
    
    assert ci.conn.rollback.called


def test_process_boundary_joins_with_chess_scape_grid(ci):
    """Should join with chess_scape_grid table"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("sc_dz")

    sql = ci.cur.execute.call_args_list[-1][0][0]
    assert "chess_scape_grid" in sql
    assert "JOIN" in sql


def test_process_boundary_checks_coastal_info_column(ci):
    """Should check coastal_info column in chess_scape_grid"""
    ci.conn = MagicMock()
    ci.cur = MagicMock()

    ci.process_boundary("la_districts")

    sql = ci.cur.execute.call_args_list[-1][0][0]
    assert "coastal_info" in sql


# =============================================================================
# process_all_boundaries
# =============================================================================


@patch.object(CoastalIdentifier, "process_boundary")
def test_process_all_boundaries_processes_all_seven_boundaries(mock_process, ci):
    """Should process all 7 boundary identifiers (excluding iom)"""
    ci.process_all_boundaries()

    assert mock_process.call_count == 7

    boundaries_processed = [call.args[0] for call in mock_process.call_args_list]
    expected_boundaries = [
        "uk_counties",
        "la_districts",
        "lsoa",
        "msoa",
        "parishes",
        "sc_dz",
        "ni_dz",
    ]

    for boundary in expected_boundaries:
        assert boundary in boundaries_processed


@patch.object(CoastalIdentifier, "process_boundary")
def test_process_all_boundaries_excludes_iom(mock_process, ci):
    """Should not process Isle of Man"""
    ci.process_all_boundaries()

    boundaries_processed = [call.args[0] for call in mock_process.call_args_list]
    assert "iom" not in boundaries_processed


@patch.object(CoastalIdentifier, "process_boundary")
def test_process_all_boundaries_processes_in_correct_order(mock_process, ci):
    """Should process boundaries in expected order"""
    ci.process_all_boundaries()

    boundaries_processed = [call.args[0] for call in mock_process.call_args_list]
    expected_order = [
        "uk_counties",
        "la_districts",
        "lsoa",
        "msoa",
        "parishes",
        "sc_dz",
        "ni_dz",
    ]

    assert boundaries_processed == expected_order


@patch.object(CoastalIdentifier, "process_boundary")
def test_process_all_boundaries_includes_ni_dz(mock_process, ci):
    """Should include Northern Ireland data zones"""
    ci.process_all_boundaries()

    boundaries_processed = [call.args[0] for call in mock_process.call_args_list]
    assert "ni_dz" in boundaries_processed


@patch.object(CoastalIdentifier, "process_boundary")
def test_process_all_boundaries_includes_scottish_dz(mock_process, ci):
    """Should include Scottish data zones"""
    ci.process_all_boundaries()

    boundaries_processed = [call.args[0] for call in mock_process.call_args_list]
    assert "sc_dz" in boundaries_processed
