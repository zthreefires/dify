from unittest.mock import Mock

from constants import UUID_NIL
from core.prompt.utils.extract_thread_messages import extract_thread_messages


def create_mock_message(id=None, parent_message_id=None):
    message = Mock()
    message.id = id
    message.parent_message_id = parent_message_id
    return message


def test_extract_thread_messages_empty_list():
    result = extract_thread_messages([])
    assert result == []


def test_extract_thread_messages_single_message_no_parent():
    message = create_mock_message(id="1", parent_message_id=None)
    result = extract_thread_messages([message])
    assert result == [message]


def test_extract_thread_messages_single_message_with_parent():
    message = create_mock_message(id="1", parent_message_id="parent1")
    result = extract_thread_messages([message])
    assert result == [message]


def test_extract_thread_messages_multiple_connected():
    message1 = create_mock_message(id="1", parent_message_id="2")
    message2 = create_mock_message(id="2", parent_message_id="3")
    message3 = create_mock_message(id="3", parent_message_id=None)

    messages = [message1, message2, message3]
    result = extract_thread_messages(messages)

    assert result == [message1, message2, message3]


def test_extract_thread_messages_with_uuid_nil():
    message1 = create_mock_message(id="1", parent_message_id="2")
    message2 = create_mock_message(id=UUID_NIL, parent_message_id=None)

    messages = [message1, message2]
    result = extract_thread_messages(messages)

    assert result == [message1, message2]


def test_extract_thread_messages_disconnected():
    message1 = create_mock_message(id="1", parent_message_id="2")
    message2 = create_mock_message(id="3", parent_message_id="4")

    messages = [message1, message2]
    result = extract_thread_messages(messages)

    assert result == [message1]


def test_extract_thread_messages_break_on_no_parent():
    message1 = create_mock_message(id="1", parent_message_id=None)
    message2 = create_mock_message(id="2", parent_message_id="3")

    messages = [message1, message2]
    result = extract_thread_messages(messages)

    assert result == [message1]


def test_extract_thread_messages_circular_reference():
    message1 = create_mock_message(id="1", parent_message_id="2")
    message2 = create_mock_message(id="2", parent_message_id="1")

    messages = [message1, message2]
    result = extract_thread_messages(messages)

    assert result == [message1, message2]


def test_extract_thread_messages_multiple_no_parent():
    message1 = create_mock_message(id="1", parent_message_id=None)
    message2 = create_mock_message(id="2", parent_message_id=None)

    messages = [message1, message2]
    result = extract_thread_messages(messages)

    assert result == [message1]


def test_extract_thread_messages_with_none_id():
    message1 = create_mock_message(id=None, parent_message_id="1")
    result = extract_thread_messages([message1])
    assert result == [message1]
