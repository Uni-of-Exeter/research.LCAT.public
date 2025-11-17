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
    print(np.array_equal(mask, expected))
    assert mask.shape == (2, 2)
    assert np.array_equal(mask, expected)

def test_get_mask_non_bias_corrected_uses_dirty_mask_and_polygon(gl):
    """
    get_mask('non_bias_corrected') should return the intersection of:
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

