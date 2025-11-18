import pytest
import numpy as np
import xarray as xr
from data.src.grid_loader import GridLoader

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
    # bias (1) + 2 * non_bias
    expected = (
        gl.masks["bias_corrected"].astype(int)
        + 2 * gl.masks["non_bias_corrected"].astype(int)
    )

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

def test_create_polygon_mask_simple_square(gl):
    """ 
    GridLoader.create_polygon_mask should return a boolean mask indicating
    which grid points fall inside the given polygon.

    Using a simple 5×5 grid and a square polygon, we check that:
    - an interior point is True, and
    - an exterior point is False.
    """
    y_size, x_size = 5, 5

    polygon_vertices = [
        (1, 1),
        (3, 1),
        (3, 3),
        (1, 3),
    ]

    mask = gl.create_polygon_mask(polygon_vertices, y_size, x_size)
    print(mask)
    assert mask.shape == (y_size, x_size)
    assert mask.dtype == bool

    # clearly inside
    assert mask[2, 2]

    # clearly outside
    assert not mask[0, 0]

def test__create_filled_land_mask_fills_small_lakes(gl):
    """
    _create_filled_land_mask should fill small 'lake' regions (False inside True)
    while leaving the large surrounding ocean (False outside) unchanged.

    We create a 5x5 mask with:
    - a border of ocean (False)
    - a block of land (True) in the middle
    - a single-cell 'lake' (False) in the centre of that land

    With a size_threshold larger than the lake but smaller than the ocean,
    only the lake should be filled.
    """
    land_mask = np.array([
        [False, False, False, False, False],
        [False,  True,  True,  True, False],
        [False,  True, False,  True, False],  # centre cell (2, 2) is a lake
        [False,  True,  True,  True, False],
        [False, False, False, False, False],
    ], dtype=bool)

    # Sanity check: lake cell is currently water
    assert land_mask[2, 2] == False

    filled = gl._create_filled_land_mask(land_mask, size_threshold=15)

    # Shape/dtype preserved
    assert filled.shape == land_mask.shape
    assert filled.dtype == bool

    # The little lake should now be filled in as land
    assert filled[2, 2] == True

    # Ocean corners should still be water
    assert filled[0, 0] == False
    assert filled[0, 4] == False
    assert filled[4, 0] == False
    assert filled[4, 4] == False

    # We should have exactly one more land cell than before
    assert np.count_nonzero(filled) == np.count_nonzero(land_mask) + 1

def test_create_coastline_mask_simple_island(gl):
    """
    GridLoader.create_coastline_mask should create a boolean mask of coastal
    land cells: land cells with some, but not all, land neighbours in a 3×3
    window.

    Using a simple 5×5 'island' in aggregated_labelled, we expect the coastline
    to be the outer ring of that island (all land cells except the centre).
    """
    # 5×5 island: 3×3 block of land surrounded by water
    aggregated_labelled = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ], dtype=int)

    gl.masks["aggregated_labelled"] = aggregated_labelled

    # For this simple case, filled_land_mask == land_mask (no lakes to fill),
    # so we stub _create_filled_land_mask to just return the input.
    def fake_filled_land_mask(land_mask):
        return land_mask

    gl._create_filled_land_mask = fake_filled_land_mask

    # Run the method under test
    gl.create_coastline_mask()

    coastline = gl.masks["coastline"]

    # Expected coastline: all land cells except the central one at (2,2)
    expected = np.array([
        [False, False, False, False, False],
        [False,  True,  True,  True, False],
        [False,  True, False,  True, False],
        [False,  True,  True,  True, False],
        [False, False, False, False, False],
    ], dtype=bool)

    assert coastline.shape == aggregated_labelled.shape
    assert coastline.dtype == bool
    np.testing.assert_array_equal(coastline, expected)

def test_create_inland_mask_simple_island(gl):
    """
    GridLoader.create_inland_mask should return a band of land cells
    near the coastline, based on binary erosion using a circular
    structuring element.

    Using a simple 5×5 island, we expect radius=1 erosion to leave
    a 1-cell-wide coastal band around the edge of the island.
    """
    # Original land mask (True = land, False = water)
    land_mask = np.array([
        [False, False, False, False, False],
        [False,  True,  True,  True, False],
        [False,  True,  True,  True, False],
        [False,  True,  True,  True, False],
        [False, False, False, False, False],
    ], dtype=bool)

    # For this test, filled_land_mask is identical (no lakes)
    filled_land_mask = land_mask.copy()

    inland = gl.create_inland_mask(
        land_mask=land_mask,
        filled_land_mask=filled_land_mask,
        radius=1
    )

    # Expected inland band: land cells that disappear after erosion
    expected = np.array([
        [False, False, False, False, False],
        [False,  True,  True,  True, False],
        [False,  True, False,  True, False],
        [False,  True,  True,  True, False],
        [False, False, False, False, False],
    ], dtype=bool)

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
