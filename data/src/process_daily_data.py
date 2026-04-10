import concurrent.futures
import gc
import inspect
import io
import os
import random
import re
import threading
import time

import numpy as np
import requests
import xarray as xr
from bs4 import BeautifulSoup
from tqdm import tqdm


class ClimateDataProcessor:

    def __init__(self, config, ensemble_member=1):
        self.conf = config
        self.rcp = None
        self.bias_corrected = None
        self.season = None
        self.variable = None
        self.ensemble_member = ensemble_member
        self.excluded_decades = []
        self.file_urls = []
        self.data_location = self.conf["chess_scape_netcdf_location"]

    def get_file_links(self):
        bias_corrected_suffix = "_bias-corrected" if self.bias_corrected else ""
        ensemble_str = f"{self.ensemble_member:02d}"

        base_url = (
            "https://dap.ceda.ac.uk/badc/deposited2021/chess-scape/data/"
            f"rcp{self.rcp}{bias_corrected_suffix}/{ensemble_str}/daily/{self.variable}/"
        )

        try:
            response = requests.get(base_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to fetch NetCDF listing from {base_url}: {exc}"
            ) from exc

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all .nc file links
        nc_files = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.endswith(".nc"):
                nc_files.append(base_url + href)

        if not nc_files:
            raise RuntimeError(
                f"No .nc files found at {base_url}; endpoint may be unavailable or listing may have changed."
            )

        self.file_urls = nc_files

    def _parse_filename_date(self, file_url):
        """Extract date components from filename"""
        filename = file_url.split("/")[-1]
        date_match = re.search(r"(\d{4})(\d{2})(\d{2})-(\d{4})(\d{2})(\d{2})", filename)

        if date_match:
            return {
                "start_month": date_match.group(2),
                "start_date": date_match.group(1)
                + date_match.group(2)
                + date_match.group(3),
            }
        return None

    def process_data_by_decade(
        self,
        variable_name,
        season,
        calculation_func,
        decades_to_include=None,
        **calc_kwargs,
    ):
        """
        Generic function to process files by decade and apply a calculation function

        Parameters:
        - variable_name: name of the variable to extract
        - season: season to filter for
        - calculation_func: function to apply to the decade data
        - decades_to_include: optional list of decade indices to process (e.g., [0, 9] for 1980 and 2070)
        - **calc_kwargs: additional arguments for the calculation function
        """

        if not self.file_urls:
            raise RuntimeError(
                "No NetCDF file URLs available for processing. "
                "Run get_file_links() successfully before process_data_by_decade()."
            )

        # Get grid dimensions from first file
        print("Getting grid dimensions...")
        response = requests.get(self.file_urls[0], timeout=30)
        file_obj = io.BytesIO(response.content)
        sample_ds = xr.open_dataset(file_obj, engine="h5netcdf")
        y_coords = sample_ds.y.values
        x_coords = sample_ds.x.values
        sample_ds.close()
        del sample_ds
        gc.collect()

        print(f"Grid size: {len(y_coords)} x {len(x_coords)}")

        file_dates = []
        for file_url in self.file_urls:
            date_info = self._parse_filename_date(file_url)
            if date_info:
                file_dates.append((file_url, date_info))
            else:
                print(
                    f"Warning: Could not extract date from filename: {file_url.split('/')[-1]}"
                )

        # Sort files by date
        sorted_file_dates = sorted(file_dates, key=lambda x: x[1]["start_date"])

        # Filter files based on season
        def filter_files_by_season(files, season):
            """Filter files based on season requirements"""
            if season == "annual":
                return [fd[0] for fd in files]  # Return just URLs

            season_months = {"summer": ["06", "07", "08"], "winter": ["12", "01", "02"]}

            if season not in season_months:
                raise ValueError(
                    f"Invalid season: {season}. Must be 'annual', 'summer', or 'winter'"
                )

            target_months = season_months[season]
            filtered_files = []

            # Use the sorted list passed into this function so decade grouping is chronological.
            for file_url, date_info in files:
                if date_info["start_month"] in target_months:
                    filtered_files.append(file_url)

            return filtered_files

        # Apply season filtering
        print(f"Filtering files for season: {season}")
        filtered_files = filter_files_by_season(sorted_file_dates, season)
        print(
            f"Files after season filtering: {len(filtered_files)} out of {len(self.file_urls)}"
        )

        # Calculate step-based decades (assuming each file represents one step/year)
        excluded_decades = [1, 2, 3, 4]

        decade_files = {}
        for i, file_url in enumerate(filtered_files):
            decade = i // 120 if season == "annual" else i // 30

            if decade not in excluded_decades:
                # If decades_to_include is specified, only include those decades
                if decades_to_include is not None and decade not in decades_to_include:
                    continue
                if decade not in decade_files:
                    decade_files[decade] = []
                decade_files[decade].append(file_url)

        print(
            f"Files per decade: {[(d, len(files)) for d, files in decade_files.items()]}"
        )

        # Process each decade
        decade_results = {}
        for decade in sorted(decade_files.keys()):
            print(
                f"\nProcessing step-decade {decade} ({len(decade_files[decade])} files)..."
            )

            # Load data for this decade
            decade_data = self.load_decade_data(decade_files[decade], variable_name)

            if decade_data is None:
                print(f"No valid data found for step-decade {decade}")
                continue

            print(f"Step-decade {decade} data shape: {decade_data.shape}")

            # Apply the calculation function
            print(f"Applying calculation for step-decade {decade}...")

            call_kwargs = dict(calc_kwargs)
            if "season" not in call_kwargs:
                try:
                    params = inspect.signature(calculation_func).parameters
                except (TypeError, ValueError):
                    params = {}
                if "season" in params:
                    call_kwargs["season"] = season

            result = calculation_func(decade_data, **call_kwargs)

            decade_results[decade] = result

            del decade_data
            gc.collect()

        return self.create_combined_dataset(decade_results, y_coords, x_coords)

    def load_decade_data(
        self, file_urls, variable_name, n_workers=4, max_retries=5, base_delay=1.0
    ):
        """Load and concatenate data from multiple files with retry logic"""

        all_data = []
        successful_files = 0
        failed_files = []
        lock = threading.Lock()

        def download_file_with_retry(file_url):
            """Download a single file with exponential backoff retry"""
            last_error = None

            for attempt in range(max_retries):
                try:
                    # Add jitter to prevent thundering herd
                    if attempt > 0:
                        delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                        print(
                            f"Retry {attempt}/{max_retries-1} for {file_url.split('/')[-1]} after {delay:.1f}s delay"
                        )
                        time.sleep(delay)

                    response = requests.get(file_url, timeout=60)  # Increased timeout

                    if response.status_code != 200:
                        last_error = f"HTTP {response.status_code}"
                        if response.status_code in [
                            429,
                            503,
                            504,
                        ]:  # Rate limiting or server errors
                            continue  # Retry these
                        else:
                            break  # Don't retry for client errors like 404

                    # Check if we got valid content
                    if len(response.content) < 1000:
                        last_error = f"Content too small: {len(response.content)} bytes"
                        continue

                    if response.content.startswith(b"<html"):
                        last_error = "Got HTML response instead of NetCDF"
                        continue

                    file_obj = io.BytesIO(response.content)
                    ds = xr.open_dataset(file_obj, engine="h5netcdf")

                    if variable_name not in ds.variables:
                        ds.close()
                        last_error = f"Variable '{variable_name}' not found"
                        break  # Don't retry for missing variables

                    data = ds[variable_name].values
                    ds.close()

                    if np.isnan(data).all():
                        last_error = "All NaN data"
                        break  # Don't retry for bad data

                    return data, None  # Success!

                except requests.exceptions.ConnectTimeout:
                    last_error = "Connection timeout"
                    continue  # Retry timeouts
                except requests.exceptions.ReadTimeout:
                    last_error = "Read timeout"
                    continue  # Retry timeouts
                except requests.exceptions.ConnectionError as e:
                    last_error = f"Connection error: {str(e)}"
                    continue  # Retry connection errors
                except Exception as e:
                    last_error = f"Unexpected error: {str(e)}"
                    # For unexpected errors, retry a few times then give up
                    if attempt < 2:
                        continue
                    break

            return (
                None,
                f"Failed after {max_retries} attempts. Last error: {last_error}",
            )

        # Use ThreadPool for I/O bound operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
            future_to_url = {
                executor.submit(download_file_with_retry, url): url for url in file_urls
            }

            for future in tqdm(
                concurrent.futures.as_completed(future_to_url),
                total=len(file_urls),
                desc="Loading files",
            ):
                url = future_to_url[future]
                data, error = future.result()

                if data is not None:
                    with lock:
                        all_data.append(data)
                        successful_files += 1
                else:
                    with lock:
                        failed_files.append((url, error))
                    print(f"FAILED: {url.split('/')[-1]} - {error}")

        # Report results
        print(f"Successfully processed {successful_files}/{len(file_urls)} files")

        if failed_files:
            print(f"\nFAILED FILES ({len(failed_files)}):")
            for url, error in failed_files:
                print(f"  {url.split('/')[-1]}: {error}")

            # Decide whether to continue or fail
            failure_rate = len(failed_files) / len(file_urls)
            if failure_rate > 0.1:  # More than 10% failed
                raise RuntimeError(
                    f"Too many files failed ({failure_rate:.1%}). "
                    f"Got {successful_files}/{len(file_urls)} files. "
                    f"This will compromise data quality."
                )
            print(
                f"WARNING: {len(failed_files)} files failed but continuing with {successful_files} files"
            )

        if not all_data:
            raise RuntimeError("No files were successfully downloaded")

        return np.concatenate(all_data, axis=0)

    def create_combined_dataset(self, decade_results, y_coords, x_coords):
        """Create xarray dataset from decade results"""
        decades = sorted(decade_results.keys())

        if not decades:
            raise ValueError("No valid decades processed")

        # Handle different result types
        first_result = decade_results[decades[0]]

        if isinstance(first_result, dict):
            # Multiple variables (like quantiles)
            combined_data = {}
            for var_name in first_result:
                var_stack = np.stack(
                    [decade_results[decade][var_name] for decade in decades], axis=0
                )
                combined_data[var_name] = (["decade", "y", "x"], var_stack)
        else:
            # Single variable
            data_stack = np.stack(
                [decade_results[decade] for decade in decades], axis=0
            )
            combined_data = {"variable": (["decade", "y", "x"], data_stack)}

        decade_coords = [int(d) for d in decades]

        print("Processing Complete")
        return xr.Dataset(
            combined_data,
            coords={"decade": decade_coords, "y": y_coords, "x": x_coords},
        )

    def calculate_quantiles(self, data, quantiles=None):
        """Calculate temperature quantiles"""

        n_time, n_y, n_x = data.shape

        if quantiles is None:
            quantiles = [95, 99]

        if "tas" in self.variable:
            # Convert temperature from Kelvin to Celsius
            data = data - 273.15

        if "pr" in self.variable:
            # Convert precipitation from kg m-2 s-1 to mm/day
            data = data * 86400

        # Reshape to (time, pixels)
        reshaped = data.reshape(n_time, -1)

        results = {}
        for q in quantiles:
            quantile = np.percentile(reshaped, q, axis=0)
            quantile_grid = quantile.reshape(n_y, n_x)
            results[f"quantile_{q}"] = quantile_grid

        return results

    def calculate_threshold_days(
        self,
        data,
        threshold,
        comparison="gte",
        convert_kelvin=False,
        convert_precip=False,
        season="annual",
    ):
        """
        Calculate mean number of days per period meeting a threshold condition.

        Parameters:
        - data: climate data array (time, y, x)
        - threshold: threshold value (in target units - Celsius or mm/day)
        - comparison: 'gte' for >= or 'lte' for <=
        - convert_kelvin: if True, convert data from Kelvin to Celsius
        - convert_precip: if True, convert data from kg m-2 s-1 to mm/day
        - season: "annual", "summer", or "winter" (affects normalization period)

        Returns:
        - 2D array of mean days per period meeting threshold for each pixel
        """
        n_time, n_y, n_x = data.shape

        # Unit conversions
        if convert_kelvin:
            data = data - 273.15
        if convert_precip:
            data = data * 86400

        # Reshape to work with all pixels at once
        data_reshaped = data.reshape(n_time, -1)  # (time, pixels)
        valid_pixels = np.isfinite(data_reshaped).any(axis=0)

        # Apply threshold comparison
        if comparison == "gte":
            meets_threshold = data_reshaped >= threshold
        elif comparison == "lte":
            meets_threshold = data_reshaped <= threshold
        else:
            raise ValueError(f"Invalid comparison: {comparison}. Use 'gte' or 'lte'")

        # Calculate number of periods for a 360-day calendar:
        # annual => 360 days, seasonal => 90 days (3 months)
        if season == "annual":
            days_per_period = 360
        elif season in ["summer", "winter"]:
            days_per_period = 90
        else:
            raise ValueError(
                f"Invalid season: {season}. Must be 'annual', 'summer', or 'winter'"
            )

        n_periods = n_time / days_per_period

        print(f"Processing {n_time} days ({n_periods:.1f} {season} periods) of data")
        print(f"Threshold: {threshold}, Comparison: {comparison}, Season: {season}")

        # Count days meeting threshold and convert to mean per period
        threshold_counts = np.sum(meets_threshold, axis=0)
        mean_per_period = threshold_counts / n_periods
        mean_per_period = mean_per_period.astype(float)
        mean_per_period[~valid_pixels] = np.nan

        # Reshape back to grid
        return mean_per_period.reshape(n_y, n_x)

    # Convenience wrappers for backward compatibility
    def calculate_tropical_nights(self, data, temp_threshold=20.0, season="annual"):
        """Calculate mean tropical nights per period (tasmin >= threshold)."""
        return self.calculate_threshold_days(
            data,
            temp_threshold,
            comparison="gte",
            convert_kelvin=True,
            season=season,
        )

    def calculate_heat_days(self, data, temp_threshold=30.0, season="annual"):
        """Calculate mean hot/extreme heat days per period (tasmax >= threshold)."""
        return self.calculate_threshold_days(
            data,
            temp_threshold,
            comparison="gte",
            convert_kelvin=True,
            season=season,
        )

    def calculate_heavy_rain_days(self, data, rain_threshold=50.0, season="annual"):
        """Calculate mean heavy rain days per period (pr >= threshold)."""
        return self.calculate_threshold_days(
            data,
            rain_threshold,
            comparison="gte",
            convert_precip=True,
            season=season,
        )

    def calculate_dry_days(self, data, rain_threshold=1.0, season="annual"):
        """Calculate mean dry days per period (pr <= threshold)."""
        return self.calculate_threshold_days(
            data,
            rain_threshold,
            comparison="lte",
            convert_precip=True,
            season=season,
        )

    def calculate_windy_days(self, data, wind_threshold=8.0, season="annual"):
        """Calculate mean windy days per period (wind speed >= threshold)."""
        return self.calculate_threshold_days(
            data, wind_threshold, comparison="gte", season=season
        )

    def generate_data(
        self,
        *,
        quantiles_config=None,
        tropical_nights_enabled=True,
        hot_days_enabled=True,
        heavy_rain_enabled=True,
        dry_days_enabled=True,
        windy_days_enabled=True,
        rcps=None,
        bias_options=None,
        seasons=None,
        variables=None,
        tropical_threshold=20.0,
        heat_threshold=30.0,
        rain_threshold=50.0,
        dry_threshold=1.0,
        wind_threshold=8.0,
    ):
        """Generate requested datasets for configured climate scenarios."""

        rcps = rcps or [60, 85]
        bias_options = bias_options or [True, False]
        seasons = seasons or ["annual", "winter", "summer"]
        variables = variables or ["tasmax", "tasmin", "pr", "sfcWind"]
        self.excluded_decades = [1, 2, 3, 4]  # Exclude 1990s, 2000s, 2010s, 2020s

        default_quantiles = {"tasmax": [99], "tasmin": [1]}
        if quantiles_config is None:
            quantiles_config = default_quantiles
        else:
            quantiles_config = {
                var: list(values) for var, values in quantiles_config.items()
            }

        saved_datasets = []

        for rcp in rcps:
            for bias in bias_options:
                for season in seasons:
                    for variable in variables:
                        quantiles = list(quantiles_config.get(variable, []))
                        compute_quantiles = bool(quantiles)
                        compute_tropical = tropical_nights_enabled and variable == "tasmin"
                        compute_hot_days = hot_days_enabled and variable == "tasmax"
                        compute_heavy_rain = heavy_rain_enabled and variable == "pr"
                        compute_dry_days = dry_days_enabled and variable == "pr"
                        compute_windy_days = windy_days_enabled and variable == "sfcWind"

                        if (
                            not compute_quantiles
                            and not compute_tropical
                            and not compute_hot_days
                            and not compute_heavy_rain
                            and not compute_dry_days
                            and not compute_windy_days
                        ):
                            print(
                                "Skipping processing for variable "
                                f"{variable} (no outputs requested)."
                            )
                            continue

                        self.rcp = rcp
                        self.bias_corrected = bias
                        self.season = season
                        self.variable = variable

                        print(
                            f"Processing RCP {rcp}, Bias Corrected: {bias}, Variable: {variable}"
                        )

                        self.get_file_links()

                        bias_suffix = "_bias-corrected" if bias else ""
                        season_folder = "seasonal" if season != "annual" else "annual"
                        ensemble_str = f"{self.ensemble_member:02d}"
                        output_dir = os.path.join(
                            self.data_location,
                            f"data/rcp{rcp}{bias_suffix}/{ensemble_str}/{season_folder}",
                        )
                        os.makedirs(output_dir, exist_ok=True)

                        if compute_quantiles:
                            quantile_dataset = self.process_data_by_decade(
                                variable,
                                season,
                                self.calculate_quantiles,
                                quantiles=quantiles,
                            )

                            quantile_fragment = "_".join(str(q) for q in quantiles)
                            if len(quantiles) == 1:
                                quantile_label = f"{variable}_{quantiles[0]}_percentile"
                            else:
                                quantile_label = (
                                    f"{variable}_{quantile_fragment}_percentiles"
                                )

                            quantile_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_{quantile_label}_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            quantile_path = os.path.join(output_dir, quantile_filename)
                            quantile_dataset.to_netcdf(quantile_path)
                            print(f"Saved dataset to {quantile_path}")
                            saved_datasets.append(quantile_path)

                        if compute_tropical:
                            tropical_dataset = self.process_data_by_decade(
                                variable,
                                season,
                                self.calculate_tropical_nights,
                                decades_to_include=[0, 9],  # 1980 and 2070 only
                                temp_threshold=tropical_threshold,
                            )

                            tropical_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_tropical_nights_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            tropical_path = os.path.join(output_dir, tropical_filename)
                            tropical_dataset.to_netcdf(tropical_path)
                            print(f"Saved dataset to {tropical_path}")
                            saved_datasets.append(tropical_path)

                        if compute_hot_days:
                            hot_days_dataset = self.process_data_by_decade(
                                variable,
                                season,
                                self.calculate_heat_days,
                                decades_to_include=[0, 9],
                                temp_threshold=heat_threshold,
                            )

                            hot_days_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_hot_heat_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            hot_days_path = os.path.join(output_dir, hot_days_filename)
                            hot_days_dataset.to_netcdf(hot_days_path)
                            print(f"Saved dataset to {hot_days_path}")
                            saved_datasets.append(hot_days_path)

                        if compute_heavy_rain:
                            heavy_rain_dataset = self.process_data_by_decade(
                                variable,
                                season,
                                self.calculate_heavy_rain_days,
                                decades_to_include=[0, 9],
                                rain_threshold=rain_threshold,
                            )

                            heavy_rain_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_heavy_rain_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            heavy_rain_path = os.path.join(
                                output_dir, heavy_rain_filename
                            )
                            heavy_rain_dataset.to_netcdf(heavy_rain_path)
                            print(f"Saved dataset to {heavy_rain_path}")
                            saved_datasets.append(heavy_rain_path)
                        if compute_dry_days:
                            dry_days_dataset = self.process_data_by_decade(
                                variable,
                                season,
                                self.calculate_dry_days,
                                decades_to_include=[0, 9],
                                rain_threshold=dry_threshold,
                            )

                            dry_days_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_dry_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            dry_days_path = os.path.join(output_dir, dry_days_filename)
                            dry_days_dataset.to_netcdf(dry_days_path)
                            print(f"Saved dataset to {dry_days_path}")
                            saved_datasets.append(dry_days_path)
                        if compute_windy_days:
                            windy_days_dataset = self.process_data_by_decade(
                                variable,
                                season,
                                self.calculate_windy_days,
                                decades_to_include=[0, 9],
                                wind_threshold=wind_threshold,
                            )

                            windy_days_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_windy_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            windy_days_path = os.path.join(
                                output_dir, windy_days_filename
                            )
                            windy_days_dataset.to_netcdf(windy_days_path)
                            print(f"Saved dataset to {windy_days_path}")
                            saved_datasets.append(windy_days_path)

        print("\n" + "=" * 60)
        print(f"SUMMARY: {len(saved_datasets)} datasets saved")
        print("=" * 60)
        for path in saved_datasets:
            print(f"  {path}")
        print("=" * 60)
