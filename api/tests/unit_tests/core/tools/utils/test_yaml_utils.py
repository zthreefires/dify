from unittest.mock import patch

import pytest
from yaml import YAMLError

from core.tools.utils.yaml_utils import load_yaml_file


def test_load_yaml_file_success(tmp_path):
    yaml_content = """
    key1: value1
    key2: value2
    """
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)

    result = load_yaml_file(str(yaml_file))

    assert result == {"key1": "value1", "key2": "value2"}


def test_load_yaml_file_empty():
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        result = load_yaml_file("")
        assert result == {}


def test_load_yaml_file_not_found_error():
    with pytest.raises(FileNotFoundError) as exc_info:
        load_yaml_file("nonexistent.yaml", ignore_error=False)
    assert "File not found" in str(exc_info.value)


def test_load_yaml_file_invalid_yaml(tmp_path):
    invalid_yaml = """
    key1: value1
        invalid_indent:
    key2: value2
    """
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text(invalid_yaml)

    with pytest.raises(YAMLError) as exc_info:
        load_yaml_file(str(yaml_file), ignore_error=False)
    assert "Failed to load YAML file" in str(exc_info.value)


def test_load_yaml_file_ignore_error(tmp_path):
    invalid_yaml = """
    key1: value1
        invalid_indent:
    key2: value2
    """
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text(invalid_yaml)

    result = load_yaml_file(str(yaml_file), ignore_error=True, default_value={"default": "value"})
    assert result == {"default": "value"}


def test_load_yaml_file_empty_content(tmp_path):
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("")

    result = load_yaml_file(str(yaml_file), default_value={"default": "value"})
    assert result == {"default": "value"}


def test_load_yaml_file_none_content(tmp_path):
    yaml_file = tmp_path / "none.yaml"
    yaml_file.write_text("null")

    result = load_yaml_file(str(yaml_file), default_value={"default": "value"})
    assert result == {"default": "value"}


def test_load_yaml_file_custom_default():
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        result = load_yaml_file("", default_value=["custom", "default"])
        assert result == ["custom", "default"]


def test_load_yaml_file_complex_yaml(tmp_path):
    complex_yaml = """
    nested:
      key1: value1
      key2:
        - item1
        - item2
    list:
      - a: 1
        b: 2
      - c: 3
        d: 4
    """
    yaml_file = tmp_path / "complex.yaml"
    yaml_file.write_text(complex_yaml)

    result = load_yaml_file(str(yaml_file))
    expected = {"nested": {"key1": "value1", "key2": ["item1", "item2"]}, "list": [{"a": 1, "b": 2}, {"c": 3, "d": 4}]}
    assert result == expected
