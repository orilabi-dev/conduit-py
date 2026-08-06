from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.slides.service import SlidesService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def test_create_slide_rejects_empty_title():
    with patch("conduit_py.google.workspace.slides.service.build"):
        service = SlidesService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.create_slide("")


def test_create_slide_returns_response_on_success():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.create.return_value.execute.return_value = {
            "presentationId": "pres123"
        }
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())
        response = service.create_slide("Test Presentation")

    assert response == {"presentationId": "pres123"}


def test_create_slide_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.create.return_value.execute.side_effect = (
            _make_http_error(403, "The caller does not have permission")
        )
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.create_slide("Test Presentation")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_get_presentation_rejects_empty_presentation_id():
    with patch("conduit_py.google.workspace.slides.service.build"):
        service = SlidesService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.get_presentation("")


def test_get_presentation_returns_response_on_success():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.get.return_value.execute.return_value = {
            "presentationId": "pres123",
            "slides": [],
        }
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())
        response = service.get_presentation("pres123")

    assert response == {"presentationId": "pres123", "slides": []}


def test_get_presentation_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.get.return_value.execute.side_effect = (
            _make_http_error(404, "Requested entity was not found")
        )
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.get_presentation("pres123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_add_slide_rejects_empty_presentation_id():
    with patch("conduit_py.google.workspace.slides.service.build"):
        service = SlidesService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.add_slide("")


def test_add_slide_returns_response_on_success():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.batchUpdate.return_value.execute.return_value = {
            "presentationId": "pres123",
            "replies": [{"createSlide": {"objectId": "slide456"}}],
        }
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())
        response = service.add_slide("pres123")

    assert response == {
        "presentationId": "pres123",
        "replies": [{"createSlide": {"objectId": "slide456"}}],
    }


def test_add_slide_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.batchUpdate.return_value.execute.side_effect = (
            _make_http_error(400, "Invalid requests")
        )
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.add_slide("pres123")

    assert exc_info.value.status_code == 400
    assert "Invalid requests" in exc_info.value.reason


def test_add_sheets_chart_rejects_empty_presentation_id():
    with patch("conduit_py.google.workspace.slides.service.build"):
        service = SlidesService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.add_sheets_chart("", "slide456", "abc123", 999)


def test_add_sheets_chart_rejects_empty_page_id():
    with patch("conduit_py.google.workspace.slides.service.build"):
        service = SlidesService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.add_sheets_chart("pres123", "", "abc123", 999)


def test_add_sheets_chart_rejects_empty_spreadsheet_id():
    with patch("conduit_py.google.workspace.slides.service.build"):
        service = SlidesService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.add_sheets_chart("pres123", "slide456", "", 999)


def test_add_sheets_chart_returns_response_on_success():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.batchUpdate.return_value.execute.return_value = {
            "presentationId": "pres123",
            "replies": [{"createSheetsChart": {"objectId": "chart789"}}],
        }
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())
        response = service.add_sheets_chart("pres123", "slide456", "abc123", 999)

    assert response == {
        "presentationId": "pres123",
        "replies": [{"createSheetsChart": {"objectId": "chart789"}}],
    }

    _, kwargs = mock_api.presentations.return_value.batchUpdate.call_args
    assert kwargs["presentationId"] == "pres123"
    request = kwargs["body"]["requests"][0]["createSheetsChart"]
    assert request["spreadsheetId"] == "abc123"
    assert request["chartId"] == 999
    assert request["elementProperties"]["pageObjectId"] == "slide456"
    assert request["linkingMode"] == "LINKED"


def test_add_sheets_chart_not_linked_produces_image_linking_mode():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.batchUpdate.return_value.execute.return_value = {
            "presentationId": "pres123",
            "replies": [{"createSheetsChart": {"objectId": "chart789"}}],
        }
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())
        service.add_sheets_chart("pres123", "slide456", "abc123", 999, linked=False)

    _, kwargs = mock_api.presentations.return_value.batchUpdate.call_args
    request = kwargs["body"]["requests"][0]["createSheetsChart"]
    assert request["linkingMode"] == "NOT_LINKED_IMAGE"


def test_add_sheets_chart_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.slides.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.presentations.return_value.batchUpdate.return_value.execute.side_effect = (
            _make_http_error(400, "Invalid requests")
        )
        mock_build.return_value = mock_api

        service = SlidesService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.add_sheets_chart("pres123", "slide456", "abc123", 999)

    assert exc_info.value.status_code == 400
    assert "Invalid requests" in exc_info.value.reason
