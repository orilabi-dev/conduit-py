"""Google Forms API service wrapper."""

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError


class FormsService:
    """Thin wrapper around the Google Forms API (``forms`` v1).

    Args:
        credentials: Authenticated Google credentials with Forms scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "forms",
            "v1",
            credentials=credentials
        )

    def create_form(
        self,
        title: str
    ) -> dict:
        """Create a new form.

        Calls ``forms().create``. The Forms API only accepts a title on
        creation — questions must be added afterward via
        ``add_text_question``.

        Args:
            title: Title for the new form. Must not be empty.

        Returns:
            A dict representing the created Forms ``Form`` resource
            (``formId``, ``info``, ``settings``, ``revisionId``,
            ``responderUri``).

        Raises:
            ValueError: If ``title`` is empty.
            GoogleAPIError: If the Forms API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not title:
            raise ValueError("Title cannot be empty")

        try:
            response = (
                self.service
                .forms()
                .create(body={"info": {"title": title}})
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to create form: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def get_form(
        self,
        form_id: str
    ) -> dict:
        """Fetch a form's full content and structure.

        Calls ``forms().get``.

        Args:
            form_id: ID of the form to fetch. Must not be empty.

        Returns:
            A dict representing the full Forms ``Form`` resource.

        Raises:
            ValueError: If ``form_id`` is empty.
            GoogleAPIError: If the Forms API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not form_id:
            raise ValueError("Form ID cannot be empty")

        try:
            response = (
                self.service
                .forms()
                .get(formId=form_id)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to get form: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def add_text_question(
        self,
        form_id: str,
        question_title: str
    ) -> dict:
        """Append a short-answer text question to the end of a form.

        The Forms API's ``createItem`` request requires an explicit
        insertion index, so this first calls ``forms().get`` to count the
        form's existing items and inserts the new question after all of
        them — otherwise a fixed index (e.g. always ``0``) would insert
        each new question before the previous ones, reversing their
        order across repeated calls.

        Args:
            form_id: ID of the form to add the question to. Must not be
                empty.
            question_title: The question's prompt text. Must not be
                empty.

        Returns:
            A dict representing the Forms API ``BatchUpdateFormResponse``
            (form ID, and a list of replies — the ``createItem`` reply
            includes the new item's ``itemId``).

        Raises:
            ValueError: If ``form_id`` or ``question_title`` is empty.
            GoogleAPIError: If the Forms API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not form_id:
            raise ValueError("Form ID cannot be empty")
        if not question_title:
            raise ValueError("Question title cannot be empty")

        try:
            form = self.service.forms().get(formId=form_id).execute()
            index = len(form.get("items", []))

            body = {
                "requests": [
                    {
                        "createItem": {
                            "item": {
                                "title": question_title,
                                "questionItem": {
                                    "question": {
                                        "required": False,
                                        "textQuestion": {},
                                    }
                                },
                            },
                            "location": {"index": index},
                        }
                    }
                ]
            }

            response = (
                self.service
                .forms()
                .batchUpdate(formId=form_id, body=body)
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to add question: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error

    def list_responses(
        self,
        form_id: str
    ) -> list:
        """List the responses submitted to a form.

        Calls ``forms().responses().list``. The Forms API paginates
        results server-side; this method returns only the first page's
        ``"responses"`` list without following ``nextPageToken``.

        Args:
            form_id: ID of the form to list responses for. Must not be
                empty.

        Returns:
            A list of Forms ``FormResponse`` resource dicts.

        Raises:
            ValueError: If ``form_id`` is empty.
            GoogleAPIError: If the Forms API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not form_id:
            raise ValueError("Form ID cannot be empty")

        try:
            response = (
                self.service
                .forms()
                .responses()
                .list(formId=form_id)
                .execute()
            )

            return response.get("responses", [])
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to list responses: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error
