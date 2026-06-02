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
from tqdm import tqdm

from data.src.download_chessscape_data import ChessScapeDownloader


class ClimateDataProcessor:

    def __init__(
        self: "ClimateDataProcessor", config: dict, ensemble_member: int = 1
    ) -> None:
        self.conf = config
        self.rcp = None
        self.bias_corrected = None
        self.season = None
        self.variable = None
        self.ensemble_member = ensemble_member
        self.excluded_decades = []
        self.file_urls = []
        self.data_location = self.conf["chess_scape_netcdf_location"]
        self._downloader = ChessScapeDownloader(config, ensemble_member)
        self.session = self._downloader.session
        self._thread_local = self._downloader._thread_local

    def _get_thread_session(
        self: "ClimateDataProcessor", n_workers: int = 4
    ) -> requests.Session:
        """Get or create a per-thread session for concurrent downloads."""
        session = getattr(self._thread_local, "session", None)
        if session is None:
            pool_size = max(8, n_workers * 2)
            session = self._downloader._create_http_session(
                pool_connections=pool_size,
                pool_maxsize=pool_size,
            )
            self._thread_local.session = session
        return session

    def get_file_links(self: "ClimateDataProcessor") -> None:
        """Populate self.file_urls with daily NetCDF URLs for the current scenario."""
        self.file_urls = self._downloader.get_daily_file_links(
            self.rcp, self.bias_corrected, self.variable
        )

    def _parse_filename_date(
        self: "ClimateDataProcessor", file_url: str
    ) -> dict | None:
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
        self: "ClimateDataProcessor",
        variable_name,
        season,
        calculation_func=None,
        decades_to_include=None,
        calculations=None,
        **calc_kwargs: object,
    ):
        """
        Generic function to process files by decade and apply a calculation function

        Parameters:
        - variable_name: name of the variable to extract
        - season: season to filter for
        - calculation_func: function to apply to the decade data (single-calculation mode)
        - decades_to_include: optional list of decade indices to process (e.g., [0, 9] for 1980 and 2070)
        - calculations: optional list of calculations in the form:
            {"name": str, "function": callable, "kwargs": dict}
        - **calc_kwargs: additional arguments for the calculation function
        """

        single_calculation_mode = calculations is None
        if single_calculation_mode:
            if calculation_func is None:
                raise ValueError(
                    "Either calculation_func or calculations must be provided"
                )
            calculations = [
                {
                    "name": "default",
                    "function": calculation_func,
                    "kwargs": dict(calc_kwargs),
                }
            ]
        elif not calculations:
            raise ValueError("calculations must contain at least one calculation")

        calculation_specs = []
        calc_names = set()
        for calc in calculations:
            name = calc.get("name")
            func = calc.get("function")
            kwargs = dict(calc.get("kwargs", {}))

            if not name or not callable(func):
                raise ValueError(
                    "Each calculation must provide a name and callable function"
                )
            if name in calc_names:
                raise ValueError(f"Duplicate calculation name: {name}")
            calc_names.add(name)
            calculation_specs.append({"name": name, "function": func, "kwargs": kwargs})

        if not self.file_urls:
            raise RuntimeError(
                "No NetCDF file URLs available for processing. "
                "Run get_file_links() successfully before process_data_by_decade()."
            )

        # Get grid dimensions from first file
        print("Getting grid dimensions...")
        response = self.session.get(self.file_urls[0], timeout=30)
        response.raise_for_status()
        file_obj = io.BytesIO(response.content)
        sample_ds = xr.open_dataset(file_obj, engine="h5netcdf")
        y_coords = sample_ds.y.to_numpy()
        x_coords = sample_ds.x.to_numpy()
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

        decade_files = {}
        for i, file_url in enumerate(filtered_files):
            decade = i // 120 if season == "annual" else i // 30

            if decade not in self.excluded_decades:
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
        decade_results_by_calc = {calc["name"]: {} for calc in calculation_specs}
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

            # Apply all requested calculations from the same loaded decade data.
            for calc in calculation_specs:
                print(
                    f"Applying calculation '{calc['name']}' for step-decade {decade}..."
                )
                call_kwargs = dict(calc["kwargs"])
                if "season" not in call_kwargs:
                    try:
                        params = inspect.signature(calc["function"]).parameters
                    except (TypeError, ValueError):
                        params = {}
                    if "season" in params:
                        call_kwargs["season"] = season

                result = calc["function"](decade_data, **call_kwargs)
                decade_results_by_calc[calc["name"]][decade] = result

            del decade_data
            gc.collect()

        datasets = {}
        for calc_name, decade_results in decade_results_by_calc.items():
            if decade_results:
                datasets[calc_name] = self.create_combined_dataset(
                    decade_results,
                    y_coords,
                    x_coords,
                )

        if single_calculation_mode:
            return datasets.get("default")
        return datasets

    def load_decade_data(
        self: "ClimateDataProcessor",
        file_urls,
        variable_name,
        n_workers=4,
        max_retries=5,
        base_delay=1.0,
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

                    session = self._get_thread_session(n_workers=n_workers)
                    response = session.get(file_url, timeout=60)

                    if response.status_code != 200:
                        last_error = f"HTTP {response.status_code}"
                        if response.status_code in [
                            429,
                            503,
                            504,
                        ]:  # Rate limiting or server errors
                            continue  # Retry these
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

                    data = ds[variable_name].to_numpy()
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
                    last_error = f"Connection error: {e!s}"
                    continue  # Retry connection errors
                except Exception as e:
                    last_error = f"Unexpected error: {e!s}"
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

    def create_combined_dataset(
        self: "ClimateDataProcessor", decade_results, y_coords, x_coords
    ):
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

    def calculate_quantiles(self: "ClimateDataProcessor", data, quantiles=None):
        """Calculate temperature quantiles"""

        n_time, n_y, n_x = data.shape

        if quantiles is None:
            quantiles = [95, 99]

        if "tas" in (self.variable or ""):
            # Convert temperature from Kelvin to Celsius
            data = data - 273.15

        if "pr" in (self.variable or ""):
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
        self: "ClimateDataProcessor",
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

        n_complete_periods = n_time // days_per_period
        remainder = n_time % days_per_period
        if remainder != 0:
            print(
                f"WARNING: {remainder} trailing days excluded (incomplete period); "
                f"using {n_complete_periods} complete periods"
            )
            meets_threshold = meets_threshold[: n_complete_periods * days_per_period]

        if n_complete_periods == 0:
            raise ValueError(
                f"Not enough data for even one complete {season} period: "
                f"got {n_time} days, need at least {days_per_period}."
            )

        print(
            f"Processing {n_time} days ({n_complete_periods} {season} periods) of data"
        )
        print(f"Threshold: {threshold}, Comparison: {comparison}, Season: {season}")

        threshold_counts = np.sum(meets_threshold, axis=0)
        mean_per_period = threshold_counts / n_complete_periods

        # Reshape back to grid
        return mean_per_period.reshape(n_y, n_x)

    # Convenience wrappers for backward compatibility
    def calculate_tropical_nights(
        self: "ClimateDataProcessor", data, temp_threshold=20.0, season="annual"
    ):
        """Calculate mean tropical nights per period (tasmin >= threshold)."""
        return self.calculate_threshold_days(
            data,
            temp_threshold,
            comparison="gte",
            convert_kelvin=True,
            season=season,
        )

    def calculate_heat_days(
        self: "ClimateDataProcessor", data, temp_threshold=30.0, season="annual"
    ):
        """Calculate mean hot/extreme heat days per period (tasmax >= threshold)."""
        return self.calculate_threshold_days(
            data,
            temp_threshold,
            comparison="gte",
            convert_kelvin=True,
            season=season,
        )

    def calculate_heavy_rain_days(
        self: "ClimateDataProcessor", data, rain_threshold=50.0, season="annual"
    ):
        """Calculate mean heavy rain days per period (pr >= threshold)."""
        return self.calculate_threshold_days(
            data,
            rain_threshold,
            comparison="gte",
            convert_precip=True,
            season=season,
        )

    def calculate_dry_days(
        self: "ClimateDataProcessor", data, rain_threshold=1.0, season="annual"
    ):
        """Calculate mean dry days per period (pr <= threshold)."""
        return self.calculate_threshold_days(
            data,
            rain_threshold,
            comparison="lte",
            convert_precip=True,
            season=season,
        )

    def calculate_windy_days(
        self: "ClimateDataProcessor", data, wind_threshold=8.0, season="annual"
    ):
        """Calculate mean windy days per period (wind speed >= threshold)."""
        return self.calculate_threshold_days(
            data, wind_threshold, comparison="gte", season=season
        )

    def generate_data(
        self: "ClimateDataProcessor",
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

                        requested_calculations = []
                        output_targets = []

                        if compute_quantiles:
                            requested_calculations.append(
                                {
                                    "name": "quantiles",
                                    "function": self.calculate_quantiles,
                                    "kwargs": {"quantiles": quantiles},
                                }
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
                            output_targets.append(
                                (
                                    "quantiles",
                                    os.path.join(output_dir, quantile_filename),
                                )
                            )

                        if compute_tropical:
                            requested_calculations.append(
                                {
                                    "name": "tropical_nights",
                                    "function": self.calculate_tropical_nights,
                                    "kwargs": {"temp_threshold": tropical_threshold},
                                }
                            )

                            tropical_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_tropical_nights_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            output_targets.append(
                                (
                                    "tropical_nights",
                                    os.path.join(output_dir, tropical_filename),
                                )
                            )

                        if compute_hot_days:
                            requested_calculations.append(
                                {
                                    "name": "hot_heat_days",
                                    "function": self.calculate_heat_days,
                                    "kwargs": {"temp_threshold": heat_threshold},
                                }
                            )

                            hot_days_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_hot_heat_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            output_targets.append(
                                (
                                    "hot_heat_days",
                                    os.path.join(output_dir, hot_days_filename),
                                )
                            )

                        if compute_heavy_rain:
                            requested_calculations.append(
                                {
                                    "name": "heavy_rain_days",
                                    "function": self.calculate_heavy_rain_days,
                                    "kwargs": {"rain_threshold": rain_threshold},
                                }
                            )

                            heavy_rain_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_heavy_rain_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            output_targets.append(
                                (
                                    "heavy_rain_days",
                                    os.path.join(output_dir, heavy_rain_filename),
                                )
                            )

                        if compute_dry_days:
                            requested_calculations.append(
                                {
                                    "name": "dry_days",
                                    "function": self.calculate_dry_days,
                                    "kwargs": {"rain_threshold": dry_threshold},
                                }
                            )

                            dry_days_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_dry_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            output_targets.append(
                                (
                                    "dry_days",
                                    os.path.join(output_dir, dry_days_filename),
                                )
                            )

                        if compute_windy_days:
                            requested_calculations.append(
                                {
                                    "name": "windy_days",
                                    "function": self.calculate_windy_days,
                                    "kwargs": {"wind_threshold": wind_threshold},
                                }
                            )

                            windy_days_filename = (
                                f"chess-scape_rcp{rcp}{bias_suffix}_{ensemble_str}_windy_days_"
                                f"uk_1km_{season}_19801201-20801130.nc"
                            )
                            output_targets.append(
                                (
                                    "windy_days",
                                    os.path.join(output_dir, windy_days_filename),
                                )
                            )

                        calculation_datasets_raw = self.process_data_by_decade(
                            variable,
                            season,
                            calculations=requested_calculations,
                        )

                        if not isinstance(calculation_datasets_raw, dict):
                            raise RuntimeError(
                                "Expected multiple calculation datasets but got single result"
                            )

                        calculation_datasets = calculation_datasets_raw

                        for calc_name, output_path in output_targets:
                            dataset = calculation_datasets.get(calc_name)
                            if dataset is None:
                                raise RuntimeError(
                                    f"Missing dataset for calculation '{calc_name}'"
                                )
                            dataset.to_netcdf(output_path)
                            print(f"Saved dataset to {output_path}")
                            saved_datasets.append(output_path)

        print("\n" + "=" * 60)
        print(f"SUMMARY: {len(saved_datasets)} datasets saved")
        print("=" * 60)
        for path in saved_datasets:
            print(f"  {path}")
        print("=" * 60)
