"""Google Docs API service wrapper."""

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError


class DocsService:
    """Thin wrapper around the Google Docs API (``docs`` v1).

    Args:
        credentials: Authenticated Google credentials with Docs scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "docs",
            "v1",
            credentials=credentials
        )

    def create_doc(
        self,
        title: str
    ) -> dict:
        """Create a new document with the given title.

        Calls ``documents().create`` with ``fields="documentId"``, so only
        the new document's ID is returned — no body content, no revision
        info, nothing else from the created resource.

        Args:
            title: Title for the new document. Must not be empty.

        Returns:
            A dict containing only the key ``documentId`` (the ID of the
            newly created document).

        Raises:
            ValueError: If ``title`` is empty.
            GoogleAPIError: If the Docs API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not title:
            raise ValueError("Sheet title cannot be empty")
        
        body = {
            "title": title
        }
        
        try:
            response = (
                self.service
                .documents()
                .create(body=body,
                fields="documentId")
                .execute()
            )
            
            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to create document: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            )