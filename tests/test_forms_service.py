from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.forms.service import FormsService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def _make_service() -> tuple[FormsService, MagicMock]:
    with patch("conduit_py.google.workspace.forms.service.build") as mock_build:
        mock_api = MagicMock()
        mock_build.return_value = mock_api
        service = FormsService(credentials=MagicMock())
    return service, mock_api


def test_create_form_rejects_empty_title():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_form("")


def test_create_form_calls_client_with_expected_body():
    service, mock_api = _make_service()
    mock_api.forms.return_value.create.return_value.execute.return_value = {
        "formId": "form123"
    }

    response = service.create_form("Feedback Survey")

    mock_api.forms.return_value.create.assert_called_once_with(
        body={"info": {"title": "Feedback Survey"}}
    )
    assert response == {"formId": "form123"}


def test_create_form_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.forms.return_value.create.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_form("Feedback Survey")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_get_form_rejects_empty_form_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_form("")


def test_get_form_returns_response_on_success():
    service, mock_api = _make_service()
    mock_api.forms.return_value.get.return_value.execute.return_value = {
        "formId": "form123",
        "info": {"title": "Feedback Survey"},
    }

    response = service.get_form("form123")

    mock_api.forms.return_value.get.assert_called_once_with(formId="form123")
    assert response == {"formId": "form123", "info": {"title": "Feedback Survey"}}


def test_get_form_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.forms.return_value.get.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.get_form("form123")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_add_text_question_rejects_empty_form_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.add_text_question("", "What's your name?")


def test_add_text_question_rejects_empty_question_title():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.add_text_question("form123", "")


def test_add_text_question_inserts_at_end_of_existing_items():
    service, mock_api = _make_service()
    mock_api.forms.return_value.get.return_value.execute.return_value = {
        "formId": "form123",
        "items": [{"itemId": "item1"}, {"itemId": "item2"}],
    }
    mock_api.forms.return_value.batchUpdate.return_value.execute.return_value = {
        "formId": "form123",
        "replies": [{"createItem": {"itemId": "item3"}}],
    }

    response = service.add_text_question("form123", "What's your name?")

    _, kwargs = mock_api.forms.return_value.batchUpdate.call_args
    assert kwargs["formId"] == "form123"
    create_item = kwargs["body"]["requests"][0]["createItem"]
    assert create_item["location"] == {"index": 2}
    assert create_item["item"]["title"] == "What's your name?"
    assert create_item["item"]["questionItem"]["question"]["textQuestion"] == {}
    assert response == {"formId": "form123", "replies": [{"createItem": {"itemId": "item3"}}]}


def test_add_text_question_inserts_at_zero_for_empty_form():
    service, mock_api = _make_service()
    mock_api.forms.return_value.get.return_value.execute.return_value = {"formId": "form123"}
    mock_api.forms.return_value.batchUpdate.return_value.execute.return_value = {}

    service.add_text_question("form123", "What's your name?")

    _, kwargs = mock_api.forms.return_value.batchUpdate.call_args
    create_item = kwargs["body"]["requests"][0]["createItem"]
    assert create_item["location"] == {"index": 0}


def test_add_text_question_wraps_http_error_from_get():
    service, mock_api = _make_service()
    mock_api.forms.return_value.get.return_value.execute.side_effect = (
        _make_http_error(404, "Requested entity was not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.add_text_question("form123", "What's your name?")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_add_text_question_wraps_http_error_from_batch_update():
    service, mock_api = _make_service()
    mock_api.forms.return_value.get.return_value.execute.return_value = {"formId": "form123"}
    mock_api.forms.return_value.batchUpdate.return_value.execute.side_effect = (
        _make_http_error(400, "Invalid requests")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.add_text_question("form123", "What's your name?")

    assert exc_info.value.status_code == 400
    assert "Invalid requests" in exc_info.value.reason


def test_list_responses_rejects_empty_form_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.list_responses("")


def test_list_responses_returns_responses_on_success():
    service, mock_api = _make_service()
    mock_api.forms.return_value.responses.return_value.list.return_value.execute.return_value = {
        "responses": [{"responseId": "resp123"}]
    }

    result = service.list_responses("form123")

    mock_api.forms.return_value.responses.return_value.list.assert_called_once_with(
        formId="form123"
    )
    assert result == [{"responseId": "resp123"}]


def test_list_responses_returns_empty_list_when_no_responses_key():
    service, mock_api = _make_service()
    mock_api.forms.return_value.responses.return_value.list.return_value.execute.return_value = {}

    result = service.list_responses("form123")

    assert result == []


def test_list_responses_wraps_http_error_with_status_and_reason():
    service, mock_api = _make_service()
    mock_api.forms.return_value.responses.return_value.list.return_value.execute.side_effect = (
        _make_http_error(403, "The caller does not have permission")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_responses("form123")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason
