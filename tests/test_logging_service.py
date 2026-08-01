from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from conduit_py.google.cloud.logging.service import CloudLoggingService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[CloudLoggingService, MagicMock]:
    with patch(
        "conduit_py.google.cloud.logging.service.logging.Client"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.project = "test-project"
        mock_client_cls.return_value = mock_client
        service = CloudLoggingService(credentials=MagicMock(), project_name="test-project")
    return service, mock_client


def test_init_builds_client_with_project_and_credentials():
    credentials = MagicMock()
    with patch(
        "conduit_py.google.cloud.logging.service.logging.Client"
    ) as mock_client_cls:
        CloudLoggingService(credentials=credentials, project_name="test-project")

    mock_client_cls.assert_called_once_with(project="test-project", credentials=credentials)


def test_write_log_rejects_empty_log_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.write_log("", "hello")


def test_write_log_rejects_empty_message():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.write_log("my-log", "")


def test_write_log_logs_text_via_logger():
    service, mock_client = _make_service()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    result = service.write_log("my-log", "hello world", severity="ERROR")

    mock_client.logger.assert_called_once_with("my-log")
    mock_logger.log_text.assert_called_once_with("hello world", severity="ERROR")
    assert result is None


def test_write_log_defaults_severity_to_default():
    service, mock_client = _make_service()
    mock_logger = MagicMock()
    mock_client.logger.return_value = mock_logger

    service.write_log("my-log", "hello world")

    _, kwargs = mock_logger.log_text.call_args
    assert kwargs["severity"] == "DEFAULT"


def test_write_log_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.logger.return_value.log_text.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.write_log("my-log", "hello world")

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_list_entries_calls_client_with_no_filter_when_log_name_omitted():
    service, mock_client = _make_service()
    mock_client.list_entries.return_value = ["entry1", "entry2"]

    result = service.list_entries()

    mock_client.list_entries.assert_called_once_with(filter_=None, max_results=None)
    assert result == ["entry1", "entry2"]


def test_list_entries_builds_filter_from_log_name():
    service, mock_client = _make_service()
    mock_client.list_entries.return_value = []

    service.list_entries(log_name="my-log", max_results=10)

    mock_client.list_entries.assert_called_once_with(
        filter_='logName="projects/test-project/logs/my-log"',
        max_results=10,
    )


def test_list_entries_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.list_entries.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_entries()

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason
