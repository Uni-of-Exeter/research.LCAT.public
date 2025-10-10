from typing import Dict
import pytest
import xarray as xr
from unittest.mock import patch

from src.grid_loader import GridLoader


@pytest.fixture
def grid_loader(mock_config: Dict[str, str]) -> GridLoader:
    """Fixture providing GridLoader instance."""
    with patch.object(GridLoader, "set_data_location"):
        return GridLoader(mock_config)


class TestCreatePolygonMask:
    """Test polygon mask creation."""

    def test_create_polygon_mask_simple_square(self, grid_loader: GridLoader) -> None:
        vertices = [(2, 2), (7, 2), (7, 7), (2, 7)]
        mask = grid_loader.create_polygon_mask(vertices, 10, 10)

        assert mask.shape == (10, 10)
        assert mask.dtype == bool
        # Check interior point is True
        assert mask[4, 4] == True
        # Check exterior point is False
        assert mask[0, 0] == False

    def test_create_polygon_mask_all_false_for_empty_polygon(
        self, grid_loader: GridLoader
    ) -> None:
        vertices = [(0, 0), (0, 0), (0, 0)]
        mask = grid_loader.create_polygon_mask(vertices, 5, 5)

        assert mask.shape == (5, 5)
        assert not mask.any()  # All False

    def test_create_polygon_mask_partially_out_of_bounds(
        self, grid_loader: GridLoader
    ) -> None:
        # Polygon partially outside: extends from -2 to 8 in a 10x10 grid
        vertices = [(-2, -2), (8, -2), (8, 8), (-2, 8)]
        mask = grid_loader.create_polygon_mask(vertices, 10, 10)

        assert mask.shape == (10, 10)
        assert mask.dtype == bool

        # Interior cells should be True
        assert mask[5, 5] == True

        # Edge cells within bounds should be True
        assert mask[0, 0] == True  # Bottom-left corner
        assert mask[7, 7] == True


class TestGetMask:
    """Test mask generation from NetCDF data."""

    def test_get_mask_bias_corrected(
        self, grid_loader: GridLoader, sample_netcdf_data: xr.Dataset
    ) -> None:
        grid_loader.data = {"bias_corrected": sample_netcdf_data}
        grid_loader.variable = "tas"

        mask = grid_loader.get_mask("bias_corrected")

        assert mask.shape == (1300, 700)
        assert mask.dtype == bool

        # Check that NaN regions are False in mask
        assert not mask[:400, :].any(), "NaN regions (y < 400) should all be False"

        # Check that non-NaN regions are True in mask
        assert mask[400:, :].all(), "Non-NaN regions (y >= 400) should all be True"

    def test_get_mask_non_bias_corrected_filters_regions(
        self, grid_loader: GridLoader, sample_non_bias_netcdf_data: xr.Dataset
    ) -> None:
        grid_loader.data = {"non_bias_corrected": sample_non_bias_netcdf_data}
        grid_loader.variable = "tas"

        mask = grid_loader.get_mask("non_bias_corrected")

        assert mask.shape == (1300, 700)
        assert mask.dtype == bool

        # NI region should be True
        assert mask[:100, :200].any()

        # Scilly Isles should be True
        assert mask[:50, 75:100].any()

        # Anything else should be False
        assert not mask[200:400, 300:500].any()
