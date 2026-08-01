"""Google Calendar API service wrapper."""

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError


class CalendarService:
    """Thin wrapper around the Google Calendar API (``calendar`` v3).

    Args:
        credentials: Authenticated Google credentials with Calendar
            scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "calendar",
            "v3",
            credentials=credentials
        )

    def create_event(
        self,
        calendar_id: str,
        summary: str,
        start_time: str,
        end_time: str
    ) -> dict:
        """Create a new event on a calendar.

        Calls ``events().insert``. ``start_time``/``end_time`` are passed
        through as the Calendar API's ``dateTime`` field, so they must be
        RFC3339 timestamps (e.g. ``"2026-01-15T09:00:00-05:00"``).

        Args:
            calendar_id: ID of the calendar to add the event to (use
                ``"primary"`` for the authenticated user's main
                calendar). Must not be empty.
            summary: Title of the event. Must not be empty.
            start_time: RFC3339 start timestamp. Must not be empty.
            end_time: RFC3339 end timestamp. Must not be empty.

        Returns:
            A dict representing the created Calendar ``Event`` resource.

        Raises:
            ValueError: If any argument is empty.
            GoogleAPIError: If the Calendar API request fails; carries
                the original ``status_code`` and ``reason`` from the
                failed request.
        """
        if not calendar_id:
            raise ValueError("Calendar ID cannot be empty")
        if not summary:
            raise ValueError("Summary cannot be empty")
        if not start_time:
            raise ValueError("Start time cannot be empty")
        if not end_time:
            raise ValueError("End time cannot be empty")

        body = {
            "summary": summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
        }

        try:
            response = (
                self.service
                .events()
                .insert(calendarId=calendar_id, body=body)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to create event: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def list_events(
        self,
        calendar_id: str,
        time_min: str | None = None
    ) -> list:
        """List events on a calendar.

        Calls ``events().list``. The Calendar API paginates results
        server-side; this method returns only the first page's
        ``"items"`` list without following ``nextPageToken``.

        Args:
            calendar_id: ID of the calendar to list events from (use
                ``"primary"`` for the authenticated user's main
                calendar). Must not be empty.
            time_min: RFC3339 timestamp; if given, only events starting
                at or after this time are returned.

        Returns:
            A list of Calendar ``Event`` resource dicts.

        Raises:
            ValueError: If ``calendar_id`` is empty.
            GoogleAPIError: If the Calendar API request fails; carries
                the original ``status_code`` and ``reason`` from the
                failed request.
        """
        if not calendar_id:
            raise ValueError("Calendar ID cannot be empty")

        try:
            request = (
                self.service.events().list(calendarId=calendar_id, timeMin=time_min)
                if time_min
                else self.service.events().list(calendarId=calendar_id)
            )
            response = request.execute()

            return response.get("items", [])
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to list events: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def get_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> dict:
        """Fetch a single event's full details.

        Calls ``events().get``.

        Args:
            calendar_id: ID of the calendar the event belongs to. Must
                not be empty.
            event_id: ID of the event to fetch. Must not be empty.

        Returns:
            A dict representing the full Calendar ``Event`` resource.

        Raises:
            ValueError: If ``calendar_id`` or ``event_id`` is empty.
            GoogleAPIError: If the Calendar API request fails; carries
                the original ``status_code`` and ``reason`` from the
                failed request.
        """
        if not calendar_id:
            raise ValueError("Calendar ID cannot be empty")
        if not event_id:
            raise ValueError("Event ID cannot be empty")

        try:
            response = (
                self.service
                .events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to get event: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def delete_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> None:
        """Delete an event from a calendar.

        Calls ``events().delete``.

        Args:
            calendar_id: ID of the calendar the event belongs to. Must
                not be empty.
            event_id: ID of the event to delete. Must not be empty.

        Raises:
            ValueError: If ``calendar_id`` or ``event_id`` is empty.
            GoogleAPIError: If the Calendar API request fails; carries
                the original ``status_code`` and ``reason`` from the
                failed request.
        """
        if not calendar_id:
            raise ValueError("Calendar ID cannot be empty")
        if not event_id:
            raise ValueError("Event ID cannot be empty")

        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to delete event: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error
