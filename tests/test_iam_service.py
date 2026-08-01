from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from conduit_py.google.cloud.iam.service import IAMService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[IAMService, MagicMock]:
    with patch("conduit_py.google.cloud.iam.service.iam_admin_v1.IAMClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.common_project_path.side_effect = (
            lambda project: f"projects/{project}"
        )
        mock_client.service_account_path.side_effect = (
            lambda project, email: f"projects/{project}/serviceAccounts/{email}"
        )
        service = IAMService(credentials=MagicMock(), project_name="test-project")
    return service, mock_client


def test_init_builds_client_with_credentials_only():
    credentials = MagicMock()
    with patch("conduit_py.google.cloud.iam.service.iam_admin_v1.IAMClient") as mock_client_cls:
        service = IAMService(credentials=credentials, project_name="test-project")

    mock_client_cls.assert_called_once_with(credentials=credentials)
    assert service.project_name == "test-project"


def test_create_service_account_rejects_empty_account_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_service_account("", "Test SA")


def test_create_service_account_rejects_empty_display_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_service_account("test-sa", "")


def test_create_service_account_calls_client_with_expected_args():
    service, mock_client = _make_service()
    fake_sa = MagicMock(name="ServiceAccount")
    mock_client.create_service_account.return_value = fake_sa

    result = service.create_service_account("test-sa", "Test SA")

    _, kwargs = mock_client.create_service_account.call_args
    assert kwargs["name"] == "projects/test-project"
    assert kwargs["account_id"] == "test-sa"
    assert kwargs["service_account"].display_name == "Test SA"
    assert result is fake_sa


def test_create_service_account_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.create_service_account.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_service_account("test-sa", "Test SA")

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_list_service_accounts_calls_client_with_project_path():
    service, mock_client = _make_service()
    mock_client.list_service_accounts.return_value = ["sa1", "sa2"]

    result = service.list_service_accounts()

    mock_client.list_service_accounts.assert_called_once_with(name="projects/test-project")
    assert result == ["sa1", "sa2"]


def test_list_service_accounts_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.list_service_accounts.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_service_accounts()

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_delete_service_account_rejects_empty_email():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_service_account("")


def test_delete_service_account_calls_client_with_service_account_path():
    service, mock_client = _make_service()

    result = service.delete_service_account("test-sa@test-project.iam.gserviceaccount.com")

    mock_client.delete_service_account.assert_called_once_with(
        name="projects/test-project/serviceAccounts/test-sa@test-project.iam.gserviceaccount.com"
    )
    assert result is None


def test_delete_service_account_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.delete_service_account.side_effect = NotFound("service account not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.delete_service_account("test-sa@test-project.iam.gserviceaccount.com")

    assert exc_info.value.status_code == 404
    assert "service account not found" in exc_info.value.reason


def test_create_service_account_key_rejects_empty_email():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_service_account_key("")


def test_create_service_account_key_calls_client_with_service_account_path():
    service, mock_client = _make_service()
    fake_key = MagicMock(name="ServiceAccountKey")
    mock_client.create_service_account_key.return_value = fake_key

    result = service.create_service_account_key("test-sa@test-project.iam.gserviceaccount.com")

    mock_client.create_service_account_key.assert_called_once_with(
        name="projects/test-project/serviceAccounts/test-sa@test-project.iam.gserviceaccount.com"
    )
    assert result is fake_key


def test_create_service_account_key_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.create_service_account_key.side_effect = NotFound("service account not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_service_account_key("test-sa@test-project.iam.gserviceaccount.com")

    assert exc_info.value.status_code == 404
    assert "service account not found" in exc_info.value.reason
