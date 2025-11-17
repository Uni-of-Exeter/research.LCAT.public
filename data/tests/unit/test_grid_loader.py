import pytest
import numpy as np
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
        [False, False]
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
