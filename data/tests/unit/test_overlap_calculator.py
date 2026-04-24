import pytest
from unittest.mock import MagicMock, patch, call

import data.src.overlap_calculator as oc_module
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

@pytest.mark.parametrize(
    "kwargs, expected",
    [
        (
            dict(host="myhost", dbname="mydb", user="myuser", password="mypass"),
            dict(host="myhost", dbname="mydb", user="myuser", password="mypass"),
        ),
        (
            dict(),
            dict(host="localhost", dbname="test_db", user="test_user", password="test_password"),
        ),
    ],
)
@patch("data.src.overlap_calculator.psycopg2")
def test_connect_to_db_connects_and_sets_conn_cur(mock_psycopg2, oc, kwargs, expected):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_psycopg2.connect.return_value = mock_conn

    oc.connect_to_db(**kwargs)

    mock_psycopg2.connect.assert_called_once_with(**expected)
    assert oc.conn is mock_conn
    assert oc.cur is mock_cursor


# =============================================================================
# set_boundary_table
# =============================================================================

@pytest.mark.parametrize(
    "boundary_identifier",
    ["uk_counties", "lsoa", "msoa", "parishes"],
)
def test_set_boundary_table_sets_names_and_resets_tracking(oc, boundary_identifier):
    oc.no_overlap_regions = {"old": "data"}
    oc.no_overlap_closest_cells = {"old": "data"}

    oc.set_boundary_table(boundary_identifier)

    assert oc.boundary_identifier == boundary_identifier
    assert oc.boundary_table_name == f"boundary_{boundary_identifier}"
    assert oc.new_table_name == f"grid_overlaps_{boundary_identifier}"
    assert oc.no_overlap_regions == {}
    assert oc.no_overlap_closest_cells == {}


# =============================================================================
# drop_table
# =============================================================================

def test_drop_table_executes_drop_query_and_commits(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()

    oc.drop_table("test_table")

    oc.cur.execute.assert_called_once_with('DROP TABLE IF EXISTS "test_table";')
    oc.conn.commit.assert_called_once()


def test_drop_table_handles_exception(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.cur.execute.side_effect = Exception("Database error")

    # Should not raise
    oc.drop_table("test_table")


# =============================================================================
# create_overlap_table
# =============================================================================

def test_create_overlap_table_raises_without_boundary_set(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = None

    with pytest.raises(ValueError, match="boundary identifier"):
        oc.create_overlap_table()


def test_create_overlap_table_creates_expected_schema_and_commits(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_uk_counties"
    oc.new_table_name = "grid_overlaps_uk_counties"

    oc.create_overlap_table()

    sql = oc.cur.execute.call_args[0][0]
    # Stronger assertions than just "CREATE TABLE"
    assert f'CREATE TABLE IF NOT EXISTS "{oc.new_table_name}"' in sql
    assert "gid INTEGER" in sql
    assert "grid_cell_id INTEGER" in sql
    assert "is_overlap BOOLEAN" in sql
    assert "bias_corrected BOOLEAN" in sql

    oc.conn.commit.assert_called_once()


# =============================================================================
# ensure_spatial_index
# =============================================================================

def test_ensure_spatial_index_creates_gist_index_and_commits(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()

    oc.ensure_spatial_index("chess_scape_grid", "geometry")

    sql = oc.cur.execute.call_args[0][0]
    assert "CREATE INDEX IF NOT EXISTS" in sql
    assert "USING GIST" in sql.upper()
    assert 'ON "chess_scape_grid"' in sql
    assert "(geometry)" in sql

    oc.conn.commit.assert_called_once()


# =============================================================================
# insert_overlaps_optimised
# =============================================================================

def test_insert_overlaps_optimised_builds_expected_query_and_commits(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_lsoa"
    oc.new_table_name = "grid_overlaps_lsoa"
    oc.grid_table_name = "chess_scape_grid"

    oc.insert_overlaps_optimised()

    sql = oc.cur.execute.call_args[0][0]
    # Check key semantics rather than vague substrings
    assert f'INSERT INTO "{oc.new_table_name}"' in sql
    assert "(gid, grid_cell_id, is_overlap, bias_corrected)" in sql
    assert "SELECT s.gid, g.grid_cell_id, TRUE, g.bias_corrected" in sql
    assert f"FROM {oc.grid_table_name} g" in sql
    assert f"JOIN {oc.boundary_table_name} s" in sql
    assert "ON ST_Intersects(g.geometry, s.geom)" in sql
    assert "WHERE ST_Intersects(ST_Envelope(g.geometry), ST_Envelope(s.geom))" in sql

    oc.conn.commit.assert_called_once()


# =============================================================================
# find_no_overlap_regions
# =============================================================================

@pytest.mark.parametrize(
    "fetchall_return, expected",
    [
        ([(1,), (5,), (10,)], [1, 5, 10]),
        ([], []),
    ],
)
def test_find_no_overlap_regions_returns_gids(oc, fetchall_return, expected):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_test"
    oc.new_table_name = "grid_overlaps_test"
    oc.cur.fetchall.return_value = fetchall_return

    result = oc.find_no_overlap_regions()

    assert result == expected
    assert oc.cur.execute.called


# =============================================================================
# find_closest_grid_cell
# =============================================================================

def test_find_closest_grid_cell_returns_triple_none_when_no_candidates(oc):
    oc.cur = MagicMock()

    out = oc.find_closest_grid_cell(region_geom="REGION", candidate_cells=[])

    assert out == (None, None, None)
    oc.cur.execute.assert_not_called()


def test_find_closest_grid_cell_executes_query_and_returns_three_values(oc):
    oc.cur = MagicMock()
    oc.cur.fetchone.return_value = (123, b"GEOM", True)

    candidates = [
        (1, b"AAA", True),
        (2, b"BBB", False),
    ]

    with patch("data.src.overlap_calculator.psycopg2.extras.execute_values") as mock_ev:
        grid_cell_id, geom, bias = oc.find_closest_grid_cell("REGION", candidates)

    assert (grid_cell_id, geom, bias) == (123, b"GEOM", True)
    # execute_values was called with the candidate rows
    mock_ev.assert_called_once()
    assert mock_ev.call_args[0][2] == candidates
    # the final SELECT was called with the region_geom parameter
    args, _ = oc.cur.execute.call_args
    assert args[1] == ("REGION",)


# =============================================================================
# find_closest_cell (bbox expansion loop)
# =============================================================================

def test_find_closest_cell_expands_bbox_until_candidate_found(oc):
    # This test protects the while-loop behaviour (no infinite loop if a later iteration finds a cell)
    oc.get_region_geometry = MagicMock(return_value="REGION")

    # bbox expansion starts at 1.0; if no cell found, multiplies by 1.5 then tries again
    oc.get_bounding_box = MagicMock(side_effect=["BBOX_1", "BBOX_2"])
    oc.get_candidate_cells = MagicMock(side_effect=[[], [("id", "geom", True)]])
    oc.find_closest_grid_cell = MagicMock(side_effect=[(None, None, None), (999, b"G", False)])

    closest_id, bbox_expansion, bias = oc.find_closest_cell(gid=7)

    assert closest_id == 999
    assert bbox_expansion == 1.5  # expanded once
    assert bias is False

    oc.get_bounding_box.assert_has_calls([call("REGION", 1.0), call("REGION", 1.5)])


# =============================================================================
# process_no_overlap_regions
# =============================================================================

def test_process_no_overlap_regions_processes_each_gid(oc):
    oc.find_no_overlap_regions = MagicMock(return_value=[1, 2, 3])
    oc.find_closest_cell = MagicMock(return_value=(100, 1.5, True))
    oc.insert_closest_cell = MagicMock()

    oc.process_no_overlap_regions()

    assert oc.find_closest_cell.call_count == 3
    assert oc.insert_closest_cell.call_count == 3


def test_process_no_overlap_regions_skips_insert_when_no_closest_cell(oc):
    oc.find_no_overlap_regions = MagicMock(return_value=[1])
    oc.find_closest_cell = MagicMock(return_value=(None, 3.0, None))
    oc.insert_closest_cell = MagicMock()

    oc.process_no_overlap_regions()

    oc.insert_closest_cell.assert_not_called()


def test_process_no_overlap_regions_only_show_plots_calls_plotter(oc):
    oc.find_no_overlap_regions = MagicMock(return_value=[1])
    oc.find_closest_cell = MagicMock(return_value=(100, 2.0, True))
    oc.plot_region_and_candidates = MagicMock()
    oc.insert_closest_cell = MagicMock()

    oc.process_no_overlap_regions(only_show_plots=True)

    oc.plot_region_and_candidates.assert_called_once_with(1, scale_factor=2.0)
    oc.insert_closest_cell.assert_called_once()  # still inserts unless closest_id is falsy


# =============================================================================
# process_all_boundary_overlaps
# =============================================================================

@patch.object(OverlapCalculator, "process_no_overlap_regions")
@patch.object(OverlapCalculator, "insert_overlaps_optimised")
@patch.object(OverlapCalculator, "ensure_spatial_index")
@patch.object(OverlapCalculator, "create_overlap_table")
@patch.object(OverlapCalculator, "drop_table")
@patch.object(OverlapCalculator, "set_boundary_table")
def test_process_all_boundary_overlaps_calls_expected_steps_per_boundary(
    mock_set, mock_drop, mock_create, mock_index, mock_insert, mock_no_overlap, oc
):
    oc.process_all_boundary_overlaps(process_no_overlaps=False)

    # 8 boundaries
    assert mock_set.call_count == 8
    assert mock_drop.call_count == 8
    assert mock_create.call_count == 8
    assert mock_insert.call_count == 8

    # 2 indexes per boundary (grid + boundary)
    assert mock_index.call_count == 16

    # no-overlap processing off
    mock_no_overlap.assert_not_called()


@patch.object(OverlapCalculator, "process_no_overlap_regions")
@patch.object(OverlapCalculator, "insert_overlaps_optimised")
@patch.object(OverlapCalculator, "ensure_spatial_index")
@patch.object(OverlapCalculator, "create_overlap_table")
@patch.object(OverlapCalculator, "drop_table")
@patch.object(OverlapCalculator, "set_boundary_table")
def test_process_all_boundary_overlaps_processes_no_overlaps_when_requested(
    mock_set, mock_drop, mock_create, mock_index, mock_insert, mock_no_overlap, oc
):
    oc.process_all_boundary_overlaps(process_no_overlaps=True)
    assert mock_no_overlap.call_count == 8


# =============================================================================
# Query helper methods
# =============================================================================

def test_get_region_geometry_queries_by_gid(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_table_name = "boundary_uk_counties"
    oc.cur.fetchone.return_value = (b"geometry_data",)

    result = oc.get_region_geometry(42)

    assert result == b"geometry_data"
    _, params = oc.cur.execute.call_args[0]
    assert params == (42,)


@pytest.mark.parametrize(
    "boundary_identifier, expected_col",
    [
        ("uk_counties", "CTYUA23NM"),
        ("la_districts", "LAD23NM"),
        ("lsoa", "LSOA21NM"),
        ("msoa", "MSOA21NM"),
        ("parishes", "PAR23NM"),
        ("sc_dz", "Name"),
        ("ni_dz", "DZ2021_nm"),
        ("iom", "NAME_ENGLI"),
    ],
)
def test_get_region_name_uses_correct_column(oc, boundary_identifier, expected_col):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.boundary_identifier = boundary_identifier
    oc.boundary_table_name = f"boundary_{boundary_identifier}"
    oc.cur.fetchone.return_value = ("RegionName",)

    name = oc.get_region_name(1)

    sql = oc.cur.execute.call_args[0][0]
    assert expected_col in sql
    assert name == "RegionName"


def test_get_grid_cell_geometry_returns_geometry_or_none(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.grid_table_name = "chess_scape_grid"

    oc.cur.fetchone.return_value = (b"cell_geometry",)
    assert oc.get_grid_cell_geometry(123) == b"cell_geometry"

    oc.cur.fetchone.return_value = None
    assert oc.get_grid_cell_geometry(123) is None


def test_get_candidate_cells_returns_triplets(oc):
    oc.conn = MagicMock()
    oc.cur = MagicMock()
    oc.grid_table_name = "chess_scape_grid"
    oc.cur.fetchall.return_value = [(1, b"G1", True), (2, b"G2", False)]

    out = oc.get_candidate_cells("BBOX")

    assert out == [(1, b"G1", True), (2, b"G2", False)]
    sql = oc.cur.execute.call_args[0][0]
    assert "SELECT g.grid_cell_id, g.geometry, g.bias_corrected" in sql
    assert oc.cur.execute.call_args[0][1] == ("BBOX",)


# =============================================================================
# plot_region_and_candidates (contract test: should not crash with triplet candidates)
# =============================================================================

@patch.object(oc_module, "plot_geometry")
@patch.object(oc_module.plt, "show")
@patch.object(oc_module.plt, "subplots")
@patch.object(oc_module, "wkb")
def test_plot_region_and_candidates_smoke_does_not_crash(
    mock_wkb, mock_subplots, _mock_show, _mock_plot_geometry, oc
):
    # Minimal fake axis object with plot method
    fake_ax = MagicMock()
    mock_subplots.return_value = (MagicMock(), fake_ax)

    # Fake centroid.xy behaviour
    fake_geom = MagicMock()
    fake_geom.centroid.xy = ([0.0], [0.0])
    mock_wkb.loads.return_value = fake_geom

    oc.boundary_identifier = "uk_counties"
    oc.get_region_geometry = MagicMock(return_value=b"REGION_GEOM")
    oc.get_region_name = MagicMock(return_value="RegionName")
    oc.get_bounding_box = MagicMock(return_value=b"BBOX_GEOM")
    oc.get_candidate_cells = MagicMock(return_value=[(1, b"CELL_GEOM", True)])
    oc.find_closest_grid_cell = MagicMock(return_value=(1, b"CELL_GEOM", True))
    oc.get_grid_cell_geometry = MagicMock(return_value=b"CELL_GEOM")

    # The main point: this should run without unpacking errors
    oc.plot_region_and_candidates(gid=1, scale_factor=1.2)

    assert oc.get_candidate_cells.called
    assert oc.find_closest_grid_cell.called