from unittest.mock import Mock

import pytest

from core.helper.code_executor.code_executor import CodeExecutionError, CodeLanguage
from core.helper.code_executor.javascript.javascript_code_provider import JavascriptCodeProvider
from core.helper.code_executor.python3.python3_code_provider import Python3CodeProvider
from core.workflow.nodes.code.code_node import CodeNode
from core.workflow.nodes.code.entities import CodeNodeData, VariableSelector
from core.workflow.nodes.code.exc import CodeNodeError, DepthLimitError, OutputValidationError
from models.workflow import WorkflowNodeExecutionStatus


@pytest.fixture
def mock_config():
    return {
        "id": "test_node",
        "data": {
            "title": "Test Code Node",
            "code_language": CodeLanguage.PYTHON3,
            "code": "test_code",
            "variables": [],
            "outputs": {},
        },
    }


@pytest.fixture
def code_node(mock_config):
    node = CodeNode("test_node", mock_config, Mock(), Mock(), Mock())
    return node


def test_get_default_config_python():
    filters = {"code_language": CodeLanguage.PYTHON3}
    config = CodeNode.get_default_config(filters)
    assert config == Python3CodeProvider.get_default_config()


def test_get_default_config_javascript():
    filters = {"code_language": CodeLanguage.JAVASCRIPT}
    config = CodeNode.get_default_config(filters)
    assert config == JavascriptCodeProvider.get_default_config()


def test_run_execution_error(code_node, mocker):
    mock_executor = mocker.patch("core.workflow.nodes.code.code_node.CodeExecutor")
    mock_executor.execute_workflow_code_template.side_effect = CodeExecutionError("Test error")

    result = code_node._run()

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert result.error == "Test error"
    assert result.error_type == "CodeExecutionError"


def test_run_code_node_error(code_node, mocker):
    mock_executor = mocker.patch("core.workflow.nodes.code.code_node.CodeExecutor")
    mock_executor.execute_workflow_code_template.side_effect = CodeNodeError("Test error")

    result = code_node._run()

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert result.error == "Test error"
    assert result.error_type == "CodeNodeError"


def test_run_success_with_outputs(code_node, mocker):
    mock_executor = mocker.patch("core.workflow.nodes.code.code_node.CodeExecutor")
    mock_executor.execute_workflow_code_template.return_value = {"test": "value"}
    code_node.node_data.outputs = {"test": CodeNodeData.Output(type="string")}

    result = code_node._run()

    assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
    assert result.outputs == {"test": "value"}


def test_check_string_none(code_node):
    assert code_node._check_string(None, "test") is None


def test_check_string_invalid_type(code_node):
    with pytest.raises(OutputValidationError):
        code_node._check_string(123, "test")


def test_check_string_too_long(code_node, mocker):
    mocker.patch("core.workflow.nodes.code.code_node.dify_config.CODE_MAX_STRING_LENGTH", 5)
    with pytest.raises(OutputValidationError):
        code_node._check_string("too long string", "test")


def test_check_number_none(code_node):
    assert code_node._check_number(None, "test") is None


def test_check_number_invalid_type(code_node):
    with pytest.raises(OutputValidationError):
        code_node._check_number("123", "test")


def test_check_number_out_of_range(code_node, mocker):
    mocker.patch("core.workflow.nodes.code.code_node.dify_config.CODE_MAX_NUMBER", 100)
    mocker.patch("core.workflow.nodes.code.code_node.dify_config.CODE_MIN_NUMBER", -100)

    with pytest.raises(OutputValidationError):
        code_node._check_number(101, "test")

    with pytest.raises(OutputValidationError):
        code_node._check_number(-101, "test")


def test_check_number_precision_too_high(code_node, mocker):
    mocker.patch("core.workflow.nodes.code.code_node.dify_config.CODE_MAX_PRECISION", 2)
    with pytest.raises(OutputValidationError):
        code_node._check_number(1.234, "test")


def test_transform_result_depth_limit(code_node, mocker):
    mocker.patch("core.workflow.nodes.code.code_node.dify_config.CODE_MAX_DEPTH", 2)

    nested_data = {"a": {"b": {"c": "value"}}}
    with pytest.raises(DepthLimitError):
        code_node._transform_result(nested_data, None)


def test_transform_result_invalid_array(code_node):
    data = {"test": [1, "string", 2]}
    with pytest.raises(OutputValidationError):
        code_node._transform_result(data, None)


def test_extract_variable_selector_mapping():
    graph_config = {}
    node_data = CodeNodeData(
        title="Test Code Node",
        code_language=CodeLanguage.PYTHON3,
        code="test",
        variables=[
            VariableSelector(variable="var1", value_selector=["selector1"]),
            VariableSelector(variable="var2", value_selector=["selector2"]),
        ],
        outputs={},
    )

    mapping = CodeNode._extract_variable_selector_to_variable_mapping(
        graph_config=graph_config, node_id="test_node", node_data=node_data
    )

    assert mapping == {"test_node.var1": ["selector1"], "test_node.var2": ["selector2"]}
