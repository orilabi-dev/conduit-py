from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.calendar.service import CalendarService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def _make_service() -> tuple[CalendarService, MagicMock]:
    with patch("conduit_py.google.workspace.calendar.service.build") as mock_build:
        mock_api = MagicMock()
        mock_build.return_value = mock_api
        service = CalendarService(credentials=MagicMock())
    return service, mock_api


def test_create_event_rejects_empty_calendar_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_event("", "Meeting", "2026-01-15T09:00:00-05:00", "2026-01-15T10:00:00-05:00")


def test_create_event_rejects_empty_summary():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_event("primary", "", "2026-01-15T09:00:00-05:00", "2026-01-15T10:00:00-05:00")


def test_create_event_rejects_empty_start_time():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_event("primary", "Meeting", "", "2026-01-15T10:00:00-05:00")


def test_create_event_rejects_empty_end_time():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_event("primary", "Meeting", "2026-01-15T09:00:00-05:00", "")


def test_create_event_calls_client_with_expected_body():
    service, mock_api = _make_service()
    mock_api.events.return_value.insert.return_value.execute.return_value = {
        "id": "event123"
    }

    response = service.create_event(
        "primary", "Meeting", "2026-01-15T09:00:00-05:00", "2026-01-15T10:00:00-05:00"
    )

    mock_api.events.return_value.insert.assert_called_once_with(
        calendarId="primary",
        body={
            "summary": "Meeting",
            "start": {"dateTime": "2026-01-15T09:00:00-05:00"},
            "end": {"dateTime": "2026-01-15T10:00:00-05:00"},
        },
    )
    assert response == {"id": "event123"}


def test_create_event_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.events.return_value.insert.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_event(
            "primary", "Meeting", "2026-01-15T09:00:00-05:00", "2026-01-15T10:00:00-05:00"
        )

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_list_events_rejects_empty_calendar_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.list_events("")


def test_list_events_returns_items_on_success():
    service, mock_api = _make_service()
    mock_api.events.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "event123", "summary": "Meeting"}]
    }

    result = service.list_events("primary")

    assert result == [{"id": "event123", "summary": "Meeting"}]


def test_list_events_returns_empty_list_when_no_items_key():
    service, mock_api = _make_service()
    mock_api.events.return_value.list.return_value.execute.return_value = {}

    result = service.list_events("primary")

    assert result == []


def test_list_events_passes_time_min_when_given():
    service, mock_api = _make_service()
    mock_api.events.return_value.list.return_value.execute.return_value = {"items": []}

    service.list_events("primary", time_min="2026-01-01T00:00:00Z")

    mock_api.events.return_value.list.assert_called_once_with(
        calendarId="primary", timeMin="2026-01-01T00:00:00Z"
    )


def test_list_events_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.events.return_value.list.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_events("primary")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_get_event_rejects_empty_calendar_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_event("", "event123")


def test_get_event_rejects_empty_event_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_event("primary", "")


def test_get_event_returns_response_on_success():
    service, mock_api = _make_service()
    mock_api.events.return_value.get.return_value.execute.return_value = {
        "id": "event123",
        "summary": "Meeting",
    }

    response = service.get_event("primary", "event123")

    mock_api.events.return_value.get.assert_called_once_with(
        calendarId="primary", eventId="event123"
    )
    assert response == {"id": "event123", "summary": "Meeting"}


def test_get_event_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.events.return_value.get.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.get_event("primary", "event123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_delete_event_rejects_empty_calendar_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_event("", "event123")


def test_delete_event_rejects_empty_event_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_event("primary", "")


def test_delete_event_calls_client_with_calendar_and_event_id():
    service, mock_api = _make_service()

    result = service.delete_event("primary", "event123")

    mock_api.events.return_value.delete.assert_called_once_with(
        calendarId="primary", eventId="event123"
    )
    assert result is None


def test_delete_event_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.events.return_value.delete.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.delete_event("primary", "event123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason
