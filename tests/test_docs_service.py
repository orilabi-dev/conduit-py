from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.docs.service import DocsService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def test_create_doc_rejects_empty_title():
    with patch("conduit_py.google.workspace.docs.service.build"):
        service = DocsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.create_doc("")


def test_create_doc_returns_response_on_success():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.create.return_value.execute.return_value = {
            "documentId": "doc123"
        }
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())
        response = service.create_doc("Test Doc")

    assert response == {"documentId": "doc123"}


def test_create_doc_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.create.return_value.execute.side_effect = (
            _make_http_error(403, "The caller does not have permission")
        )
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.create_doc("Test Doc")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_get_document_rejects_empty_document_id():
    with patch("conduit_py.google.workspace.docs.service.build"):
        service = DocsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.get_document("")


def test_get_document_returns_response_on_success():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.get.return_value.execute.return_value = {
            "documentId": "doc123",
            "title": "Test Doc",
            "body": {"content": []},
        }
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())
        response = service.get_document("doc123")

    assert response == {
        "documentId": "doc123",
        "title": "Test Doc",
        "body": {"content": []},
    }


def test_get_document_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.get.return_value.execute.side_effect = (
            _make_http_error(404, "Requested entity was not found")
        )
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.get_document("doc123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_append_text_rejects_empty_document_id():
    with patch("conduit_py.google.workspace.docs.service.build"):
        service = DocsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.append_text("", "Hello world")


def test_append_text_rejects_empty_text():
    with patch("conduit_py.google.workspace.docs.service.build"):
        service = DocsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.append_text("doc123", "")


def test_append_text_returns_response_on_success():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.batchUpdate.return_value.execute.return_value = {
            "documentId": "doc123",
            "replies": [{}],
        }
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())
        response = service.append_text("doc123", "Hello world")

    assert response == {"documentId": "doc123", "replies": [{}]}


def test_append_text_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.batchUpdate.return_value.execute.side_effect = (
            _make_http_error(400, "Invalid requests")
        )
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.append_text("doc123", "Hello world")

    assert exc_info.value.status_code == 400
    assert "Invalid requests" in exc_info.value.reason


def test_insert_image_rejects_empty_document_id():
    with patch("conduit_py.google.workspace.docs.service.build"):
        service = DocsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.insert_image("", "https://example.com/image.png")


def test_insert_image_rejects_empty_image_uri():
    with patch("conduit_py.google.workspace.docs.service.build"):
        service = DocsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.insert_image("doc123", "")


def test_insert_image_returns_response_on_success():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.get.return_value.execute.return_value = {
            "body": {"content": [{"endIndex": 25}]}
        }
        mock_api.documents.return_value.batchUpdate.return_value.execute.return_value = {
            "documentId": "doc123",
            "replies": [{}],
        }
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())
        response = service.insert_image("doc123", "https://example.com/image.png")

    assert response == {"documentId": "doc123", "replies": [{}]}

    _, kwargs = mock_api.documents.return_value.batchUpdate.call_args
    assert kwargs["documentId"] == "doc123"
    request = kwargs["body"]["requests"][0]["insertInlineImage"]
    assert request["uri"] == "https://example.com/image.png"
    assert request["location"]["index"] == 24


def test_insert_image_wraps_http_error_from_get():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.get.return_value.execute.side_effect = (
            _make_http_error(404, "Requested entity was not found")
        )
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.insert_image("doc123", "https://example.com/image.png")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_insert_image_wraps_http_error_from_batch_update():
    with patch("conduit_py.google.workspace.docs.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.documents.return_value.get.return_value.execute.return_value = {
            "body": {"content": [{"endIndex": 25}]}
        }
        mock_api.documents.return_value.batchUpdate.return_value.execute.side_effect = (
            _make_http_error(400, "Invalid requests")
        )
        mock_build.return_value = mock_api

        service = DocsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.insert_image("doc123", "https://example.com/image.png")

    assert exc_info.value.status_code == 400
    assert "Invalid requests" in exc_info.value.reason
