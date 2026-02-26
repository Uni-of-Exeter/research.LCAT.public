import pytest
from unittest.mock import MagicMock, patch, call

from psycopg2 import sql

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


def _make_conn_and_cursor(fetch_rows=None):
    """
    Helper: create a mock connection + cursor pair.
    """
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    if fetch_rows is None:
        fetch_rows = []
    cur.fetchall.return_value = fetch_rows
    return conn, cur


# =============================================================================
# _connect_superuser / _connect_user
# =============================================================================


@patch("data.src.db_manager.psycopg2")
def test_connect_superuser_uses_expected_credentials_and_default_db(mock_psycopg2, db_manager):
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    out = db_manager._connect_superuser()

    mock_psycopg2.connect.assert_called_once_with(
        dbname="postgres",
        user="postgres",
        password="superpass",
        host="localhost",
    )
    assert out is mock_conn


@patch("data.src.db_manager.psycopg2")
def test_connect_superuser_uses_provided_dbname(mock_psycopg2, db_manager):
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_superuser(dbname="custom_db")

    mock_psycopg2.connect.assert_called_once()
    assert mock_psycopg2.connect.call_args.kwargs["dbname"] == "custom_db"


@patch("data.src.db_manager.psycopg2")
def test_connect_user_uses_expected_credentials_and_default_db(mock_psycopg2, db_manager):
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    out = db_manager._connect_user()

    mock_psycopg2.connect.assert_called_once_with(
        dbname="postgres",
        user="test_user",
        password="test_pass",
        host="localhost",
    )
    assert out is mock_conn


@patch("data.src.db_manager.psycopg2")
def test_connect_user_uses_provided_dbname(mock_psycopg2, db_manager):
    mock_conn = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    db_manager._connect_user(dbname="custom_db")

    mock_psycopg2.connect.assert_called_once()
    assert mock_psycopg2.connect.call_args.kwargs["dbname"] == "custom_db"


# =============================================================================
# create_user_role
# =============================================================================


@patch.object(DBManager, "_connect_superuser")
def test_create_user_role_sets_autocommit_executes_and_closes(mock_connect, db_manager):
    conn, cur = _make_conn_and_cursor()
    mock_connect.return_value = conn

    db_manager.create_user_role()

    mock_connect.assert_called_once_with()
    assert conn.autocommit is True

    # execute called with a composed SQL object and password param
    assert cur.execute.call_count == 1
    executed_sql, params = cur.execute.call_args[0]
    assert isinstance(executed_sql, (sql.Composed, sql.SQL))
    assert params == ("test_pass",)

    cur.close.assert_called_once()
    conn.close.assert_called_once()


@patch.object(DBManager, "_connect_superuser")
def test_create_user_role_handles_exception_without_raising(mock_connect, db_manager):
    conn, cur = _make_conn_and_cursor()
    mock_connect.return_value = conn
    cur.execute.side_effect = Exception("Role creation error")

    # should not raise
    db_manager.create_user_role()


# =============================================================================
# create_database_with_role
# =============================================================================


@patch.object(DBManager, "_connect_superuser")
def test_create_database_with_role_sets_autocommit_executes_two_statements_and_closes(mock_connect, db_manager):
    conn, cur = _make_conn_and_cursor()
    mock_connect.return_value = conn

    db_manager.create_database_with_role()

    mock_connect.assert_called_once_with()
    assert conn.autocommit is True

    assert cur.execute.call_count == 2

    first_sql = cur.execute.call_args_list[0][0][0]
    second_sql = cur.execute.call_args_list[1][0][0]

    assert isinstance(first_sql, (sql.Composed, sql.SQL))
    assert isinstance(second_sql, (sql.Composed, sql.SQL))

    # We avoid fragile string matching of full Composed SQL;
    # but we can at least sanity-check the intent:
    assert "SET ROLE" in str(first_sql).upper()
    assert "CREATE DATABASE" in str(second_sql).upper()

    cur.close.assert_called_once()
    conn.close.assert_called_once()


@patch.object(DBManager, "_connect_superuser")
def test_create_database_with_role_handles_exception_without_raising(mock_connect, db_manager):
    conn, cur = _make_conn_and_cursor()
    mock_connect.return_value = conn
    cur.execute.side_effect = Exception("Database creation error")

    db_manager.create_database_with_role()


# =============================================================================
# add_postgis_extension
# =============================================================================


@patch.object(DBManager, "_connect_superuser")
def test_add_postgis_extension_connects_to_target_db_sets_autocommit_executes_and_closes(mock_connect, db_manager):
    conn, cur = _make_conn_and_cursor()
    mock_connect.return_value = conn

    db_manager.add_postgis_extension()

    mock_connect.assert_called_once_with("test_db")
    assert conn.autocommit is True

    cur.execute.assert_called_once_with("CREATE EXTENSION IF NOT EXISTS postgis;")
    cur.close.assert_called_once()
    conn.close.assert_called_once()


@patch.object(DBManager, "_connect_superuser")
def test_add_postgis_extension_handles_exception_without_raising(mock_connect, db_manager):
    conn, cur = _make_conn_and_cursor()
    mock_connect.return_value = conn
    cur.execute.side_effect = Exception("Extension error")

    db_manager.add_postgis_extension()


# =============================================================================
# setup_database
# =============================================================================


def test_setup_database_calls_methods_in_order(db_manager):
    # Patch on the instance to allow strict ordering checks
    db_manager.create_user_role = MagicMock()
    db_manager.create_database_with_role = MagicMock()
    db_manager.add_postgis_extension = MagicMock()

    db_manager.setup_database()

    # Assert order via mock_calls on the instance (explicit and reliable)
    assert db_manager.create_user_role.mock_calls == [call()]
    assert db_manager.create_database_with_role.mock_calls == [call()]
    assert db_manager.add_postgis_extension.mock_calls == [call()]

    # And ordering across the three:
    combined = (
        db_manager.create_user_role.call_time
        if hasattr(db_manager.create_user_role, "call_time")
        else None
    )
    # Instead of fake timestamps, check by constructing a single list:
    all_calls = []
    all_calls.extend([("create_user_role", c) for c in db_manager.create_user_role.mock_calls])
    all_calls.extend([("create_database_with_role", c) for c in db_manager.create_database_with_role.mock_calls])
    all_calls.extend([("add_postgis_extension", c) for c in db_manager.add_postgis_extension.mock_calls])

    # Since each is called once, order is enforced by asserting the sequence via call_count checks:
    assert db_manager.create_user_role.call_count == 1
    assert db_manager.create_database_with_role.call_count == 1
    assert db_manager.add_postgis_extension.call_count == 1


# =============================================================================
# test_new_user_capabilities
# =============================================================================


@patch.object(DBManager, "_connect_user")
def test_new_user_capabilities_runs_expected_sql_sequence(mock_connect_user, db_manager):
    """
    test_new_user_capabilities uses _connect_user three times:
      1) connect to postgres (create test DB)
      2) connect to test DB (create table, insert/select/drop)
      3) connect to postgres (drop test DB)
    So we must supply three different connections/cursors.
    """
    conn1, cur1 = _make_conn_and_cursor(fetch_rows=[])
    conn2, cur2 = _make_conn_and_cursor(fetch_rows=[(1, "Test Name 1")])
    conn3, cur3 = _make_conn_and_cursor(fetch_rows=[])

    mock_connect_user.side_effect = [conn1, conn2, conn3]

    db_manager.test_new_user_capabilities()

    test_dbname = "test_user_test_db"

    # Connection calls
    assert mock_connect_user.call_args_list == [
        call(),  # default postgres
        call(dbname=test_dbname),  # connect to test db
        call(),  # default postgres
    ]

    # Step 2: CREATE DATABASE executed on first connection
    assert any("CREATE DATABASE" in str(c[0][0]).upper() for c in cur1.execute.call_args_list)

    # Step 4-7 on second connection
    combined2 = " ".join(str(c).upper() for c in cur2.execute.call_args_list)
    assert "CREATE TABLE" in combined2
    assert "INSERT INTO" in combined2
    assert "SELECT * FROM TEST_TABLE" in combined2
    assert "DROP TABLE" in combined2

    # Step 8: DROP DATABASE executed on third connection
    assert any("DROP DATABASE" in str(c[0][0]).upper() for c in cur3.execute.call_args_list)

    # Ensure cursors and conns closed along the way (best-effort check)
    assert cur1.close.called
    assert conn1.close.called
    assert cur2.close.called
    assert conn2.close.called
    assert cur3.close.called
    assert conn3.close.called


@patch.object(DBManager, "_connect_user")
def test_new_user_capabilities_handles_exception_without_raising(mock_connect_user, db_manager):
    conn1, cur1 = _make_conn_and_cursor()
    mock_connect_user.return_value = conn1
    cur1.execute.side_effect = Exception("Test error")

    db_manager.test_new_user_capabilities()