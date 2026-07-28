"""Auth strategy selection for Google credentials.

Contains ``GoogleAuthManager``, which decides whether to authenticate via a
service account, OAuth (cached token and/or client secret), or Application
Default Credentials, based on which arguments were supplied.
"""

from enum import Enum
from pathlib import Path

from conduit_py.google.auth.adc import ADCAuthenticator
from conduit_py.google.auth.oauth import OAuthAuthenticator
from conduit_py.google.auth.service_account import ServiceAccountAuthenticator


class GoogleAuthManager:
    """Selects and delegates to the appropriate Google authenticator."""

    @staticmethod
    def authenticate(
        scopes: list[str | Enum],
        token_path: Path | None = None,
        oauth_client_path: Path | None = None,
        service_account_path: Path | None = None,
    ):
        """Resolve Google credentials using a fixed precedence order.

        Precedence, most to least specific:
            1. ``service_account_path`` — if given, authenticates via
               ``ServiceAccountAuthenticator`` and nothing else is
               considered.
            2. ``token_path`` and/or ``oauth_client_path`` — if either is
               given, authenticates via ``OAuthAuthenticator`` (a cached
               token is reused/refreshed if valid; otherwise a new OAuth
               flow is started, provided ``oauth_client_path`` was given).
            3. Application Default Credentials (ADC) — used only when none
               of the above were supplied.

        Args:
            scopes: Google OAuth scopes to request.
            token_path: Path to a cached OAuth token (JSON).
            oauth_client_path: Path to an OAuth client secrets file.
            service_account_path: Path to a service account key file.

        Returns:
            A Google credentials object: a
            ``google.oauth2.service_account.Credentials``, a
            ``google.oauth2.credentials.Credentials``, or the ADC default
            credentials, depending on which path was taken.

        Raises:
            GoogleAuthError: If the OAuth path is taken, no valid cached
                token is found, and no ``oauth_client_path`` was given to
                start a new flow, or ``oauth_client_path`` was given but
                does not exist.
        """
        # Precedence: service accounts are the most explicit/unambiguous choice, so
        # they win outright; OAuth (token cache and/or client secret) is next; ADC
        # is only the fallback when nothing else was supplied.
        if service_account_path:
            return ServiceAccountAuthenticator().authenticate(
                service_account_path=service_account_path,
                scopes=scopes
            )

        if token_path or oauth_client_path:
            return OAuthAuthenticator().authenticate(
                oauth_client_path=oauth_client_path,
                token_path=token_path,
                scopes=scopes
            )

        return ADCAuthenticator.authenticate(
            scopes=scopes
        )