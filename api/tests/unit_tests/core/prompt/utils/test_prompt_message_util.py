from core.model_runtime.entities import (
    ImagePromptMessageContent,
    PromptMessage,
    PromptMessageRole,
    TextPromptMessageContent,
)
from core.prompt.simple_prompt_transform import ModelMode
from core.prompt.utils.prompt_message_util import PromptMessageUtil


def test_chat_mode_text_only():
    messages = [
        PromptMessage(role=PromptMessageRole.USER, content="Hello"),
        PromptMessage(role=PromptMessageRole.ASSISTANT, content="Hi there"),
        PromptMessage(role=PromptMessageRole.SYSTEM, content="Be helpful"),
    ]

    result = PromptMessageUtil.prompt_messages_to_prompt_for_saving(ModelMode.CHAT, messages)

    assert len(result) == 3
    assert result[0] == {"role": "user", "text": "Hello", "files": []}
    assert result[1] == {"role": "assistant", "text": "Hi there", "files": []}
    assert result[2] == {"role": "system", "text": "Be helpful", "files": []}


def test_completion_mode():
    text_content = TextPromptMessageContent(data="Complete this")
    image_content = ImagePromptMessageContent(
        data="imagedata1234567890...endimagedata", detail="low", format="png", mime_type="image/png"
    )

    message = PromptMessage(role=PromptMessageRole.USER, content=[text_content, image_content])

    result = PromptMessageUtil.prompt_messages_to_prompt_for_saving(ModelMode.COMPLETION, [message])

    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result[0]["text"] == "Complete this"
    assert len(result[0]["files"]) == 1
    assert result[0]["files"][0]["type"] == "image"
    assert "...[TRUNCATED]..." in result[0]["files"][0]["data"]


def test_chat_mode_empty_message_list():
    result = PromptMessageUtil.prompt_messages_to_prompt_for_saving(ModelMode.CHAT, [])

    assert result == []


def test_completion_mode_empty_content():
    message = PromptMessage(role=PromptMessageRole.USER, content=[])

    result = PromptMessageUtil.prompt_messages_to_prompt_for_saving(ModelMode.COMPLETION, [message])

    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result[0]["text"] == ""
    assert "files" not in result[0]
