"""Google Gmail API service wrapper."""

import base64
from email.mime.text import MIMEText

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError


class GmailService:
    """Thin wrapper around the Gmail API (``gmail`` v1).

    All methods operate on the authenticated user's own mailbox
    (Gmail's ``userId="me"``).

    Args:
        credentials: Authenticated Google credentials with Gmail scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "gmail",
            "v1",
            credentials=credentials
        )

    def send_message(
        self,
        to: str,
        subject: str,
        body: str
    ) -> dict:
        """Send a plain-text email as the authenticated user.

        Builds a MIME text message, base64url-encodes it, and calls
        ``users().messages().send``.

        Args:
            to: Recipient email address. Must not be empty.
            subject: Email subject. Must not be empty.
            body: Plain-text email body. Must not be empty.

        Returns:
            A dict representing the sent Gmail ``Message`` resource
            (``id``, ``threadId``, ``labelIds``).

        Raises:
            ValueError: If ``to``, ``subject``, or ``body`` is empty.
            GoogleAPIError: If the Gmail API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not to:
            raise ValueError("Recipient cannot be empty")
        if not subject:
            raise ValueError("Subject cannot be empty")
        if not body:
            raise ValueError("Body cannot be empty")

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            response = (
                self.service
                .users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to send message: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def list_messages(
        self,
        query: str | None = None
    ) -> list:
        """List messages in the authenticated user's mailbox.

        Calls ``users().messages().list``. The Gmail API paginates
        results server-side; this method returns only the first page's
        ``"messages"`` list without following ``nextPageToken``.

        Args:
            query: A Gmail search query (e.g. ``"is:unread"``,
                ``"from:someone@example.com"``). If omitted, lists all
                messages.

        Returns:
            A list of message stubs, each a dict with only ``id`` and
            ``threadId`` — call ``get_message`` for full content.

        Raises:
            GoogleAPIError: If the Gmail API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        try:
            request = (
                self.service.users().messages().list(userId="me", q=query)
                if query
                else self.service.users().messages().list(userId="me")
            )
            response = request.execute()

            return response.get("messages", [])
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to list messages: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def get_message(
        self,
        message_id: str
    ) -> dict:
        """Fetch a message's full content and metadata.

        Calls ``users().messages().get``.

        Args:
            message_id: ID of the message to fetch. Must not be empty.

        Returns:
            A dict representing the full Gmail ``Message`` resource.

        Raises:
            ValueError: If ``message_id`` is empty.
            GoogleAPIError: If the Gmail API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not message_id:
            raise ValueError("Message ID cannot be empty")

        try:
            response = (
                self.service
                .users()
                .messages()
                .get(userId="me", id=message_id)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to get message: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def trash_message(
        self,
        message_id: str
    ) -> dict:
        """Move a message to Trash.

        Calls ``users().messages().trash``. This is recoverable — unlike
        a permanent delete, a trashed message can be restored (or is
        auto-purged after 30 days) — which is why it's the only removal
        method this service exposes.

        Args:
            message_id: ID of the message to trash. Must not be empty.

        Returns:
            A dict representing the updated Gmail ``Message`` resource.

        Raises:
            ValueError: If ``message_id`` is empty.
            GoogleAPIError: If the Gmail API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not message_id:
            raise ValueError("Message ID cannot be empty")

        try:
            response = (
                self.service
                .users()
                .messages()
                .trash(userId="me", id=message_id)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to trash message: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error
