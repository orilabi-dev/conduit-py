"""OAuth 2.0 authentication using a cached token and/or client secret."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from conduit_py.google.exceptions import GoogleAuthError


class OAuthAuthenticator:
    """Authenticates using an OAuth 2.0 installed-app flow.

    Loads and refreshes a cached token when available; otherwise runs a new
    local-server OAuth consent flow using an OAuth client secrets file.
    """

    @staticmethod
    def authenticate(
        scopes: list[str],
        oauth_client_path: Path | None = None,
        token_path: Path | None = None
    ) -> Credentials:
        """Resolve OAuth credentials, refreshing or re-authorizing as needed.

        Steps, in order:
            1. If ``token_path`` exists, load the cached token.
            2. If the loaded credentials are expired but have a refresh
               token, refresh them, persisting the refreshed token via
               ``_persist_token`` (only if ``token_path`` was given).
            3. If credentials are still missing or invalid, start a new
               local-server OAuth flow using ``oauth_client_path`` and
               persist the resulting token via ``_persist_token`` (only if
               ``token_path`` was given).

        Args:
            scopes: Google OAuth scopes to request.
            oauth_client_path: Path to an OAuth client secrets file.
                Required to start a new authorization flow; not needed if a
                valid cached token is found.
            token_path: Path to a cached OAuth token (JSON). Read from if it
                exists, and written to after a successful refresh or new
                authorization — but only when this argument is provided.

        Returns:
            A ``google.oauth2.credentials.Credentials`` instance, valid for
            the requested scopes.

        Raises:
            GoogleAuthError: If no valid cached token is found and
                ``oauth_client_path`` was not provided, or if
                ``oauth_client_path`` was provided but does not point to an
                existing file.
        """
        creds = None

        # 1. Load existing token
        if token_path and token_path.exists():
            creds = Credentials.from_authorized_user_file(
                filename=token_path,
                scopes=scopes,
            )

        # 2. Refresh expired credentials
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if token_path:
                OAuthAuthenticator._persist_token(token_path, creds)

        # 3. If no valid credentials, start a new OAuth flow
        if not creds or not creds.valid:
            if not oauth_client_path:
                raise GoogleAuthError(
                    "No valid cached token was found and oauth_client_path "
                    "was not provided; an OAuth client secret is required "
                    "to start a new authorization flow."
                )

            if not oauth_client_path.exists():
                raise GoogleAuthError(
                    f"OAuth client credentials not found: {oauth_client_path}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                oauth_client_path,
                scopes=scopes,
            )

            creds = flow.run_local_server(
                port=0
            )

            if token_path:
                OAuthAuthenticator._persist_token(token_path, creds)

        return creds

    @staticmethod
    def _persist_token(token_path: Path, creds: Credentials) -> None:
        """Write a token to disk, creating parent directories as needed.

        Called from ``authenticate`` only when a ``token_path`` was
        supplied; with no ``token_path``, refreshed or newly issued
        credentials are returned to the caller but never written to disk.

        Args:
            token_path: Destination path for the serialized token JSON.
            creds: Credentials whose ``to_json()`` output is written.
        """
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
