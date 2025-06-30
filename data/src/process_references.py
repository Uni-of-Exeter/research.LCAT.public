import json

import pandas as pd

from src import scrape_doi


class ProcessReferences:
    """
    Class to perform processing of the references from the .CSV Google Sheets to a .json file.
    """

    def __init__(self, csv_filepath):
        self.df = None
        self.doi_lookups = {}
        self.failed_doi_lookups = []
        self.processed_references = {}

        self.load_references(csv_filepath)

    def load_references(self, csv_filepath):
        """
        Load references from CSV file. This should be downloaded from Google Sheets.
        """

        self.df = pd.read_csv(csv_filepath)

    def clean_references(self):
        """
        Clean up reference type column to ensure correct filtering by reference type.
        """

        dirty_reference_types = self.df["Reference_Type"].unique().tolist()

        # Create mapping of dirty strings to clean strings
        string_mapping = {}

        for dirty_string in dirty_reference_types:
            clean_string = " ".join(word.capitalize() for word in dirty_string.lower().strip().split())

            if dirty_string not in string_mapping:
                string_mapping[dirty_string] = clean_string

        self.df["Reference_Type"] = self.df["Reference_Type"].map(string_mapping)

        # Finally replace NaNs with ""
        self.df.fillna("", inplace=True)

    def doi_lookup_row(self, row):
        """
        Perform DOI lookup & parsing for reference row. This scraping is brittle. Failed lookups are stored
        only for investigation: they are not used later on. If successful scraping occurs, the data is stored
        in self.doi_lookups, keyed by row_id, and
        """

        row_type = row["Reference_Type"]
        row_id = row["Reference_ID"]

        # Scrape data
        try:
            response, data = scrape_doi.scrape(row)
        except Exception:
            self.failed_doi_lookups.append(row_id)

        # Parse result
        if row_type == "Journal Article" or row_type == "Report":
            try:
                self.doi_lookups[row_id] = scrape_doi.read_article(row, data)
            except Exception:
                print(f"DOI Journal Article parsing failed for reference ID: {row_id}")
                self.failed_doi_lookups.append(row_id)

        elif row_type == "Book" or row_type == "Book Section":
            try:
                self.doi_lookups[row_id] = scrape_doi.read_book(row, data)
            except Exception:
                print(f"DOI Book parsing failed for reference ID: {row_id}")
                self.failed_doi_lookups.append(row_id)

        else:
            print("Neither Journal Article nor Book found: no DOI lookup performed")
            return

    def perform_doi_lookups(self, scrape_all_rows=False):
        """
        Perform DOI lookups. Set scrape_all_rows to True to scrape all rows (with DOIs) from scratch, which would
        take a while. If set to False, only rows with no titles are scraped.
        """

        # Perform scraping for all rows with a DOI, even if they have data already
        if scrape_all_rows:
            rows_to_scrape_df = self.df.loc[self.df["DOI"] != ""]

        # Perform scraping only for rows with a DOI with no title
        else:
            rows_to_scrape_df = self.df.loc[(self.df["DOI"] != "") & (self.df["Title"] == "")]

        print(f"{len(rows_to_scrape_df)} references found for scraping\n")

        for index, row in rows_to_scrape_df.iterrows():
            print(f"DOI lookup: {index} / {len(rows_to_scrape_df)}")
            self.doi_lookup_row(row)

    def process_references(self):
        """
        Process all rows, using DOI lookups if available. Remember that if the the titles and DOIs are
        present, no scraping will occur, and the original rows will be used.
        """

        for _, row in self.df.iterrows():
            row_id = row["Reference_ID"]

            if row_id in self.doi_lookups:
                self.processed_references[row_id] = self.doi_lookups[row_id]

            else:
                ref = {
                    "type": row["Reference_Type"],
                    "doi": row["DOI"],
                    "article_id": row_id,
                    "link": row["URL"],
                    "link_replacement": row["Replacement_URL"],
                    "title": row["Title"],
                    "authors": row["Authors"],
                    "date": row["Date"],
                    "journal": row["Journal"],
                    "issue": row["Volume/Issue"],
                }

                self.processed_references[row_id] = ref

        print(f"{len(self.processed_references)} references will be saved in the json.")

    def save_json(self, output_filename):
        """
        Save the processed references to json.
        """

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(self.processed_references, f, ensure_ascii=False, indent=4)
