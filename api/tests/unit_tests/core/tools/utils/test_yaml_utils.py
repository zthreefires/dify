import pytest
from yaml import YAMLError

from core.tools.utils.yaml_utils import load_yaml_file


def test_load_yaml_file_success(tmp_path):
    # Create a temporary YAML file
    yaml_content = """
    key1: value1
    key2: value2
    """
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)

    # Test loading the file
    result = load_yaml_file(str(yaml_file))
    assert result == {"key1": "value1", "key2": "value2"}


def test_load_yaml_file_empty(tmp_path):
    # Test with empty YAML file
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("")

    result = load_yaml_file(str(yaml_file))
    assert result == {}


def test_load_yaml_file_not_found():
    # Test with non-existent file
    result = load_yaml_file("nonexistent.yaml")
    assert result == {}

    # Test with non-existent file and ignore_error=False
    with pytest.raises(FileNotFoundError) as exc_info:
        load_yaml_file("nonexistent.yaml", ignore_error=False)
    assert "File not found" in str(exc_info.value)


def test_load_yaml_file_invalid_yaml(tmp_path):
    # Create invalid YAML content
    invalid_yaml = """
    key1: value1
        invalid:
      - bad indentation
    """
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text(invalid_yaml)

    # Test with invalid YAML and ignore_error=True
    result = load_yaml_file(str(yaml_file))
    assert result == {}

    # Test with invalid YAML and ignore_error=False
    with pytest.raises(YAMLError) as exc_info:
        load_yaml_file(str(yaml_file), ignore_error=False)
    assert "Failed to load YAML file" in str(exc_info.value)


def test_load_yaml_file_custom_default():
    # Test with custom default value
    default = {"default": "value"}
    result = load_yaml_file("nonexistent.yaml", default_value=default)
    assert result == default


def test_load_yaml_file_none_path():
    # Test with None file path
    result = load_yaml_file(None)
    assert result == {}

    with pytest.raises(FileNotFoundError):
        load_yaml_file(None, ignore_error=False)


def test_load_yaml_file_empty_path():
    # Test with empty file path
    result = load_yaml_file("")
    assert result == {}

    with pytest.raises(FileNotFoundError):
        load_yaml_file("", ignore_error=False)
