import operator
from collections import OrderedDict
from unittest.mock import patch

from core.helper.position_helper import (
    get_position_map,
    get_provider_position_map,
    get_tool_position_map,
    is_filtered,
    pin_position_map,
    sort_by_position_map,
    sort_to_dict_by_position_map,
)


def test_get_position_map(tmp_path):
    yaml_content = """
    - item1
    - item2
    - item3
    """
    position_file = tmp_path / "_position.yaml"
    position_file.write_text(yaml_content)

    result = get_position_map(str(tmp_path))
    assert result == {"item1": 0, "item2": 1, "item3": 2}


def test_get_position_map_empty(tmp_path):
    position_file = tmp_path / "_position.yaml"
    position_file.write_text("")

    result = get_position_map(str(tmp_path))
    assert result == {}


def test_get_position_map_invalid_items(tmp_path):
    yaml_content = """
    - item1
    - 123
    - ""
    - item2
    """
    position_file = tmp_path / "_position.yaml"
    position_file.write_text(yaml_content)

    result = get_position_map(str(tmp_path))
    assert result == {"item1": 0, "item2": 1}


def test_pin_position_map():
    original_map = {"a": 0, "b": 1, "c": 2, "d": 3}
    pin_list = ["c", "a"]

    result = pin_position_map(original_map, pin_list)
    assert result == {"c": 0, "a": 1, "b": 2, "d": 3}


def test_pin_position_map_empty():
    assert pin_position_map({}, []) == {}
    assert pin_position_map({"a": 0}, []) == {"a": 0}
    assert pin_position_map({}, ["a"]) == {"a": 0}


def test_is_filtered():
    include_set = {"item1", "item2"}
    exclude_set = {"item3"}

    assert not is_filtered(include_set, exclude_set, {"name": "item1"}, operator.itemgetter("name"))
    assert not is_filtered(include_set, exclude_set, {"name": "item2"}, operator.itemgetter("name"))
    assert is_filtered(include_set, exclude_set, {"name": "item3"}, operator.itemgetter("name"))
    assert is_filtered(include_set, exclude_set, {"name": "item4"}, operator.itemgetter("name"))


def test_is_filtered_empty_sets():
    assert not is_filtered(set(), set(), {"name": "item1"}, operator.itemgetter("name"))
    assert not is_filtered(set(), set(), None, operator.itemgetter("name"))


def test_sort_by_position_map():
    position_map = {"a": 0, "b": 1, "c": 2}
    data = [{"name": "c"}, {"name": "a"}, {"name": "b"}, {"name": "d"}]

    result = sort_by_position_map(position_map, data, operator.itemgetter("name"))
    assert [item["name"] for item in result] == ["a", "b", "c", "d"]


def test_sort_by_position_map_empty():
    assert sort_by_position_map({}, [], operator.itemgetter("name")) == []
    assert sort_by_position_map(None, [], operator.itemgetter("name")) == []


def test_sort_to_dict_by_position_map():
    position_map = {"a": 0, "b": 1, "c": 2}
    data = [{"name": "c"}, {"name": "a"}, {"name": "b"}, {"name": "d"}]

    result = sort_to_dict_by_position_map(position_map, data, operator.itemgetter("name"))
    assert list(result.keys()) == ["a", "b", "c", "d"]
    assert isinstance(result, OrderedDict)


@patch("core.helper.position_helper.dify_config")
def test_get_tool_position_map(mock_config, tmp_path):
    mock_config.POSITION_TOOL_PINS_LIST = ["tool1", "tool2"]

    yaml_content = """
    - tool1
    - tool3
    - tool2
    """
    position_file = tmp_path / "_position.yaml"
    position_file.write_text(yaml_content)

    result = get_tool_position_map(str(tmp_path))
    assert result == {"tool1": 0, "tool2": 1, "tool3": 2}


@patch("core.helper.position_helper.dify_config")
def test_get_provider_position_map(mock_config, tmp_path):
    mock_config.POSITION_PROVIDER_PINS_LIST = ["provider1", "provider2"]

    yaml_content = """
    - provider1
    - provider3
    - provider2
    """
    position_file = tmp_path / "_position.yaml"
    position_file.write_text(yaml_content)

    result = get_provider_position_map(str(tmp_path))
    assert result == {"provider1": 0, "provider2": 1, "provider3": 2}
