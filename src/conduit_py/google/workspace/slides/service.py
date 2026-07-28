"""Google Slides API service wrapper."""

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError


class SlidesService:
    """Thin wrapper around the Google Slides API (``slides`` v1).

    Args:
        credentials: Authenticated Google credentials with Slides scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "slides",
            "v1",
            credentials=credentials
        )

    def create_slide(
        self,
        title: str
    ) -> dict:
        """Create a new presentation with the given title.

        Calls ``presentations().create`` with ``fields="presentationId"``,
        so only the new presentation's ID is returned — no slides, no
        layout/master data, nothing else from the created resource.

        Args:
            title: Title for the new presentation. Must not be empty.

        Returns:
            A dict containing only the key ``presentationId`` (the ID of
            the newly created presentation).

        Raises:
            ValueError: If ``title`` is empty.
            GoogleAPIError: If the Slides API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not title:
            raise ValueError("Slide title cannot be empty")
        
        body = {
            "title": title
        }
        
        try:
            response = (
                self.service
                .presentations()
                .create(body=body,
                fields="presentationId")
                .execute()
            )
            
            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to create spreadsheet: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            )