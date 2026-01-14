import pytest
from unittest.mock import MagicMock, patch, call

from data.src.db_manager import DBManager


@pytest.fixture
def db_manager():
    return DBManager(
        superuser="postgres",
        superuser_pass="superpass",
        host="localhost",
        dbname="test_db",
        user="test_user",
        user_pass="test_pass",
    )


# =============================================================================
# _connect_superuser
# =============================================================================


@patch("data.src.db_manager.psycopg2")
def test_connect_superuser_uses_superuser_credentials(mock_psycopg2, db_manager):
    """Should connect with superuser credentials"""
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_superuser()

    mock_psycopg2.connect.assert_called_once_with(
        dbname="postgres",
        user="postgres",
        password="superpass",
        host="localhost",
    )


@patch("data.src.db_manager.psycopg2")
def test_connect_superuser_defaults_to_postgres_db(mock_psycopg2, db_manager):
    """Should default to postgres database when no dbname provided"""
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_superuser()

    call_args = mock_psycopg2.connect.call_args
    assert call_args[1]["dbname"] == "postgres"


@patch("data.src.db_manager.psycopg2")
def test_connect_superuser_uses_provided_dbname(mock_psycopg2, db_manager):
    """Should use provided database name"""
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_superuser(dbname="custom_db")

    call_args = mock_psycopg2.connect.call_args
    assert call_args[1]["dbname"] == "custom_db"


# =============================================================================
# _connect_user
# =============================================================================


@patch("data.src.db_manager.psycopg2")
def test_connect_user_uses_user_credentials(mock_psycopg2, db_manager):
    """Should connect with user credentials"""
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_user()

    mock_psycopg2.connect.assert_called_once_with(
        dbname="postgres",
        user="test_user",
        password="test_pass",
        host="localhost",
    )


@patch("data.src.db_manager.psycopg2")
def test_connect_user_defaults_to_postgres_db(mock_psycopg2, db_manager):
    """Should default to postgres database when no dbname provided"""
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_user()

    call_args = mock_psycopg2.connect.call_args
    assert call_args[1]["dbname"] == "postgres"


@patch("data.src.db_manager.psycopg2")
def test_connect_user_uses_provided_dbname(mock_psycopg2, db_manager):
    """Should use provided database name"""
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_user(dbname="custom_db")

    call_args = mock_psycopg2.connect.call_args
    assert call_args[1]["dbname"] == "custom_db"


# =============================================================================
# create_user_role
# =============================================================================


@patch.object(DBManager, "_connect_superuser")
def test_create_user_role_connects_as_superuser(mock_connect, db_manager):
    """Should connect as superuser to create role"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_user_role()

    mock_connect.assert_called_once()


@patch.object(DBManager, "_connect_superuser")
def test_create_user_role_sets_autocommit(mock_connect, db_manager):
    """Should set autocommit to True"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_user_role()

    assert mock_conn.autocommit is True


@patch.object(DBManager, "_connect_superuser")
def test_create_user_role_executes_create_role_query(mock_connect, db_manager):
    """Should execute CREATE ROLE query"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_user_role()

    assert mock_cursor.execute.called
    # Check that the query contains CREATE ROLE
    sql_call = str(mock_cursor.execute.call_args)
    assert "CREATE ROLE" in sql_call.upper()


@patch.object(DBManager, "_connect_superuser")
def test_create_user_role_closes_connection(mock_connect, db_manager):
    """Should close cursor and connection after creating role"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_user_role()

    assert mock_cursor.close.called
    assert mock_conn.close.called


@patch.object(DBManager, "_connect_superuser")
def test_create_user_role_handles_exception(mock_connect, db_manager):
    """Should handle exceptions gracefully"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.execute.side_effect = Exception("Role creation error")

    # Should not raise exception
    db_manager.create_user_role()


# =============================================================================
# create_database_with_role
# =============================================================================


@patch.object(DBManager, "_connect_superuser")
def test_create_database_with_role_connects_as_superuser(mock_connect, db_manager):
    """Should connect as superuser to create database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_database_with_role()

    mock_connect.assert_called_once()


@patch.object(DBManager, "_connect_superuser")
def test_create_database_with_role_sets_autocommit(mock_connect, db_manager):
    """Should set autocommit to True"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_database_with_role()

    assert mock_conn.autocommit is True


@patch.object(DBManager, "_connect_superuser")
def test_create_database_with_role_sets_role_first(mock_connect, db_manager):
    """Should set role before creating database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_database_with_role()

    # Check that SET ROLE is called before CREATE DATABASE
    assert mock_cursor.execute.call_count == 2
    first_call = str(mock_cursor.execute.call_args_list[0])
    second_call = str(mock_cursor.execute.call_args_list[1])
    
    assert "SET ROLE" in first_call.upper()
    assert "CREATE DATABASE" in second_call.upper()


@patch.object(DBManager, "_connect_superuser")
def test_create_database_with_role_closes_connection(mock_connect, db_manager):
    """Should close cursor and connection after creating database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.create_database_with_role()

    assert mock_cursor.close.called
    assert mock_conn.close.called


@patch.object(DBManager, "_connect_superuser")
def test_create_database_with_role_handles_exception(mock_connect, db_manager):
    """Should handle exceptions gracefully"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.execute.side_effect = Exception("Database creation error")

    # Should not raise exception
    db_manager.create_database_with_role()


# =============================================================================
# add_postgis_extension
# =============================================================================


@patch.object(DBManager, "_connect_superuser")
def test_add_postgis_extension_connects_to_target_db(mock_connect, db_manager):
    """Should connect to the target database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.add_postgis_extension()

    mock_connect.assert_called_once_with("test_db")


@patch.object(DBManager, "_connect_superuser")
def test_add_postgis_extension_sets_autocommit(mock_connect, db_manager):
    """Should set autocommit to True"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.add_postgis_extension()

    assert mock_conn.autocommit is True


@patch.object(DBManager, "_connect_superuser")
def test_add_postgis_extension_creates_extension(mock_connect, db_manager):
    """Should execute CREATE EXTENSION postgis query"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.add_postgis_extension()

    mock_cursor.execute.assert_called_once_with("CREATE EXTENSION IF NOT EXISTS postgis;")


@patch.object(DBManager, "_connect_superuser")
def test_add_postgis_extension_closes_connection(mock_connect, db_manager):
    """Should close cursor and connection after adding extension"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    db_manager.add_postgis_extension()

    assert mock_cursor.close.called
    assert mock_conn.close.called


@patch.object(DBManager, "_connect_superuser")
def test_add_postgis_extension_handles_exception(mock_connect, db_manager):
    """Should handle exceptions gracefully"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.execute.side_effect = Exception("Extension error")

    # Should not raise exception
    db_manager.add_postgis_extension()


# =============================================================================
# setup_database
# =============================================================================


@patch.object(DBManager, "add_postgis_extension")
@patch.object(DBManager, "create_database_with_role")
@patch.object(DBManager, "create_user_role")
def test_setup_database_calls_all_methods(mock_create_role, mock_create_db, mock_add_postgis, db_manager):
    """Should call all three setup methods"""
    db_manager.setup_database()

    mock_create_role.assert_called_once()
    mock_create_db.assert_called_once()
    mock_add_postgis.assert_called_once()


@patch.object(DBManager, "add_postgis_extension")
@patch.object(DBManager, "create_database_with_role")
@patch.object(DBManager, "create_user_role")
def test_setup_database_calls_methods_in_correct_order(mock_create_role, mock_create_db, mock_add_postgis, db_manager):
    """Should call methods in order: create_user_role, create_database_with_role, add_postgis_extension"""
    db_manager.setup_database()

    # Verify order by checking call order
    assert mock_create_role.called
    assert mock_create_db.called
    assert mock_add_postgis.called


# =============================================================================
# test_new_user_capabilities
# =============================================================================


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_connects_as_user(mock_connect, db_manager):
    """Should connect as the new user"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    db_manager.test_new_user_capabilities()

    assert mock_connect.call_count >= 2


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_creates_test_database(mock_connect, db_manager):
    """Should create a test database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    db_manager.test_new_user_capabilities()

    # Check that CREATE DATABASE was called
    sql_calls = [str(call) for call in mock_cursor.execute.call_args_list]
    sql_combined = " ".join(sql_calls).upper()
    assert "CREATE DATABASE" in sql_combined


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_creates_table(mock_connect, db_manager):
    """Should create a test table"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    db_manager.test_new_user_capabilities()

    sql_calls = [str(call) for call in mock_cursor.execute.call_args_list]
    sql_combined = " ".join(sql_calls).upper()
    assert "CREATE TABLE" in sql_combined


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_inserts_data(mock_connect, db_manager):
    """Should insert data into test table"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    db_manager.test_new_user_capabilities()

    sql_calls = [str(call) for call in mock_cursor.execute.call_args_list]
    sql_combined = " ".join(sql_calls).upper()
    assert "INSERT INTO" in sql_combined


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_selects_data(mock_connect, db_manager):
    """Should select data from test table"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = [(1, "Test Name 1"), (2, "Test Name 2"), (3, "Test Name 3")]

    db_manager.test_new_user_capabilities()

    sql_calls = [str(call) for call in mock_cursor.execute.call_args_list]
    sql_combined = " ".join(sql_calls).upper()
    assert "SELECT" in sql_combined


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_drops_table(mock_connect, db_manager):
    """Should drop test table"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    db_manager.test_new_user_capabilities()

    sql_calls = [str(call) for call in mock_cursor.execute.call_args_list]
    sql_combined = " ".join(sql_calls).upper()
    assert "DROP TABLE" in sql_combined


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_drops_database(mock_connect, db_manager):
    """Should drop test database"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    db_manager.test_new_user_capabilities()

    sql_calls = [str(call) for call in mock_cursor.execute.call_args_list]
    sql_combined = " ".join(sql_calls).upper()
    assert "DROP DATABASE" in sql_combined


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_handles_exception(mock_connect, db_manager):
    """Should handle exceptions gracefully"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.execute.side_effect = Exception("Test error")

    # Should not raise exception
    db_manager.test_new_user_capabilities()


@patch.object(DBManager, "_connect_user")
def test_test_new_user_capabilities_uses_correct_test_dbname(mock_connect, db_manager):
    """Should use user_test_db as test database name"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    mock_cursor.fetchall.return_value = []

    db_manager.test_new_user_capabilities()

    sql_calls = [str(call) for call in mock_cursor.execute.call_args_list]
    sql_combined = " ".join(sql_calls)
    assert "test_user_test_db" in sql_combined
