from unittest.mock import MagicMock, patch

import pytest

from conduit_py.google.auth.oauth import OAuthAuthenticator
from conduit_py.google.exceptions import GoogleAuthError


def _fake_flow(creds):
    flow = MagicMock()
    flow.run_local_server.return_value = creds
    return flow


def test_raises_clear_error_when_no_token_and_no_client_secret(tmp_path):
    with pytest.raises(GoogleAuthError, match="oauth_client_path"):
        OAuthAuthenticator.authenticate(
            scopes=["scope"],
            token_path=tmp_path / "missing_token.json",
        )


def test_raises_when_client_secret_file_missing(tmp_path):
    missing = tmp_path / "does_not_exist.json"

    with pytest.raises(GoogleAuthError):
        OAuthAuthenticator.authenticate(
            scopes=["scope"],
            oauth_client_path=missing,
        )


def test_runs_flow_and_persists_token_to_explicit_path(tmp_path):
    client_secret = tmp_path / "client_secret.json"
    client_secret.write_text("{}")
    token_path = tmp_path / "nested" / "token.json"

    creds = MagicMock()
    creds.to_json.return_value = '{"fake": true}'

    with patch(
        "conduit_py.google.auth.oauth.InstalledAppFlow.from_client_secrets_file",
        return_value=_fake_flow(creds),
    ):
        result = OAuthAuthenticator.authenticate(
            scopes=["scope"],
            oauth_client_path=client_secret,
            token_path=token_path,
        )

    assert result is creds
    assert token_path.exists()
    assert token_path.read_text() == '{"fake": true}'


def test_does_not_write_anywhere_when_token_path_omitted(tmp_path, monkeypatch):
    client_secret = tmp_path / "client_secret.json"
    client_secret.write_text("{}")

    creds = MagicMock()
    creds.to_json.return_value = '{"fake": true}'

    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    with patch(
        "conduit_py.google.auth.oauth.InstalledAppFlow.from_client_secrets_file",
        return_value=_fake_flow(creds),
    ):
        result = OAuthAuthenticator.authenticate(
            scopes=["scope"],
            oauth_client_path=client_secret,
        )

    assert result is creds
    assert list(cwd.iterdir()) == []
