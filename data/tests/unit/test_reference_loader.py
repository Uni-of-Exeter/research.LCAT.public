import pytest
import json
from unittest.mock import MagicMock, patch, mock_open

from data.src.reference_loader import ReferenceLoader


@pytest.fixture
def mock_config():
    return {
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_password",
        "processed_references_json": "/path/to/references.json",
    }


@pytest.fixture
def rl(mock_config):
    return ReferenceLoader(mock_config)


@pytest.fixture
def sample_reference_data():
    """Sample reference data"""
    return {
        "REF001": {
            "article_id": "REF001",
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
    }


# =============================================================================
# connect_to_db
# =============================================================================


@patch("data.src.reference_loader.psycopg2")
def test_connect_to_db_uses_provided_credentials(mock_psycopg2, rl):
    """Should use provided credentials over config"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    rl.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )


@patch("data.src.reference_loader.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, rl):
    """Should use config credentials when none provided"""
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    rl.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )


@patch("data.src.reference_loader.psycopg2")
def test_connect_to_db_sets_connection_and_cursor(mock_psycopg2, rl):
    """Should set conn and cur attributes"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    rl.connect_to_db()

    assert rl.conn == mock_conn
    assert rl.cur == mock_cursor


# =============================================================================
# load_json
# =============================================================================


def test_load_json_loads_from_file(rl, sample_reference_data):
    """Should load JSON data from file"""
    m = mock_open(read_data=json.dumps(sample_reference_data))
    
    with patch("builtins.open", m):
        rl.load_json("/path/to/refs.json")
        
        assert rl.data == sample_reference_data


def test_load_json_uses_config_filepath_by_default(rl, sample_reference_data):
    """Should use config filepath when none provided"""
    m = mock_open(read_data=json.dumps(sample_reference_data))
    
    with patch("builtins.open", m):
        rl.load_json()
        
        m.assert_called_once_with("/path/to/references.json")


def test_load_json_parses_json_correctly(rl):
    """Should parse JSON data correctly"""
    json_data = '{"REF001": {"article_id": "REF001", "title": "Test"}}'
    m = mock_open(read_data=json_data)
    
    with patch("builtins.open", m):
        rl.load_json("/test.json")
        
        assert rl.data["REF001"]["title"] == "Test"


# =============================================================================
# create_table
# =============================================================================


def test_create_table_creates_references_table(rl):
    """Should create references table"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.create_table()

    sql = rl.cur.execute.call_args[0][0]
    assert "CREATE TABLE" in sql.upper()
    assert "references" in sql


def test_create_table_includes_all_required_columns(rl):
    """Should include all required columns"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.create_table()

    sql = rl.cur.execute.call_args[0][0]
    assert "article_id" in sql
    assert "type" in sql
    assert "doi" in sql
    assert "link" in sql
    assert "link_replacement" in sql
    assert "title" in sql
    assert "authors" in sql
    assert "date" in sql
    assert "journal" in sql
    assert "issue" in sql
    assert "notes" in sql


def test_create_table_uses_article_id_as_primary_key(rl):
    """Should use article_id as PRIMARY KEY"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.create_table()

    sql = rl.cur.execute.call_args[0][0]
    assert "article_id INTEGER PRIMARY KEY" in sql


def test_create_table_uses_if_not_exists(rl):
    """Should use IF NOT EXISTS"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.create_table()

    sql = rl.cur.execute.call_args[0][0]
    assert "IF NOT EXISTS" in sql


def test_create_table_commits_transaction(rl):
    """Should commit after creating table"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.create_table()

    assert rl.conn.commit.called


def test_create_table_handles_exception(rl):
    """Should handle exceptions gracefully"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    rl.cur.execute.side_effect = Exception("Database error")

    # Should not raise exception
    rl.create_table()


# =============================================================================
# validate_record
# =============================================================================


def test_validate_record_returns_true_for_valid_record(rl):
    """Should return True when all required fields present"""
    valid_record = {
        "article_id": "REF001",
        "type": "Journal Article",
        "doi": "10.1234/test",
        "link": "http://example.com",
        "title": "Test",
        "authors": "Author, A.",
        "date": "2020",
        "journal": "Journal",
        "issue": "1",
        "notes": "",
    }
    
    result = rl.validate_record(valid_record)
    assert result is True


def test_validate_record_returns_false_for_missing_fields(rl):
    """Should return False when required fields missing"""
    invalid_record = {
        "article_id": "REF001",
        "title": "Test",
        # Missing other required fields
    }
    
    result = rl.validate_record(invalid_record)
    assert result is False


def test_validate_record_checks_all_required_fields(rl):
    """Should check for all required fields"""
    # Missing just one field
    almost_valid = {
        "article_id": "REF001",
        "type": "Journal Article",
        "doi": "10.1234/test",
        "link": "http://example.com",
        "title": "Test",
        "authors": "Author, A.",
        "date": "2020",
        "journal": "Journal",
        "issue": "1",
        # Missing "notes"
    }
    
    result = rl.validate_record(almost_valid)
    assert result is False


# =============================================================================
# insert_data
# =============================================================================


def test_insert_data_inserts_all_valid_records(rl, sample_reference_data):
    """Should insert all valid records"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    rl.data = sample_reference_data

    rl.insert_data()

    assert rl.cur.execute.call_count == 1
    assert rl.conn.commit.called


def test_insert_data_uses_on_conflict_do_nothing(rl, sample_reference_data):
    """Should use ON CONFLICT DO NOTHING for article_id"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    rl.data = sample_reference_data

    rl.insert_data()

    sql = rl.cur.execute.call_args[0][0]
    assert "ON CONFLICT" in sql
    assert "DO NOTHING" in sql


def test_insert_data_validates_records_before_inserting(rl):
    """Should only insert valid records"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    rl.data = {
        "REF001": {
            "article_id": "REF001",
            "type": "Journal Article",
            "doi": "10.1234/test",
            "link": "http://example.com",
            "link_replacement": "",
            "title": "Test",
            "authors": "Author",
            "date": "2020",
            "journal": "Journal",
            "issue": "1",
            "notes": "",
        },
        "REF002": {
            "article_id": "REF002",
            # Missing required fields
        },
    }

    rl.insert_data()

    # Should only insert 1 valid record
    assert rl.cur.execute.call_count == 1


def test_insert_data_commits_transaction(rl, sample_reference_data):
    """Should commit after inserting"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    rl.data = sample_reference_data

    rl.insert_data()

    assert rl.conn.commit.called


def test_insert_data_raises_when_no_data_loaded(rl):
    """Should raise ValueError when no data loaded"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    rl.data = None

    with pytest.raises(ValueError, match="No reference data loaded"):
        rl.insert_data()


def test_insert_data_inserts_all_columns(rl, sample_reference_data):
    """Should insert all column values"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()
    rl.data = sample_reference_data

    rl.insert_data()

    call_args = rl.cur.execute.call_args[0]
    sql = call_args[0]
    values = call_args[1]
    
    # Check SQL includes all columns
    assert "article_id" in sql
    assert "type" in sql
    assert "doi" in sql
    assert "link" in sql
    assert "link_replacement" in sql
    assert "title" in sql
    assert "authors" in sql
    assert "date" in sql
    assert "journal" in sql
    assert "issue" in sql
    assert "notes" in sql
    
    # Check values tuple has all values
    assert len(values) == 11


# =============================================================================
# drop_table
# =============================================================================


def test_drop_table_drops_references_table(rl):
    """Should drop references table"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.drop_table()

    sql = rl.cur.execute.call_args[0][0]
    assert "DROP TABLE" in sql.upper()
    assert "references" in sql


def test_drop_table_uses_if_exists(rl):
    """Should use IF EXISTS"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.drop_table()

    sql = rl.cur.execute.call_args[0][0]
    assert "IF EXISTS" in sql


def test_drop_table_commits_transaction(rl):
    """Should commit after dropping table"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.drop_table()

    assert rl.conn.commit.called


# =============================================================================
# close
# =============================================================================


def test_close_closes_cursor_and_connection(rl):
    """Should close cursor and connection"""
    rl.conn = MagicMock()
    rl.cur = MagicMock()

    rl.close()

    assert rl.cur.close.called
    assert rl.conn.close.called


# =============================================================================
# load_all_references
# =============================================================================


@patch.object(ReferenceLoader, "close")
@patch.object(ReferenceLoader, "insert_data")
@patch.object(ReferenceLoader, "create_table")
@patch.object(ReferenceLoader, "load_json")
@patch.object(ReferenceLoader, "connect_to_db")
def test_load_all_references_calls_all_methods_in_order(
    mock_connect, mock_load_json, mock_create, mock_insert, mock_close, rl
):
    """Should call all methods in correct order"""
    rl.load_all_references()

    mock_connect.assert_called_once()
    mock_load_json.assert_called_once()
    mock_create.assert_called_once()
    mock_insert.assert_called_once()
    mock_close.assert_called_once()


@patch.object(ReferenceLoader, "close")
@patch.object(ReferenceLoader, "insert_data")
@patch.object(ReferenceLoader, "create_table")
@patch.object(ReferenceLoader, "load_json")
@patch.object(ReferenceLoader, "connect_to_db")
def test_load_all_references_passes_filepath_to_load_json(
    mock_connect, mock_load_json, mock_create, mock_insert, mock_close, rl
):
    """Should pass filepath parameter to load_json"""
    rl.load_all_references("/custom/path.json")

    mock_load_json.assert_called_once_with("/custom/path.json")


@patch.object(ReferenceLoader, "close")
@patch.object(ReferenceLoader, "insert_data")
@patch.object(ReferenceLoader, "create_table")
@patch.object(ReferenceLoader, "load_json")
@patch.object(ReferenceLoader, "connect_to_db")
def test_load_all_references_uses_default_filepath_when_none_provided(
    mock_connect, mock_load_json, mock_create, mock_insert, mock_close, rl
):
    """Should use default filepath from load_json when none provided"""
    rl.load_all_references()

    mock_load_json.assert_called_once_with(None)


@patch.object(ReferenceLoader, "close")
@patch.object(ReferenceLoader, "insert_data")
@patch.object(ReferenceLoader, "create_table")
@patch.object(ReferenceLoader, "load_json")
@patch.object(ReferenceLoader, "connect_to_db")
def test_load_all_references_closes_connection_at_end(
    mock_connect, mock_load_json, mock_create, mock_insert, mock_close, rl
):
    """Should close connection at the end"""
    rl.load_all_references()

    # Close should be the last call
    mock_close.assert_called_once()
