import json

import pytest

from core.llm_generator.output_parser.errors import OutputParserError
from libs.json_in_md_parser import parse_and_check_json_markdown, parse_json_markdown


def test_parse_json_markdown_with_code_block():
    json_str = """```json
    {
        "key": "value"
    }
    ```"""
    result = parse_json_markdown(json_str)
    assert result == {"key": "value"}


def test_parse_json_markdown_with_backticks():
    json_str = """`{"key": "value"}`"""
    result = parse_json_markdown(json_str)
    assert result == {"key": "value"}


def test_parse_json_markdown_with_braces():
    json_str = """{"key": "value"}"""
    result = parse_json_markdown(json_str)
    assert result == {"key": "value"}


def test_parse_json_markdown_invalid():
    json_str = """some text without json"""
    with pytest.raises(ValueError) as exc_info:
        parse_json_markdown(json_str)
    assert str(exc_info.value) == "could not find json block in the output."


def test_parse_json_markdown_malformed():
    json_str = """```json
    {
        "key": "value",
    }
    ```"""
    with pytest.raises(json.JSONDecodeError):
        parse_json_markdown(json_str)


def test_parse_and_check_json_markdown_valid():
    json_str = """```json
    {
        "key1": "value1",
        "key2": "value2"
    }
    ```"""
    result = parse_and_check_json_markdown(json_str, ["key1", "key2"])
    assert result == {"key1": "value1", "key2": "value2"}


def test_parse_and_check_json_markdown_missing_key():
    json_str = """```json
    {
        "key1": "value1"
    }
    ```"""
    with pytest.raises(OutputParserError) as exc_info:
        parse_and_check_json_markdown(json_str, ["key1", "key2"])
    assert "expected key `key2` to be present" in str(exc_info.value)


def test_parse_and_check_json_markdown_invalid_json():
    json_str = """```json
    {
        "key1": "value1",
    }
    ```"""
    with pytest.raises(OutputParserError) as exc_info:
        parse_and_check_json_markdown(json_str, ["key1"])
    assert "got invalid json object" in str(exc_info.value)


def test_parse_json_markdown_nested():
    json_str = """```json
    {
        "key1": {
            "nested": "value"
        },
        "key2": [1, 2, 3]
    }
    ```"""
    result = parse_json_markdown(json_str)
    assert result == {"key1": {"nested": "value"}, "key2": [1, 2, 3]}


def test_parse_json_markdown_empty():
    json_str = """```json
    {}
    ```"""
    result = parse_json_markdown(json_str)
    assert result == {}


def test_parse_json_markdown_multiple_blocks():
    json_str = """```json
    {"key": "value"}
    ```"""
    result = parse_json_markdown(json_str)
    assert result == {"key": "value"}


def test_parse_json_markdown_with_whitespace():
    json_str = """

    ```json
    {
        "key": "value"
    }
    ```

    """
    result = parse_json_markdown(json_str)
    assert result == {"key": "value"}


def test_parse_json_markdown_with_double_backticks():
    json_str = """``{"key": "value"}``"""
    result = parse_json_markdown(json_str)
    assert result == {"key": "value"}


def test_parse_json_markdown_with_mixed_quotes():
    json_str = """```json
    {
        "key1": 'value1',
        "key2": "value2"
    }
    ```"""
    with pytest.raises(json.JSONDecodeError):
        parse_json_markdown(json_str)


def test_parse_json_markdown_with_comments():
    json_str = """```json
    {
        // This is a comment
        "key": "value"
    }
    ```"""
    with pytest.raises(json.JSONDecodeError):
        parse_json_markdown(json_str)


def test_parse_and_check_json_markdown_empty_keys():
    json_str = """```json
    {
        "key1": "value1"
    }
    ```"""
    result = parse_and_check_json_markdown(json_str, [])
    assert result == {"key1": "value1"}


def test_parse_and_check_json_markdown_with_null_values():
    json_str = """```json
    {
        "key1": null,
        "key2": "value2"
    }
    ```"""
    result = parse_and_check_json_markdown(json_str, ["key1", "key2"])
    assert result == {"key1": None, "key2": "value2"}