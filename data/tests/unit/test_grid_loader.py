import pytest
from unittest.mock import MagicMock
import os
import numpy as np
import xarray as xr
import conftest
from data.src.grid_loader import GridLoader
import data.src.grid_loader as grid_loader_module  # <- patch xr here (module-level)

# =============================================================================
# create fixtures
# =============================================================================

@pytest.fixture
def cfg():
    """A minimal config dictionary so GridLoader can construct."""
    return {"chess_scape_netcdf_location": "."}


@pytest.fixture
def gl(cfg):
    """
    A fresh GridLoader instance for each test.
    Its DB connection is NOT used in unit tests.
    """
    loader = GridLoader(cfg)
    loader.data = {}   # wipe any real data
    loader.masks = {}  # wipe any previous masks
    loader.data_location = "/root"
    return loader


def test_fixture_sanity(gl):
    assert isinstance(gl, GridLoader)
    assert gl.data == {}
    assert gl.masks == {}

# =============================================================================
# netcdf functions
# =============================================================================


def test_open_netcdf_file_calls_xarray_open_dataset(monkeypatch, gl):
    fake_ds = MagicMock()
    fake_ds.y.size = 10
    fake_ds.x.size = 20
    fake_ds.time.size = 30

    fake_xr = MagicMock()
    fake_xr.open_dataset.return_value = fake_ds

    # Patch the module-global `xr` used by GridLoader.open_netcdf_file
    monkeypatch.setattr(grid_loader_module, "xr", fake_xr)

    out = gl.open_netcdf_file("/some/file.nc")

    fake_xr.open_dataset.assert_called_once_with("/some/file.nc", engine="netcdf4")
    assert out is fake_ds


def test_open_netcdf_file_returns_none_on_error(monkeypatch, gl):
    fake_xr = MagicMock()
    fake_xr.open_dataset.side_effect = FileNotFoundError("nope")

    # Patch the module-global `xr` used by GridLoader.open_netcdf_file
    monkeypatch.setattr(grid_loader_module, "xr", fake_xr)

    out = gl.open_netcdf_file("/missing/file.nc")

    # This assumes open_netcdf_file returns None on error.
    # If your implementation currently raises or hits UnboundLocalError,
    # fix open_netcdf_file by initialising data=None before try.
    assert out is None


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

    # ACT: call the method to trigger defaults
    gl.open_netcdf_files()

    # ASSERT: state set
    assert gl.variable == "tas"
    assert gl.data["bias_corrected"] == "BIAS_DS"
    assert gl.data["non_bias_corrected"] == "NONBIAS_DS"

    # ASSERT: paths built correctly
    bias_path = gl.open_netcdf_file.call_args_list[0].args[0]
    nonbias_path = gl.open_netcdf_file.call_args_list[1].args[0]

    # Don't require "/root/" specifically (join may produce "/rootdata" if mis-set etc.)
    assert bias_path.startswith(gl.data_location)
    assert nonbias_path.startswith(gl.data_location)

    assert "rcp60_bias-corrected" in bias_path
    assert "rcp60_bias-corrected" not in nonbias_path

    assert bias_path.endswith(
        os.path.join(
            "data",
            "rcp60_bias-corrected",
            "01",
            "annual",
            "chess-scape_rcp60_bias-corrected_01_tas_uk_1km_annual_19801201-20801130.nc",
        )
    )
    assert nonbias_path.endswith(
        os.path.join(
            "data",
            "rcp60",
            "01",
            "annual",
            "chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc",
        )
    )
# =============================================================================
# cached masks
# =============================================================================

def test_aggregate_cached_masks(gl):
    """
    GridLoader.aggregate_cached_masks should add boolean masks together.
    True becomes 1, False becomes 0.
    Then it produces a matrix of integers representing the sum.
    """
    # Create 2 simple fake masks
    gl.masks["bias_corrected"] = np.array([
        [True, False],
        [False, True]
    ])

    gl.masks["non_bias_corrected"] = np.array([
        [False, True],
        [False, True]
    ])

    gl.aggregate_cached_masks()

    # Expected:
    # [[1,1],
    #  [0,1]]
    expected = np.array([
        [1, 1],
        [0, 1]
    ])

    assert np.array_equal(gl.masks["aggregated"], expected)

def test_create_aggregated_labelled_mask(gl):
    """
    GridLoader.create_aggregated_labelled_mask should combine the
    existing boolean masks for bias_corrected and non_bias_corrected
    into a single integer-labelled mask.

    bias_corrected      → label 1
    non_bias_corrected  → label 2
    both True           → label 3 (1 + 2)
    neither             → label 0
    """
    # Fake tiny masks
    gl.masks["bias_corrected"] = np.array([
        [True,  False],
        [False, True]
    ])

    gl.masks["non_bias_corrected"] = np.array([
        [False, True],
        [False, True]
    ])

    # Run the method
    gl.create_aggregated_labelled_mask()

    # Expected output:
    expected = np.array([
        [1, 2],  # (True, False)  and (False, True)
        [0, 3],  # (False, False) and (True, True)
    ])
    assert np.array_equal(gl.masks["aggregated_labelled"], expected)

# =============================================================================
# get_masks
# =============================================================================


def test_get_mask_bias_corrected(gl):
    """
    GridLoader.get_mask('bias_corrected') should return a boolean mask showing
    where the chosen variable is not NaN in the first time slice.
    """
    gl.variable = "tas"

    # Tiny fake data: shape (time=1, y=2, x=2)
    da = xr.DataArray(
        [[[1.0, np.nan],
          [np.nan, 2.0]]],
        dims=("time", "y", "x"),
    )
    ds = xr.Dataset({"tas": da})

    gl.data["bias_corrected"] = ds

    mask = gl.get_mask("bias_corrected")

    # Expected: True where tas is not NaN in time slice 0
    expected = ~da.isnull().values[0]

    assert mask.shape == (2, 2)
    assert np.array_equal(mask, expected)

def test_get_mask_non_bias_corrected_uses_dirty_mask_and_polygon(gl):
    """
    GridLoader.get_mask('non_bias_corrected') should return the intersection of:
    - where data is not NaN (dirty_mask), and
    - the combined polygon mask (NI ∪ Scilly Isles).
    """
    gl.variable = "tas"

    # Tiny fake data: shape (time=1, y=3, x=3)
    da = xr.DataArray(
        [[[1.0,    np.nan, 1.0],
          [np.nan, 1.0,    np.nan],
          [1.0,    np.nan, 1.0]]],
        dims=("time", "y", "x"),
    )
    ds = xr.Dataset({"tas": da})
    gl.data["non_bias_corrected"] = ds

    dirty_mask = ~da.isnull().values[0]

    # Define two fake polygon masks
    mask_ni = np.array([
        [True,  False, False],
        [False, True,  False],
        [False, False, False],
    ])

    mask_scilly = np.array([
        [False, False, False],
        [False, False, True],
        [False, False, False],
    ])

    # Stub create_polygon_mask so the first call returns mask_ni
    # and the second call returns mask_scilly
    masks_iter = iter([mask_ni, mask_scilly])

    def fake_create_polygon_mask(vertices, y_size, x_size):
        return next(masks_iter)

    gl.create_polygon_mask = fake_create_polygon_mask

    mask = gl.get_mask("non_bias_corrected")

    expected = dirty_mask & (mask_ni | mask_scilly)

    assert mask.shape == (3, 3)
    assert np.array_equal(mask, expected)

# =============================================================================
# create_polygon_masks
# =============================================================================

@pytest.mark.parametrize(
    "polygon_vertices, inside_points, outside_points",
    [
        # Central square: (1,1)-(3,1)-(3,3)-(1,3)
        (
            [(1, 1), (3, 1), (3, 3), (1, 3)],
            # points comfortably inside the square
            [(2, 2)],
            # clearly outside
            [(0, 0), (4, 4)],
        ),
        # Slightly smaller full-ish square in the middle
        (
            [(0.5, 0.5), (3.5, 0.5), (3.5, 3.5), (0.5, 3.5)],
            [(2, 2), (1, 2), (2, 1)],   # inside-ish points
            [(0, 0), (4, 4)],           # definitely outside
        ),
        # Diamond shape
        (
            [(2, 0), (4, 2), (2, 4), (0, 2)],
            [(2, 2), (2, 3)],           # safely inside
            [(0, 0), (4, 0), (0, 4)],   # clearly outside corners
        ),
    ],
)
def test_create_polygon_mask_variants(gl, polygon_vertices, inside_points, outside_points):
    """
    Test that create_polygon_mask correctly marks points inside a given
    polygon as True and points clearly outside the polygon as False.

    Rather than asserting an entire mask (which can be sensitive to the
    underlying point-in-polygon boundary rules), this test checks that:
      - all provided inside_points evaluate to True,
      - all provided outside_points evaluate to False.

    This verifies the intended behaviour without depending on the precise
    boundary semantics of Path.contains_points.
    """
    y_size, x_size = 5, 5

    mask = gl.create_polygon_mask(polygon_vertices, y_size, x_size)

    assert mask.shape == (y_size, x_size)
    assert mask.dtype == bool

    # Points we believe are clearly inside should be True
    for (y, x) in inside_points:
        assert mask[y, x], f"Expected inside point {(y,x)} to be True"

    # Points we believe are clearly outside should be False
    for (y, x) in outside_points:
        assert not mask[y, x], f"Expected outside point {(y,x)} to be False"

# =============================================================================
# _create_filled_land_masks
# =============================================================================

@pytest.mark.parametrize(
    "land_mask, size_threshold, expected",
    [
        # 1-cell lake; threshold enough to fill that lake, smaller than big ocean component
        (conftest.SMALL_LAKE_MASK, 5, conftest.EXPECTED_SMALL_LAKE_FILLED),

        # 4-cell lake; threshold too small → nothing filled
        (conftest.BIG_LAKE_MASK, 3, conftest.EXPECTED_BIG_LAKE_UNCHANGED),

        # 4-cell lake; threshold big enough to fill the lake, still smaller than ocean
        (conftest.BIG_LAKE_MASK, 10, conftest.EXPECTED_BIG_LAKE_FILLED),
    ],
)
def test__create_filled_land_mask_handles_lakes(gl, land_mask, size_threshold, expected):
    """
    Verify that _create_filled_land_mask returns a boolean mask identical
    in shape to the input and fills only the lake regions that fall under
    the specified size_threshold.

    This directly asserts equality against an explicitly provided expected
    mask, ensuring deterministic behaviour for various lake sizes.
    """
    filled = gl._create_filled_land_mask(land_mask, size_threshold=size_threshold)

    assert filled.shape == land_mask.shape
    assert filled.dtype == bool

    # Direct comparison with explicit expected mask
    np.testing.assert_array_equal(filled, expected)

# =============================================================================
# create_coastline_mask
# =============================================================================

@pytest.mark.parametrize(
    "aggregated_labelled, expected_coastline",
    [
        # Case 1: 5x5 island with 3x3 solid land block in the middle
        (
            np.array([
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
            ], dtype=int),
            np.array([
                [False, False, False, False, False],
                [False,  True,  True,  True, False],
                [False,  True, False,  True, False],
                [False,  True,  True,  True, False],
                [False, False, False, False, False],
            ], dtype=bool),
        ),

        # Case 2: plus-shaped island – every land cell touches ocean,
        # so all land cells should be coastline.
        (
            np.array([
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
                [1, 1, 1, 1, 1],
                [0, 0, 1, 0, 0],
                [0, 0, 1, 0, 0],
            ], dtype=int),
            np.array([
                [False, False,  True, False, False],
                [False, False,  True, False, False],
                [ True,  True,  True,  True,  True],
                [False, False,  True, False, False],
                [False, False,  True, False, False],
            ], dtype=bool),
        ),

        # Case 3: tiny 3x3 grid with a single land cell in the centre.
        # That lone land cell is coastline (has some but not all land neighbours:
        # it has only itself).
        (
            np.array([
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0],
            ], dtype=int),
            np.array([
                [False, False, False],
                [False,  True, False],
                [False, False, False],
            ], dtype=bool),
        ),
    

    ],
)
def test_create_coastline_mask_parametrised(gl, aggregated_labelled, expected_coastline):
    """
    GridLoader.create_coastline_mask should mark as coastline any land cell
    that has some, but not all, land neighbours in its 3x3 neighbourhood.
    """

    gl.masks["aggregated_labelled"] = aggregated_labelled

    # For these synthetic tests, we don't want lake-filling to interfere,
    # so stub _create_filled_land_mask to be the identity function.
    def fake_filled_land_mask(land_mask):
        return land_mask

    gl._create_filled_land_mask = fake_filled_land_mask

    # Run the method under test
    gl.create_coastline_mask()
    coastline = gl.masks["coastline"]

    land_mask = aggregated_labelled.astype(bool)

    # Basic invariants
    assert coastline.shape == aggregated_labelled.shape
    assert coastline.dtype == bool

    # Coastline must always be a subset of land
    assert np.all(coastline <= land_mask)

    # Exact expected patterns for these synthetic grids
    np.testing.assert_array_equal(coastline, expected_coastline)

# =============================================================================
# create_inland_mask
# =============================================================================

@pytest.mark.parametrize(
    "land_mask, radius, expected",
    [
        # ---------------------------------------------------------------
        # CASE 1: radius = 0 → structuring element is a single pixel.
        # Erosion with a 1-pixel element leaves the land mask unchanged,
        # so inland_mask = land & ~eroded = land & ~land = all False.
        # This exercises the "no erosion" pathway.
        # ---------------------------------------------------------------
        (
            np.array([
                [False, False, False, False, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False, False, False, False, False],
            ], dtype=bool),
            0,
            np.array([
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
                [False, False, False, False, False],
            ], dtype=bool),
        ),

        # ---------------------------------------------------------------
        # CASE 2: radius = 1 on the same 3×3 "island" in the middle.
        #
        # The circular structuring element erodes away the central cell
        # (which has enough land neighbours), leaving a hollow 3×3 ring.
        # inland_mask = original land minus eroded land → the outer ring
        # becomes "inland band".
        #
        # This exercises the "partial erosion" / coastal-band behaviour.
        # ---------------------------------------------------------------
        (
            np.array([
                [False, False, False, False, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False, False, False, False, False],
            ], dtype=bool),
            1,
            np.array([
                [False, False, False, False, False],
                [False,  True,  True,  True, False],
                [False,  True, False,  True, False],
                [False,  True,  True,  True, False],
                [False, False, False, False, False],
            ], dtype=bool),
        ),

        # CASE 3: radius 2 → full erosion → whole island becomes inland
        (
            np.array([
                [False, False, False, False, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False, False, False, False, False],
            ], dtype=bool),
            2,
            np.array([
                [False, False, False, False, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False,  True,  True,  True, False],
                [False, False, False, False, False],
            ], dtype=bool),
        ),
    ],
)
def test_create_inland_mask_various_shapes(gl, land_mask, radius, expected):
    """
    GridLoader.create_inland_mask should correctly identify "inland band"
    cells as those land cells that are lost under binary erosion with a
    circular structuring element of the given radius.
    """
    filled_land_mask = land_mask.copy()

    inland = gl.create_inland_mask(
        land_mask=land_mask,
        filled_land_mask=filled_land_mask,
        radius=radius,
    )

    assert inland.shape == land_mask.shape
    assert inland.dtype == bool
    np.testing.assert_array_equal(inland, expected)

# =============================================================================
# create_coastal_mask
# =============================================================================

@pytest.mark.parametrize(
    "aggregated_labelled, coastline_mask, inland_bands, expected",
    [
        # Case 1: plus-shaped land with coastline on the "arms"
        # and a 10km inland band at the centre only.
        #
        #   O L O
        #   L L L
        #   O L O
        #
        (
            np.array([
                [0, 1, 0],
                [1, 1, 1],
                [0, 1, 0],
            ], dtype=int),
            np.array([
                [False, True,  False],
                [True,  False, True ],
                [False, True,  False],
            ], dtype=bool),
            {
                10: np.array([
                    [False, False, False],
                    [False, True,  False],
                    [False, False, False],
                ], dtype=bool),
                # other radii → no inland band
            },
            np.array([
                [0, 1, 0],
                [1, 10, 1],
                [0, 1, 0],
            ], dtype=int),
        ),

        # Case 2: solid 3×3 land block with only the centre in the 10km band
        # and no coastline at all.
        #
        #   L L L
        #   L L L
        #   L L L
        #
        # Expectation:
        # - corners and edges remain plain land (2)
        # - centre cell is 10
        # - no coastline cells (no 1s)
        (
            np.array([
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
            ], dtype=int),
            np.array([
                [False, False, False],
                [False, False, False],
                [False, False, False],
            ], dtype=bool),
            {
                10: np.array([
                    [False, False, False],
                    [False, True,  False],
                    [False, False, False],
                ], dtype=bool),
            },
            np.array([
                [2, 2, 2],
                [2, 10, 2],
                [2, 2, 2],
            ], dtype=int),
        ),

        # Case 3: solid 3×3 land block with coastline on the outer ring
        # and both 10km and 20km inland bands defined.
        #
        #   L L L
        #   L L L
        #   L L L
        #
        # coastline_mask: outer ring
        # inland_10:      cross (non-corner arms)
        # inland_20:      centre cell
        #
        # Because create_coastal_mask_with_inland_regions:
        #   - sets land=2,
        #   - then 20, then 10,
        #   - then coastline (1) last,
        # the final result is:
        #   - outer ring = 1 (coastline overrides land/bands)
        #   - centre     = 20 (only in 20km band)
        (
            np.array([
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
            ], dtype=int),
            np.array([
                [True,  True,  True],
                [True,  False, True],
                [True,  True,  True],
            ], dtype=bool),
            {
                10: np.array([
                    [False, True,  False],
                    [True,  False, True ],
                    [False, True,  False],
                ], dtype=bool),
                20: np.array([
                    [False, False, False],
                    [False, True,  False],
                    [False, False, False],
                ], dtype=bool),
            },
            np.array([
                [1, 1, 1],
                [1, 20, 1],
                [1, 1, 1],
            ], dtype=int),
        ),
    ],
)
def test_create_coastal_mask_with_inland_regions(gl, aggregated_labelled, coastline_mask, inland_bands, expected):
    """
    GridLoader.create_coastal_mask_with_inland_regions should combine:
    - the land mask (aggregated_labelled > 0),
    - inland distance bands (via create_inland_mask),
    - and the coastline mask,
    into a single integer mask using the documented codes:
        0 = ocean, 1 = coastline, 2 = land,
        10/20/30/40/50 = 10/20/... km from coast.
    """
    gl.masks["aggregated_labelled"] = aggregated_labelled
    gl.masks["coastline"] = coastline_mask

    def fake_create_inland_mask(land, filled, radius):
        # Use the provided inland mask for this radius if present,
        # otherwise no inland band for that radius.
        return inland_bands.get(radius, np.zeros_like(land, dtype=bool))

    gl.create_inland_mask = fake_create_inland_mask

    gl.create_coastal_mask_with_inland_regions()
    final = gl.masks["final_coastal_mask"]

    assert final.shape == aggregated_labelled.shape
    np.testing.assert_array_equal(final, expected)

    # Basic sanity on coastal_map
    assert gl.coastal_map[0] == "ocean"
    assert gl.coastal_map[1] == "coastline"
    assert gl.coastal_map[2] == "land"
    assert gl.coastal_map[10] == "10km from coast"
    assert gl.coastal_map[20] == "20km from coast"
