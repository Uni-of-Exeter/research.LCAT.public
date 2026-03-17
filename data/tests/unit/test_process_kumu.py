import json
import pytest
from unittest.mock import mock_open, patch

from data.src.process_kumu import ProcessKumu


# -----------------------------------------------------------------------------
# helpers / fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def pk_from_data():
    """
    Build ProcessKumu with mocked file IO returning the given dict.
    Usage:
        pk = pk_from_data({"elements": [...]})
    """
    def _make(data):
        m = mock_open(read_data=json.dumps(data))
        with patch("builtins.open", m):
            return ProcessKumu("input.json")
    return _make


# -----------------------------------------------------------------------------
# load_data / init
# -----------------------------------------------------------------------------

def test_init_loads_json(pk_from_data):
    pk = pk_from_data({"elements": [], "connections": []})
    assert pk.data == {"elements": [], "connections": []}
    # Don't over-specify type here; class currently sets {} then later becomes list
    assert pk.filtered_data == {} or pk.filtered_data == []


def test_load_data_opens_filename(pk_from_data):
    data = {"elements": []}
    m = mock_open(read_data=json.dumps(data))
    with patch("builtins.open", m):
        ProcessKumu("myfile.json")
    m.assert_called_once_with("myfile.json")


# -----------------------------------------------------------------------------
# filter_data
# -----------------------------------------------------------------------------

def test_filter_data_keeps_only_action_with_layer_and_drops_keys(pk_from_data):
    pk = pk_from_data(
        {
            "elements": [
                # keep: Action + has layer
                {
                    "id": "keep",
                    "attributes": {
                        "element type": "Action",
                        "layer": ["Coastal security In Full"],
                        "climate_hazard": "flood",
                        "un_sdg": "x",
                        "vulnerability": "y",
                        "keep_this": "ok",
                    },
                },
                # drop: Action but missing layer
                {"id": "no_layer", "attributes": {"element type": "Action"}},
                # drop: not an Action
                {"id": "not_action", "attributes": {"element type": "Other", "layer": ["x"]}},
                # drop: missing "element type" entirely
                {"id": "no_type", "attributes": {"layer": ["x"]}},
            ]
        }
    )

    pk.filter_data()

    assert isinstance(pk.filtered_data, list)
    assert [e["id"] for e in pk.filtered_data] == ["keep"]

    attrs = pk.filtered_data[0]["attributes"]
    # dropped keys
    assert "element type" not in attrs
    assert "climate_hazard" not in attrs
    assert "un_sdg" not in attrs
    assert "vulnerability" not in attrs
    # preserved key
    assert attrs["keep_this"] == "ok"
    # layer preserved
    assert attrs["layer"] == ["Coastal security In Full"]


# -----------------------------------------------------------------------------
# update_layer_names
# -----------------------------------------------------------------------------

def test_update_layer_names_replaces_only_matching_phrase(pk_from_data):
    pk = pk_from_data({"elements": []})
    pk.filtered_data = [
        {"attributes": {"layer": ["Pathogenic Marine Microorganisms in full", "Other layer"]}},
        {"attributes": {"layer": ["Unrelated"]}},
    ]

    pk.update_layer_names()

    assert pk.filtered_data[0]["attributes"]["layer"][0] == "Marine Health Hazards in full"
    assert pk.filtered_data[0]["attributes"]["layer"][1] == "Other layer"
    assert pk.filtered_data[1]["attributes"]["layer"][0] == "Unrelated"


# -----------------------------------------------------------------------------
# _capitalise_except_and
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "text, expected",
    [
        ("food and personal security", "Food and Personal Security"),
        ("coastal", "Coastal"),
        ("THIS and that", "This and That"),  # note: .capitalize() normalises
        ("and", "and"),
    ],
)
def test_capitalise_except_and(text, expected, pk_from_data):
    pk = pk_from_data({"elements": []})
    assert pk._capitalise_except_and(text) == expected


# -----------------------------------------------------------------------------
# aggregate_layers
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "layers, expected",
    [
        (
            ["coastal security in full", "food and personal security in full"],
            ["Coastal Security", "Food and Personal Security"],
        ),
        (
            ["Coastal Security In Full"],
            ["Coastal Security"],
        ),
        (
            ["coastal security in full", "other layer"],
            ["Coastal Security"],
        ),
        (
            ["other layer"],
            [],
        ),
    ],
)
def test_aggregate_layers_extracts_and_formats_hazards(pk_from_data, layers, expected):
    pk = pk_from_data({"elements": []})
    pk.filtered_data = [{"attributes": {"layer": layers}}]

    pk.aggregate_layers()

    assert pk.filtered_data[0]["attributes"]["aggregated_layers"] == expected


def test_aggregate_layers_does_not_mutate_original_layer_list(pk_from_data):
    pk = pk_from_data({"elements": []})
    layers = ["coastal security in full", "other layer"]
    pk.filtered_data = [{"attributes": {"layer": layers[:]}}]

    pk.aggregate_layers()

    assert pk.filtered_data[0]["attributes"]["layer"] == layers  # unchanged
    assert pk.filtered_data[0]["attributes"]["aggregated_layers"] == ["Coastal Security"]


# -----------------------------------------------------------------------------
# save_json
# -----------------------------------------------------------------------------

def test_save_json_calls_json_dump_with_indent_4(pk_from_data):
    pk = pk_from_data({"elements": []})
    pk.filtered_data = [{"id": "1", "attributes": {"layer": ["test"]}}]

    m = mock_open()
    with patch("builtins.open", m) as open_mock, patch("json.dump") as dump_mock:
        pk.save_json("output.json")

    open_mock.assert_called_once_with("output.json", "w")
    # Ensure we dump the filtered_data into the file handle returned by open()
    dump_mock.assert_called_once()
    args, kwargs = dump_mock.call_args
    assert args[0] == pk.filtered_data
    assert args[1] == open_mock.return_value.__enter__.return_value
    assert kwargs["indent"] == 4