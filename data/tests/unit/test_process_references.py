import pytest
import pandas as pd
import json
from unittest.mock import MagicMock, patch, mock_open

from data.src.process_references import ProcessReferences


@pytest.fixture
def sample_df():
    """Sample DataFrame with reference data"""
    return pd.DataFrame({
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
        "Notes": ["", "", ""]
    })


# =============================================================================
# __init__ and load_references
# =============================================================================


def test_init_loads_references(sample_df):
    """Should load CSV data on initialization"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")
        
        assert pr.df is not None
        assert len(pr.df) == 3
        assert pr.doi_lookups == {}
        assert pr.failed_doi_lookups == []
        assert pr.processed_references == {}


# =============================================================================
# clean_references
# =============================================================================


def test_clean_references_capitalizes_reference_types():
    """Should capitalize reference type strings"""
    df = pd.DataFrame({
        "Reference_ID": ["REF001", "REF002"],
        "Reference_Type": ["journal article", "BOOK SECTION"],
        "DOI": ["", ""],
        "Title": ["", ""]
    })
    
    with patch("pandas.read_csv", return_value=df):
        pr = ProcessReferences("test.csv")
        pr.clean_references()
        
        assert pr.df["Reference_Type"].iloc[0] == "Journal Article"
        assert pr.df["Reference_Type"].iloc[1] == "Book Section"


def test_clean_references_strips_whitespace():
    """Should strip extra whitespace from reference types"""
    df = pd.DataFrame({
        "Reference_ID": ["REF001"],
        "Reference_Type": ["  journal   article  "],
        "DOI": [""],
        "Title": [""]
    })
    
    with patch("pandas.read_csv", return_value=df):
        pr = ProcessReferences("test.csv")
        pr.clean_references()
        
        assert pr.df["Reference_Type"].iloc[0] == "Journal Article"


def test_clean_references_replaces_nans_with_empty_string():
    """Should replace NaN values with empty strings"""
    df = pd.DataFrame({
        "Reference_ID": ["REF001"],
        "Reference_Type": ["Journal Article"],
        "DOI": [None],
        "Title": [None]
    })
    
    with patch("pandas.read_csv", return_value=df):
        pr = ProcessReferences("test.csv")
        pr.clean_references()
        
        assert pr.df["DOI"].iloc[0] == ""
        assert pr.df["Title"].iloc[0] == ""


# =============================================================================
# doi_lookup_row
# =============================================================================


@patch("data.src.process_references.scrape_doi.scrape")
@patch("data.src.process_references.scrape_doi.read_article")
def test_doi_lookup_row_journal_article(mock_read_article, mock_scrape, sample_df):
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")

        mock_scrape.return_value = (MagicMock(), {"title": "Test"})
        expected = {"title": "Test Paper", "doi": "10.1234/test1"}
        mock_read_article.return_value = expected

        row = sample_df.iloc[0]
        pr.doi_lookup_row(row)

        mock_read_article.assert_called_once()
        mock_scrape.assert_called_once()

        assert pr.doi_lookups["REF001"] == expected
        assert "REF001" not in pr.failed_doi_lookups


@patch("data.src.process_references.scrape_doi.scrape")
@patch("data.src.process_references.scrape_doi.read_book")
def test_doi_lookup_row_book(mock_read_book, mock_scrape, sample_df):
    """Should process book DOI lookup"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")

        mock_scrape.return_value = (MagicMock(), {"title": "Test Book"})
        expected = {"title": "Test Book", "doi": "10.1234/test2"}
        mock_read_book.return_value = expected

        row = sample_df.iloc[1]
        pr.doi_lookup_row(row)

        mock_read_book.assert_called_once()
        assert pr.doi_lookups["REF002"] == expected
        assert "REF002" not in pr.failed_doi_lookups
        

@patch("data.src.process_references.scrape_doi.scrape")
@patch("data.src.process_references.scrape_doi.read_article")
def test_doi_lookup_row_handles_scrape_failure(mock_read_article, mock_scrape, sample_df):
    """Should record scrape failures and not attempt parsing"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")

        mock_scrape.side_effect = Exception("Scrape error")

        row = sample_df.iloc[0]  # Journal Article
        pr.doi_lookup_row(row)

        assert "REF001" in pr.failed_doi_lookups
        assert "REF001" not in pr.doi_lookups
        mock_read_article.assert_not_called()


@patch("data.src.process_references.scrape_doi.scrape")
@patch("data.src.process_references.scrape_doi.read_article")
def test_doi_lookup_row_handles_parsing_failure(mock_read_article, mock_scrape, sample_df):
    """Should record parsing failures and not store lookup data"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")

        mock_scrape.return_value = (MagicMock(), {"title": "Test"})
        mock_read_article.side_effect = Exception("Parse error")

        row = sample_df.iloc[0]
        pr.doi_lookup_row(row)

        assert "REF001" in pr.failed_doi_lookups
        assert "REF001" not in pr.doi_lookups


# =============================================================================
# perform_doi_lookups
# =============================================================================


@patch.object(ProcessReferences, "doi_lookup_row")
def test_perform_doi_lookups_scrapes_rows_with_dois(mock_lookup, sample_df):
    """Should scrape all rows that have DOIs (when scrape_all_rows=True)"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")

        pr.perform_doi_lookups(scrape_all_rows=True)

        # REF001 and REF002 have DOIs, REF003 doesn't
        assert mock_lookup.call_count == 2

        scraped_ids = [call.args[0]["Reference_ID"] for call in mock_lookup.call_args_list]
        assert set(scraped_ids) == {"REF001", "REF002"}


@patch.object(ProcessReferences, "doi_lookup_row")
def test_perform_doi_lookups_scrapes_only_missing_titles(mock_lookup, sample_df):
    """Should only scrape rows with DOIs but no titles (when scrape_all_rows=False)"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")

        pr.perform_doi_lookups(scrape_all_rows=False)

        # Only REF002 has a DOI but no title in sample_df
        assert mock_lookup.call_count == 1

        scraped_row = mock_lookup.call_args[0][0]
        assert scraped_row["Reference_ID"] == "REF002"


@patch.object(ProcessReferences, "doi_lookup_row")
def test_perform_doi_lookups_skips_rows_without_dois(mock_lookup):
    """Should not scrape rows without DOIs"""
    df = pd.DataFrame({
        "Reference_ID": ["REF001"],
        "Reference_Type": ["Journal Article"],
        "DOI": [""],
        "Title": [""]
    })
    
    with patch("pandas.read_csv", return_value=df):
        pr = ProcessReferences("test.csv")
        pr.perform_doi_lookups(scrape_all_rows=True)
        
        assert mock_lookup.call_count == 0


# =============================================================================
# process_references
# =============================================================================


def test_process_references_uses_doi_lookups(sample_df):
    """Should use DOI lookup data when available"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")
        
        # Simulate successful DOI lookup
        pr.doi_lookups["REF001"] = {"title": "Scraped Title", "doi": "10.1234/test1"}
        
        pr.process_references()
        
        assert "REF001" in pr.processed_references
        assert pr.processed_references["REF001"]["title"] == "Scraped Title"


def test_process_references_uses_original_data_without_lookup(sample_df):
    """Should use original CSV data when no DOI lookup available"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")
        
        pr.process_references()
        
        assert "REF003" in pr.processed_references
        assert pr.processed_references["REF003"]["title"] == "Manual Entry"
        assert pr.processed_references["REF003"]["article_id"] == "REF003"
        assert pr.processed_references["REF003"]["type"] == "Report"


def test_process_references_includes_all_fields(sample_df):
    """Should include all required fields in processed references"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")
        
        pr.process_references()
        
        ref = pr.processed_references["REF001"]
        assert "type" in ref
        assert "doi" in ref
        assert "article_id" in ref
        assert "title" in ref
        assert "authors" in ref
        assert "date" in ref
        assert "link" in ref
        assert "link_replacement" in ref
        assert "journal" in ref
        assert "issue" in ref
        assert "notes" in ref


def test_process_references_processes_all_rows(sample_df):
    """Should process all rows in DataFrame"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")
        
        pr.process_references()
        
        assert len(pr.processed_references) == 3


# =============================================================================
# save_json
# =============================================================================


def test_save_json_writes_to_file(sample_df):
    """Should write processed references to JSON file"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")
        pr.processed_references = {"REF001": {"title": "Test"}}
        
        m = mock_open()
        with patch("builtins.open", m):
            pr.save_json("output.json")
            m.assert_called_once_with("output.json", "w", encoding="utf-8")


def test_save_json_creates_valid_json(sample_df):
    """Should create valid JSON with proper encoding"""
    with patch("pandas.read_csv", return_value=sample_df):
        pr = ProcessReferences("test.csv")
        pr.processed_references = {"REF001": {"title": "Test Paper"}}
        
        with patch("builtins.open", mock_open()):
            with patch("json.dump") as mock_dump:
                pr.save_json("output.json")
                
                mock_dump.assert_called_once()
                assert mock_dump.call_args[1]["ensure_ascii"] is False
                assert mock_dump.call_args[1]["indent"] == 4
