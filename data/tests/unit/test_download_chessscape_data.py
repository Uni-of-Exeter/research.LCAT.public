import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import requests

from data.src.download_chessscape_data import ChessScapeDownloader

# =============================================================================
# FIXTURES
# =============================================================================

HTML_LISTING = """
<html><body>
<a href="chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc">tas</a>
<a href="chess-scape_rcp60_01_pr_uk_1km_annual_19801201-20801130.nc">pr</a>
<a href="chess-scape_rcp60_01_hurs_uk_1km_annual_19801201-20801130.nc">hurs</a>
<a href="chess-scape_rcp60_01_dtr_uk_1km_annual_19801201-20801130.nc">dtr</a>
</body></html>
"""

DAILY_HTML_LISTING = """
<html><body>
<a href="chess-scape_rcp60_01_tasmax_uk_1km_daily_19801201-19811130.nc">file1</a>
<a href="chess-scape_rcp60_01_tasmax_uk_1km_daily_19811201-19821130.nc">file2</a>
</body></html>
"""


@pytest.fixture
def config(tmp_path):
    return {"chess_scape_netcdf_location": str(tmp_path)}


@pytest.fixture
def downloader(config):
    return ChessScapeDownloader(config)


def _make_response(text: str, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.text = text
    resp.raise_for_status = MagicMock()
    if status >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(response=resp)
    return resp


# =============================================================================
# Initialisation
# =============================================================================


class TestInit:
    def test_data_location_set_from_config(self, config):
        d = ChessScapeDownloader(config)
        assert d.data_location == config["chess_scape_netcdf_location"]

    def test_ensemble_str_zero_padded(self, config):
        d = ChessScapeDownloader(config, ensemble_member=1)
        assert d._ensemble_str() == "01"

    def test_bias_suffix_bias_corrected(self, downloader):
        assert downloader._bias_suffix(True) == "_bias-corrected"

    def test_bias_suffix_non_bias(self, downloader):
        assert downloader._bias_suffix(False) == ""

    def test_session_created(self, downloader):
        assert downloader.session is not None


# =============================================================================
# _list_nc_files
# =============================================================================


class TestListNcFiles:
    def test_returns_nc_filenames(self, downloader):
        with patch.object(downloader.session, "get", return_value=_make_response(HTML_LISTING)):
            result = downloader._list_nc_files("https://example.com/dir/")
        assert "chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc" in result
        assert "chess-scape_rcp60_01_pr_uk_1km_annual_19801201-20801130.nc" in result

    def test_filters_non_nc_links(self, downloader):
        html = "<html><body><a href='file.nc'>nc</a><a href='file.txt'>txt</a></body></html>"
        with patch.object(downloader.session, "get", return_value=_make_response(html)):
            result = downloader._list_nc_files("https://example.com/dir/")
        assert result == ["file.nc"]

    def test_raises_on_request_error(self, downloader):
        with patch.object(
            downloader.session, "get", side_effect=requests.ConnectionError("timeout")
        ):
            with pytest.raises(RuntimeError, match="Failed to fetch NetCDF listing"):
                downloader._list_nc_files("https://example.com/dir/")

    def test_raises_on_http_error(self, downloader):
        with patch.object(
            downloader.session, "get", return_value=_make_response("", status=404)
        ):
            with pytest.raises(RuntimeError, match="Failed to fetch NetCDF listing"):
                downloader._list_nc_files("https://example.com/dir/")


# =============================================================================
# download_base_files
# =============================================================================


class TestDownloadBaseFiles:
    def _patch_list(self, downloader, filenames):
        """Patch _list_nc_files to return the given filenames."""
        return patch.object(downloader, "_list_nc_files", return_value=filenames)

    def _patch_download(self, downloader):
        return patch.object(downloader, "_download_file")

    def test_skips_existing_files(self, downloader, tmp_path):
        """Files that already exist on disk are skipped."""
        filename = "chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc"
        dest_dir = tmp_path / "data" / "rcp60" / "01" / "annual"
        dest_dir.mkdir(parents=True)
        (dest_dir / filename).write_bytes(b"existing")

        # Patch _list_nc_files only for the annual aggregation; seasonal returns nothing
        def _list_side_effect(url):
            return [filename] if "/annual/" in url else []

        with patch.object(downloader, "_list_nc_files", side_effect=_list_side_effect):
            with self._patch_download(downloader) as mock_dl:
                downloader.download_base_files(rcps=[60], bias_options=[False])

        mock_dl.assert_not_called()

    def test_downloads_missing_base_variable_file(self, downloader):
        """A missing base-variable file is downloaded."""
        filename = "chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc"

        # Only return a file for the annual directory; seasonal returns nothing
        def _list_side_effect(url):
            return [filename] if "/annual/" in url else []

        with patch.object(downloader, "_list_nc_files", side_effect=_list_side_effect):
            with self._patch_download(downloader) as mock_dl:
                downloader.download_base_files(rcps=[60], bias_options=[False])

        mock_dl.assert_called_once()
        _, dest = mock_dl.call_args[0]
        assert filename in dest

    def test_filters_out_non_base_variables(self, downloader):
        """Files not matching BASE_VARIABLES (e.g. hurs, dtr) are not downloaded."""
        filenames = [
            "chess-scape_rcp60_01_hurs_uk_1km_annual_19801201-20801130.nc",
            "chess-scape_rcp60_01_dtr_uk_1km_annual_19801201-20801130.nc",
        ]

        with self._patch_list(downloader, filenames):
            with self._patch_download(downloader) as mock_dl:
                downloader.download_base_files(rcps=[60], bias_options=[False])

        mock_dl.assert_not_called()

    def test_dry_run_does_not_download(self, downloader):
        """dry_run=True prints intent but never calls _download_file."""
        filename = "chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc"

        with self._patch_list(downloader, [filename]):
            with self._patch_download(downloader) as mock_dl:
                downloader.download_base_files(rcps=[60], bias_options=[False], dry_run=True)

        mock_dl.assert_not_called()

    def test_dry_run_prints_would_download(self, downloader, capsys):
        filename = "chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc"

        with self._patch_list(downloader, [filename]):
            with self._patch_download(downloader):
                downloader.download_base_files(rcps=[60], bias_options=[False], dry_run=True)

        assert "[dry-run]" in capsys.readouterr().out

    def test_max_downloads_stops_early(self, downloader):
        """max_downloads=1 stops after the first real download."""
        filenames = [
            "chess-scape_rcp60_01_tas_uk_1km_annual_19801201-20801130.nc",
            "chess-scape_rcp60_01_pr_uk_1km_annual_19801201-20801130.nc",
        ]

        with self._patch_list(downloader, filenames):
            with self._patch_download(downloader) as mock_dl:
                downloader.download_base_files(
                    rcps=[60], bias_options=[False], max_downloads=1
                )

        assert mock_dl.call_count == 1

    def test_failed_listing_counted_as_failure(self, downloader, capsys):
        with patch.object(
            downloader, "_list_nc_files", side_effect=RuntimeError("404")
        ):
            downloader.download_base_files(rcps=[60], bias_options=[False])

        out = capsys.readouterr().out
        assert "FAILED listing" in out
        assert "failed: 2" in out  # annual + seasonal

    def test_uses_bias_corrected_subfolder(self, downloader):
        """Bias-corrected files land in rcp60_bias-corrected subfolder."""
        filename = "chess-scape_rcp60_bias-corrected_01_tas_uk_1km_annual_19801201-20801130.nc"

        with self._patch_list(downloader, [filename]):
            with self._patch_download(downloader) as mock_dl:
                downloader.download_base_files(rcps=[60], bias_options=[True])

        _, dest = mock_dl.call_args[0]
        assert "rcp60_bias-corrected" in dest


# =============================================================================
# get_daily_file_links
# =============================================================================


class TestGetDailyFileLinks:
    def test_returns_full_urls(self, downloader):
        with patch.object(
            downloader, "_list_nc_files",
            return_value=[
                "chess-scape_rcp60_01_tasmax_uk_1km_daily_19801201-19811130.nc",
                "chess-scape_rcp60_01_tasmax_uk_1km_daily_19811201-19821130.nc",
            ],
        ):
            urls = downloader.get_daily_file_links(rcp=60, bias=False, variable="tasmax")

        assert len(urls) == 2
        assert all(u.startswith("https://") for u in urls)
        assert all(u.endswith(".nc") for u in urls)

    def test_constructs_correct_url_non_bias(self, downloader):
        with patch.object(
            downloader, "_list_nc_files", return_value=["file.nc"]
        ) as mock_list:
            downloader.get_daily_file_links(rcp=60, bias=False, variable="tas")

        called_url = mock_list.call_args[0][0]
        assert "/rcp60/" in called_url
        assert "/daily/tas/" in called_url
        assert "_bias-corrected" not in called_url

    def test_constructs_correct_url_bias_corrected(self, downloader):
        with patch.object(
            downloader, "_list_nc_files", return_value=["file.nc"]
        ) as mock_list:
            downloader.get_daily_file_links(rcp=85, bias=True, variable="pr")

        called_url = mock_list.call_args[0][0]
        assert "/rcp85_bias-corrected/" in called_url
        assert "/daily/pr/" in called_url

    def test_raises_when_no_files_found(self, downloader):
        with patch.object(downloader, "_list_nc_files", return_value=[]):
            with pytest.raises(RuntimeError, match="No .nc files found"):
                downloader.get_daily_file_links(rcp=60, bias=False, variable="tas")

    def test_raises_on_listing_failure(self, downloader):
        with patch.object(
            downloader, "_list_nc_files", side_effect=RuntimeError("connection error")
        ):
            with pytest.raises(RuntimeError):
                downloader.get_daily_file_links(rcp=60, bias=False, variable="tas")


# =============================================================================
# _download_file
# =============================================================================


class TestDownloadFile:
    def test_writes_file_to_disk(self, downloader, tmp_path):
        dest = str(tmp_path / "subdir" / "file.nc")
        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.raise_for_status = MagicMock()
        mock_response.iter_content.return_value = [b"data_chunk"]

        with patch.object(downloader.session, "get", return_value=mock_response):
            downloader._download_file("https://example.com/file.nc", dest)

        assert os.path.exists(dest)
        assert open(dest, "rb").read() == b"data_chunk"

    def test_creates_parent_directory(self, downloader, tmp_path):
        dest = str(tmp_path / "new" / "nested" / "dir" / "file.nc")
        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.raise_for_status = MagicMock()
        mock_response.iter_content.return_value = [b"x"]

        with patch.object(downloader.session, "get", return_value=mock_response):
            downloader._download_file("https://example.com/file.nc", dest)

        assert os.path.exists(os.path.dirname(dest))

    def test_cleans_up_partial_file_on_error(self, downloader, tmp_path):
        dest = str(tmp_path / "file.nc")

        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.raise_for_status = MagicMock()
        mock_response.iter_content.side_effect = requests.ConnectionError("dropped")

        with patch.object(downloader.session, "get", return_value=mock_response):
            with pytest.raises(requests.ConnectionError):
                downloader._download_file("https://example.com/file.nc", dest)

        assert not os.path.exists(dest)
