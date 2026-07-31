from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from conduit_py.google.cloud.bigquery.service import BigQueryService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[BigQueryService, MagicMock]:
    with patch("conduit_py.google.cloud.bigquery.service.bigquery.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        service = BigQueryService(credentials=MagicMock(), project_name="test-project")
    return service, mock_client


def test_init_builds_client_with_project_and_credentials():
    credentials = MagicMock()
    with patch("conduit_py.google.cloud.bigquery.service.bigquery.Client") as mock_client_cls:
        BigQueryService(credentials=credentials, project_name="test-project")

    mock_client_cls.assert_called_once_with(project="test-project", credentials=credentials)


def test_query_and_wait_rejects_empty_query():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.query_and_wait("")


def test_query_and_wait_returns_rows_on_success():
    service, mock_client = _make_service()
    mock_client.query_and_wait.return_value = ["row1", "row2"]

    result = service.query_and_wait("SELECT 1")

    mock_client.query_and_wait.assert_called_once_with("SELECT 1")
    assert result == ["row1", "row2"]


def test_query_and_wait_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.query_and_wait.side_effect = NotFound("table not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.query_and_wait("SELECT 1")

    assert exc_info.value.status_code == 404
    assert "table not found" in exc_info.value.reason


def test_query_rejects_empty_query():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.query("")


def test_query_returns_job_without_waiting():
    service, mock_client = _make_service()
    fake_job = MagicMock(name="QueryJob")
    mock_client.query.return_value = fake_job

    result = service.query("SELECT 1")

    mock_client.query.assert_called_once_with("SELECT 1")
    assert result is fake_job


def test_query_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.query.side_effect = NotFound("bad query")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.query("SELECT 1")

    assert exc_info.value.status_code == 404
    assert "bad query" in exc_info.value.reason
