from unittest.mock import Mock

import pytest

from core.prompt.utils.get_thread_messages_length import get_thread_messages_length


@pytest.fixture
def mock_db_session(mocker):
    mock_session = Mock()
    mocker.patch("core.prompt.utils.get_thread_messages_length.db.session", mock_session)
    return mock_session


def test_get_thread_messages_length_empty(mock_db_session):
    mock_db_session.query().filter().order_by.return_value.all.return_value = []
    result = get_thread_messages_length("conv_id")
    assert result == 0


def test_get_thread_messages_length_with_messages(mock_db_session):
    messages = [
        Mock(id="3", parent_message_id="2", answer="answer 3"),
        Mock(id="2", parent_message_id="1", answer="answer 2"),
        Mock(id="1", parent_message_id=None, answer="answer 1"),
    ]
    mock_db_session.query().filter().order_by.return_value.all.return_value = messages
    result = get_thread_messages_length("conv_id")
    assert result == 3


def test_get_thread_messages_length_with_empty_answer(mock_db_session):
    messages = [
        Mock(id="3", parent_message_id="2", answer=""),
        Mock(id="2", parent_message_id="1", answer="answer 2"),
        Mock(id="1", parent_message_id=None, answer="answer 1"),
    ]
    mock_db_session.query().filter().order_by.return_value.all.return_value = messages
    result = get_thread_messages_length("conv_id")
    assert result == 2


def test_get_thread_messages_length_single_message(mock_db_session):
    messages = [Mock(id="1", parent_message_id=None, answer="answer 1")]
    mock_db_session.query().filter().order_by.return_value.all.return_value = messages
    result = get_thread_messages_length("conv_id")
    assert result == 1


def test_get_thread_messages_length_non_sequential(mock_db_session):
    messages = [
        Mock(id="3", parent_message_id="2", answer="answer 3"),
        Mock(id="1", parent_message_id=None, answer="answer 1"),
        Mock(id="2", parent_message_id="1", answer="answer 2"),
    ]
    mock_db_session.query().filter().order_by.return_value.all.return_value = messages
    result = get_thread_messages_length("conv_id")
    assert result == 2


def test_get_thread_messages_length_with_broken_chain(mock_db_session):
    messages = [
        Mock(id="3", parent_message_id="2", answer="answer 3"),
        Mock(id="2", parent_message_id="non_existent", answer="answer 2"),
        Mock(id="1", parent_message_id=None, answer="answer 1"),
    ]
    mock_db_session.query().filter().order_by.return_value.all.return_value = messages
    result = get_thread_messages_length("conv_id")
    assert result == 3


def test_get_thread_messages_length_with_circular_reference(mock_db_session):
    messages = [
        Mock(id="3", parent_message_id="2", answer="answer 3"),
        Mock(id="2", parent_message_id="3", answer="answer 2"),
        Mock(id="1", parent_message_id=None, answer="answer 1"),
    ]
    mock_db_session.query().filter().order_by.return_value.all.return_value = messages
    result = get_thread_messages_length("conv_id")
    assert result == 3
