from unittest.mock import Mock

import pytest

from core.memory.token_buffer_memory import TokenBufferMemory
from core.model_runtime.entities import (
    AssistantPromptMessage,
    ImagePromptMessageContent,
    TextPromptMessageContent,
    UserPromptMessage,
)
from models.model import AppMode, Conversation, Message, MessageFile


@pytest.fixture
def mock_conversation():
    conversation = Mock(spec=Conversation)
    conversation.id = "conv_123"
    conversation.mode = AppMode.CHAT
    conversation.app = Mock()
    conversation.app.tenant_id = "tenant_123"
    conversation.model_config = {
        "file_upload": {
            "enabled": True,
            "number_limits": 5,
            "allowed_file_upload_methods": ["local_file"],
            "image": {"detail": "low"},
        }
    }
    return conversation


@pytest.fixture
def mock_model_instance():
    model_instance = Mock()
    model_instance.get_llm_num_tokens.return_value = 100
    return model_instance


@pytest.fixture
def memory(mock_conversation, mock_model_instance):
    return TokenBufferMemory(mock_conversation, mock_model_instance)


def test_get_history_prompt_messages_empty(memory, mocker):
    mock_query = Mock()
    mock_query.limit.return_value = Mock(all=lambda: [])
    mock_query.order_by.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mocker.patch("core.memory.token_buffer_memory.db.session.query", return_value=mock_query)
    mocker.patch("core.memory.token_buffer_memory.extract_thread_messages", return_value=[])

    messages = memory.get_history_prompt_messages()
    assert messages == []


def test_get_history_prompt_messages_basic(memory, mocker):
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_1"
    mock_message.query = "test query"
    mock_message.answer = "test answer"
    mock_message.workflow_run_id = None

    mock_query = Mock()
    mock_query.limit.return_value = Mock(all=lambda: [mock_message])
    mock_query.order_by.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mocker.patch("core.memory.token_buffer_memory.db.session.query", return_value=mock_query)
    mocker.patch("core.memory.token_buffer_memory.extract_thread_messages", return_value=[mock_message])
    mocker.patch(
        "core.memory.token_buffer_memory.db.session.query", return_value=Mock(filter=lambda *args: Mock(all=lambda: []))
    )

    messages = memory.get_history_prompt_messages()

    assert len(messages) == 2
    assert isinstance(messages[0], UserPromptMessage)
    assert messages[0].content == "test query"
    assert isinstance(messages[1], AssistantPromptMessage)
    assert messages[1].content == "test answer"


def test_get_history_prompt_messages_with_files(memory, mocker):
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_1"
    mock_message.query = "test query"
    mock_message.answer = "test answer"
    mock_message.workflow_run_id = None

    mock_file = Mock(spec=MessageFile)
    mock_file.belongs_to = "user"

    mock_query = Mock()
    mock_query.limit.return_value = Mock(all=lambda: [mock_message])
    mock_query.order_by.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mocker.patch("core.memory.token_buffer_memory.extract_thread_messages", return_value=[mock_message])
    mocker.patch(
        "core.memory.token_buffer_memory.db.session.query",
        return_value=Mock(filter=lambda *args: Mock(all=lambda: [mock_file])),
    )
    mocker.patch("core.memory.token_buffer_memory.file_factory.build_from_message_files", return_value=[Mock()])
    mocker.patch(
        "core.memory.token_buffer_memory.file_manager.to_prompt_message_content",
        return_value=ImagePromptMessageContent(data="test_image", format="jpeg", mime_type="image/jpeg"),
    )

    messages = memory.get_history_prompt_messages()

    assert len(messages) == 2
    assert isinstance(messages[0], UserPromptMessage)
    assert isinstance(messages[0].content, list)
    assert isinstance(messages[1], AssistantPromptMessage)


def test_get_history_prompt_text_basic(memory, mocker):
    mock_messages = [UserPromptMessage(content="test query"), AssistantPromptMessage(content="test answer")]

    mocker.patch.object(memory, "get_history_prompt_messages", return_value=mock_messages)

    text = memory.get_history_prompt_text(human_prefix="Human", ai_prefix="Assistant")

    assert text == "Human: test query\nAssistant: test answer"


def test_get_history_prompt_text_with_image(memory, mocker):
    mock_messages = [
        UserPromptMessage(
            content=[
                TextPromptMessageContent(data="test query"),
                ImagePromptMessageContent(data="test_image", format="jpeg", mime_type="image/jpeg"),
            ]
        ),
        AssistantPromptMessage(content="test answer"),
    ]

    mocker.patch.object(memory, "get_history_prompt_messages", return_value=mock_messages)

    text = memory.get_history_prompt_text()

    assert text == "Human: test query\n[image]\nAssistant: test answer"


def test_token_limit_pruning(memory, mocker):
    mock_messages = [
        UserPromptMessage(content="test query 1"),
        AssistantPromptMessage(content="test answer 1"),
        UserPromptMessage(content="test query 2"),
        AssistantPromptMessage(content="test answer 2"),
    ]

    mock_query = Mock()
    mock_query.limit.return_value = Mock(all=lambda: [Mock(query="test query", answer="test answer")])
    mock_query.order_by.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mocker.patch("core.memory.token_buffer_memory.db.session.query", return_value=mock_query)
    mocker.patch(
        "core.memory.token_buffer_memory.extract_thread_messages",
        return_value=[Mock(query="test query", answer="test answer")],
    )
    memory.model_instance.get_llm_num_tokens.side_effect = [2500, 1000]

    mocker.patch.object(memory, "get_history_prompt_messages", return_value=mock_messages)

    text = memory.get_history_prompt_text(max_token_limit=2000)

    assert "test query 2" in text
    assert "test answer 2" in text


def test_get_history_prompt_messages_with_workflow(memory, mocker):
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_1"
    mock_message.query = "test query"
    mock_message.answer = "test answer"
    mock_message.workflow_run_id = "workflow_123"

    mock_workflow_run = Mock()
    mock_workflow_run.workflow.features_dict = {
        "file_upload": {
            "enabled": True,
            "number_limits": 5,
            "allowed_file_upload_methods": ["local_file"],
            "image": {"detail": "low"},
        }
    }

    mock_query = Mock()
    mock_query.limit.return_value = Mock(all=lambda: [mock_message])
    mock_query.order_by.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mocker.patch("core.memory.token_buffer_memory.db.session.query", return_value=mock_query)
    mocker.patch("core.memory.token_buffer_memory.extract_thread_messages", return_value=[mock_message])
    mocker.patch(
        "core.memory.token_buffer_memory.db.session.query",
        return_value=Mock(filter=lambda *args: Mock(first=lambda: mock_workflow_run)),
    )
    mocker.patch("core.memory.token_buffer_memory.file_factory.build_from_message_files", return_value=[])

    messages = memory.get_history_prompt_messages()

    assert len(messages) == 2
    assert isinstance(messages[0], UserPromptMessage)
    assert messages[0].content == "test query"
    assert isinstance(messages[1], AssistantPromptMessage)
    assert messages[1].content == "test answer"


def test_get_history_prompt_messages_with_message_limit(memory, mocker):
    mock_message = Mock(spec=Message)
    mock_message.id = "msg_1"
    mock_message.query = "test query"
    mock_message.answer = "test answer"
    mock_message.workflow_run_id = None

    mock_query = Mock()
    mock_query.limit.return_value = Mock(all=lambda: [mock_message])
    mock_query.order_by.return_value = mock_query
    mock_query.filter.return_value = mock_query

    mocker.patch("core.memory.token_buffer_memory.db.session.query", return_value=mock_query)
    mocker.patch("core.memory.token_buffer_memory.extract_thread_messages", return_value=[mock_message])
    mocker.patch("core.memory.token_buffer_memory.file_factory.build_from_message_files", return_value=[])

    messages = memory.get_history_prompt_messages(message_limit=10)

    assert len(messages) == 2
    mock_query.limit.assert_called_with(10)
