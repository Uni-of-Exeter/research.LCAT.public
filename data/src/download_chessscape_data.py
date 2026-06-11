import os
import threading

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CEDA_BASE = "https://dap.ceda.ac.uk/badc/deposited2021/chess-scape/data"

BASE_VARIABLES = ["pr", "rsds", "sfcWind", "tas", "tasmax", "tasmin"]
DERIVED_VARIABLES = [
    "tropical_nights",
    "hot_heat_days",
    "heavy_rain_days",
    "dry_days",
    "windy_days",
    "tasmax_99_percentile",
    "tasmin_1_percentile",
]

RCPS = [60, 85]
BIAS_OPTIONS = [True, False]
ENSEMBLE = 1


class ChessScapeDownloader:
    """Downloads CHESS-SCAPE NetCDF files from CEDA.

    Handles both:
    - Base annual/seasonal files (tas, pr, sfcWind, tasmin, tasmax, rsds), which
      are stored flat in CEDA directories without per-variable subfolders.
    - Daily files (for all variables), which are stored per-variable in subfolders
      and are used as input by ClimateDataProcessor.
    """

    def __init__(self: "ChessScapeDownloader", config: dict, ensemble_member: int = 1) -> None:
        self.conf = config
        self.ensemble_member = ensemble_member
        self.data_location = self.conf["chess_scape_netcdf_location"]
        self.session = self._create_http_session()
        self._thread_local = threading.local()

    def _create_http_session(self: "ChessScapeDownloader", pool_connections: int = 20, pool_maxsize: int = 20) -> requests.Session:
        """Create a requests session with retry and connection pooling."""
        session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "HEAD"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _ensemble_str(self: "ChessScapeDownloader") -> str:
        return f"{self.ensemble_member:02d}"

    def _bias_suffix(self: "ChessScapeDownloader", bias: bool) -> str:
        return "_bias-corrected" if bias else ""

    def _list_nc_files(self: "ChessScapeDownloader", url: str) -> list[str]:
        """Fetch a CEDA directory listing and return all .nc filenames found."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch NetCDF listing from {url}: {exc}") from exc

        soup = BeautifulSoup(response.text, "html.parser")
        return [a["href"] for a in soup.find_all("a", href=True) if isinstance(a["href"], str) and a["href"].endswith(".nc")]

    def _download_file(self: "ChessScapeDownloader", url: str, dest: str) -> None:
        """Stream-download a single file to dest, cleaning up on failure."""
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            with self.session.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                        f.write(chunk)
        except requests.RequestException:
            if os.path.exists(dest):
                os.remove(dest)
            raise

    def download_base_files(
        self: "ChessScapeDownloader",
        rcps: list[int] | None = None,
        bias_options: list[bool] | None = None,
        dry_run: bool = False,
        max_downloads: int | None = None,
    ) -> None:
        """Download base CHESS-SCAPE annual and seasonal files from CEDA.

        Base variable files (pr, rsds, sfcWind, tas, tasmax, tasmin) are stored
        flat in CEDA directories — no per-variable subfolders. This method lists
        each directory and downloads only files matching BASE_VARIABLES, skipping
        any that already exist locally.

        Args:
            rcps: RCP scenarios to download (default: [60, 85]).
            bias_options: Bias-correction options to download (default: [True, False]).
            dry_run: If True, print what would be downloaded without fetching.
            max_downloads: Stop after this many actual downloads (useful for testing).
        """
        rcps = rcps or RCPS
        bias_options = bias_options if bias_options is not None else BIAS_OPTIONS
        ensemble_str = self._ensemble_str()

        downloaded = skipped = failed = 0

        for rcp in rcps:
            for bias in bias_options:
                for aggregation in ["annual", "seasonal"]:
                    bias_suffix = self._bias_suffix(bias)
                    url = f"{CEDA_BASE}/rcp{rcp}{bias_suffix}/{ensemble_str}/{aggregation}/"

                    try:
                        nc_files = self._list_nc_files(url)
                    except RuntimeError as exc:
                        print(f"  FAILED listing {url}: {exc}")
                        failed += 1
                        continue

                    # Filter to base variables only
                    nc_files = [f for f in nc_files if any(f"_{v}_" in f for v in BASE_VARIABLES)]

                    for filename in nc_files:
                        folder = "seasonal" if aggregation == "seasonal" else "annual"
                        dest = os.path.join(
                            self.data_location,
                            f"data/rcp{rcp}{bias_suffix}/{ensemble_str}/{folder}",
                            filename,
                        )

                        if os.path.exists(dest):
                            skipped += 1
                            continue

                        if dry_run:
                            print(f"  [dry-run] Would download: {dest}")
                            downloaded += 1
                            continue

                        if max_downloads is not None and downloaded >= max_downloads:
                            print(f"  Reached max_downloads={max_downloads}, stopping.")
                            print(f"\nDone — downloaded: {downloaded}, skipped: {skipped}, failed: {failed}")
                            return

                        try:
                            self._download_file(url + filename, dest)
                            print(f"  Downloaded: {filename}")
                            downloaded += 1
                        except requests.RequestException as exc:
                            print(f"  FAILED {filename}: {exc}")
                            failed += 1

        print(f"\nDone — downloaded: {downloaded}, skipped: {skipped}, failed: {failed}")

    def get_daily_file_links(self: "ChessScapeDownloader", rcp: int, bias: bool, variable: str) -> list[str]:
        """Return full URLs for all daily NetCDF files for a given scenario and variable.

        Daily files are stored in per-variable subfolders on CEDA:
        .../daily/{variable}/

        Args:
            rcp: RCP scenario (60 or 85).
            bias: Whether to use bias-corrected data.
            variable: Variable name (e.g. 'tasmax', 'pr').

        Returns:
            List of fully-qualified .nc file URLs.
        """
        bias_suffix = self._bias_suffix(bias)
        ensemble_str = self._ensemble_str()
        base_url = f"{CEDA_BASE}/rcp{rcp}{bias_suffix}/{ensemble_str}/daily/{variable}/"

        nc_files = self._list_nc_files(base_url)

        if not nc_files:
            raise RuntimeError(f"No .nc files found at {base_url}; endpoint may be unavailable or listing may have changed.")

        return [base_url + f for f in nc_files]
