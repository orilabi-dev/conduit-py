from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.drive.service import DriveService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def _make_service() -> tuple[DriveService, MagicMock]:
    with patch("conduit_py.google.workspace.drive.service.build") as mock_build:
        mock_api = MagicMock()
        mock_build.return_value = mock_api
        service = DriveService(credentials=MagicMock())
    return service, mock_api


def test_upload_file_rejects_empty_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.upload_file("", b"content")


def test_upload_file_rejects_empty_content():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.upload_file("report.txt", b"")


def test_upload_file_returns_id_on_success():
    service, mock_api = _make_service()
    mock_api.files.return_value.create.return_value.execute.return_value = {
        "id": "file123"
    }

    response = service.upload_file("report.txt", b"content")

    assert response == {"id": "file123"}


def test_upload_file_includes_parent_folder_when_given():
    service, mock_api = _make_service()
    mock_api.files.return_value.create.return_value.execute.return_value = {
        "id": "file123"
    }

    service.upload_file("report.txt", b"content", parent_folder_id="folder456")

    _, kwargs = mock_api.files.return_value.create.call_args
    assert kwargs["body"]["parents"] == ["folder456"]


def test_upload_file_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.files.return_value.create.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.upload_file("report.txt", b"content")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_download_file_rejects_empty_file_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.download_file("")


def test_download_file_returns_raw_bytes_on_success():
    service, mock_api = _make_service()
    mock_api.files.return_value.get_media.return_value.execute.return_value = b"raw bytes"

    result = service.download_file("file123")

    mock_api.files.return_value.get_media.assert_called_once_with(fileId="file123")
    assert result == b"raw bytes"


def test_download_file_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.files.return_value.get_media.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.download_file("file123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_list_files_returns_files_on_success():
    service, mock_api = _make_service()
    mock_api.files.return_value.list.return_value.execute.return_value = {
        "files": [{"id": "file123", "name": "report.txt"}]
    }

    result = service.list_files()

    assert result == [{"id": "file123", "name": "report.txt"}]


def test_list_files_returns_empty_list_when_no_files_key():
    service, mock_api = _make_service()
    mock_api.files.return_value.list.return_value.execute.return_value = {}

    result = service.list_files()

    assert result == []


def test_list_files_passes_query_when_given():
    service, mock_api = _make_service()
    mock_api.files.return_value.list.return_value.execute.return_value = {"files": []}

    service.list_files(query="name contains 'report'")

    mock_api.files.return_value.list.assert_called_once_with(
        q="name contains 'report'"
    )


def test_list_files_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.files.return_value.list.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_files()

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_delete_file_rejects_empty_file_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_file("")


def test_delete_file_calls_client_with_file_id():
    service, mock_api = _make_service()

    result = service.delete_file("file123")

    mock_api.files.return_value.delete.assert_called_once_with(fileId="file123")
    assert result is None


def test_delete_file_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.files.return_value.delete.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.delete_file("file123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_share_file_rejects_empty_file_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.share_file("", "user@example.com")


def test_share_file_rejects_empty_email():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.share_file("file123", "")


def test_share_file_calls_client_with_expected_permission_body():
    service, mock_api = _make_service()
    mock_api.permissions.return_value.create.return_value.execute.return_value = {
        "id": "permission123"
    }

    result = service.share_file("file123", "user@example.com", role="writer")

    mock_api.permissions.return_value.create.assert_called_once_with(
        fileId="file123",
        body={
            "type": "user",
            "role": "writer",
            "emailAddress": "user@example.com",
        },
        sendNotificationEmail=False,
    )
    assert result == {"id": "permission123"}


def test_share_file_defaults_to_reader_role():
    service, mock_api = _make_service()
    mock_api.permissions.return_value.create.return_value.execute.return_value = {}

    service.share_file("file123", "user@example.com")

    _, kwargs = mock_api.permissions.return_value.create.call_args
    assert kwargs["body"]["role"] == "reader"


def test_share_file_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.permissions.return_value.create.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.share_file("file123", "user@example.com")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason
