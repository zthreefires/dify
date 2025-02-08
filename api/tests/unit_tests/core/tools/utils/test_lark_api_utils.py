from unittest.mock import Mock, patch

import pytest

from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.utils.lark_api_utils import LarkRequest, lark_auth


@pytest.fixture
def mock_redis():
    with patch("extensions.ext_redis.redis_client") as mock:
        yield mock


@pytest.fixture
def lark_request():
    return LarkRequest("test_app_id", "test_app_secret")


def test_lark_auth_missing_credentials():
    with pytest.raises(ToolProviderCredentialValidationError) as exc:
        lark_auth({})
    assert str(exc.value) == "app_id and app_secret is required"


def test_lark_auth_invalid_credentials():
    with patch("core.tools.utils.lark_api_utils.LarkRequest") as mock_lark:
        mock_lark.return_value.tenant_access_token = None
        with pytest.raises(ToolProviderCredentialValidationError):
            lark_auth({"app_id": "invalid", "app_secret": "invalid"})


def test_convert_add_records_valid_json(lark_request):
    json_str = '[{"field1": "value1"}, {"field2": "value2"}]'
    result = lark_request.convert_add_records(json_str)
    assert len(result) == 2
    assert result[0]["fields"] == '{"field1": "value1"}'
    assert result[1]["fields"] == '{"field2": "value2"}'


def test_convert_add_records_invalid_json(lark_request):
    with pytest.raises(ValueError) as exc:
        lark_request.convert_add_records("invalid json")
    assert str(exc.value) == "The input string is not valid JSON"


def test_convert_add_records_not_list(lark_request):
    with pytest.raises(ValueError) as exc:
        lark_request.convert_add_records('{"not": "a list"}')
    assert str(exc.value) == "An error occurred while processing the data: Parsed data must be a list"


def test_convert_update_records_valid_json(lark_request):
    json_str = (
        '[{"fields": {"field1": "value1"}, "record_id": "1"}, {"fields": {"field2": "value2"}, "record_id": "2"}]'
    )
    result = lark_request.convert_update_records(json_str)
    assert len(result) == 2
    assert result[0]["fields"] == '{"field1": "value1"}'
    assert result[0]["record_id"] == "1"
    assert result[1]["fields"] == '{"field2": "value2"}'
    assert result[1]["record_id"] == "2"


def test_convert_update_records_invalid_json(lark_request):
    with pytest.raises(ValueError) as exc:
        lark_request.convert_update_records("invalid json")
    assert str(exc.value) == "The input string is not valid JSON"


def test_convert_update_records_not_list(lark_request):
    with pytest.raises(ValueError) as exc:
        lark_request.convert_update_records('{"not": "a list"}')
    assert str(exc.value) == "An error occurred while processing the data: Parsed data must be a list"


def test_convert_update_records_missing_fields(lark_request):
    with pytest.raises(ValueError) as exc:
        lark_request.convert_update_records('[{"record_id": "1"}]')
    assert str(exc.value) == (
        "An error occurred while processing the data: Each record must contain 'fields' and 'record_id'"
    )


@pytest.mark.asyncio
async def test_create_document(lark_request):
    mock_response = {"code": 0, "data": {"document_id": "test_doc"}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.create_document("Test Title", "Test Content", "folder123")
        assert result == {"document_id": "test_doc"}


@pytest.mark.asyncio
async def test_write_document(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.write_document("doc123", "New Content")
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_get_document_content(lark_request):
    mock_response = {"code": 0, "data": {"content": "Test Content"}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.get_document_content("doc123")
        assert result == "Test Content"


@pytest.mark.asyncio
async def test_send_bot_message(lark_request):
    mock_response = {"code": 0, "data": {"message_id": "msg123"}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.send_bot_message("chat", "user123", "text", "Hello")
        assert result == {"message_id": "msg123"}


@pytest.mark.asyncio
async def test_send_webhook_message(lark_request):
    mock_response = {"code": 0}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.send_webhook_message("webhook_url", "text", "Hello")
        assert result == {"code": 0}


@pytest.mark.asyncio
async def test_create_task(lark_request):
    mock_response = {"code": 0, "data": {"task_id": "task123"}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.create_task("Test Task", "2025-01-01", "2025-01-02", "2025-01-02", "Description")
        assert result == {"task_id": "task123"}


@pytest.mark.asyncio
async def test_update_task(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.update_task(
            "task123",
            "Updated Task",
            "2025-01-01",
            "2025-01-02",
            "2025-01-02",
            "New Description",
        )
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_delete_task(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.delete_task("task123")
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_create_spreadsheet(lark_request):
    mock_response = {"code": 0, "data": {"spreadsheet_token": "sheet123"}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.create_spreadsheet("Test Sheet", "folder123")
        assert result == {"spreadsheet_token": "sheet123"}


@pytest.mark.asyncio
async def test_add_rows(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.add_rows("sheet123", "sheet1", "Sheet1", 1, "test data")
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_add_cols(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.add_cols("sheet123", "sheet1", "Sheet1", 1, "test data")
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_create_base(lark_request):
    mock_response = {"code": 0, "data": {"app_token": "base123"}}
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.create_base("Test Base", "folder123")
        assert result == {"app_token": "base123"}


@pytest.mark.asyncio
async def test_add_records(lark_request):
    mock_response = {"code": 0, "data": {"records": ["rec1", "rec2"]}}
    records = '[{"field1": "value1"}, {"field2": "value2"}]'
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.add_records("base123", "table1", "Table1", records)
        assert result == {"records": ["rec1", "rec2"]}


@pytest.mark.asyncio
async def test_update_records(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    records = '[{"fields": {"field1": "new_value"}, "record_id": "rec1"}]'
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.update_records("base123", "table1", "Table1", records, "open_id")
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_delete_records(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    record_ids = '["rec1", "rec2"]'
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.delete_records("base123", "table1", "Table1", record_ids)
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_create_table(lark_request):
    mock_response = {"code": 0, "data": {"table_id": "table123"}}
    fields = '[{"field_name": "test", "type": "text"}]'
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.create_table("base123", "Test Table", "Default View", fields)
        assert result == {"table_id": "table123"}


@pytest.mark.asyncio
async def test_delete_tables(lark_request):
    mock_response = {"code": 0, "data": {"success": True}}
    table_ids = '["table1", "table2"]'
    table_names = '["Table1", "Table2"]'
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.delete_tables("base123", table_ids, table_names)
        assert result == {"success": True}


@pytest.mark.asyncio
async def test_read_records(lark_request):
    mock_response = {"code": 0, "data": {"records": [{"id": "rec1"}]}}
    record_ids = '["rec1"]'
    with patch("httpx.request", return_value=Mock(json=lambda: mock_response)):
        result = lark_request.read_records("base123", "table1", "Table1", record_ids)
        assert result == {"records": [{"id": "rec1"}]}
