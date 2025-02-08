from unittest.mock import Mock, patch

import pytest

from core.model_runtime.entities.llm_entities import LLMResult, LLMUsage
from core.model_runtime.entities.message_entities import AssistantPromptMessage, PromptMessage
from core.model_runtime.errors.invoke import (
    InvokeAuthorizationError,
    InvokeBadRequestError,
    InvokeConnectionError,
    InvokeRateLimitError,
    InvokeServerUnavailableError,
)
from core.tools.utils.model_invocation_utils import InvokeModelError, ModelInvocationUtils


@pytest.fixture
def mock_model_manager():
    with patch("core.tools.utils.model_invocation_utils.ModelManager") as mock:
        manager = Mock()
        mock.return_value = manager
        yield manager


@pytest.fixture
def mock_db_session():
    with patch("core.tools.utils.model_invocation_utils.db.session") as mock:
        yield mock


def test_get_max_llm_context_tokens_success(mock_model_manager):
    model_instance = Mock()
    model_type_instance = Mock()
    schema = Mock()
    schema.model_properties = {"context_size": 2048}

    model_type_instance.get_model_schema.return_value = schema
    model_instance.model_type_instance = model_type_instance
    mock_model_manager.get_default_model_instance.return_value = model_instance

    result = ModelInvocationUtils.get_max_llm_context_tokens("tenant_123")
    assert result == 2048


def test_get_max_llm_context_tokens_no_model(mock_model_manager):
    mock_model_manager.get_default_model_instance.return_value = None

    with pytest.raises(InvokeModelError, match="Model not found"):
        ModelInvocationUtils.get_max_llm_context_tokens("tenant_123")


def test_get_max_llm_context_tokens_no_schema(mock_model_manager):
    model_instance = Mock()
    model_type_instance = Mock()
    model_type_instance.get_model_schema.return_value = None
    model_instance.model_type_instance = model_type_instance
    mock_model_manager.get_default_model_instance.return_value = model_instance

    with pytest.raises(InvokeModelError, match="No model schema found"):
        ModelInvocationUtils.get_max_llm_context_tokens("tenant_123")


def test_calculate_tokens_success(mock_model_manager):
    model_instance = Mock()
    model_instance.get_llm_num_tokens.return_value = 100
    mock_model_manager.get_default_model_instance.return_value = model_instance

    prompt_messages = [PromptMessage(content="test message", role="user")]
    result = ModelInvocationUtils.calculate_tokens("tenant_123", prompt_messages)
    assert result == 100


def test_calculate_tokens_no_model(mock_model_manager):
    mock_model_manager.get_default_model_instance.return_value = None

    with pytest.raises(InvokeModelError, match="Model not found"):
        ModelInvocationUtils.calculate_tokens("tenant_123", [])


def test_invoke_success(mock_model_manager, mock_db_session):
    model_instance = Mock()
    model_instance.provider = "test_provider"
    model_instance.get_llm_num_tokens.return_value = 100

    response = LLMResult(
        model="test_model",
        prompt_messages=[PromptMessage(content="test", role="user")],
        message=AssistantPromptMessage(content="test response", role="assistant"),
        usage=LLMUsage(
            prompt_tokens=100,
            completion_tokens=50,
            prompt_unit_price=0.01,
            prompt_price_unit=1000,
            completion_unit_price=0.01,
            completion_price_unit=1000,
            total_tokens=150,
            prompt_price=0.001,
            completion_price=0.0005,
            total_price=0.0015,
            latency=1.5,
            currency="USD",
        ),
    )
    model_instance.invoke_llm.return_value = response
    mock_model_manager.get_default_model_instance.return_value = model_instance

    result = ModelInvocationUtils.invoke(
        "user_123",
        "tenant_123",
        "test_tool_type",
        "test_tool_name",
        [PromptMessage(content="test", role="user")],
    )

    assert result == response
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called()


@pytest.mark.parametrize(
    ("error", "expected_message"),
    [
        (InvokeRateLimitError("rate limit"), "Invoke rate limit error: rate limit"),
        (InvokeBadRequestError("bad request"), "Invoke bad request error: bad request"),
        (InvokeConnectionError("connection error"), "Invoke connection error: connection error"),
        (InvokeAuthorizationError("auth error"), "Invoke authorization error"),
        (InvokeServerUnavailableError("server error"), "Invoke server unavailable error: server error"),
        (Exception("generic error"), "Invoke error: generic error"),
    ],
)
def test_invoke_errors(mock_model_manager, mock_db_session, error, expected_message):
    model_instance = Mock()
    model_instance.provider = "test_provider"
    model_instance.get_llm_num_tokens.return_value = 100
    model_instance.invoke_llm.side_effect = error
    mock_model_manager.get_default_model_instance.return_value = model_instance

    with pytest.raises(InvokeModelError, match=expected_message):
        ModelInvocationUtils.invoke(
            "user_123",
            "tenant_123",
            "test_tool_type",
            "test_tool_name",
            [PromptMessage(content="test", role="user")],
        )
