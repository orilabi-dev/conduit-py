from unittest.mock import MagicMock, patch

import pytest

from conduit_py.google.client import GoogleClient
from conduit_py.google.scopes import SheetsScope


def test_raises_when_no_scopes_given():
    with pytest.raises(ValueError):
        GoogleClient(scopes=[])


def test_normalizes_enum_and_string_scopes():
    with patch(
        "conduit_py.google.client.GoogleAuthManager.authenticate",
        return_value=MagicMock(),
    ) as mock_auth, patch("conduit_py.google.client.WorkspaceClient"):
        GoogleClient(scopes=[SheetsScope.WRITE, "https://example.com/custom"])

    _, kwargs = mock_auth.call_args
    assert kwargs["scopes"] == [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://example.com/custom",
    ]


def test_coerces_string_paths_to_path_objects(tmp_path):
    oauth_path = str(tmp_path / "oauth.json")

    with patch(
        "conduit_py.google.client.GoogleAuthManager.authenticate",
        return_value=MagicMock(),
    ) as mock_auth, patch("conduit_py.google.client.WorkspaceClient"):
        GoogleClient(scopes=[SheetsScope.WRITE], oauth_client_path=oauth_path)

    _, kwargs = mock_auth.call_args
    assert kwargs["oauth_client_path"] == tmp_path / "oauth.json"


def test_cloud_is_none_when_no_project_name_given():
    with patch(
        "conduit_py.google.client.GoogleAuthManager.authenticate",
        return_value=MagicMock(),
    ), patch("conduit_py.google.client.WorkspaceClient"), patch(
        "conduit_py.google.client.CloudClient"
    ) as mock_cloud_cls:
        client = GoogleClient(scopes=[SheetsScope.WRITE])

    mock_cloud_cls.assert_not_called()
    assert client.cloud is None


def test_cloud_is_built_when_project_name_given():
    credentials = MagicMock()

    with patch(
        "conduit_py.google.client.GoogleAuthManager.authenticate",
        return_value=credentials,
    ), patch("conduit_py.google.client.WorkspaceClient"), patch(
        "conduit_py.google.client.CloudClient"
    ) as mock_cloud_cls:
        client = GoogleClient(scopes=[SheetsScope.WRITE], project_name="test-project")

    mock_cloud_cls.assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.cloud is mock_cloud_cls.return_value
