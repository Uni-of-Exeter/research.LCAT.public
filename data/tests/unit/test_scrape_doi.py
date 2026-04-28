import pytest
from unittest.mock import MagicMock, patch

from data.src.scrape_doi import scrape, read_article, read_book


# -----------------------------------------------------------------------------
# helpers (builders)
# -----------------------------------------------------------------------------

def make_row(ref_type="Journal Article", ref_id="REF001", doi="10.1234/test",
             url="http://example.com", repl=""):
    return {
        "Reference_Type": ref_type,
        "Reference_ID": ref_id,
        "DOI": doi,
        "URL": url,
        "Replacement_URL": repl,
    }


def make_article_crossref(
    title="Test Paper",
    contributors=None,
    publication_date=None,
    journal_title="Test Journal",
    issue=None,
):
    if contributors is None:
        contributors = {"person_name": {"given_name": "John", "surname": "Doe", "@contributor_role": "author"}}
    if publication_date is None:
        publication_date = {"year": "2020"}

    journal = {
        "journal_article": {
            "titles": {"title": title},
            "contributors": contributors,
            "publication_date": publication_date,
        },
        "journal_metadata": {"full_title": journal_title},
    }

    if issue is not None:
        journal["journal_issue"] = {"issue": issue}

    return {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {"journal": journal}
                        }
                    }
                }
            }
        }
    }


def make_book_crossref(
    metadata_key="book_metadata",
    title="Test Book",
    contributors=None,
    publication_date=None,
    content_item=None,
):
    if contributors is None:
        contributors = {"person_name": {"given_name": "John", "surname": "Doe"}}
    if publication_date is None:
        publication_date = {"year": "2020"}

    book = {
        metadata_key: {
            "titles": {"title": title},
            "contributors": contributors,
            "publication_date": publication_date,
        }
    }
    if content_item is not None:
        book["content_item"] = content_item

    return {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {"book": book}
                        }
                    }
                }
            }
        }
    }


# -----------------------------------------------------------------------------
# scrape
# -----------------------------------------------------------------------------

@patch("data.src.scrape_doi.xmltodict.parse")
@patch("data.src.scrape_doi.urllib.request.build_opener")
def test_scrape_sets_accept_header_and_opens_doi(mock_build_opener, mock_parse):
    mock_opener = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b"<xml/>"

    # IMPORTANT: scrape() uses a context manager now (with opener.open(...) as r)
    mock_opener.open.return_value.__enter__.return_value = mock_response

    mock_build_opener.return_value = mock_opener
    mock_parse.return_value = {"ok": True}

    row = {"DOI": "10.1234/test", "Reference_Type": "Journal Article"}

    data = scrape(row)

    assert mock_opener.addheaders == [("Accept", "application/vnd.crossref.unixsd+xml")]
    mock_opener.open.assert_called_once_with("https://doi.org/10.1234/test", timeout=20)
    assert data == {"ok": True}


# -----------------------------------------------------------------------------
# read_article
# -----------------------------------------------------------------------------

def test_read_article_basic_fields_and_issue_extraction():
    row = make_row()
    d = make_article_crossref(issue="4")
    out = read_article(row, d)

    assert out["type"] == row["Reference_Type"]
    assert out["article_id"] == row["Reference_ID"]
    assert out["doi"] == row["DOI"]
    assert out["link"] == row["URL"]
    assert out["link_replacement"] == row["Replacement_URL"]
    assert out["journal"] == "Test Journal"
    assert out["issue"] == "4"


@pytest.mark.parametrize(
    "title_in, expected",
    [
        ("Plain Title", "Plain Title"),
        ({"#text": "Dict Title"}, "Dict Title"),
    ],
)
def test_read_article_title_handles_string_or_dict(title_in, expected):
    row = make_row()
    d = make_article_crossref(title=title_in)
    out = read_article(row, d)
    assert out["title"] == expected


def test_read_article_authors_filters_to_author_role_when_list():
    row = make_row()
    contributors = {
        "person_name": [
            {"given_name": "John", "surname": "Doe", "@contributor_role": "author"},
            {"given_name": "Ed", "surname": "Itor", "@contributor_role": "editor"},
            {"given_name": "Jane", "surname": "Smith", "@contributor_role": "author"},
        ]
    }
    d = make_article_crossref(contributors=contributors)
    out = read_article(row, d)

    assert out["authors"] == "John Doe, Jane Smith"


def test_read_article_single_contributor_should_respect_contributor_role():
    """
    Single contributors should respect @contributor_role.
    Editors shouldn't be included in the authors field.
    """
    row = make_row()
    contributors = {"person_name": {"given_name": "Ed", "surname": "Itor", "@contributor_role": "editor"}}
    d = make_article_crossref(contributors=contributors)
    out = read_article(row, d)

    # editor shouldn't be treated as an author
    assert out["authors"] == ""


def test_read_article_publication_date_list_prefers_print_year():
    row = make_row()
    publication_date = [
        {"@media_type": "online", "year": "2019"},
        {"@media_type": "print", "year": "2020"},
    ]
    d = make_article_crossref(publication_date=publication_date)
    out = read_article(row, d)
    assert out["date"] == "2020"


def test_read_article_publication_date_list_without_print_should_not_be_empty():
    """
    When publication_date is a list without a 'print' media type entry,
    should fall back to the first available year rather than returning empty string.
    """
    row = make_row()
    publication_date = [
        {"@media_type": "online", "year": "2019"},
    ]
    d = make_article_crossref(publication_date=publication_date)
    out = read_article(row, d)

    assert out["date"] == "2019"


# -----------------------------------------------------------------------------
# read_book
# -----------------------------------------------------------------------------

def test_read_book_basic_fields_and_empty_journal_issue():
    row = make_row(ref_type="Book", ref_id="REF002", doi="10.1234/book")
    d = make_book_crossref(title="Climate Change Handbook")
    out = read_book(row, d)

    assert out["type"] == row["Reference_Type"]
    assert out["article_id"] == row["Reference_ID"]
    assert out["doi"] == row["DOI"]
    assert out["link"] == row["URL"]
    assert out["link_replacement"] == row["Replacement_URL"]
    assert out["title"] == "Climate Change Handbook"
    assert out["journal"] == ""
    assert out["issue"] == ""


@pytest.mark.parametrize("metadata_key", ["book_metadata", "book_series_metadata"])
def test_read_book_handles_metadata_key_variants(metadata_key):
    row = make_row(ref_type="Book", ref_id="REF002", doi="10.1234/book")
    d = make_book_crossref(metadata_key=metadata_key, title="Series Title")
    out = read_book(row, d)
    assert out["title"] == "Series Title"


def test_read_book_authors_from_content_item_person_name_dict():
    row = make_row(ref_type="Book Section", ref_id="REF002", doi="10.1234/book")
    content_item = {
        "contributors": {"person_name": {"given_name": "Chapter", "surname": "Author"}}
    }
    d = make_book_crossref(title="Book Title", content_item=content_item)
    out = read_book(row, d)

    assert out["authors"] == "Chapter Author"


def test_read_book_handles_organization_contributor():
    row = make_row(ref_type="Book", ref_id="REF002", doi="10.1234/book")
    contributors = {"organization": [{"#text": "IPCC"}]}
    d = make_book_crossref(contributors=contributors)
    out = read_book(row, d)

    assert out["authors"] == "IPCC"


def test_read_book_publication_date_list_uses_first_year():
    row = make_row(ref_type="Book", ref_id="REF002", doi="10.1234/book")
    d = make_book_crossref(publication_date=[{"year": "2021"}, {"year": "2022"}])
    out = read_book(row, d)

    assert out["date"] == "2021"