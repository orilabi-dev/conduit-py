"""Google Cloud Firestore API service wrapper."""

from google.api_core.exceptions import GoogleAPICallError
from google.auth.credentials import Credentials
from google.cloud import firestore
from google.cloud.firestore_v1.stream_generator import StreamGenerator

from conduit_py.google.exceptions import GoogleAPIError


class FirestoreService:
    """Reads and writes documents using a shared ``firestore.Client``.

    Args:
        credentials: Authenticated Google credentials with Firestore
            access.
        project_name: The GCP project the Firestore database belongs to.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.client = firestore.Client(
            project=project_name,
            credentials=credentials
        )

    def create_document(
        self,
        collection: str,
        document_id: str,
        data: dict
    ) -> None:
        """Create or overwrite a document.

        Calls ``DocumentReference.set``, which creates the document if it
        doesn't exist and fully overwrites it (not merges) if it does.

        Args:
            collection: The collection to create the document in.
            document_id: The ID to create the document under.
            data: The document's field data.

        Raises:
            ValueError: If ``collection``, ``document_id``, or ``data``
                is empty.
            GoogleAPIError: If the document cannot be written.
        """
        if not collection:
            raise ValueError("Collection cannot be empty")

        if not document_id:
            raise ValueError("Document ID cannot be empty")

        if not data:
            raise ValueError("Data cannot be empty")

        try:
            self.client.collection(collection).document(document_id).set(data)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create document: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def get_document(
        self,
        collection: str,
        document_id: str
    ) -> dict | None:
        """Fetch a document's field data.

        Calls ``DocumentReference.get``. Firestore doesn't raise when a
        document is missing — it returns a snapshot with no data — so
        this method returns ``None`` in that case instead of raising.

        Args:
            collection: The collection containing the document.
            document_id: The document to fetch.

        Returns:
            The document's field data, or ``None`` if it doesn't exist.

        Raises:
            ValueError: If ``collection`` or ``document_id`` is empty.
            GoogleAPIError: If the document cannot be fetched.
        """
        if not collection:
            raise ValueError("Collection cannot be empty")

        if not document_id:
            raise ValueError("Document ID cannot be empty")

        try:
            snapshot = self.client.collection(collection).document(document_id).get()
            return snapshot.to_dict()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to get document: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def update_document(
        self,
        collection: str,
        document_id: str,
        data: dict
    ) -> None:
        """Update specific fields of an existing document.

        Calls ``DocumentReference.update``, which merges ``data`` into
        the existing document rather than overwriting it. Unlike
        ``create_document``, this fails if the document doesn't exist.

        Args:
            collection: The collection containing the document.
            document_id: The document to update.
            data: The field values to merge in.

        Raises:
            ValueError: If ``collection``, ``document_id``, or ``data``
                is empty.
            GoogleAPIError: If the document cannot be updated, including
                if it doesn't exist.
        """
        if not collection:
            raise ValueError("Collection cannot be empty")

        if not document_id:
            raise ValueError("Document ID cannot be empty")

        if not data:
            raise ValueError("Data cannot be empty")

        try:
            self.client.collection(collection).document(document_id).update(data)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to update document: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def delete_document(
        self,
        collection: str,
        document_id: str
    ) -> None:
        """Delete a document.

        Calls ``DocumentReference.delete``.

        Args:
            collection: The collection containing the document.
            document_id: The document to delete.

        Raises:
            ValueError: If ``collection`` or ``document_id`` is empty.
            GoogleAPIError: If the document cannot be deleted.
        """
        if not collection:
            raise ValueError("Collection cannot be empty")

        if not document_id:
            raise ValueError("Document ID cannot be empty")

        try:
            self.client.collection(collection).document(document_id).delete()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to delete document: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_documents(
        self,
        collection: str
    ) -> StreamGenerator:
        """Stream the documents in a collection.

        Calls ``CollectionReference.stream``.

        Args:
            collection: The collection to list documents from.

        Returns:
            A generator over the collection's ``DocumentSnapshot``
            objects (each with ``.id`` and ``.to_dict()``).

        Raises:
            ValueError: If ``collection`` is empty.
            GoogleAPIError: If the documents cannot be listed.
        """
        if not collection:
            raise ValueError("Collection cannot be empty")

        try:
            return self.client.collection(collection).stream()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list documents: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
