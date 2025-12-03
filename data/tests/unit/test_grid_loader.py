import pytest
import numpy as np
import xarray as xr
from data.src.grid_loader import GridLoader
from conftest import *

@pytest.fixture
def cfg():
    """
    A minimal config dictionary so GridLoader can construct.
    """
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
    return loader

def test_fixture_sanity(gl):
    assert isinstance(gl, GridLoader)
    assert gl.data == {}
    assert gl.masks == {}

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

@pytest.mark.parametrize(
    "land_mask, size_threshold, expected",
    [
        # 1-cell lake; threshold enough to fill that lake, smaller than big ocean component
        (SMALL_LAKE_MASK, 5, EXPECTED_SMALL_LAKE_FILLED),

        # 4-cell lake; threshold too small → nothing filled
        (BIG_LAKE_MASK, 3, EXPECTED_BIG_LAKE_UNCHANGED),

        # 4-cell lake; threshold big enough to fill the lake, still smaller than ocean
        (BIG_LAKE_MASK, 10, EXPECTED_BIG_LAKE_FILLED),
    ],
)
def test__create_filled_land_mask_handles_lakes(gl, land_mask, size_threshold, expected):
    filled = gl._create_filled_land_mask(land_mask, size_threshold=size_threshold)

    assert filled.shape == land_mask.shape
    assert filled.dtype == bool

    # Direct comparison with explicit expected mask
    np.testing.assert_array_equal(filled, expected)

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

import numpy as np
import pytest


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

        # ---------------------------------------------------------------
        # CASE 3: two separate components:
        #
        #   - a THICK 3-cell horizontal bar at row 1
        #   - a THIN single-cell "blob" at (3, 1)
        #
        # With radius = 1:
        #   * the bar shrinks to a single cell in the middle
        #   * the isolated single cell is completely eroded away
        #
        # inland_mask = land & ~eroded, so:
        #   - the *ends* of the bar are inland band (they disappear)
        #   - the thin isolated blob is also entirely inland
        #
        # This exercises the "mixed" behaviour where:
        #   - thick regions produce a narrow inland band
        #   - thin regions are fully classified as inland.
        # ---------------------------------------------------------------
        (
            np.array([
                [False, False, False, False, False],
                [False,  True,  True,  True, False],
                [False, False, False, False, False],
                [False,  True, False, False, False],
                [False, False, False, False, False],
            ], dtype=bool),
            1,
            np.array([
                [False, False, False, False, False],
                [False,  True, False,  True, False],  # ends of bar are inland
                [False, False, False, False, False],
                [False,  True, False, False, False],  # thin blob is fully inland
                [False, False, False, False, False],
            ], dtype=bool),
        ),
        # CASE 4: radius 2 → full erosion → whole island becomes inland
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


def test_create_coastal_mask_with_inland_regions(gl):
    """
    GridLoader.create_coastal_mask_with_inland_regions should combine:
    - the land mask,
    - the inland distance bands (from create_inland_mask),
    - and the coastline mask,
    into a single integer mask with the expected codes.
    """
    # 3x3 land shape: a plus (+) of land cells
    # L = land (aggregated_labelled > 0), O = ocean
    #
    #   O L O
    #   L L L
    #   O L O
    #
    aggregated_labelled = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ], dtype=int)
    land_mask = aggregated_labelled.astype(bool)

    gl.masks["aggregated_labelled"] = aggregated_labelled

    # Define a fake coastline: the "arms" of the plus, but not the centre
    coastline_mask = np.array([
        [False, True,  False],
        [True,  False, True ],
        [False, True,  False],
    ], dtype=bool)
    gl.masks["coastline"] = coastline_mask

    # Define a fake inward 10km band: only the centre cell
    inward_10_mask = np.array([
        [False, False, False],
        [False, True,  False],
        [False, False, False],
    ], dtype=bool)

    # Stub create_inland_mask to return our inward_10_mask for radius=10,
    # and no bands (all False) for other radii.
    def fake_create_inland_mask(land, filled, radius):
        if radius == 10:
            return inward_10_mask
        return np.zeros_like(land, dtype=bool)

    gl.create_inland_mask = fake_create_inland_mask

    # Run method under test
    gl.create_coastal_mask_with_inland_regions()

    final = gl.masks["final_coastal_mask"]

    # Expected codes:
    # - 0: ocean            → outer corners
    # - 1: coastline        → arms of the plus
    # - 10: 10km band       → centre cell
    #
    expected = np.array([
        [0, 1, 0],
        [1, 10, 1],
        [0, 1, 0],
    ], dtype=int)

    assert final.shape == aggregated_labelled.shape
    np.testing.assert_array_equal(final, expected)

    # Also check the coastal_map was set as documented
    assert gl.coastal_map[0] == "ocean"
    assert gl.coastal_map[1] == "coastline"
    assert gl.coastal_map[10] == "10km from coast"

