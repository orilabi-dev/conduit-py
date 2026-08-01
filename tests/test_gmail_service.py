import base64
from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.gmail.service import GmailService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def _make_service() -> tuple[GmailService, MagicMock]:
    with patch("conduit_py.google.workspace.gmail.service.build") as mock_build:
        mock_api = MagicMock()
        mock_build.return_value = mock_api
        service = GmailService(credentials=MagicMock())
    return service, mock_api


def test_send_message_rejects_empty_to():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.send_message("", "Subject", "Body")


def test_send_message_rejects_empty_subject():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.send_message("to@example.com", "", "Body")


def test_send_message_rejects_empty_body():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.send_message("to@example.com", "Subject", "")


def test_send_message_sends_base64url_encoded_mime_message():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.send.return_value.execute.return_value = {
        "id": "msg123"
    }

    response = service.send_message("to@example.com", "Hello", "Hi there")

    _, kwargs = mock_api.users.return_value.messages.return_value.send.call_args
    assert kwargs["userId"] == "me"
    raw = kwargs["body"]["raw"]
    decoded = base64.urlsafe_b64decode(raw).decode()
    assert "to@example.com" in decoded
    assert "Hello" in decoded
    assert "Hi there" in decoded
    assert response == {"id": "msg123"}


def test_send_message_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.send.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.send_message("to@example.com", "Hello", "Hi there")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_list_messages_returns_messages_on_success():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        "messages": [{"id": "msg123", "threadId": "thread123"}]
    }

    result = service.list_messages()

    assert result == [{"id": "msg123", "threadId": "thread123"}]


def test_list_messages_returns_empty_list_when_no_messages_key():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.list.return_value.execute.return_value = {}

    result = service.list_messages()

    assert result == []


def test_list_messages_passes_query_when_given():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        "messages": []
    }

    service.list_messages(query="is:unread")

    mock_api.users.return_value.messages.return_value.list.assert_called_once_with(
        userId="me", q="is:unread"
    )


def test_list_messages_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.list.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_messages()

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_get_message_rejects_empty_message_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_message("")


def test_get_message_returns_response_on_success():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        "id": "msg123",
        "snippet": "Hi there",
    }

    response = service.get_message("msg123")

    mock_api.users.return_value.messages.return_value.get.assert_called_once_with(
        userId="me", id="msg123"
    )
    assert response == {"id": "msg123", "snippet": "Hi there"}


def test_get_message_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.get.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.get_message("msg123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_trash_message_rejects_empty_message_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.trash_message("")


def test_trash_message_calls_client_with_message_id():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.trash.return_value.execute.return_value = {
        "id": "msg123",
        "labelIds": ["TRASH"],
    }

    response = service.trash_message("msg123")

    mock_api.users.return_value.messages.return_value.trash.assert_called_once_with(
        userId="me", id="msg123"
    )
    assert response == {"id": "msg123", "labelIds": ["TRASH"]}


def test_trash_message_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.users.return_value.messages.return_value.trash.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.trash_message("msg123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason
