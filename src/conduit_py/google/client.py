"""Main authenticated client for Google Workspace services.

Contains ``GoogleClient``, which resolves credentials via
``GoogleAuthManager`` and exposes a ``WorkspaceClient`` for Sheets/Docs/Slides
access.
"""

from enum import Enum
from pathlib import Path

from conduit_py.google.auth.manager import GoogleAuthManager
from conduit_py.google.workspace.client import WorkspaceClient


class GoogleClient:
    """Authenticates against Google and exposes Workspace service clients.

    On construction, resolves credentials for the requested scopes via
    ``GoogleAuthManager.authenticate`` (service account > OAuth > ADC, in
    that precedence) and builds a ``WorkspaceClient`` exposing ``.sheets``,
    ``.docs``, and ``.slides``.

    Args:
        scopes: Google OAuth scopes to request, as raw scope strings or
            members of a ``conduit_py.google.scopes`` enum. Must not be
            empty.
        token_path: Path to a cached OAuth token (JSON). Read if present;
            written back to after a successful OAuth flow or refresh.
        oauth_client_path: Path to an OAuth client secrets file, used to
            start a new OAuth flow when no valid cached token is found.
        service_account_path: Path to a service account key file. When
            given, it takes precedence over OAuth/ADC.

    Raises:
        ValueError: If ``scopes`` is empty.
        GoogleAuthError: If the OAuth path is selected but no valid cached
            token is found and no ``oauth_client_path`` was given, or a
            given credential file path does not exist.

    Attributes:
        scopes: The normalized list of scope strings actually requested.
        credentials: The resolved Google credentials object.
        workspace: A ``WorkspaceClient`` wired up with ``credentials``.
    """
    def __init__(
        self,
        scopes: list[str | Enum],
        token_path: str | Path | None = None,
        oauth_client_path: str | Path | None = None,
        service_account_path: str | Path | None = None
    ):  
        if not scopes:
            raise ValueError(
                "Provide at least one Google scope."
            )
        
        if token_path and not isinstance(token_path, Path):
            token_path = Path(token_path)

        if oauth_client_path and not isinstance(oauth_client_path, Path):
            oauth_client_path = Path(oauth_client_path)

        if service_account_path and not isinstance(service_account_path, Path):
            service_account_path = Path(service_account_path)
        
        self.scopes = self._normalize_scopes(scopes)
        
        self.credentials = GoogleAuthManager.authenticate(
            token_path=token_path,
            oauth_client_path=oauth_client_path,
            service_account_path=service_account_path,
            scopes=self.scopes
        )
        
        self.workspace = WorkspaceClient(
            credentials=self.credentials
        )
        
    @staticmethod
    def _normalize_scopes(scopes) -> list[str]:
        """Convert raw scope strings and/or enum members into plain strings.

        Args:
            scopes: Scopes as raw strings, ``Enum`` members (e.g. from
                ``conduit_py.google.scopes``), or a mix of both.

        Returns:
            A list of plain scope strings suitable for the Google auth
            libraries.
        """
        return [scope.value if isinstance(scope,Enum) else scope for scope in scopes]