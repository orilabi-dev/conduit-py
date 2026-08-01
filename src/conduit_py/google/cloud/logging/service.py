"""Google Cloud Logging API service wrapper."""

from collections.abc import Iterator

from google.api_core.exceptions import GoogleAPICallError
from google.auth.credentials import Credentials
from google.cloud import logging
from google.cloud.logging_v2.entries import LogEntry

from conduit_py.google.exceptions import GoogleAPIError


class CloudLoggingService:
    """Writes and reads log entries using a shared ``logging.Client``.

    Args:
        credentials: Authenticated Google credentials with Cloud Logging
            access.
        project_name: The GCP project logs are written to and read from.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.client = logging.Client(
            project=project_name,
            credentials=credentials
        )

    def write_log(
        self,
        log_name: str,
        message: str,
        severity: str = "DEFAULT"
    ) -> None:
        """Write a text log entry.

        Args:
            log_name: The log to write to (created automatically on
                first write if it doesn't exist).
            message: The text of the log entry.
            severity: The entry's severity level (e.g. ``"DEFAULT"``,
                ``"INFO"``, ``"WARNING"``, ``"ERROR"``). Defaults to
                ``"DEFAULT"``.

        Raises:
            ValueError: If ``log_name`` or ``message`` is empty.
            GoogleAPIError: If the log entry cannot be written.
        """
        if not log_name:
            raise ValueError("Log name cannot be empty")

        if not message:
            raise ValueError("Message cannot be empty")

        try:
            self.client.logger(log_name).log_text(message, severity=severity)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to write log entry: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_entries(
        self,
        log_name: str | None = None,
        max_results: int | None = None
    ) -> Iterator[LogEntry]:
        """List log entries in the client's project.

        Args:
            log_name: If given, restricts results to entries from this
                log only. If omitted, lists entries from every log in
                the project.
            max_results: Maximum number of entries to return. If
                omitted, all matching entries are returned.

        Returns:
            An iterator over matching ``LogEntry`` objects, most recent
            first.

        Raises:
            GoogleAPIError: If the log entries cannot be listed.
        """
        try:
            filter_ = (
                f'logName="projects/{self.client.project}/logs/{log_name}"'
                if log_name
                else None
            )
            return self.client.list_entries(filter_=filter_, max_results=max_results)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list log entries: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
