from unittest.mock import Mock, patch

import pytest
from flask import Flask

from core.agent.cot_chat_agent_runner import CotChatAgentRunner
from core.model_runtime.entities import (
    AssistantPromptMessage,
    SystemPromptMessage,
    TextPromptMessageContent,
    UserPromptMessage,
)
from core.model_runtime.entities.message_entities import ImagePromptMessageContent


@pytest.fixture
def mock_app_config():
    config = Mock()
    config.agent = Mock()
    config.agent.prompt = Mock()
    config.agent.prompt.first_prompt = "{{instruction}} {{tools}} {{tool_names}}"
    return config


@pytest.fixture
def mock_files():
    return [
        Mock(
            type="image",
            path="/tmp/test.jpg",
        )
    ]


@pytest.fixture
def mock_application_generate_entity():
    entity = Mock()
    entity.file_upload_config = Mock()
    entity.file_upload_config.image_config = Mock()
    entity.file_upload_config.image_config.detail = ImagePromptMessageContent.DETAIL.LOW
    return entity


@pytest.fixture
def mock_agent(mock_app_config):
    with patch("flask.current_app") as mock_current_app:
        mock_flask_app = Flask(__name__)
        mock_current_app._get_current_object.return_value = mock_flask_app

        agent = Mock(spec=CotChatAgentRunner)
        agent._instruction = "test instruction"
        agent._prompt_messages_tools = [Mock(name="tool1"), Mock(name="tool2")]
        agent._query = "test query"
        agent._agent_scratchpad = []
        agent.organize_agent_history = Mock(return_value=[])

        return agent


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_system_prompt(mock_agent):
    result = mock_agent._organize_system_prompt()

    assert isinstance(result, SystemPromptMessage)
    assert "test instruction" in result.content
    assert "tool1, tool2" in result.content


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_system_prompt_no_agent_config(mock_agent):
    mock_agent.app_config.agent = None

    with pytest.raises(ValueError, match="Agent configuration is not set"):
        mock_agent._organize_system_prompt()


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_system_prompt_no_prompt_config(mock_agent):
    mock_agent.app_config.agent.prompt = None

    with pytest.raises(ValueError, match="Agent prompt configuration is not set"):
        mock_agent._organize_system_prompt()


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_user_query_with_files(mock_agent, mock_files, mock_application_generate_entity):
    with patch("core.file.file_manager.to_prompt_message_content") as mock_to_content:
        mock_to_content.return_value = Mock()
        mock_agent.files = mock_files
        mock_agent.application_generate_entity = mock_application_generate_entity

        result = mock_agent._organize_user_query("test query", [])

        assert len(result) == 1
        assert isinstance(result[0], UserPromptMessage)
        assert len(result[0].content) == 2
        assert isinstance(result[0].content[0], TextPromptMessageContent)
        assert result[0].content[0].data == "test query"


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_user_query_without_files(mock_agent):
    mock_agent.files = None

    result = mock_agent._organize_user_query("test query", [])

    assert len(result) == 1
    assert isinstance(result[0], UserPromptMessage)
    assert result[0].content == "test query"


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_prompt_messages_without_scratchpad(mock_agent):
    mock_agent._organize_system_prompt = Mock(return_value=SystemPromptMessage(content="system"))
    mock_agent._organize_historic_prompt_messages = Mock(return_value=[])

    result = mock_agent._organize_prompt_messages()

    assert len(result) == 2
    assert isinstance(result[0], SystemPromptMessage)
    assert isinstance(result[1], UserPromptMessage)


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_prompt_messages_with_scratchpad(mock_agent):
    mock_agent._organize_system_prompt = Mock(return_value=SystemPromptMessage(content="system"))
    mock_agent._organize_historic_prompt_messages = Mock(return_value=[])

    mock_unit = Mock()
    mock_unit.is_final.return_value = True
    mock_unit.agent_response = "final response"
    mock_agent._agent_scratchpad = [mock_unit]

    result = mock_agent._organize_prompt_messages()

    assert len(result) == 4
    assert isinstance(result[0], SystemPromptMessage)
    assert isinstance(result[1], UserPromptMessage)
    assert isinstance(result[2], AssistantPromptMessage)
    assert isinstance(result[3], UserPromptMessage)
    assert "Final Answer: final response" in result[2].content


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_prompt_messages_with_non_final_scratchpad(mock_agent):
    mock_agent._organize_system_prompt = Mock(return_value=SystemPromptMessage(content="system"))
    mock_agent._organize_historic_prompt_messages = Mock(return_value=[])

    mock_unit = Mock()
    mock_unit.is_final.return_value = False
    mock_unit.thought = "test thought"
    mock_unit.action_str = "test action"
    mock_unit.observation = "test observation"
    mock_agent._agent_scratchpad = [mock_unit]

    result = mock_agent._organize_prompt_messages()

    assert len(result) == 4
    assert isinstance(result[2], AssistantPromptMessage)
    assert "Thought: test thought" in result[2].content
    assert "Action: test action" in result[2].content
    assert "Observation: test observation" in result[2].content


@pytest.mark.skip(reason="Test requires Flask SQLAlchemy setup")
def test_organize_prompt_messages_with_multiple_scratchpad_units(mock_agent):
    mock_agent._organize_system_prompt = Mock(return_value=SystemPromptMessage(content="system"))
    mock_agent._organize_historic_prompt_messages = Mock(return_value=[])

    unit1 = Mock()
    unit1.is_final.return_value = False
    unit1.thought = "thought 1"
    unit1.action_str = "action 1"
    unit1.observation = "observation 1"

    unit2 = Mock()
    unit2.is_final.return_value = True
    unit2.agent_response = "final response"

    mock_agent._agent_scratchpad = [unit1, unit2]

    result = mock_agent._organize_prompt_messages()

    assert len(result) == 4
    assert isinstance(result[2], AssistantPromptMessage)
    assert "Thought: thought 1" in result[2].content
    assert "Action: action 1" in result[2].content
    assert "Observation: observation 1" in result[2].content
    assert "Final Answer: final response" in result[2].content
