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

    def update_layer_names(self):
        """
        We need to update one layer name: Pathogenic Marine Microorganisms -> Marine Health Hazards.
        """

        for adaptation in self.filtered_data:
            layer_data = adaptation["attributes"]["layer"]

            for i, layer in enumerate(layer_data):
                if "Pathogenic Marine Microorganisms" in layer:
                    layer_data[i] = layer.replace("Pathogenic Marine Microorganisms", "Marine Health Hazards")

    def _capitalise_except_and(self, text):
        """
        Capitalise words except "and".
        """

        words = text.split()
        capitalized_words = [word.capitalize() if word.lower() != "and" else word for word in words]

        return " ".join(capitalized_words)

    def aggregate_layers(self):
        """
        Aggregate the clean layers and store in the .json.

        i.e. ["Coastal security In Full", "Food and personal security in full"] -> ["Coastal Security", "Food and Personal Security"]
        """

        splitter = " in full"

        for adaptation in self.filtered_data:
            layer_data = adaptation["attributes"]["layer"]
            new_layer_data = []

            for layer in layer_data:
                lower_layer = layer.lower()

                if splitter in lower_layer:
                    splits = lower_layer.split(splitter)
                    hazard = splits[0]
                    formatted_hazard = self._capitalise_except_and(hazard)
                    new_layer_data.append(formatted_hazard)

            adaptation["attributes"]["aggregated_layers"] = new_layer_data

    def save_json(self, output_filename):
        """
        Save the filtered data as a json file.
        """

        with open(output_filename, "w") as f:
            json.dump(self.filtered_data, f, indent=4)
