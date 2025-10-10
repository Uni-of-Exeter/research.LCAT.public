from typing import Dict
import numpy as np
import xarray as xr
import pytest


@pytest.fixture
def mock_config() -> Dict[str, str]:
    """Fixture providing mock configuration."""
    return {
        "chess_scape_netcdf_location": "/path/to/netcdf",
        "host": "localhost",
        "dbname": "test_db",
        "user": "test_user",
        "user_pass": "test_pass",
    }


@pytest.fixture
def sample_netcdf_data() -> xr.Dataset:
    """Fixture providing sample xarray dataset."""
    x = np.arange(0, 700) * 1000
    y = np.arange(0, 1300) * 1000
    time = np.arange(10)

    data = np.ones((10, 1300, 700))
    data[:, :400, :] = np.nan  # No data in some regions

    dataset = xr.Dataset(
        {"tas": (["time", "y", "x"], data)}, coords={"time": time, "y": y, "x": x}
    )
    return dataset


@pytest.fixture
def sample_non_bias_netcdf_data() -> xr.Dataset:
    """Fixture providing sample non-bias-corrected xarray dataset."""
    x = np.arange(0, 700) * 1000
    y = np.arange(0, 1300) * 1000
    time = np.arange(10)

    # Create data with different NaN pattern for non-bias-corrected
    data = np.ones((10, 1300, 700))
    data[:, 500:, :] = np.nan
    data[:, :100, :200] = 1.0  # NI region
    data[:, :50, 75:100] = 1.0  # Scilly Isles region

    dataset = xr.Dataset(
        {"tas": (["time", "y", "x"], data)}, coords={"time": time, "y": y, "x": x}
    )
    return dataset
