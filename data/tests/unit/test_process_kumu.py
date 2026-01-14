import pytest
import json
from unittest.mock import MagicMock, patch, mock_open

from data.src.process_kumu import ProcessKumu


# =============================================================================
# __init__ and load_data
# =============================================================================


def test_init_loads_data():
    """Should load JSON data on initialization"""
    mock_data = {"elements": [], "connections": []}
    
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        
        assert pk.data == mock_data
        assert pk.filtered_data == {}


def test_load_data_opens_file():
    """Should open and read JSON file"""
    mock_data = {"elements": [{"id": "1"}]}
    
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        
        m.assert_called_once_with("test.json")


# =============================================================================
# filter_data
# =============================================================================


def test_filter_data_filters_action_elements():
    """Should filter elements where element type is Action"""
    mock_data = {
        "elements": [
            {
                "id": "1",
                "attributes": {
                    "element type": "Action",
                    "layer": ["Coastal security In Full"],
                    "climate_hazard": "flood"
                }
            },
            {
                "id": "2",
                "attributes": {
                    "element type": "Other",
                    "layer": ["test"]
                }
            }
        ]
    }
    
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filter_data()
        
        assert len(pk.filtered_data) == 1
        assert pk.filtered_data[0]["id"] == "1"


def test_filter_data_drops_specified_keys():
    """Should drop element type, climate_hazard, un_sdg, vulnerability keys"""
    mock_data = {
        "elements": [
            {
                "id": "1",
                "attributes": {
                    "element type": "Action",
                    "layer": ["test"],
                    "climate_hazard": "flood",
                    "un_sdg": "goal1",
                    "vulnerability": "high",
                    "keep_this": "value"
                }
            }
        ]
    }
    
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filter_data()
        
        attrs = pk.filtered_data[0]["attributes"]
        assert "element type" not in attrs
        assert "climate_hazard" not in attrs
        assert "un_sdg" not in attrs
        assert "vulnerability" not in attrs
        assert "keep_this" in attrs


def test_filter_data_requires_layer_attribute():
    """Should only include elements with layer attribute"""
    mock_data = {
        "elements": [
            {
                "id": "1",
                "attributes": {
                    "element type": "Action",
                    "layer": ["test"]
                }
            },
            {
                "id": "2",
                "attributes": {
                    "element type": "Action"
                    # No layer attribute
                }
            }
        ]
    }
    
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filter_data()
        
        assert len(pk.filtered_data) == 1
        assert pk.filtered_data[0]["id"] == "1"


# =============================================================================
# update_layer_names
# =============================================================================


def test_update_layer_names_replaces_pathogenic_marine():
    """Should replace Pathogenic Marine Microorganisms with Marine Health Hazards"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filtered_data = [
            {
                "attributes": {
                    "layer": ["Pathogenic Marine Microorganisms in full"]
                }
            }
        ]
        
        pk.update_layer_names()
        
        assert pk.filtered_data[0]["attributes"]["layer"][0] == "Marine Health Hazards in full"


def test_update_layer_names_preserves_other_layers():
    """Should not modify other layer names"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filtered_data = [
            {
                "attributes": {
                    "layer": ["Coastal security In Full", "Other layer"]
                }
            }
        ]
        
        pk.update_layer_names()
        
        assert pk.filtered_data[0]["attributes"]["layer"][0] == "Coastal security In Full"
        assert pk.filtered_data[0]["attributes"]["layer"][1] == "Other layer"


# =============================================================================
# _capitalise_except_and
# =============================================================================


def test_capitalise_except_and_capitalises_words():
    """Should capitalize words except 'and'"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        
        result = pk._capitalise_except_and("food and personal security")
        assert result == "Food and Personal Security"


def test_capitalise_except_and_handles_single_word():
    """Should handle single word"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        
        result = pk._capitalise_except_and("coastal")
        assert result == "Coastal"


def test_capitalise_except_and_preserves_lowercase_and():
    """Should keep 'and' lowercase"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        
        result = pk._capitalise_except_and("this and that")
        assert result == "This and That"


# =============================================================================
# aggregate_layers
# =============================================================================


def test_aggregate_layers_splits_on_in_full():
    """Should split layers on ' in full' and capitalize"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filtered_data = [
            {
                "attributes": {
                    "layer": ["coastal security in full", "food and personal security in full"]
                }
            }
        ]
        
        pk.aggregate_layers()
        
        aggregated = pk.filtered_data[0]["attributes"]["aggregated_layers"]
        assert "Coastal Security" in aggregated
        assert "Food and Personal Security" in aggregated


def test_aggregate_layers_handles_mixed_case():
    """Should handle mixed case input"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filtered_data = [
            {
                "attributes": {
                    "layer": ["Coastal Security In Full"]
                }
            }
        ]
        
        pk.aggregate_layers()
        
        assert pk.filtered_data[0]["attributes"]["aggregated_layers"][0] == "Coastal Security"


def test_aggregate_layers_skips_layers_without_in_full():
    """Should skip layers that don't contain ' in full'"""
    m = mock_open(read_data='{"elements": []}')
    with patch("builtins.open", m):
        pk = ProcessKumu("test.json")
        pk.filtered_data = [
            {
                "attributes": {
                    "layer": ["coastal security in full", "other layer"]
                }
            }
        ]
        
        pk.aggregate_layers()
        
        aggregated = pk.filtered_data[0]["attributes"]["aggregated_layers"]
        assert len(aggregated) == 1
        assert "Coastal Security" in aggregated


# =============================================================================
# save_json
# =============================================================================


def test_save_json_writes_filtered_data():
    """Should write filtered_data to JSON file"""
    m_read = mock_open(read_data='{"elements": []}')
    m_write = mock_open()
    
    with patch("builtins.open", m_read):
        pk = ProcessKumu("test.json")
        pk.filtered_data = [{"id": "1", "attributes": {"layer": ["test"]}}]
    
    with patch("builtins.open", m_write):
        pk.save_json("output.json")
        
        m_write.assert_called_once_with("output.json", "w")


def test_save_json_creates_valid_json():
    """Should create valid JSON with indent"""
    m_read = mock_open(read_data='{"elements": []}')
    
    with patch("builtins.open", m_read):
        pk = ProcessKumu("test.json")
        pk.filtered_data = [{"test": "data"}]
    
    with patch("builtins.open", mock_open()) as m_write:
        with patch("json.dump") as mock_dump:
            pk.save_json("output.json")
            
            mock_dump.assert_called_once()
            assert mock_dump.call_args[0][0] == [{"test": "data"}]
            assert mock_dump.call_args[1]["indent"] == 4
