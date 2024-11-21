import json


class ProcessKumu:
    """
    Class to handle processing of a Kumu data export, provided as json.
    """

    def __init__(self, filename):
        self.data = None
        self.filtered_data = {}
        self.load_data(filename)

    def load_data(self, filename):
        """
        Load adaptation data from Kumu export, i.e. the json file.
        """

        with open(filename) as file:
            self.data = json.load(file)

    def filter_data(self):
        """
        Filter the data, retaining "Action" elements (i.e. adaptation data),
        and dropping other keys that are not required.
        """

        keys_to_drop = ["element type", "climate_hazard", "un_sdg", "vulnerability"]

        adaptation_elements = [
            e
            for e in self.data["elements"]
            if "element type" in e["attributes"] and e["attributes"]["element type"] == "Action"
        ].copy()

        self.filtered_data = [
            {
                **element,
                "attributes": {k: v for k, v in element["attributes"].items() if k not in keys_to_drop},
            }
            for element in adaptation_elements
            if "layer" in element["attributes"]
        ]

    def save_json(self, output_filename):
        """
        Save the filtered data as a json file.
        """

        with open(output_filename, "w") as f:
            json.dump(self.filtered_data, f, indent=4)
