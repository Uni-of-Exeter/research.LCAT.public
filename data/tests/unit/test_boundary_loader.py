import pytest
from unittest.mock import MagicMock, patch

from data.src.boundary_loader import BoundaryLoader


@pytest.fixture
def mock_config():
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
        "uk_counties_shp": "/path/to/counties.shp",
    }


@pytest.fixture
def bl(mock_config):
    return BoundaryLoader(mock_config)


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.boundary_loader.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, bl):
    """Should use provided credentials over config"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    bl.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )


@patch("data.src.boundary_loader.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, bl):
    """Should use config credentials when none provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    bl.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )


@patch("data.src.boundary_loader.psycopg2")
def test_connect_to_db_sets_connection_string(mock_psycopg2, bl):
    """Should build connection string for psql"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    bl.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    assert bl.connection_string == "postgresql://myuser:mypass@myhost/mydb"


# =============================================================================
# load_boundary
# =============================================================================


@patch("data.src.boundary_loader.os.system")
def test_load_boundary_builds_correct_command(mock_system, bl):
    """Should build correct shp2pgsql command"""
    bl.connection_string = "postgresql://user:pass@localhost/db"
    bl.target_projection = "27700"

    bl.load_boundary(
        boundary_identifier="uk_counties",
        source_projection="27700",
        filepath="/path/to/counties.shp",
    )

    cmd = mock_system.call_args[0][0]
    assert "shp2pgsql" in cmd
    assert "-s 27700:27700" in cmd
    assert "/path/to/counties.shp" in cmd
    assert "boundary_uk_counties" in cmd
    assert "postgresql://user:pass@localhost/db" in cmd


@patch("data.src.boundary_loader.os.system")
def test_load_boundary_uses_config_filepath_when_not_provided(mock_system, bl):
    """Should fall back to config for filepath"""
    bl.connection_string = "postgresql://user:pass@localhost/db"
    bl.target_projection = "27700"

    bl.load_boundary(
        boundary_identifier="uk_counties",
        source_projection="27700",
        # No filepath provided
    )

    cmd = mock_system.call_args[0][0]
    assert "/path/to/counties.shp" in cmd  # From config


@patch("data.src.boundary_loader.os.system")
def test_load_boundary_handles_different_projections(mock_system, bl):
    """Should handle source != target projection"""
    bl.connection_string = "postgresql://user:pass@localhost/db"
    bl.target_projection = "4326"

    bl.load_boundary(
        boundary_identifier="ni_dz",
        source_projection="29902",
        filepath="/path/to/ni.shp",
    )

    cmd = mock_system.call_args[0][0]
    assert "-s 29902:4326" in cmd


# =============================================================================
# load_all_boundaries
# =============================================================================


@patch.object(BoundaryLoader, "load_boundary")
@patch.object(BoundaryLoader, "drop_table")
def test_load_all_boundaries_drops_all_tables(mock_drop, mock_load, bl):
    """Should drop all 8 boundary tables"""
    bl.load_all_boundaries()

    assert mock_drop.call_count == 8

    dropped_tables = [call.args[0] for call in mock_drop.call_args_list]
    assert "boundary_uk_counties" in dropped_tables
    assert "boundary_la_districts" in dropped_tables
    assert "boundary_ni_dz" in dropped_tables
    assert "boundary_iom" in dropped_tables


@patch.object(BoundaryLoader, "load_boundary")
@patch.object(BoundaryLoader, "drop_table")
def test_load_all_boundaries_loads_with_correct_projections(mock_drop, mock_load, bl):
    """Should call load_boundary with correct source projections"""
    bl.load_all_boundaries()

    assert mock_load.call_count == 8

    # Check specific projections
    calls = {call.args[0]: call.args[1] for call in mock_load.call_args_list}
    assert calls["uk_counties"] == "27700"
    assert calls["ni_dz"] == "29902"
    assert calls["iom"] == "4326"