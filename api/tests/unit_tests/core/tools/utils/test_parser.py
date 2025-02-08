import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from core.tools.entities.tool_entities import ToolParameter
from core.tools.errors import ToolApiSchemaError, ToolNotSupportedError, ToolProviderNotFoundError
from core.tools.utils.parser import ApiBasedToolSchemaParser


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def basic_openapi_dict():
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "description": "Test Description", "version": "1.0.0"},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {
            "/test": {
                "get": {
                    "operationId": "testOperation",
                    "description": "Test endpoint",
                    "parameters": [
                        {
                            "name": "param1",
                            "description": "Test parameter",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                }
            }
        },
    }


def test_get_tool_parameter_type():
    # Test string type
    param = {"type": "string"}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) == ToolParameter.ToolParameterType.STRING

    # Test number type
    param = {"type": "integer"}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) == ToolParameter.ToolParameterType.NUMBER
    param = {"type": "number"}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) == ToolParameter.ToolParameterType.NUMBER

    # Test boolean type
    param = {"type": "boolean"}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) == ToolParameter.ToolParameterType.BOOLEAN

    # Test file type
    param = {"format": "binary"}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) == ToolParameter.ToolParameterType.FILE

    # Test schema type
    param = {"schema": {"type": "string"}}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) == ToolParameter.ToolParameterType.STRING

    # Test empty parameter
    param = {}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) is None

    # Test unknown type
    param = {"type": "unknown"}
    assert ApiBasedToolSchemaParser._get_tool_parameter_type(param) is None


def test_parse_openapi_yaml_to_tool_bundle_invalid():
    with pytest.raises(ToolApiSchemaError, match="Invalid openapi yaml."):
        ApiBasedToolSchemaParser.parse_openapi_yaml_to_tool_bundle("", None, None)


def test_parse_openapi_yaml_to_tool_bundle(app):
    with app.test_request_context():
        yaml = """
        openapi: 3.0.0
        info:
          title: Test API
          description: Test Description
          version: 1.0.0
        servers:
          - url: https://api.example.com
        paths:
          /test:
            get:
              operationId: testOperation
              description: Test endpoint
              parameters:
                - name: param1
                  description: Test parameter
                  required: true
                  schema:
                    type: string
        """
        bundles = ApiBasedToolSchemaParser.parse_openapi_yaml_to_tool_bundle(yaml, None, None)
        assert len(bundles) == 1
        assert bundles[0].server_url == "https://api.example.com/test"
        assert bundles[0].method == "get"


def test_parse_swagger_to_openapi():
    swagger = {
        "swagger": "2.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {"/test": {"get": {"operationId": "testOp", "summary": "Test operation"}}},
        "definitions": {},
    }

    openapi = ApiBasedToolSchemaParser.parse_swagger_to_openapi(swagger, None, None)
    assert openapi["openapi"] == "3.0.0"
    assert openapi["paths"]["/test"]["get"]["operationId"] == "testOp"


def test_parse_swagger_no_servers():
    swagger = {"swagger": "2.0", "info": {"title": "Test", "version": "1.0"}, "servers": [], "paths": {}}
    with pytest.raises(ToolApiSchemaError):
        ApiBasedToolSchemaParser.parse_swagger_to_openapi(swagger, None, None)


@patch("core.tools.utils.parser.get")
def test_parse_openai_plugin_json_to_tool_bundle(mock_get, app):
    with app.test_request_context():
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        openapi: 3.0.0
        info:
          title: Test
          version: 1.0.0
        servers:
          - url: https://api.example.com
        paths:
          /test:
            get:
              operationId: testOp
              description: Test
        """
        mock_get.return_value = mock_response

        plugin_json = json.dumps({"api": {"type": "openapi", "url": "https://example.com/openapi.yaml"}})
        bundles = ApiBasedToolSchemaParser.parse_openai_plugin_json_to_tool_bundle(plugin_json, None, None)
        assert len(bundles) == 1


def test_parse_openai_plugin_invalid_json():
    with pytest.raises(ToolProviderNotFoundError):
        ApiBasedToolSchemaParser.parse_openai_plugin_json_to_tool_bundle("invalid json", None, None)


def test_parse_openai_plugin_unsupported_type():
    plugin_json = json.dumps({"api": {"type": "unsupported", "url": "https://example.com"}})
    with pytest.raises(ToolNotSupportedError):
        ApiBasedToolSchemaParser.parse_openai_plugin_json_to_tool_bundle(plugin_json, None, None)


def test_auto_parse_to_tool_bundle(app):
    with app.test_request_context():
        # Test valid OpenAPI JSON
        openapi_json = json.dumps(
            {
                "openapi": "3.0.0",
                "info": {"title": "Test", "version": "1.0"},
                "servers": [{"url": "https://api.example.com"}],
                "paths": {"/test": {"get": {"operationId": "testOp", "description": "Test"}}},
            }
        )

        bundles, schema_type = ApiBasedToolSchemaParser.auto_parse_to_tool_bundle(openapi_json)
        assert len(bundles) == 1
        assert schema_type == "openapi"

        # Test invalid content
        with pytest.raises(ToolApiSchemaError):
            ApiBasedToolSchemaParser.auto_parse_to_tool_bundle("")
