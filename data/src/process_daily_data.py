import concurrent.futures
import gc
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
    def __init__(self, config):
        self.conf = config
        self.rcp = None
        self.bias_corrected = None
        self.variable = None
        self.excluded_decades = []
        self.file_urls = []
        self.data_location = self.conf["chess_scape_netcdf_location"]

    def get_file_links(self):
        bias_corrected_suffix = "_bias-corrected" if self.bias_corrected else ""

        base_url = f"https://dap.ceda.ac.uk/badc/deposited2021/chess-scape/data/rcp{self.rcp}{bias_corrected_suffix}/01/daily/{self.variable}/"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all .nc file links
        nc_files = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.endswith(".nc"):
                nc_files.append(base_url + href)

        self.file_urls = nc_files

    def process_data_by_decade(self, variable_name, calculation_func, **calc_kwargs):
        """
        Generic function to process files by decade and apply a calculation function

        Parameters:
        - file_urls: list of URLs to process
        - variable_name: name of the variable to extract
        - calculation_func: function to apply to the decade data
        - **calc_kwargs: additional arguments for the calculation function
        """

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

        # Sort files by date to ensure proper chronological order
        def extract_date(file_url):
            filename = file_url.split("/")[-1]
            date_match = re.search(r"(\d{8})-(\d{8})", filename)
            if date_match:
                return date_match.group(1)  # Start date
            return filename

        sorted_files = sorted(self.file_urls, key=extract_date)

        # Calculate step-based decades (assuming each file represents one step/year)
        # For December-to-December years, we need to group files in sets of 10
        excluded_decades = [1, 2, 3, 4]

        decade_files = {}
        for i, file_url in enumerate(sorted_files):
            decade = i // 120  # Each decade = 120 consecutive monthly files

            if decade not in excluded_decades:
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
            result = calculation_func(decade_data, **calc_kwargs)

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

    def calculate_quantiles(self, data, quantiles=[95, 99]):
        """Calculate temperature quantiles"""

        n_time, n_y, n_x = data.shape

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

    def generate_data(self):

        rcps = [60, 85]
        bias_corrected = [True, False]

        variables = ["tasmin"]
        self.excluded_decades = [1, 2, 3, 4]  # Exclude 1990s, 2000s, 2010s, 2020s

        for rcp in rcps:
            for bias in bias_corrected:
                for variable in variables:
                    self.rcp = rcp
                    self.bias_corrected = bias
                    self.variable = variable

                    print(
                        f"Processing RCP {rcp}, Bias Corrected: {bias}, Variable: {variable}"
                    )

                    self.get_file_links()

                    # Process data by decade and calculate quantiles
                    # TODO check if we need 99 and 95 quantiles in seperate files
                    dataset = self.process_data_by_decade(
                        self.variable,
                        self.calculate_quantiles,
                        quantiles=[1],
                    )

                    bias_corrected_folder = "_bias-corrected" if bias else ""
                    season_folder = "annual"

                    # Create filepath
                    sub_folders = (
                        f"data/rcp{rcp}{bias_corrected_folder}/01/{season_folder}"
                    )

                    # Save the dataset to a NetCDF file

                    filename = f"chess-scape_rcp{rcp}{'_bias-corrected' if bias else ''}_01_{variable}_1_percentile_uk_1km_annual_19801201-20801130.nc"
                    filepath = os.path.join(self.data_location, sub_folders, filename)
                    dataset.to_netcdf(filepath)
                    print(f"Saved dataset to {filepath}")
