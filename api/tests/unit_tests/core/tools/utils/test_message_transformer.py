import pytest

from core.file import File, FileTransferMethod, FileType
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.utils.message_transformer import ToolFileMessageTransformer


@pytest.fixture
def basic_message():
    return ToolInvokeMessage(
        type=ToolInvokeMessage.MessageType.TEXT, message="test message", meta={}, save_as="test.txt"
    )


@pytest.fixture
def image_message():
    return ToolInvokeMessage(
        type=ToolInvokeMessage.MessageType.IMAGE, message="http://example.com/image.jpg", meta={}, save_as="image.jpg"
    )


@pytest.fixture
def blob_message():
    return ToolInvokeMessage(
        type=ToolInvokeMessage.MessageType.BLOB,
        message=b"test blob",
        meta={"mime_type": "image/png"},
        save_as="blob.png",
    )


@pytest.fixture
def file_message():
    file = File(
        id="123",
        size=100,
        type=FileType.IMAGE,
        extension=".jpg",
        mime_type="image/jpeg",
        transfer_method=FileTransferMethod.TOOL_FILE,
        related_id="file123",
        tenant_id="tenant1",
        storage_key="storage123",
    )

    return ToolInvokeMessage(
        type=ToolInvokeMessage.MessageType.FILE, message="file content", meta={"file": file}, save_as="file.jpg"
    )


def test_transform_text_message(basic_message):
    result = ToolFileMessageTransformer.transform_tool_invoke_messages([basic_message], "user1", "tenant1", "conv1")
    assert len(result) == 1
    assert result[0].type == ToolInvokeMessage.MessageType.TEXT
    assert result[0].message == "test message"


def test_transform_file_message(file_message):
    result = ToolFileMessageTransformer.transform_tool_invoke_messages([file_message], "user1", "tenant1", "conv1")

    assert len(result) == 1
    assert result[0].type == ToolInvokeMessage.MessageType.IMAGE_LINK
    assert result[0].message == "/files/tools/file123.jpg"


def test_get_tool_file_url():
    url = ToolFileMessageTransformer.get_tool_file_url("123", ".jpg")
    assert url == "/files/tools/123.jpg"

    url = ToolFileMessageTransformer.get_tool_file_url("123", None)
    assert url == "/files/tools/123.bin"


def test_transform_link_message():
    link_msg = ToolInvokeMessage(
        type=ToolInvokeMessage.MessageType.LINK, message="https://example.com", meta={}, save_as="link.txt"
    )

    result = ToolFileMessageTransformer.transform_tool_invoke_messages([link_msg], "user1", "tenant1", "conv1")

    assert len(result) == 1
    assert result[0].type == ToolInvokeMessage.MessageType.LINK
    assert result[0].message == "https://example.com"
