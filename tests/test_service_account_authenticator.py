from unittest.mock import patch

from conduit_py.google.auth.service_account import ServiceAccountAuthenticator


def test_authenticate_passes_path_and_scopes_through(tmp_path):
    sa_path = tmp_path / "sa.json"

    with patch(
        "conduit_py.google.auth.service_account.Credentials.from_service_account_file",
        return_value="sa-creds",
    ) as mock_from_file:
        result = ServiceAccountAuthenticator.authenticate(
            service_account_path=sa_path,
            scopes=["scope"],
        )

    assert result == "sa-creds"
    mock_from_file.assert_called_once_with(sa_path, scopes=["scope"])
