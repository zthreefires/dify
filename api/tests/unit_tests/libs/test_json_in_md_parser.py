import pytest

from core.llm_generator.output_parser.errors import OutputParserError
from libs.json_in_md_parser import parse_and_check_json_markdown, parse_json_markdown


def test_parse_json_markdown_with_code_block():
    json_str = """```json
    {
        "key": "value",
        "number": 42
    }
    ```"""
    expected = {"key": "value", "number": 42}
    assert parse_json_markdown(json_str) == expected


def test_parse_json_markdown_with_backticks():
    json_str = """`{"key": "value"}`"""
    expected = {"key": "value"}
    assert parse_json_markdown(json_str) == expected


def test_parse_json_markdown_with_braces():
    json_str = """{"key": "value"}"""
    expected = {"key": "value"}
    assert parse_json_markdown(json_str) == expected


def test_parse_json_markdown_with_whitespace():
    json_str = """
    ```json
    {
        "key": "value"
    }
    ```
    """
    expected = {"key": "value"}
    assert parse_json_markdown(json_str) == expected


def test_parse_json_markdown_invalid():
    json_str = "This is not JSON"
    with pytest.raises(ValueError, match="could not find json block in the output."):
        parse_json_markdown(json_str)


def test_parse_and_check_json_markdown_valid():
    json_str = """```json
    {
        "key1": "value1",
        "key2": "value2"
    }
    ```"""
    expected_keys = ["key1", "key2"]
    result = parse_and_check_json_markdown(json_str, expected_keys)
    assert result == {"key1": "value1", "key2": "value2"}


def test_parse_and_check_json_markdown_missing_key():
    json_str = """```json
    {
        "key1": "value1"
    }
    ```"""
    expected_keys = ["key1", "missing_key"]
    with pytest.raises(OutputParserError, match="got invalid return object"):
        parse_and_check_json_markdown(json_str, expected_keys)


def test_parse_and_check_json_markdown_invalid_json():
    json_str = """```json
    {
        "key1": "value1",
        invalid json
    }
    ```"""
    expected_keys = ["key1"]
    with pytest.raises(OutputParserError, match="got invalid json object"):
        parse_and_check_json_markdown(json_str, expected_keys)


def test_parse_json_markdown_nested():
    json_str = """```json
    {
        "key": {
            "nested": "value",
            "array": [1, 2, 3]
        }
    }
    ```"""
    expected = {"key": {"nested": "value", "array": [1, 2, 3]}}
    assert parse_json_markdown(json_str) == expected


def test_parse_json_markdown_empty_object():
    json_str = """```json
    {}
    ```"""
    expected = {}
    assert parse_json_markdown(json_str) == expected
