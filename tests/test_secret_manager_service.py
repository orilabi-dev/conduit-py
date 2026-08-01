from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound, PermissionDenied

from conduit_py.google.cloud.secret_manager.service import SecretManagerService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[SecretManagerService, MagicMock]:
    with patch(
        "conduit_py.google.cloud.secret_manager.service.secretmanager.SecretManagerServiceClient"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        service = SecretManagerService(credentials=MagicMock(), project_name="test-project")
    return service, mock_client


def test_init_builds_client_with_credentials_only():
    credentials = MagicMock()
    with patch(
        "conduit_py.google.cloud.secret_manager.service.secretmanager.SecretManagerServiceClient"
    ) as mock_client_cls:
        service = SecretManagerService(credentials=credentials, project_name="test-project")

    mock_client_cls.assert_called_once_with(credentials=credentials)
    assert service.project_name == "test-project"


def test_create_secret_rejects_empty_secret_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_secret("")


def test_create_secret_calls_client_with_expected_request():
    service, mock_client = _make_service()
    mock_client.create_secret.return_value = "created-secret"

    result = service.create_secret("my-secret")

    mock_client.create_secret.assert_called_once_with(
        request={
            "parent": "projects/test-project",
            "secret_id": "my-secret",
            "secret": {"replication": {"automatic": {}}},
        }
    )
    assert result == "created-secret"


def test_create_secret_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.create_secret.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_secret("my-secret")

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_add_secret_version_rejects_empty_secret_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.add_secret_version("", payload="value")


def test_add_secret_version_rejects_empty_payload():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.add_secret_version("my-secret", payload="")


def test_add_secret_version_encodes_str_payload_and_calls_client():
    service, mock_client = _make_service()
    mock_client.add_secret_version.return_value = "created-version"

    result = service.add_secret_version("my-secret", payload="hunter2")

    mock_client.add_secret_version.assert_called_once_with(
        request={
            "parent": "projects/test-project/secrets/my-secret",
            "payload": {"data": b"hunter2"},
        }
    )
    assert result == "created-version"


def test_add_secret_version_passes_bytes_payload_through_unchanged():
    service, mock_client = _make_service()

    service.add_secret_version("my-secret", payload=b"raw-bytes")

    _, kwargs = mock_client.add_secret_version.call_args
    assert kwargs["request"]["payload"]["data"] == b"raw-bytes"


def test_add_secret_version_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.add_secret_version.side_effect = NotFound("secret not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.add_secret_version("my-secret", payload="value")

    assert exc_info.value.status_code == 404
    assert "secret not found" in exc_info.value.reason


def test_access_secret_version_rejects_empty_secret_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.access_secret_version("")


def test_access_secret_version_defaults_to_latest_and_returns_payload_bytes():
    service, mock_client = _make_service()
    mock_response = MagicMock()
    mock_response.payload.data = b"hunter2"
    mock_client.access_secret_version.return_value = mock_response

    result = service.access_secret_version("my-secret")

    mock_client.access_secret_version.assert_called_once_with(
        request={"name": "projects/test-project/secrets/my-secret/versions/latest"}
    )
    assert result == b"hunter2"


def test_access_secret_version_uses_given_version_id():
    service, mock_client = _make_service()
    mock_client.access_secret_version.return_value = MagicMock()

    service.access_secret_version("my-secret", version_id="3")

    mock_client.access_secret_version.assert_called_once_with(
        request={"name": "projects/test-project/secrets/my-secret/versions/3"}
    )


def test_access_secret_version_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.access_secret_version.side_effect = NotFound("version not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.access_secret_version("my-secret")

    assert exc_info.value.status_code == 404
    assert "version not found" in exc_info.value.reason


def test_list_secrets_calls_client_with_expected_request():
    service, mock_client = _make_service()
    mock_client.list_secrets.return_value = ["secret1", "secret2"]

    result = service.list_secrets()

    mock_client.list_secrets.assert_called_once_with(
        request={"parent": "projects/test-project"}
    )
    assert result == ["secret1", "secret2"]


def test_list_secrets_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.list_secrets.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_secrets()

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_list_secret_versions_rejects_empty_secret_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.list_secret_versions("")


def test_list_secret_versions_calls_client_with_expected_request():
    service, mock_client = _make_service()
    mock_client.list_secret_versions.return_value = ["version1", "version2"]

    result = service.list_secret_versions("my-secret")

    mock_client.list_secret_versions.assert_called_once_with(
        request={"parent": "projects/test-project/secrets/my-secret"}
    )
    assert result == ["version1", "version2"]


def test_list_secret_versions_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.list_secret_versions.side_effect = NotFound("secret not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_secret_versions("my-secret")

    assert exc_info.value.status_code == 404
    assert "secret not found" in exc_info.value.reason


def test_delete_secret_rejects_empty_secret_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_secret("")


def test_delete_secret_calls_client_with_expected_request():
    service, mock_client = _make_service()

    result = service.delete_secret("my-secret")

    mock_client.delete_secret.assert_called_once_with(
        request={"name": "projects/test-project/secrets/my-secret"}
    )
    assert result is None


def test_delete_secret_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.delete_secret.side_effect = NotFound("secret not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.delete_secret("my-secret")

    assert exc_info.value.status_code == 404
    assert "secret not found" in exc_info.value.reason


def test_secret_exists_rejects_empty_secret_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.secret_exists("")


def test_secret_exists_returns_true_when_secret_found():
    service, mock_client = _make_service()
    mock_client.get_secret.return_value = MagicMock()

    result = service.secret_exists("my-secret")

    mock_client.get_secret.assert_called_once_with(
        request={"name": "projects/test-project/secrets/my-secret"}
    )
    assert result is True


def test_secret_exists_returns_false_on_not_found():
    service, mock_client = _make_service()
    mock_client.get_secret.side_effect = NotFound("secret not found")

    result = service.secret_exists("my-secret")

    assert result is False


def test_secret_exists_wraps_other_api_call_errors():
    service, mock_client = _make_service()
    mock_client.get_secret.side_effect = PermissionDenied("access denied")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.secret_exists("my-secret")

    assert exc_info.value.status_code == 403
    assert "access denied" in exc_info.value.reason
