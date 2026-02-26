import json
import pandas as pd
import pytest
from unittest.mock import MagicMock, mock_open, patch

from data.src.process_references import ProcessReferences


# -----------------------------------------------------------------------------
# fixtures / helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Reference_ID": ["REF001", "REF002", "REF003"],
            "Reference_Type": ["Journal Article", "Book", "Report"],
            "DOI": ["10.1234/test1", "10.1234/test2", ""],
            "Title": ["Test Paper 1", "", "Manual Entry"],
            "Authors": ["Author, A.", "Author, B.", "Author, C."],
            "Date": ["2020", "2021", "2022"],
            "Journal": ["Test Journal", "", ""],
            "Volume/Issue": ["1(2)", "", ""],
            "URL": ["http://example.com/1", "http://example.com/2", ""],
            "Replacement_URL": ["", "", ""],
            "Notes": ["", "", ""],
        }
    )


@pytest.fixture
def pr_from_df():
    """Create ProcessReferences with pandas.read_csv patched to return the provided df."""
    def _make(df: pd.DataFrame) -> ProcessReferences:
        with patch("pandas.read_csv", return_value=df):
            return ProcessReferences("test.csv")
    return _make


# -----------------------------------------------------------------------------
# clean_references
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "dirty, expected",
    [
        ("journal article", "Journal Article"),
        ("BOOK SECTION", "Book Section"),
        ("  journal   article  ", "Journal Article"),
        ("rePorT", "Report"),
    ],
)
def test_clean_references_normalises_reference_type_strings(pr_from_df, dirty, expected):
    df = pd.DataFrame(
        {
            "Reference_ID": ["REF001"],
            "Reference_Type": [dirty],
            "DOI": [""],
            "Title": [""],
        }
    )
    pr = pr_from_df(df)
    pr.clean_references()

    assert pr.df.loc[0, "Reference_Type"] == expected


def test_clean_references_fills_nans_with_empty_string(pr_from_df):
    df = pd.DataFrame(
        {
            "Reference_ID": ["REF001"],
            "Reference_Type": ["Journal Article"],
            "DOI": [None],
            "Title": [None],
        }
    )
    pr = pr_from_df(df)
    pr.clean_references()

    assert pr.df.loc[0, "DOI"] == ""
    assert pr.df.loc[0, "Title"] == ""


# -----------------------------------------------------------------------------
# doi_lookup_row
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "ref_type, parser_attr",
    [
        ("Journal Article", "read_article"),
        ("Report", "read_article"),
        ("Book", "read_book"),
        ("Book Section", "read_book"),
    ],
)
def test_doi_lookup_row_routes_to_correct_parser(pr_from_df, ref_type, parser_attr):
    df = pd.DataFrame(
        {
            "Reference_ID": ["REF001"],
            "Reference_Type": [ref_type],
            "DOI": ["10.1234/x"],
            "Title": [""],
            "Authors": [""],
            "Date": [""],
            "Journal": [""],
            "Volume/Issue": [""],
            "URL": [""],
            "Replacement_URL": [""],
            "Notes": [""],
        }
    )
    pr = pr_from_df(df)

    with patch("data.src.process_references.scrape_doi.scrape", return_value=(MagicMock(), {"any": "data"})) as mock_scrape, \
         patch(f"data.src.process_references.scrape_doi.{parser_attr}", return_value={"parsed": True}) as mock_parser:
        pr.doi_lookup_row(df.iloc[0])

    mock_scrape.assert_called_once()
    mock_parser.assert_called_once()
    assert pr.doi_lookups["REF001"] == {"parsed": True}
    assert pr.failed_doi_lookups == []


def test_doi_lookup_row_records_failed_scrape(pr_from_df, sample_df):
    pr = pr_from_df(sample_df)

    with patch("data.src.process_references.scrape_doi.scrape", side_effect=Exception("boom")) as mock_scrape, \
         patch("data.src.process_references.scrape_doi.read_article") as mock_read_article:
        pr.doi_lookup_row(sample_df.iloc[0])  # Journal Article

    mock_scrape.assert_called_once()
    mock_read_article.assert_not_called()
    assert "REF001" in pr.failed_doi_lookups
    assert "REF001" not in pr.doi_lookups


def test_doi_lookup_row_records_failed_parse(pr_from_df, sample_df):
    pr = pr_from_df(sample_df)

    with patch("data.src.process_references.scrape_doi.scrape", return_value=(MagicMock(), {"any": "data"})), \
         patch("data.src.process_references.scrape_doi.read_article", side_effect=Exception("parse fail")):
        pr.doi_lookup_row(sample_df.iloc[0])  # Journal Article

    assert "REF001" in pr.failed_doi_lookups
    assert "REF001" not in pr.doi_lookups


def test_doi_lookup_row_skips_scrape_for_unhandled_reference_type(pr_from_df):
    df = pd.DataFrame(
        {
            "Reference_ID": ["REFX"],
            "Reference_Type": ["Website"],
            "DOI": ["10.1234/x"],
            "Title": [""],
            "Authors": [""],
            "Date": [""],
            "Journal": [""],
            "Volume/Issue": [""],
            "URL": [""],
            "Replacement_URL": [""],
            "Notes": [""],
        }
    )
    pr = pr_from_df(df)

    with patch("data.src.process_references.scrape_doi.scrape") as mock_scrape:
        pr.doi_lookup_row(df.iloc[0])

    mock_scrape.assert_not_called()
    assert pr.doi_lookups == {}
    assert pr.failed_doi_lookups == []

# -----------------------------------------------------------------------------
# perform_doi_lookups
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "scrape_all_rows, expected_ids",
    [
        (True, {"REF001", "REF002"}),   # all rows with DOI != ""
        (False, {"REF002"}),           # DOI != "" and Title == ""
    ],
)
def test_perform_doi_lookups_selects_correct_rows(pr_from_df, sample_df, scrape_all_rows, expected_ids):
    pr = pr_from_df(sample_df)

    with patch.object(ProcessReferences, "doi_lookup_row") as mock_lookup:
        pr.perform_doi_lookups(scrape_all_rows=scrape_all_rows)

    called_ids = {call.args[0]["Reference_ID"] for call in mock_lookup.call_args_list}
    assert called_ids == expected_ids


def test_perform_doi_lookups_skips_when_no_dois(pr_from_df):
    df = pd.DataFrame(
        {
            "Reference_ID": ["REF001"],
            "Reference_Type": ["Journal Article"],
            "DOI": [""],
            "Title": [""],
        }
    )
    pr = pr_from_df(df)

    with patch.object(ProcessReferences, "doi_lookup_row") as mock_lookup:
        pr.perform_doi_lookups(scrape_all_rows=True)

    mock_lookup.assert_not_called()


# -----------------------------------------------------------------------------
# process_references
# -----------------------------------------------------------------------------

def test_process_references_prefers_doi_lookups_over_raw_rows(pr_from_df, sample_df):
    pr = pr_from_df(sample_df)

    pr.doi_lookups["REF001"] = {"title": "Scraped Title", "doi": "10.1234/test1"}
    pr.process_references()

    assert pr.processed_references["REF001"] == {"title": "Scraped Title", "doi": "10.1234/test1"}


def test_process_references_builds_expected_fallback_shape(pr_from_df, sample_df):
    pr = pr_from_df(sample_df)
    pr.process_references()

    ref = pr.processed_references["REF003"]  # report with manual entry
    assert ref == {
        "type": "Report",
        "doi": "",
        "article_id": "REF003",
        "link": "",
        "link_replacement": "",
        "title": "Manual Entry",
        "authors": "Author, C.",
        "date": "2022",
        "journal": "",
        "issue": "",
        "notes": "",
    }


def test_process_references_processes_every_row(pr_from_df, sample_df):
    pr = pr_from_df(sample_df)
    pr.process_references()
    assert set(pr.processed_references.keys()) == {"REF001", "REF002", "REF003"}


# -----------------------------------------------------------------------------
# save_json
# -----------------------------------------------------------------------------

def test_save_json_dumps_processed_references_with_expected_options(pr_from_df, sample_df):
    pr = pr_from_df(sample_df)
    pr.processed_references = {"REF001": {"title": "Test Paper"}}

    m = mock_open()
    with patch("builtins.open", m) as open_mock, patch("json.dump") as dump_mock:
        pr.save_json("output.json")

    open_mock.assert_called_once_with("output.json", "w", encoding="utf-8")
    dump_mock.assert_called_once()

    args, kwargs = dump_mock.call_args
    assert args[0] == pr.processed_references
    assert args[1] == open_mock.return_value.__enter__.return_value
    assert kwargs["ensure_ascii"] is False
    assert kwargs["indent"] == 4