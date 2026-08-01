from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.tasks.service import TasksService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def _make_service() -> tuple[TasksService, MagicMock]:
    with patch("conduit_py.google.workspace.tasks.service.build") as mock_build:
        mock_api = MagicMock()
        mock_build.return_value = mock_api
        service = TasksService(credentials=MagicMock())
    return service, mock_api


def test_create_task_rejects_empty_tasklist_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_task("", "Buy milk")


def test_create_task_rejects_empty_title():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_task("@default", "")


def test_create_task_calls_client_with_expected_body():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.insert.return_value.execute.return_value = {
        "id": "task123"
    }

    response = service.create_task("@default", "Buy milk")

    mock_api.tasks.return_value.insert.assert_called_once_with(
        tasklist="@default", body={"title": "Buy milk"}
    )
    assert response == {"id": "task123"}


def test_create_task_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.insert.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_task("@default", "Buy milk")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_list_tasks_rejects_empty_tasklist_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.list_tasks("")


def test_list_tasks_returns_items_on_success():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "task123", "title": "Buy milk"}]
    }

    result = service.list_tasks("@default")

    mock_api.tasks.return_value.list.assert_called_once_with(tasklist="@default")
    assert result == [{"id": "task123", "title": "Buy milk"}]


def test_list_tasks_returns_empty_list_when_no_items_key():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.list.return_value.execute.return_value = {}

    result = service.list_tasks("@default")

    assert result == []


def test_list_tasks_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.list.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_tasks("@default")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_complete_task_rejects_empty_tasklist_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.complete_task("", "task123")


def test_complete_task_rejects_empty_task_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.complete_task("@default", "")


def test_complete_task_calls_client_with_completed_status():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.patch.return_value.execute.return_value = {
        "id": "task123",
        "status": "completed",
    }

    response = service.complete_task("@default", "task123")

    mock_api.tasks.return_value.patch.assert_called_once_with(
        tasklist="@default", task="task123", body={"status": "completed"}
    )
    assert response == {"id": "task123", "status": "completed"}


def test_complete_task_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.patch.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.complete_task("@default", "task123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_delete_task_rejects_empty_tasklist_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_task("", "task123")


def test_delete_task_rejects_empty_task_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_task("@default", "")


def test_delete_task_calls_client_with_tasklist_and_task_id():
    service, mock_api = _make_service()

    result = service.delete_task("@default", "task123")

    mock_api.tasks.return_value.delete.assert_called_once_with(
        tasklist="@default", task="task123"
    )
    assert result is None


def test_delete_task_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.tasks.return_value.delete.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.delete_task("@default", "task123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason
