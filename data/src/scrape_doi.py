import urllib.request

import xmltodict


def scrape(row):
    """
    Scrapes reference information for a given row, based on DOI.
    """

    row_doi = row["DOI"]
    row_type = row["Reference_Type"]

    opener = urllib.request.build_opener()
    opener.addheaders = [("Accept", "application/vnd.crossref.unixsd+xml")]

    print(f"Scraping {row_type}: {row_doi}...")

    r = opener.open("http://dx.doi.org/" + row_doi)
    d = xmltodict.parse(r.read())

    return r, d


def read_article(row, d):
    """
    Read article data scraped by DOI.
    """

    journal = d["crossref_result"]["query_result"]["body"]["query"]["doi_record"]["crossref"]["journal"]
    article = journal["journal_article"]
    title = article["titles"]["title"]

    if isinstance(title, dict):
        title = title["#text"]

    authors = ""

    alist = article["contributors"]["person_name"]
    if isinstance(alist, list):
        for contributor in alist:
            if contributor["@contributor_role"] == "author":
                authors += contributor["given_name"] + " " + contributor["surname"] + ", "
    else:
        authors += alist["given_name"] + " " + alist["surname"] + ", "

    date = ""
    if isinstance(article["publication_date"], list):
        for d in article["publication_date"]:
            if d["@media_type"] == "print":
                date = d["year"]
    else:
        date = article["publication_date"]["year"]

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
        "authors": authors.strip(", "),
        "date": date,
        "journal": journal_title,
        "issue": issue,
    }


def read_book(row, d):
    """
    Read book data scraped by DOI.
    """

    book = d["crossref_result"]["query_result"]["body"]["query"]["doi_record"]["crossref"]["book"]

    main_key = "book_metadata"
    if main_key not in book:
        main_key = "book_series_metadata"

    title = book[main_key]["titles"]["title"]

    authors = ""
    if "content_item" in book:
        names = book["content_item"]["contributors"]["person_name"]
        if isinstance(names, list):
            for contributor in names:
                authors += contributor["given_name"] + " " + contributor["surname"] + ", "
        else:
            authors += names["given_name"] + " " + names["surname"] + ", "
    else:
        if "organization" in book[main_key]["contributors"]:
            contributor = book[main_key]["contributors"]["organization"][0]
            authors += contributor["#text"]
        else:
            names = book[main_key]["contributors"]["person_name"]

            if isinstance(names, list):
                for contributor in names:
                    authors += contributor["given_name"] + " " + contributor["surname"] + ", "

            else:
                contributor = book[main_key]["contributors"]["person_name"]
                authors += contributor["given_name"] + " " + contributor["surname"] + ", "

    date_struct = book[main_key]["publication_date"]

    date = date_struct[0]["year"] if isinstance(date_struct, list) else date_struct["year"]

    journal_title = ""
    issue = ""

    return {
        "type": row["Reference_Type"],
        "doi": row["DOI"],
        "article_id": row["Reference_ID"],
        "link": row["URL"],
        "link_replacement": row["Replacement_URL"],
        "title": title,
        "authors": authors.strip(", "),
        "date": date,
        "journal": journal_title,
        "issue": issue,
    }
