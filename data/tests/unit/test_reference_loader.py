import json
from unittest.mock import MagicMock, patch, mock_open

import pytest

# adjust this import to your actual module path
from data.src.reference_loader import ReferenceLoader


@pytest.fixture
def config():
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
        "processed_references_json": "/path/to/references.json",
    }


@pytest.fixture
def rl(config):
    return ReferenceLoader(config)


@pytest.fixture
def db_ready_rl(rl):
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    return rl


@pytest.fixture
def valid_record():
    return {
        "article_id": 1,
        "type": "Journal Article",
        "doi": "10.1234/test",
        "link": "http://example.com",
        "link_replacement": "",
        "title": "Test Paper",
        "authors": "Author, A.",
        "date": "2020",
        "journal": "Test Journal",
        "issue": "1(2)",
        "notes": "",
    }


# -----------------------------------------------------------------------------
# connect_to_db
# -----------------------------------------------------------------------------

@patch("data.src.reference_loader.psycopg2.connect")
def test_connect_to_db_uses_provided_credentials(connect, rl):
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value = cur
    connect.return_value = conn

    rl.connect_to_db(host="h", dbname="d", user="u", password="p")

    connect.assert_called_once_with(host="h", dbname="d", user="u", password="p")
    assert rl.conn is conn
    assert rl.cur is cur


@patch("data.src.reference_loader.psycopg2.connect")
@pytest.mark.parametrize(
    "kwargs",
    [
        {},  # none provided
        {"host": "h"},  # partial creds => should fall back to config (current behaviour)
        {"dbname": "d"},
        {"user": "u"},
        {"password": "p"},
        {"host": "h", "dbname": "d", "user": "u"},  # missing password
    ],
)
def test_connect_to_db_falls_back_to_config_if_any_missing(connect, rl, kwargs):
    conn = MagicMock()
    conn.cursor.return_value = MagicMock()
    connect.return_value = conn

    rl.connect_to_db(**kwargs)

    connect.assert_called_once_with(
        host=rl.conf["host"],
        dbname=rl.conf["dbname"],
        user=rl.conf["user"],
        password=rl.conf["user_pass"],
    )


# -----------------------------------------------------------------------------
# load_json
# -----------------------------------------------------------------------------

def test_load_json_uses_explicit_filepath(rl, valid_record):
    sample = {"1": valid_record}
    m = mock_open(read_data=json.dumps(sample))

    with patch("builtins.open", m):
        rl.load_json("/tmp/custom.json")

    m.assert_called_once_with("/tmp/custom.json")
    assert rl.data == sample


def test_load_json_uses_config_filepath_by_default(rl, valid_record):
    sample = {"1": valid_record}
    m = mock_open(read_data=json.dumps(sample))

    with patch("builtins.open", m):
        rl.load_json()

    m.assert_called_once_with(rl.conf["processed_references_json"])
    assert rl.data == sample


# -----------------------------------------------------------------------------
# validate_record
# -----------------------------------------------------------------------------

def test_validate_record_true_when_all_required_present(rl, valid_record):
    assert rl.validate_record(valid_record) is True


@pytest.mark.parametrize(
    "missing_key",
    [
        "article_id",
        "type",
        "doi",
        "link",
        "title",
        "authors",
        "date",
        "journal",
        "issue",
        "notes",
        # this one is the important bug: insert_data requires it but validate_record doesn't
        "link_replacement",
    ],
)
def test_validate_record_false_when_required_missing(rl, valid_record, missing_key):
    record = dict(valid_record)
    record.pop(missing_key)

    # desired behaviour:
    # - either validate_record should require link_replacement
    # - or insert_data should not assume it exists
    #
    # this will currently FAIL for missing_key == "link_replacement" until code is fixed.
    assert rl.validate_record(record) is False


# -----------------------------------------------------------------------------
# create_table
# -----------------------------------------------------------------------------

def test_create_table_executes_and_commits(db_ready_rl):
    db_ready_rl.create_table()
    db_ready_rl.cur.execute.assert_called_once()
    db_ready_rl.conn.commit.assert_called_once()


def test_create_table_uses_integer_primary_key_for_article_id(db_ready_rl):
    """
    article_id should be an INTEGER primary key.
    """
    db_ready_rl.create_table()
    sql = db_ready_rl.cur.execute.call_args[0][0]
    assert "article_id" in sql
    assert "PRIMARY KEY" in sql.upper()
    assert "ARTICLE_ID INTEGER" in sql.upper() or "ARTICLE_ID INT" in sql.upper()


# -----------------------------------------------------------------------------
# insert_data
# -----------------------------------------------------------------------------

def test_insert_data_raises_if_no_data_loaded(db_ready_rl):
    db_ready_rl.data = None
    with pytest.raises(ValueError, match="No reference data loaded"):
        db_ready_rl.insert_data()


def test_insert_data_inserts_only_valid_records(db_ready_rl, valid_record):
    db_ready_rl.data = {
        "1": valid_record,
        "2": {"article_id": 2},  # invalid
    }

    db_ready_rl.insert_data()

    # one insert for the valid record only
    assert db_ready_rl.cur.execute.call_count == 1
    db_ready_rl.conn.commit.assert_called_once()


def test_insert_data_uses_on_conflict_do_nothing(db_ready_rl, valid_record):
    db_ready_rl.data = {"1": valid_record}

    db_ready_rl.insert_data()

    sql = db_ready_rl.cur.execute.call_args[0][0].upper()
    assert "ON CONFLICT" in sql
    assert "DO NOTHING" in sql


def test_insert_data_passes_expected_values_tuple(db_ready_rl, valid_record):
    db_ready_rl.data = {"1": valid_record}

    db_ready_rl.insert_data()

    _, values = db_ready_rl.cur.execute.call_args[0]
    assert values == (
        valid_record["article_id"],
        valid_record["type"],
        valid_record["doi"],
        valid_record["link"],
        valid_record["link_replacement"],
        valid_record["title"],
        valid_record["authors"],
        valid_record["date"],
        valid_record["journal"],
        valid_record["issue"],
        valid_record["notes"],
    )


# -----------------------------------------------------------------------------
# drop_table / close / load_all_references
# -----------------------------------------------------------------------------

def test_drop_table_executes_and_commits(db_ready_rl):
    db_ready_rl.drop_table()
    db_ready_rl.cur.execute.assert_called_once()
    db_ready_rl.conn.commit.assert_called_once()


def test_close_closes_cursor_and_connection(rl):
    rl.cur = MagicMock()
    rl.conn = MagicMock()
    rl.close()
    rl.cur.close.assert_called_once()
    rl.conn.close.assert_called_once()


def test_load_all_references_calls_steps_in_order(rl):
    calls = []

    def record(name):
        def _fn(*args, **kwargs):
            calls.append(name)
        return _fn

    rl.connect_to_db = record("connect")
    rl.load_json = record("load_json")
    rl.create_table = record("create_table")
    rl.insert_data = record("insert_data")
    rl.close = record("close")

    rl.load_all_references("/tmp/refs.json")

    assert calls == ["connect", "load_json", "create_table", "insert_data", "close"]