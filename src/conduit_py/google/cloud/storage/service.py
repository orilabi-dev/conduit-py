"""Google Cloud Storage API service wrapper."""

from google.api_core.exceptions import GoogleAPICallError
from google.api_core.page_iterator import HTTPIterator
from google.auth.credentials import Credentials
from google.cloud import storage
from google.cloud.storage import Bucket

from conduit_py.google.exceptions import GoogleAPIError


class CloudStorageService:
    """Manages buckets and objects using a shared ``storage.Client``.

    Args:
        credentials: Authenticated Google credentials with Cloud Storage
            access.
        project_name: The GCP project to create/list buckets in.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.client = storage.Client(
            project=project_name,
            credentials=credentials
        )

    def create_bucket(
        self,
        bucket_name: str
    ) -> Bucket:
        """Create a new bucket in the client's project.

        Args:
            bucket_name: The globally-unique name for the new bucket.

        Returns:
            The created ``Bucket``.

        Raises:
            ValueError: If ``bucket_name`` is empty.
            GoogleAPIError: If the bucket cannot be created.
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")

        try:
            return self.client.create_bucket(bucket_name)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create bucket: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_buckets(self) -> HTTPIterator:
        """List the buckets in the client's project.

        Returns:
            An iterator over the project's ``Bucket`` objects.

        Raises:
            GoogleAPIError: If the buckets cannot be listed.
        """
        try:
            return self.client.list_buckets()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list buckets: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def upload_blob(
        self,
        bucket_name: str,
        blob_name: str,
        data: str | bytes
    ) -> None:
        """Upload data to an object in a bucket, overwriting it if present.

        Args:
            bucket_name: The bucket to upload into.
            blob_name: The destination object name.
            data: The content to upload. ``str`` values are UTF-8 encoded.

        Raises:
            ValueError: If ``bucket_name``, ``blob_name``, or ``data`` is
                empty.
            GoogleAPIError: If the upload fails.
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")

        if not blob_name:
            raise ValueError("Blob name cannot be empty")

        if not data:
            raise ValueError("Data cannot be empty")

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(data)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to upload blob: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def download_blob(
        self,
        bucket_name: str,
        blob_name: str
    ) -> bytes:
        """Download an object's raw content.

        Args:
            bucket_name: The bucket containing the object.
            blob_name: The object to download.

        Returns:
            The object's raw content as bytes.

        Raises:
            ValueError: If ``bucket_name`` or ``blob_name`` is empty.
            GoogleAPIError: If the download fails.
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")

        if not blob_name:
            raise ValueError("Blob name cannot be empty")

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to download blob: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_blobs(
        self,
        bucket_name: str
    ) -> HTTPIterator:
        """List the objects in a bucket.

        Args:
            bucket_name: The bucket to list objects from.

        Returns:
            An iterator over the bucket's ``Blob`` objects.

        Raises:
            ValueError: If ``bucket_name`` is empty.
            GoogleAPIError: If the objects cannot be listed.
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")

        try:
            return self.client.list_blobs(bucket_name)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list blobs: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def delete_blob(
        self,
        bucket_name: str,
        blob_name: str
    ) -> None:
        """Delete an object from a bucket.

        Args:
            bucket_name: The bucket containing the object.
            blob_name: The object to delete.

        Raises:
            ValueError: If ``bucket_name`` or ``blob_name`` is empty.
            GoogleAPIError: If the object cannot be deleted.
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")

        if not blob_name:
            raise ValueError("Blob name cannot be empty")

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to delete blob: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
