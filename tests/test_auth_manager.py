from unittest.mock import patch

from conduit_py.google.auth.manager import GoogleAuthManager


def test_service_account_path_takes_precedence(tmp_path):
    sa_path = tmp_path / "sa.json"

    with patch(
        "conduit_py.google.auth.manager.ServiceAccountAuthenticator.authenticate",
        return_value="sa-creds",
    ) as mock_sa, patch(
        "conduit_py.google.auth.manager.OAuthAuthenticator.authenticate"
    ) as mock_oauth:
        result = GoogleAuthManager.authenticate(
            scopes=["scope"],
            oauth_client_path=tmp_path / "oauth.json",
            service_account_path=sa_path,
        )

    assert result == "sa-creds"
    mock_sa.assert_called_once_with(service_account_path=sa_path, scopes=["scope"])
    mock_oauth.assert_not_called()


def test_oauth_client_path_used_when_no_service_account(tmp_path):
    oauth_path = tmp_path / "oauth.json"

    with patch(
        "conduit_py.google.auth.manager.OAuthAuthenticator.authenticate",
        return_value="oauth-creds",
    ) as mock_oauth:
        result = GoogleAuthManager.authenticate(
            scopes=["scope"],
            oauth_client_path=oauth_path,
        )

    assert result == "oauth-creds"
    mock_oauth.assert_called_once_with(
        oauth_client_path=oauth_path, token_path=None, scopes=["scope"]
    )


def test_token_path_alone_routes_to_oauth(tmp_path):
    token_path = tmp_path / "token.json"

    with patch(
        "conduit_py.google.auth.manager.OAuthAuthenticator.authenticate",
        return_value="oauth-creds",
    ) as mock_oauth:
        result = GoogleAuthManager.authenticate(
            scopes=["scope"],
            token_path=token_path,
        )

    assert result == "oauth-creds"
    mock_oauth.assert_called_once_with(
        oauth_client_path=None, token_path=token_path, scopes=["scope"]
    )


def test_falls_back_to_adc_when_nothing_provided():
    with patch(
        "conduit_py.google.auth.manager.ADCAuthenticator.authenticate",
        return_value="adc-creds",
    ) as mock_adc:
        result = GoogleAuthManager.authenticate(scopes=["scope"])

    assert result == "adc-creds"
    mock_adc.assert_called_once_with(scopes=["scope"])
