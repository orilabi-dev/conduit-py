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

    def get_document(
        self,
        document_id: str
    ) -> dict:
        """Fetch a document's full content and structure.

        Calls ``documents().get``, so the response contains the complete
        Document resource: title, revision ID, and the full body content
        (paragraphs, text runs, tables, etc.) — unlike ``create_doc``,
        which only returns the new document's ID.

        Args:
            document_id: ID of the document to fetch. Must not be empty.

        Returns:
            A dict representing the full Google Docs ``Document`` resource.

        Raises:
            ValueError: If ``document_id`` is empty.
            GoogleAPIError: If the Docs API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not document_id:
            raise ValueError("Document ID cannot be empty")

        try:
            response = (
                self.service
                .documents()
                .get(documentId=document_id)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to get document: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error

    def append_text(
        self,
        document_id: str,
        text: str
    ) -> dict:
        """Append text to the end of a document's body.

        Calls ``documents().batchUpdate`` with a single ``insertText``
        request targeting ``endOfSegmentLocation``, which inserts the text
        immediately before the end of the document body.

        Args:
            document_id: ID of the document to update. Must not be empty.
            text: Text to append. Must not be empty.

        Returns:
            A dict representing the Docs API ``BatchUpdateDocumentResponse``
            (document ID and a list of replies, one per request — the
            ``insertText`` request produces an empty reply).

        Raises:
            ValueError: If ``document_id`` or ``text`` is empty.
            GoogleAPIError: If the Docs API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not document_id:
            raise ValueError("Document ID cannot be empty")
        if not text:
            raise ValueError("Text cannot be empty")

        try:
            response = (
                self.service
                .documents()
                .batchUpdate(
                    documentId=document_id,
                    body={
                        "requests": [
                            {
                                "insertText": {
                                    "endOfSegmentLocation": {},
                                    "text": text,
                                }
                            }
                        ]
                    },
                )
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to append text: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error

    def insert_image(
        self,
        document_id: str,
        image_uri: str
    ) -> dict:
        """Insert an image at the end of a document's body.

        Calls ``documents().batchUpdate`` with an ``insertInlineImage``
        request. Since that request type has no "end of document" shorthand
        (unlike ``append_text``'s ``insertText``), this first calls
        ``documents().get`` to compute the correct insertion index.

        Args:
            document_id: ID of the document to insert into. Must not be
                empty.
            image_uri: A publicly accessible URL Google's servers can fetch
                the image from (e.g. a public GCS object URL, a Drive file
                shared as "anyone with the link", or a signed URL) — max
                50MB, must resolve within the fetch window Google enforces
                on this request. Raw bytes are not accepted; the image must
                already be hosted somewhere reachable. Must not be empty.

        Returns:
            A dict representing the Docs API ``BatchUpdateDocumentResponse``.

        Raises:
            ValueError: If ``document_id`` or ``image_uri`` is empty.
            GoogleAPIError: If the Docs API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not document_id:
            raise ValueError("Document ID cannot be empty")
        if not image_uri:
            raise ValueError("Image URI cannot be empty")

        try:
            doc = self.service.documents().get(documentId=document_id).execute()
            end_index = doc["body"]["content"][-1]["endIndex"] - 1

            body = {
                "requests": [
                    {
                        "insertInlineImage": {
                            "uri": image_uri,
                            "location": {"index": end_index},
                        }
                    }
                ]
            }

            response = (
                self.service
                .documents()
                .batchUpdate(documentId=document_id, body=body)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to insert image: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error