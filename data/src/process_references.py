import json

import pandas as pd

from src import scrape_doi


class ProcessReferences:
    """
    Class to perform processing of the references from the .CSV Google Sheets.
    """

    def __init__(self, csv_filepath):
        self.df = None
        self.bad_references = {}
        self.doi_lookups = {}
        self.failed_doi_lookups = []
        self.processed_references = {}

        self.load_references(csv_filepath)

    def load_references(self, csv_filepath):
        """
        Load references from CSV file.
        """

        self.df = pd.read_csv(csv_filepath)

    def load_bad_references(self, bad_references):
        """
        Load bad reference list.
        """

        self.bad_references = bad_references

    def clean_references(self):
        """
        Clean up reference type column to ensure correct filtering by
        reference type.
        """

        dirty_reference_types = self.df["Reference_Type"].unique().tolist()

        # Create mapping of dirty strings to clean strings
        string_mapping = {}

        for dirty_string in dirty_reference_types:
            clean_string = " ".join(word.capitalize() for word in dirty_string.lower().strip().split())

            if dirty_string not in string_mapping:
                string_mapping[dirty_string] = clean_string

        self.df["Reference_Type"] = self.df["Reference_Type"].map(string_mapping)

        # Finally clean title, DOI replacement URL columns for later
        self.df["Title for website/report/article"] = self.df["Title for website/report/article"].fillna("")
        self.df["Replacement_URL"] = self.df["Replacement_URL"].fillna("")
        self.df["DOI"] = self.df["DOI"].fillna("")

    def doi_lookup_row(self, row):
        """
        Perform DOI lookup & parsing for reference row. This is brittle.
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

    def perform_doi_lookups(self):
        """
        Perform DOI lookups for all rows, considering bad references. Only references
        with DOIs will be processed.
        """

        doi_references_df = self.df.loc[~self.df["DOI"].isna()]

        print(f"{len(doi_references_df)} references with DOIs found\n")

        for index, row in doi_references_df.iterrows():
            print(f"DOI lookup: {index} / {len(doi_references_df)}")

            row_id = row["Reference_ID"]
            row_type = row["Reference_Type"]

            if row_type not in self.bad_references:
                print(f"Reference type {row_type} not included in bad_references. Attempting DOI lookup.")
                self.doi_lookup_row(row)

            else:
                if row_id in self.bad_references[row_type]:
                    print(f"Reference {row_id} is a bad reference: no lookup will be performed.")

                else:
                    self.doi_lookup_row(row)

    def process_references(self):
        """
        Process all rows, using DOI lookups if available.
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
                    "title": row["Title for website/report/article"],
                    "authors": "",
                    "date": "",
                    "journal": "",
                    "issue": "",
                }

                self.processed_references[row_id] = ref

    def save_json(self, output_filename):
        """
        Save the processed references to json.
        """

        with open(output_filename, "w") as f:
            json.dump(self.processed_references, f, indent=4)
