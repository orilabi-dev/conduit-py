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
