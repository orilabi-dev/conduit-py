"""Top-level public entry point for conduit_py.

Contains ``Conduit``, the single class most callers import to obtain an
authenticated Google client.
"""

from enum import Enum
from pathlib import Path

from conduit_py.google.client import GoogleClient


class Conduit:
    """Public factory for authenticated Google service clients."""

    @staticmethod
    def google(
        scopes: list[str | Enum],
        token_path: str | Path | None = None,
        oauth_client_path: str | Path | None = None,
        service_account_path: str | Path | None = None
    ) -> GoogleClient:
        """Build an authenticated ``GoogleClient`` for the given scopes.

        This is the main public entry point for conduit_py: call it with the
        Google API scopes you need and whichever credential material is
        available, and it authenticates and wires up ``workspace.sheets``,
        ``.docs``, and ``.slides`` services for you.

        Authentication precedence (see
        ``conduit_py.google.auth.manager.GoogleAuthManager.authenticate``):
        1. ``service_account_path``, if provided.
        2. ``token_path`` and/or ``oauth_client_path``, if either is provided.
        3. Application Default Credentials (ADC), as a fallback.

        Args:
            scopes: Google OAuth scopes to request, as raw scope strings or
                members of a ``conduit_py.google.scopes`` enum (e.g.
                ``GoogleScopes.SHEETS.WRITE``). Must not be empty.
            token_path: Path to a cached OAuth token (JSON). Read if present;
                written back to after a successful OAuth flow or refresh.
            oauth_client_path: Path to an OAuth client secrets file, used to
                start a new OAuth flow when no valid cached token is found.
            service_account_path: Path to a service account key file. When
                given, it takes precedence over OAuth/ADC.

        Returns:
            A ``GoogleClient`` with credentials resolved and ``workspace``
            services ready to use.

        Raises:
            ValueError: If ``scopes`` is empty.
            GoogleAuthError: If the OAuth path is selected but no valid
                cached token is found and no ``oauth_client_path`` was given
                to start a new flow, or a given credential file path does
                not exist.
        """
        return GoogleClient(
            scopes=scopes,
            token_path=token_path,
            oauth_client_path=oauth_client_path,
            service_account_path=service_account_path
        )