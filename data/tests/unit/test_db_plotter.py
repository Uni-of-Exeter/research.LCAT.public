import pytest
from unittest.mock import MagicMock, patch

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
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    dbp.connect_to_db(host="myhost", dbname="mydb", user="myuser", password="mypass")

    mock_psycopg2.connect.assert_called_once_with(
        host="myhost", dbname="mydb", user="myuser", password="mypass"
    )


@patch("data.src.db_plotter.psycopg2")
def test_connect_to_db_falls_back_to_config(mock_psycopg2, dbp):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = MagicMock()
    mock_psycopg2.connect.return_value = mock_conn

    dbp.connect_to_db()

    mock_psycopg2.connect.assert_called_once_with(
        host="localhost", dbname="test_db", user="test_user", password="test_password"
    )


@patch("data.src.db_plotter.psycopg2")
def test_connect_to_db_sets_connection_and_cursor(mock_psycopg2, dbp):
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


def test_set_clean_boundary_names_sets_expected_mapping(dbp):
    expected = {
        "uk_counties": "UK Counties and Unitary Authorities",
        "la_districts": "LA Districts",
        "lsoa": "LSOAs",
        "msoa": "MSOAs",
        "parishes": "Parishes",
        "sc_dz": "Scotland Data Zones",
        "ni_dz": "Northern Ireland Data Zones",
        "iom": "Isle of Man",
    }
    assert dbp.clean_boundary_names == expected


# =============================================================================
# SQL getters
# =============================================================================


def test_get_boundary_geometry_queries_correct_table(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_boundary_geometry("uk_counties")

    sql = dbp.cur.execute.call_args[0][0]
    assert 'FROM "boundary_uk_counties"' in sql
    assert "SELECT gid, geom" in sql


def test_get_boundary_geometry_returns_fetched_data(dbp):
    dbp.cur = MagicMock()
    mock_data = [(1, b"geom1"), (2, b"geom2")]
    dbp.cur.fetchall.return_value = mock_data

    assert dbp.get_boundary_geometry("lsoa") == mock_data


def test_get_grid_geometry_queries_chess_scape_grid(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_grid_geometry()

    sql = dbp.cur.execute.call_args[0][0]
    assert 'FROM "chess_scape_grid"' in sql
    assert "SELECT grid_cell_id, geometry, bias_corrected, coastal_info" in sql


def test_get_grid_geometry_returns_rows(dbp):
    dbp.cur = MagicMock()
    mock_data = [(1, b"geom1", True, "coastline")]
    dbp.cur.fetchall.return_value = mock_data

    assert dbp.get_grid_geometry() == mock_data


def test_get_chess_data_queries_correct_table_and_column(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_chess_data(rcp=60, season="annual", variable="tas", decade=1980)

    sql = dbp.cur.execute.call_args[0][0]
    assert 'FROM "chess_scape_rcp60_annual"' in sql
    assert 'SELECT grid_cell_id, "tas_1980"' in sql


def test_get_chess_data_returns_rows(dbp):
    dbp.cur = MagicMock()
    mock_data = [(1, 15.5), (2, 16.2)]
    dbp.cur.fetchall.return_value = mock_data

    assert dbp.get_chess_data(60, "annual", "tas", 1980) == mock_data


def test_get_geometry_by_gid_uses_parameter(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_geometry_by_gid("uk_counties", 42)

    sql, params = dbp.cur.execute.call_args[0]
    assert "WHERE s.gid = %s" in sql
    assert params == (42,)


def test_get_region_name_by_gid_uses_correct_column_and_param(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchone.return_value = ("Test County",)

    name = dbp.get_region_name_by_gid("uk_counties", 1)

    sql, params = dbp.cur.execute.call_args[0]
    assert "CTYUA23NM" in sql
    assert params == (1,)
    assert name == "Test County"


def test_get_overlapping_cells_queries_expected_join_and_param(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_overlapping_cells("lsoa", 42)

    sql, params = dbp.cur.execute.call_args[0]
    assert 'FROM "grid_overlaps_lsoa"' in sql
    assert 'JOIN "chess_scape_grid"' in sql
    assert "WHERE o.gid = %s" in sql
    assert params == (42,)


def test_get_cached_chess_data_queries_correct_table_and_column(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_cached_chess_data("uk_counties", "tas", 1980, 60, "annual")

    sql = dbp.cur.execute.call_args[0][0]
    assert 'FROM "cache_uk_counties_to_rcp60_annual"' in sql
    assert 'SELECT gid, "tas_1980"' in sql


def test_get_no_overlap_geometry_queries_expected_subquery(dbp):
    dbp.cur = MagicMock()
    dbp.cur.fetchall.return_value = []

    dbp.get_no_overlap_geometry("uk_counties")

    sql = dbp.cur.execute.call_args[0][0]
    assert 'FROM "boundary_uk_counties" bt' in sql
    assert 'FROM "grid_overlaps_uk_counties" ot' in sql
    assert "WHERE ot.is_overlap = FALSE" in sql
    assert "WHERE bt.gid IN" in sql


# =============================================================================
# Plotting methods: keep these lightweight and meaningful
# =============================================================================


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb.loads")
def test_plot_boundary_calls_get_boundary_geometry_and_plots(mock_wkb_loads, mock_gdf_cls, mock_show, dbp):
    # Arrange: boundary geometry rows
    with patch.object(dbp, "get_boundary_geometry", return_value=[(1, "00"), (2, "00")]) as mock_get:
        # Avoid shapely parsing complexities
        mock_wkb_loads.return_value = MagicMock()

        # Mock GeoDataFrame instance and its plot method
        gdf_instance = MagicMock()
        mock_gdf_cls.return_value = gdf_instance
        gdf_instance.plot.return_value = MagicMock()

        # Act
        dbp.plot_boundary("uk_counties")

        # Assert
        mock_get.assert_called_once_with("uk_counties")
        assert mock_gdf_cls.called
        assert gdf_instance.plot.called
        mock_show.assert_called_once()


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb.loads")
def test_plot_boundary_coloured_by_coastal_queries_is_coastal(mock_wkb_loads, mock_gdf_cls, mock_show, dbp):
    dbp.cur = MagicMock()
    # First fetchall: coastal_data
    dbp.cur.fetchall.return_value = [(1, True), (2, False)]

    with patch.object(dbp, "get_boundary_geometry", return_value=[(1, "00"), (2, "00")]):
        mock_wkb_loads.return_value = MagicMock()
        gdf_instance = MagicMock()
        mock_gdf_cls.return_value = gdf_instance

        dbp.plot_boundary_coloured_by_coastal("uk_counties")

        # Ensure we ran a query mentioning is_coastal
        executed_sql = " ".join(str(c[0][0]) for c in dbp.cur.execute.call_args_list)
        assert "is_coastal" in executed_sql


@patch("data.src.db_plotter.plt.show")
@patch("data.src.db_plotter.gpd.GeoDataFrame")
@patch("data.src.db_plotter.wkb.loads")
def test_plot_boundary_coloured_by_cache_calls_data_sources(mock_wkb_loads, mock_gdf_cls, mock_show, dbp):
    with patch.object(dbp, "get_boundary_geometry", return_value=[(1, "00")]) as mock_boundary, \
         patch.object(dbp, "get_cached_chess_data", return_value=[(1, 12.3)]) as mock_cache:
        mock_wkb_loads.return_value = MagicMock()
        gdf_instance = MagicMock()
        mock_gdf_cls.return_value = gdf_instance

        dbp.plot_boundary_coloured_by_cache("uk_counties", "tas", 1980, 60, "annual")

        mock_boundary.assert_called_once_with("uk_counties")
        mock_cache.assert_called_once_with("uk_counties", "tas", 1980, 60, "annual")
        mock_show.assert_called_once()

