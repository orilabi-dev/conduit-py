"""Google Drive API service wrapper."""

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaInMemoryUpload

from conduit_py.google.exceptions import GoogleAPIError


class DriveService:
    """Thin wrapper around the Google Drive API (``drive`` v3).

    Args:
        credentials: Authenticated Google credentials with Drive scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "drive",
            "v3",
            credentials=credentials
        )

    def upload_file(
        self,
        name: str,
        content: bytes,
        mime_type: str = "application/octet-stream",
        parent_folder_id: str | None = None
    ) -> dict:
        """Upload content as a new Drive file.

        Calls ``files().create`` with an in-memory media upload and
        ``fields="id"``, so only the new file's ID is returned — no
        metadata, no parents, nothing else from the created resource.

        Args:
            name: Name for the new file. Must not be empty.
            content: The file's raw bytes. Must not be empty.
            mime_type: MIME type of ``content``. Defaults to
                ``"application/octet-stream"``.
            parent_folder_id: ID of the Drive folder to create the file
                in. If omitted, the file is created at the root of My
                Drive.

        Returns:
            A dict containing only the key ``id`` (the ID of the newly
            created file).

        Raises:
            ValueError: If ``name`` or ``content`` is empty.
            GoogleAPIError: If the Drive API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not name:
            raise ValueError("File name cannot be empty")
        if not content:
            raise ValueError("Content cannot be empty")

        body = {"name": name}
        if parent_folder_id:
            body["parents"] = [parent_folder_id]

        media = MediaInMemoryUpload(content, mimetype=mime_type)

        try:
            response = (
                self.service
                .files()
                .create(body=body, media_body=media, fields="id")
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to upload file: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def download_file(
        self,
        file_id: str
    ) -> bytes:
        """Download a file's raw content.

        Calls ``files().get_media``, which returns the file's raw bytes
        directly rather than a JSON metadata response.

        Args:
            file_id: ID of the file to download. Must not be empty.

        Returns:
            The file's raw content as bytes.

        Raises:
            ValueError: If ``file_id`` is empty.
            GoogleAPIError: If the Drive API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not file_id:
            raise ValueError("File ID cannot be empty")

        try:
            return (
                self.service
                .files()
                .get_media(fileId=file_id)
                .execute()
            )
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to download file: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def list_files(
        self,
        query: str | None = None
    ) -> list:
        """List files visible to the authenticated identity.

        Calls ``files().list``. The Drive API paginates results
        server-side; this method returns only the first page's
        ``"files"`` list without following ``nextPageToken``.

        Args:
            query: A Drive API search query (e.g.
                ``"name contains 'report'"``). If omitted, lists all
                accessible files.

        Returns:
            A list of file metadata dicts (``id``, ``name``, and
            ``mimeType`` by default, per the API's default ``fields``).

        Raises:
            GoogleAPIError: If the Drive API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        try:
            request = (
                self.service.files().list(q=query)
                if query
                else self.service.files().list()
            )
            response = request.execute()

            return response.get("files", [])
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to list files: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def delete_file(
        self,
        file_id: str
    ) -> None:
        """Permanently delete a file, bypassing the trash.

        Calls ``files().delete``.

        Args:
            file_id: ID of the file to delete. Must not be empty.

        Raises:
            ValueError: If ``file_id`` is empty.
            GoogleAPIError: If the Drive API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not file_id:
            raise ValueError("File ID cannot be empty")

        try:
            self.service.files().delete(fileId=file_id).execute()
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to delete file: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def share_file(
        self,
        file_id: str,
        email: str,
        role: str = "reader"
    ) -> dict:
        """Grant a user access to a file.

        Calls ``permissions().create`` with a ``user``-type permission.
        Notification emails to the grantee are suppressed.

        Args:
            file_id: ID of the file to share. Must not be empty.
            email: Email address of the user to grant access to. Must
                not be empty.
            role: Drive permission role to grant (``"reader"``,
                ``"writer"``, or ``"commenter"``). Defaults to
                ``"reader"``.

        Returns:
            A dict representing the created Drive ``Permission``
            resource.

        Raises:
            ValueError: If ``file_id`` or ``email`` is empty.
            GoogleAPIError: If the Drive API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not file_id:
            raise ValueError("File ID cannot be empty")
        if not email:
            raise ValueError("Email cannot be empty")

        try:
            response = (
                self.service
                .permissions()
                .create(
                    fileId=file_id,
                    body={
                        "type": "user",
                        "role": role,
                        "emailAddress": email,
                    },
                    sendNotificationEmail=False,
                )
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to share file: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error
