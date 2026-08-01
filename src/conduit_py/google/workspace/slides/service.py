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

    def get_presentation(
        self,
        presentation_id: str
    ) -> dict:
        """Fetch a presentation's full content and structure.

        Calls ``presentations().get``, so the response contains the
        complete Presentation resource: slides, layouts, masters, and
        page size — unlike ``create_slide``, which only returns the new
        presentation's ID.

        Args:
            presentation_id: ID of the presentation to fetch. Must not be
                empty.

        Returns:
            A dict representing the full Google Slides ``Presentation``
            resource.

        Raises:
            ValueError: If ``presentation_id`` is empty.
            GoogleAPIError: If the Slides API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not presentation_id:
            raise ValueError("Presentation ID cannot be empty")

        try:
            response = (
                self.service
                .presentations()
                .get(presentationId=presentation_id)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to get presentation: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error

    def add_slide(
        self,
        presentation_id: str
    ) -> dict:
        """Add a new blank slide to an existing presentation.

        Calls ``presentations().batchUpdate`` with a single ``createSlide``
        request. The new slide's object ID can be found in the response at
        ``replies[0]["createSlide"]["objectId"]``, useful for chaining
        further edits (e.g. adding shapes/text to the new slide), but this
        method returns the raw batchUpdate response without unpacking it.

        Args:
            presentation_id: ID of the presentation to add a slide to.
                Must not be empty.

        Returns:
            A dict representing the Slides API
            ``BatchUpdatePresentationResponse`` (presentation ID and a
            list of replies, one per request).

        Raises:
            ValueError: If ``presentation_id`` is empty.
            GoogleAPIError: If the Slides API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not presentation_id:
            raise ValueError("Presentation ID cannot be empty")

        try:
            response = (
                self.service
                .presentations()
                .batchUpdate(
                    presentationId=presentation_id,
                    body={"requests": [{"createSlide": {}}]},
                )
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to add slide: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error