"""Google Tasks API service wrapper."""

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError


class TasksService:
    """Thin wrapper around the Google Tasks API (``tasks`` v1).

    Args:
        credentials: Authenticated Google credentials with Tasks scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "tasks",
            "v1",
            credentials=credentials
        )

    def create_task(
        self,
        tasklist_id: str,
        title: str
    ) -> dict:
        """Create a new task on a task list.

        Calls ``tasks().insert``.

        Args:
            tasklist_id: ID of the task list to add the task to (use
                ``"@default"`` for the authenticated user's default
                list). Must not be empty.
            title: Title of the task. Must not be empty.

        Returns:
            A dict representing the created Tasks ``Task`` resource.

        Raises:
            ValueError: If ``tasklist_id`` or ``title`` is empty.
            GoogleAPIError: If the Tasks API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not tasklist_id:
            raise ValueError("Task list ID cannot be empty")
        if not title:
            raise ValueError("Title cannot be empty")

        try:
            response = (
                self.service
                .tasks()
                .insert(tasklist=tasklist_id, body={"title": title})
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to create task: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def list_tasks(
        self,
        tasklist_id: str
    ) -> list:
        """List tasks on a task list.

        Calls ``tasks().list``. The Tasks API paginates results
        server-side; this method returns only the first page's
        ``"items"`` list without following ``nextPageToken``. Completed
        tasks are included unless ``tasklist_id``'s list has them
        hidden by the API's own default filtering.

        Args:
            tasklist_id: ID of the task list to list tasks from (use
                ``"@default"`` for the authenticated user's default
                list). Must not be empty.

        Returns:
            A list of Tasks ``Task`` resource dicts.

        Raises:
            ValueError: If ``tasklist_id`` is empty.
            GoogleAPIError: If the Tasks API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not tasklist_id:
            raise ValueError("Task list ID cannot be empty")

        try:
            response = (
                self.service
                .tasks()
                .list(tasklist=tasklist_id)
                .execute()
            )

            return response.get("items", [])
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to list tasks: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def complete_task(
        self,
        tasklist_id: str,
        task_id: str
    ) -> dict:
        """Mark a task as completed.

        Calls ``tasks().patch`` with ``status="completed"``, leaving all
        other fields (title, notes, due date) unchanged.

        Args:
            tasklist_id: ID of the task list the task belongs to. Must
                not be empty.
            task_id: ID of the task to complete. Must not be empty.

        Returns:
            A dict representing the updated Tasks ``Task`` resource.

        Raises:
            ValueError: If ``tasklist_id`` or ``task_id`` is empty.
            GoogleAPIError: If the Tasks API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not tasklist_id:
            raise ValueError("Task list ID cannot be empty")
        if not task_id:
            raise ValueError("Task ID cannot be empty")

        try:
            response = (
                self.service
                .tasks()
                .patch(
                    tasklist=tasklist_id,
                    task=task_id,
                    body={"status": "completed"},
                )
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to complete task: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def delete_task(
        self,
        tasklist_id: str,
        task_id: str
    ) -> None:
        """Delete a task.

        Calls ``tasks().delete``.

        Args:
            tasklist_id: ID of the task list the task belongs to. Must
                not be empty.
            task_id: ID of the task to delete. Must not be empty.

        Raises:
            ValueError: If ``tasklist_id`` or ``task_id`` is empty.
            GoogleAPIError: If the Tasks API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not tasklist_id:
            raise ValueError("Task list ID cannot be empty")
        if not task_id:
            raise ValueError("Task ID cannot be empty")

        try:
            self.service.tasks().delete(
                tasklist=tasklist_id, task=task_id
            ).execute()
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to delete task: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error
