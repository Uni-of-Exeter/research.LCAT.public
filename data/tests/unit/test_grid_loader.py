import os
from unittest.mock import MagicMock

import numpy as np
import pytest
import xarray as xr

from data.src.grid_loader import GridLoader
import data.src.grid_loader as grid_loader_module  # patch module-level xr used by GridLoader


# =============================================================================
# Fixtures / helpers
# =============================================================================

@pytest.fixture
def cfg():
    # minimal config required by GridLoader.__init__/set_data_location
    return {
        "chess_scape_netcdf_location": ".",
        # DB fields not needed for unit tests
    }


@pytest.fixture
def gl(cfg):
    loader = GridLoader(cfg)
    loader.data = {}
    loader.masks = {}
    loader.data_location = "/root"  # stable, but not important
    return loader


def _ds_from_values(var: str, values_3d: np.ndarray) -> xr.Dataset:
    """
    Convenience builder for tiny netcdf-like datasets:
    values_3d shape: (time, y, x)
    """
    da = xr.DataArray(values_3d, dims=("time", "y", "x"))
    return xr.Dataset({var: da})


# =============================================================================
# set_data_location
# =============================================================================

def test_set_data_location_defaults_to_config(cfg):
    loader = GridLoader(cfg)
    assert loader.data_location == cfg["chess_scape_netcdf_location"]


def test_set_data_location_accepts_override(gl):
    gl.set_data_location("/tmp/somewhere")
    assert gl.data_location == "/tmp/somewhere"


# =============================================================================
# open_netcdf_file / open_netcdf_files
# =============================================================================

def test_open_netcdf_file_calls_xarray_open_dataset(monkeypatch, gl):
    fake_ds = MagicMock()
    fake_ds.y.size = 10
    fake_ds.x.size = 20
    fake_ds.time.size = 30

    fake_xr = MagicMock()
    fake_xr.open_dataset.return_value = fake_ds
    monkeypatch.setattr(grid_loader_module, "xr", fake_xr)

    out = gl.open_netcdf_file("/some/file.nc")
    fake_xr.open_dataset.assert_called_once_with("/some/file.nc", engine="netcdf4")
    assert out is fake_ds


def test_open_netcdf_file_raises_on_error(monkeypatch, gl):
    fake_xr = MagicMock()
    fake_xr.open_dataset.side_effect = FileNotFoundError("nope")
    monkeypatch.setattr(grid_loader_module, "xr", fake_xr)

    with pytest.raises(RuntimeError, match="netcdf file open failed"):
        gl.open_netcdf_file("/missing/file.nc")


def test_open_netcdf_files_uses_provided_paths_and_sets_state(gl):
    gl.open_netcdf_file = MagicMock(side_effect=["BIAS_DS", "NONBIAS_DS"])

    gl.open_netcdf_files(
        filepath_bias_corrected="/a/bias.nc",
        filepath_non_bias_corrected="/b/nonbias.nc",
        variable="tas",
    )

    gl.open_netcdf_file.assert_any_call("/a/bias.nc")
    gl.open_netcdf_file.assert_any_call("/b/nonbias.nc")
    assert gl.data["bias_corrected"] == "BIAS_DS"
    assert gl.data["non_bias_corrected"] == "NONBIAS_DS"
    assert gl.variable == "tas"


def test_open_netcdf_files_defaults_build_paths_and_sets_variable(gl):
    gl.open_netcdf_file = MagicMock(side_effect=["BIAS_DS", "NONBIAS_DS"])

    gl.open_netcdf_files()

    assert gl.variable == "tas"
    assert gl.data["bias_corrected"] == "BIAS_DS"
    assert gl.data["non_bias_corrected"] == "NONBIAS_DS"

    bias_path = gl.open_netcdf_file.call_args_list[0].args[0]
    nonbias_path = gl.open_netcdf_file.call_args_list[1].args[0]

    assert bias_path.startswith(gl.data_location)
    assert nonbias_path.startswith(gl.data_location)
    assert "rcp60_bias-corrected" in bias_path
    assert "rcp60_bias-corrected" not in nonbias_path


# =============================================================================
# create_polygon_mask
# =============================================================================

@pytest.mark.parametrize(
    "polygon_vertices, inside_points, outside_points",
    [
        ([(1, 1), (3, 1), (3, 3), (1, 3)], [(2, 2)], [(0, 0), (4, 4)]),
        ([(0.5, 0.5), (3.5, 0.5), (3.5, 3.5), (0.5, 3.5)], [(2, 2), (1, 2), (2, 1)], [(0, 0), (4, 4)]),
        ([(2, 0), (4, 2), (2, 4), (0, 2)], [(2, 2), (2, 3)], [(0, 0), (4, 0), (0, 4)]),
    ],
)
def test_create_polygon_mask_marks_inside_and_outside(gl, polygon_vertices, inside_points, outside_points):
    y_size, x_size = 5, 5
    mask = gl.create_polygon_mask(polygon_vertices, y_size, x_size)

    assert mask.shape == (y_size, x_size)
    assert mask.dtype == bool

    for (y, x) in inside_points:
        assert mask[y, x], f"Expected {(y, x)} to be inside"

    for (y, x) in outside_points:
        assert not mask[y, x], f"Expected {(y, x)} to be outside"


# =============================================================================
# get_mask
# =============================================================================

def test_get_mask_bias_corrected_returns_non_nan_mask(gl):
    gl.variable = "tas"
    ds = _ds_from_values(
        "tas",
        np.array([[[1.0, np.nan],
                   [np.nan, 2.0]]]),
    )
    gl.data["bias_corrected"] = ds

    mask = gl.get_mask("bias_corrected")
    expected = ~ds["tas"][0].isnull().values

    assert mask.shape == (2, 2)
    assert np.array_equal(mask, expected)


def test_get_mask_non_bias_corrected_intersects_dirty_mask_with_polygons(gl):
    gl.variable = "tas"
    ds = _ds_from_values(
        "tas",
        np.array([[[1.0, np.nan, 1.0],
                   [np.nan, 1.0, np.nan],
                   [1.0, np.nan, 1.0]]]),
    )
    gl.data["non_bias_corrected"] = ds
    dirty_mask = ~ds["tas"][0].isnull().values

    mask_ni = np.array(
        [[True,  False, False],
         [False, True,  False],
         [False, False, False]],
        dtype=bool,
    )
    mask_scilly = np.array(
        [[False, False, False],
         [False, False, True],
         [False, False, False]],
        dtype=bool,
    )

    # create_polygon_mask is called twice: NI then Scilly
    masks_iter = iter([mask_ni, mask_scilly])
    gl.create_polygon_mask = lambda vertices, y_size, x_size: next(masks_iter)

    out = gl.get_mask("non_bias_corrected")
    expected = dirty_mask & (mask_ni | mask_scilly)

    assert out.shape == (3, 3)
    assert np.array_equal(out, expected)


# =============================================================================
# cache_masks / aggregate_cached_masks / create_aggregated_labelled_mask
# =============================================================================

def test_cache_masks_raises_if_data_not_loaded(gl):
    gl.data = {"bias_corrected": "only_one"}
    with pytest.raises(ValueError, match="netcdf data not loaded"):
        gl.cache_masks()


def test_cache_masks_populates_masks_for_both_keys(gl):
    gl.data = {"bias_corrected": "DS1", "non_bias_corrected": "DS2"}
    gl.get_mask = MagicMock(side_effect=[np.ones((2, 2), dtype=bool), np.zeros((2, 2), dtype=bool)])

    gl.cache_masks()

    assert "bias_corrected" in gl.masks
    assert "non_bias_corrected" in gl.masks
    assert gl.get_mask.call_count == 2


def test_aggregate_cached_masks_requires_both_masks(gl):
    gl.masks = {"bias_corrected": np.ones((2, 2), dtype=bool)}
    with pytest.raises(ValueError, match="masks not cached"):
        gl.aggregate_cached_masks()


def test_aggregate_cached_masks_adds_boolean_masks_as_ints(gl):
    gl.masks["bias_corrected"] = np.array([[True, False], [False, True]])
    gl.masks["non_bias_corrected"] = np.array([[False, True], [False, True]])

    gl.aggregate_cached_masks()

    expected = gl.masks["bias_corrected"] | gl.masks["non_bias_corrected"]
    assert gl.masks["aggregated"].dtype == bool
    assert np.array_equal(gl.masks["aggregated"], expected)


def test_create_aggregated_labelled_mask_encodes_bias_1_nonbias_2(gl):
    gl.masks["bias_corrected"] = np.array([[True, False], [False, True]])
    gl.masks["non_bias_corrected"] = np.array([[False, True], [False, True]])

    gl.create_aggregated_labelled_mask()

    expected = np.array([[1, 2], [0, 3]])
    assert np.array_equal(gl.masks["aggregated_labelled"], expected)


# =============================================================================
# _create_filled_land_mask
# =============================================================================

# These masks are designed so the "ocean" (False) component is huge,
# and internal "lakes" (False holes inside True land) are small components.
SMALL_LAKE_MASK = np.array(
    [
        [False, False, False, False, False],
        [False,  True,  True,  True, False],
        [False,  True, False,  True, False],  # 1-cell lake at (2,2)
        [False,  True,  True,  True, False],
        [False, False, False, False, False],
    ],
    dtype=bool,
)

EXPECTED_SMALL_LAKE_FILLED = np.array(
    [
        [False, False, False, False, False],
        [False,  True,  True,  True, False],
        [False,  True,  True,  True, False],
        [False,  True,  True,  True, False],
        [False, False, False, False, False],
    ],
    dtype=bool,
)

BIG_LAKE_MASK = np.array(
    [
        [False, False, False, False, False, False],
        [False,  True,  True,  True,  True, False],
        [False,  True, False, False,  True, False],  # 4-cell lake (2x2) in middle
        [False,  True, False, False,  True, False],
        [False,  True,  True,  True,  True, False],
        [False, False, False, False, False, False],
    ],
    dtype=bool,
)

EXPECTED_BIG_LAKE_FILLED = np.array(
    [
        [False, False, False, False, False, False],
        [False,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True, False],
        [False, False, False, False, False, False],
    ],
    dtype=bool,
)

EXPECTED_BIG_LAKE_UNCHANGED = BIG_LAKE_MASK.copy()


@pytest.mark.parametrize(
    "land_mask, size_threshold, expected",
    [
        (SMALL_LAKE_MASK, 5, EXPECTED_SMALL_LAKE_FILLED),
        (BIG_LAKE_MASK, 3, EXPECTED_BIG_LAKE_UNCHANGED),
        (BIG_LAKE_MASK, 10, EXPECTED_BIG_LAKE_FILLED),
    ],
)
def test__create_filled_land_mask_fills_only_small_holes(gl, land_mask, size_threshold, expected):
    filled = gl._create_filled_land_mask(land_mask, size_threshold=size_threshold)
    assert filled.shape == land_mask.shape
    assert filled.dtype == bool
    np.testing.assert_array_equal(filled, expected)


# =============================================================================
# create_coastline_mask
# =============================================================================

@pytest.mark.parametrize(
    "aggregated_labelled, expected_coastline",
    [
        (
            np.array(
                [
                    [0, 0, 0, 0, 0],
                    [0, 1, 1, 1, 0],
                    [0, 1, 1, 1, 0],
                    [0, 1, 1, 1, 0],
                    [0, 0, 0, 0, 0],
                ],
                dtype=int,
            ),
            np.array(
                [
                    [False, False, False, False, False],
                    [False,  True,  True,  True, False],
                    [False,  True, False,  True, False],
                    [False,  True,  True,  True, False],
                    [False, False, False, False, False],
                ],
                dtype=bool,
            ),
        ),
        (
            np.array(
                [
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 0, 0],
                    [1, 1, 1, 1, 1],
                    [0, 0, 1, 0, 0],
                    [0, 0, 1, 0, 0],
                ],
                dtype=int,
            ),
            np.array(
                [
                    [False, False,  True, False, False],
                    [False, False,  True, False, False],
                    [ True,  True,  True,  True,  True],
                    [False, False,  True, False, False],
                    [False, False,  True, False, False],
                ],
                dtype=bool,
            ),
        ),
        (
            np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=int),
            np.array([[False, False, False], [False, True, False], [False, False, False]], dtype=bool),
        ),
    ],
)
def test_create_coastline_mask_expected_patterns(gl, aggregated_labelled, expected_coastline):
    gl.masks["aggregated_labelled"] = aggregated_labelled

    # prevent lake filling from changing synthetic patterns
    gl._create_filled_land_mask = lambda land_mask: land_mask

    gl.create_coastline_mask()
    coastline = gl.masks["coastline"]
    land = aggregated_labelled.astype(bool)

    assert coastline.dtype == bool
    assert coastline.shape == aggregated_labelled.shape
    assert np.all(coastline <= land)  # coastline must be subset of land
    np.testing.assert_array_equal(coastline, expected_coastline)


# =============================================================================
# create_inland_mask
# =============================================================================

@pytest.mark.parametrize(
    "land_mask, radius, expected",
    [
        (
            np.array(
                [
                    [False, False, False, False, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False, False, False, False, False],
                ],
                dtype=bool,
            ),
            0,
            np.zeros((5, 5), dtype=bool),
        ),
        (
            np.array(
                [
                    [False, False, False, False, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False, False, False, False, False],
                ],
                dtype=bool,
            ),
            1,
            np.array(
                [
                    [False, False, False, False, False],
                    [False,  True,  True,  True, False],
                    [False,  True, False,  True, False],
                    [False,  True,  True,  True, False],
                    [False, False, False, False, False],
                ],
                dtype=bool,
            ),
        ),
        (
            np.array(
                [
                    [False, False, False, False, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False, False, False, False, False],
                ],
                dtype=bool,
            ),
            2,
            np.array(
                [
                    [False, False, False, False, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False,  True,  True,  True, False],
                    [False, False, False, False, False],
                ],
                dtype=bool,
            ),
        ),
    ],
)
def test_create_inland_mask_various_radii(gl, land_mask, radius, expected):
    filled = land_mask.copy()
    out = gl.create_inland_mask(land_mask=land_mask, filled_land_mask=filled, radius=radius)

    assert out.shape == land_mask.shape
    assert out.dtype == bool
    np.testing.assert_array_equal(out, expected)


# =============================================================================
# create_coastal_mask_with_inland_regions
# =============================================================================

@pytest.mark.parametrize(
    "aggregated_labelled, coastline_mask, inland_bands, expected",
    [
        (
            np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=int),
            np.array([[False, True, False], [True, False, True], [False, True, False]], dtype=bool),
            {10: np.array([[False, False, False], [False, True, False], [False, False, False]], dtype=bool)},
            np.array([[0, 1, 0], [1, 10, 1], [0, 1, 0]], dtype=int),
        ),
        (
            np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=int),
            np.zeros((3, 3), dtype=bool),
            {10: np.array([[False, False, False], [False, True, False], [False, False, False]], dtype=bool)},
            np.array([[2, 2, 2], [2, 10, 2], [2, 2, 2]], dtype=int),
        ),
        (
            np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=int),
            np.array([[True, True, True], [True, False, True], [True, True, True]], dtype=bool),
            {
                10: np.array([[False, True, False], [True, False, True], [False, True, False]], dtype=bool),
                20: np.array([[False, False, False], [False, True, False], [False, False, False]], dtype=bool),
            },
            np.array([[1, 1, 1], [1, 20, 1], [1, 1, 1]], dtype=int),
        ),
    ],
)
def test_create_coastal_mask_with_inland_regions(gl, aggregated_labelled, coastline_mask, inland_bands, expected):
    gl.masks["aggregated_labelled"] = aggregated_labelled
    gl.masks["coastline"] = coastline_mask

    def fake_create_inland_mask(land_mask, filled_land_mask, radius):
        return inland_bands.get(radius, np.zeros_like(land_mask, dtype=bool))

    gl.create_inland_mask = fake_create_inland_mask

    gl.create_coastal_mask_with_inland_regions()
    final = gl.masks["final_coastal_mask"]

    assert final.shape == aggregated_labelled.shape
    np.testing.assert_array_equal(final, expected)

    assert gl.coastal_map[0] == "ocean"
    assert gl.coastal_map[1] == "coastline"
    assert gl.coastal_map[2] == "land"
    assert gl.coastal_map[10] == "10km from coast"
    assert gl.coastal_map[20] == "20km from coast"


# =============================================================================
# create_grid_data_rows
# =============================================================================

def test_create_grid_data_rows_raises_on_shape_mismatch(gl):
    # minimal bias_corrected ds just for x/y vectors
    gl.data["bias_corrected"] = xr.Dataset(
        {
            "x": xr.DataArray(np.array([0.0, 1.0]), dims=("x",)),
            "y": xr.DataArray(np.array([0.0, 1.0]), dims=("y",)),
        }
    )

    gl.masks["aggregated_labelled"] = np.ones((2, 2), dtype=int)
    gl.masks["final_coastal_mask"] = np.ones((3, 3), dtype=int)  # mismatch
    gl.coastal_map = {1: "coastline"}

    with pytest.raises(ValueError, match="Shape mismatch"):
        gl.create_grid_data_rows()


def test_create_grid_data_rows_skips_zeros_and_builds_rows(gl):
    # Build x/y vectors (2x2 grid -> edges must be length 3)
    gl.data["bias_corrected"] = xr.Dataset(
        {
            "x": xr.DataArray(np.array([1000.0, 2000.0]), dims=("x",)),
            "y": xr.DataArray(np.array([3000.0, 4000.0]), dims=("y",)),
        }
    )

    # One data cell at (0,0) bias-corrected label=1, one at (1,1) non-bias label=2
    gl.masks["aggregated_labelled"] = np.array([[1, 0], [0, 2]], dtype=int)
    gl.masks["final_coastal_mask"] = np.array([[10, 0], [0, 20]], dtype=int)
    gl.coastal_map = {0: "ocean", 10: "10km from coast", 20: "20km from coast"}

    rows = gl.create_grid_data_rows()

    # should only create rows for 2 non-zero cells
    assert len(rows) == 2

    # row format: (grid_cell_id, poly.wkt, tag, coastal_label)
    ids = [r[0] for r in rows]
    assert set(ids) == {0, 3}  # (0,0)->0 ; (1,1)-> 1*2 + 1 = 3

    tags = {r[0]: r[2] for r in rows}
    assert tags[0] == "TRUE"   # mask==1
    assert tags[3] == "FALSE"  # mask==2

    coastal = {r[0]: r[3] for r in rows}
    assert coastal[0] == "10km from coast"
    assert coastal[3] == "20km from coast"