import urllib.request
import urllib.error

import xmltodict


CROSSREF_ACCEPT_HEADER = ("Accept", "application/vnd.crossref.unixsd+xml")
DOI_BASE_URL = "https://doi.org/"


def scrape(row, timeout=20):
    """
    Scrape Crossref metadata for a given row, based on DOI.

    Returns:
        (response, parsed_dict)

    Raises:
        KeyError if DOI is missing from row
        URLError / HTTPError for network issues
        xmltodict parsing exceptions for malformed XML
    """
    row_doi = row["DOI"]
    row_type = row.get("Reference_Type", "Unknown")

    opener = urllib.request.build_opener()
    opener.addheaders = [CROSSREF_ACCEPT_HEADER]

    print(f"Scraping {row_type}: {row_doi}...")

    # Use https://doi.org/ and ensure the response is closed
    url = DOI_BASE_URL + row_doi
    r = opener.open(url, timeout=timeout)
    raw = r.read()
    
    d = xmltodict.parse(raw)
    return r, d


def _title_to_str(title):
    if isinstance(title, dict):
        return title.get("#text", "")
    return title


def _names_to_authors_string(names, require_role=None):
    """
    Convert Crossref person_name structure (dict or list) into "Given Surname, Given Surname".
    If require_role is set (e.g. "author"), will filter list/dict by @contributor_role.
    """
    if not names:
        return ""

    people = names if isinstance(names, list) else [names]

    out = []
    for p in people:
        if require_role is not None:
            if p.get("@contributor_role") != require_role:
                continue
        given = p.get("given_name", "")
        surname = p.get("surname", "")
        full = (given + " " + surname).strip()
        if full:
            out.append(full)

    return ", ".join(out)


def _extract_year(publication_date):
    """
    publication_date can be dict or list of dicts.
    Prefer print year, otherwise first available year.
    """
    if not publication_date:
        return ""

    if isinstance(publication_date, list):
        # Prefer print if present
        for item in publication_date:
            if item.get("@media_type") == "print" and "year" in item:
                return item["year"]
        # Otherwise fall back to first year we can find
        for item in publication_date:
            if "year" in item:
                return item["year"]
        return ""

    # dict
    return publication_date.get("year", "")


def read_article(row, d):
    """
    Read article data scraped by DOI.
    More robust handling for:
    - title as dict
    - contributors list/dict with role filtering
    - publication_date list with no print entry
    """
    journal = d["crossref_result"]["query_result"]["body"]["query"]["doi_record"]["crossref"]["journal"]
    article = journal["journal_article"]

    title = _title_to_str(article["titles"]["title"])

    # Contributors: include authors only, regardless of list/dict
    names = article.get("contributors", {}).get("person_name")
    authors = _names_to_authors_string(names, require_role="author")

    date = _extract_year(article.get("publication_date"))

    journal_title = journal["journal_metadata"]["full_title"]

    issue = ""
    if "journal_issue" in journal and "issue" in journal["journal_issue"]:
        issue = journal["journal_issue"]["issue"]

    return {
        "type": row["Reference_Type"],
        "article_id": row["Reference_ID"],
        "doi": row["DOI"],
        "link": row["URL"],
        "link_replacement": row["Replacement_URL"],
        "title": title,
        "authors": authors,
        "date": date,
        "journal": journal_title,
        "issue": issue,
    }


def _org_to_str(org):
    # org can be list[dict] or dict; prefer #text if present
    if isinstance(org, list) and org:
        org = org[0]
    if isinstance(org, dict):
        return org.get("#text", "")
    if isinstance(org, str):
        return org
    return ""


def read_book(row, d):
    """
    Read book data scraped by DOI.
    More robust handling for:
    - book_metadata vs book_series_metadata
    - title as dict
    - organization contributor shapes
    """
    book = d["crossref_result"]["query_result"]["body"]["query"]["doi_record"]["crossref"]["book"]

    main_key = "book_metadata"
    if main_key not in book:
        main_key = "book_series_metadata"

    title = _title_to_str(book[main_key]["titles"]["title"])

    authors = ""
    if "content_item" in book:
        names = book["content_item"].get("contributors", {}).get("person_name")
        authors = _names_to_authors_string(names)
    else:
        contrib = book[main_key].get("contributors", {})
        if "organization" in contrib:
            authors = _org_to_str(contrib["organization"])
        else:
            names = contrib.get("person_name")
            authors = _names_to_authors_string(names)

    date = _extract_year(book[main_key].get("publication_date"))

    return {
        "type": row["Reference_Type"],
        "doi": row["DOI"],
        "article_id": row["Reference_ID"],
        "link": row["URL"],
        "link_replacement": row["Replacement_URL"],
        "title": title,
        "authors": authors,
        "date": date,
        "journal": "",
        "issue": "",
    }