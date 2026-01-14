import pytest
from unittest.mock import MagicMock, patch, mock_open

from data.src.scrape_doi import scrape, read_article, read_book


# =============================================================================
# scrape
# =============================================================================


@patch("data.src.scrape_doi.urllib.request.build_opener")
def test_scrape_builds_opener_with_accept_header(mock_build_opener):
    """Should build opener with crossref accept header"""
    mock_opener = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'<?xml version="1.0"?><crossref_result></crossref_result>'
    mock_opener.open.return_value = mock_response
    mock_build_opener.return_value = mock_opener
    
    row = {"DOI": "10.1234/test", "Reference_Type": "Journal Article"}
    
    scrape(row)
    
    assert mock_opener.addheaders == [("Accept", "application/vnd.crossref.unixsd+xml")]


@patch("data.src.scrape_doi.urllib.request.build_opener")
def test_scrape_opens_doi_url(mock_build_opener):
    """Should open DOI URL with dx.doi.org"""
    mock_opener = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'<?xml version="1.0"?><crossref_result></crossref_result>'
    mock_opener.open.return_value = mock_response
    mock_build_opener.return_value = mock_opener
    
    row = {"DOI": "10.1234/test", "Reference_Type": "Journal Article"}
    
    scrape(row)
    
    mock_opener.open.assert_called_once_with("http://dx.doi.org/10.1234/test")


@patch("data.src.scrape_doi.urllib.request.build_opener")
def test_scrape_returns_response_and_parsed_data(mock_build_opener):
    """Should return response and parsed XML data"""
    mock_opener = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'<?xml version="1.0"?><crossref_result><test>data</test></crossref_result>'
    mock_opener.open.return_value = mock_response
    mock_build_opener.return_value = mock_opener
    
    row = {"DOI": "10.1234/test", "Reference_Type": "Journal Article"}
    
    response, data = scrape(row)
    
    assert response == mock_response
    assert isinstance(data, dict)


@patch("data.src.scrape_doi.urllib.request.build_opener")
def test_scrape_parses_xml_response(mock_build_opener):
    """Should parse XML response using xmltodict"""
    mock_opener = MagicMock()
    mock_response = MagicMock()
    mock_response.read.return_value = b'<?xml version="1.0"?><root><element>value</element></root>'
    mock_opener.open.return_value = mock_response
    mock_build_opener.return_value = mock_opener
    
    row = {"DOI": "10.1234/test", "Reference_Type": "Journal Article"}
    
    _, data = scrape(row)
    
    assert "root" in data
    assert data["root"]["element"] == "value"


# =============================================================================
# read_article
# =============================================================================


def test_read_article_extracts_title():
    """Should extract article title"""
    row = {
        "Reference_Type": "Journal Article",
        "Reference_ID": "REF001",
        "DOI": "10.1234/test",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "journal": {
                                    "journal_article": {
                                        "titles": {"title": "Test Paper Title"},
                                        "contributors": {"person_name": {"given_name": "John", "surname": "Doe", "@contributor_role": "author"}},
                                        "publication_date": {"year": "2020"}
                                    },
                                    "journal_metadata": {"full_title": "Test Journal"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_article(row, data)
    
    assert result["title"] == "Test Paper Title"


def test_read_article_extracts_authors():
    """Should extract and format author names"""
    row = {
        "Reference_Type": "Journal Article",
        "Reference_ID": "REF001",
        "DOI": "10.1234/test",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "journal": {
                                    "journal_article": {
                                        "titles": {"title": "Test Paper"},
                                        "contributors": {
                                            "person_name": [
                                                {"given_name": "John", "surname": "Doe", "@contributor_role": "author"},
                                                {"given_name": "Jane", "surname": "Smith", "@contributor_role": "author"}
                                            ]
                                        },
                                        "publication_date": {"year": "2020"}
                                    },
                                    "journal_metadata": {"full_title": "Test Journal"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_article(row, data)
    
    assert "John Doe" in result["authors"]
    assert "Jane Smith" in result["authors"]


def test_read_article_extracts_year():
    """Should extract publication year"""
    row = {
        "Reference_Type": "Journal Article",
        "Reference_ID": "REF001",
        "DOI": "10.1234/test",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "journal": {
                                    "journal_article": {
                                        "titles": {"title": "Test Paper"},
                                        "contributors": {"person_name": {"given_name": "John", "surname": "Doe", "@contributor_role": "author"}},
                                        "publication_date": {"year": "2020"}
                                    },
                                    "journal_metadata": {"full_title": "Test Journal"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_article(row, data)
    
    assert result["date"] == "2020"


def test_read_article_extracts_journal_title():
    """Should extract journal title"""
    row = {
        "Reference_Type": "Journal Article",
        "Reference_ID": "REF001",
        "DOI": "10.1234/test",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "journal": {
                                    "journal_article": {
                                        "titles": {"title": "Test Paper"},
                                        "contributors": {"person_name": {"given_name": "John", "surname": "Doe", "@contributor_role": "author"}},
                                        "publication_date": {"year": "2020"}
                                    },
                                    "journal_metadata": {"full_title": "Nature Climate Change"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_article(row, data)
    
    assert result["journal"] == "Nature Climate Change"


def test_read_article_includes_all_required_fields():
    """Should include all required fields in result"""
    row = {
        "Reference_Type": "Journal Article",
        "Reference_ID": "REF001",
        "DOI": "10.1234/test",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "journal": {
                                    "journal_article": {
                                        "titles": {"title": "Test"},
                                        "contributors": {"person_name": {"given_name": "J", "surname": "D", "@contributor_role": "author"}},
                                        "publication_date": {"year": "2020"}
                                    },
                                    "journal_metadata": {"full_title": "Journal"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_article(row, data)
    
    assert "type" in result
    assert "article_id" in result
    assert "doi" in result
    assert "link" in result
    assert "link_replacement" in result
    assert "title" in result
    assert "authors" in result
    assert "date" in result
    assert "journal" in result
    assert "issue" in result


def test_read_article_handles_dict_title():
    """Should handle title as dict with #text key"""
    row = {
        "Reference_Type": "Journal Article",
        "Reference_ID": "REF001",
        "DOI": "10.1234/test",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "journal": {
                                    "journal_article": {
                                        "titles": {"title": {"#text": "Test Paper with Dict Title"}},
                                        "contributors": {"person_name": {"given_name": "John", "surname": "Doe", "@contributor_role": "author"}},
                                        "publication_date": {"year": "2020"}
                                    },
                                    "journal_metadata": {"full_title": "Journal"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_article(row, data)
    
    assert result["title"] == "Test Paper with Dict Title"


# =============================================================================
# read_book
# =============================================================================


def test_read_book_extracts_title():
    """Should extract book title"""
    row = {
        "Reference_Type": "Book",
        "Reference_ID": "REF002",
        "DOI": "10.1234/book",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "book": {
                                    "book_metadata": {
                                        "titles": {"title": "Climate Change Handbook"},
                                        "contributors": {"person_name": {"given_name": "John", "surname": "Doe"}},
                                        "publication_date": {"year": "2020"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_book(row, data)
    
    assert result["title"] == "Climate Change Handbook"


def test_read_book_extracts_authors_from_content_item():
    """Should extract authors from content_item"""
    row = {
        "Reference_Type": "Book Section",
        "Reference_ID": "REF002",
        "DOI": "10.1234/book",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "book": {
                                    "book_metadata": {
                                        "titles": {"title": "Book Title"},
                                        "contributors": {"person_name": {"given_name": "Editor", "surname": "Name"}},
                                        "publication_date": {"year": "2020"}
                                    },
                                    "content_item": {
                                        "contributors": {
                                            "person_name": {"given_name": "Chapter", "surname": "Author"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_book(row, data)
    
    assert "Chapter Author" in result["authors"]


def test_read_book_extracts_year():
    """Should extract publication year"""
    row = {
        "Reference_Type": "Book",
        "Reference_ID": "REF002",
        "DOI": "10.1234/book",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "book": {
                                    "book_metadata": {
                                        "titles": {"title": "Test Book"},
                                        "contributors": {"person_name": {"given_name": "J", "surname": "D"}},
                                        "publication_date": {"year": "2021"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_book(row, data)
    
    assert result["date"] == "2021"


def test_read_book_handles_book_series_metadata():
    """Should handle book_series_metadata instead of book_metadata"""
    row = {
        "Reference_Type": "Book",
        "Reference_ID": "REF002",
        "DOI": "10.1234/book",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "book": {
                                    "book_series_metadata": {
                                        "titles": {"title": "Book Series Title"},
                                        "contributors": {"person_name": {"given_name": "Series", "surname": "Editor"}},
                                        "publication_date": {"year": "2020"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_book(row, data)
    
    assert result["title"] == "Book Series Title"


def test_read_book_includes_all_required_fields():
    """Should include all required fields in result"""
    row = {
        "Reference_Type": "Book",
        "Reference_ID": "REF002",
        "DOI": "10.1234/book",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "book": {
                                    "book_metadata": {
                                        "titles": {"title": "Test"},
                                        "contributors": {"person_name": {"given_name": "A", "surname": "B"}},
                                        "publication_date": {"year": "2020"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_book(row, data)
    
    assert "type" in result
    assert "article_id" in result
    assert "doi" in result
    assert "link" in result
    assert "link_replacement" in result
    assert "title" in result
    assert "authors" in result
    assert "date" in result
    assert "journal" in result  # Empty for books
    assert "issue" in result  # Empty for books


def test_read_book_handles_organization_contributor():
    """Should handle organization as contributor"""
    row = {
        "Reference_Type": "Book",
        "Reference_ID": "REF002",
        "DOI": "10.1234/book",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "book": {
                                    "book_metadata": {
                                        "titles": {"title": "Test Book"},
                                        "contributors": {
                                            "organization": [{"#text": "IPCC"}]
                                        },
                                        "publication_date": {"year": "2020"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_book(row, data)
    
    assert "IPCC" in result["authors"]


def test_read_book_handles_list_of_authors():
    """Should handle multiple authors as list"""
    row = {
        "Reference_Type": "Book",
        "Reference_ID": "REF002",
        "DOI": "10.1234/book",
        "URL": "http://example.com",
        "Replacement_URL": ""
    }
    
    data = {
        "crossref_result": {
            "query_result": {
                "body": {
                    "query": {
                        "doi_record": {
                            "crossref": {
                                "book": {
                                    "book_metadata": {
                                        "titles": {"title": "Test Book"},
                                        "contributors": {
                                            "person_name": [
                                                {"given_name": "First", "surname": "Author"},
                                                {"given_name": "Second", "surname": "Author"}
                                            ]
                                        },
                                        "publication_date": {"year": "2020"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    result = read_book(row, data)
    
    assert "First Author" in result["authors"]
    assert "Second Author" in result["authors"]
