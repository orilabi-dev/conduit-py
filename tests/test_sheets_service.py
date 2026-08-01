from unittest.mock import MagicMock, patch

import httplib2
import pytest
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError
from conduit_py.google.workspace.sheets.service import SheetsService


def _make_http_error(status: int, message: str) -> HttpError:
    resp = httplib2.Response({"status": status})
    resp.reason = message
    body = f'{{"error": {{"message": "{message}"}}}}'.encode()
    return HttpError(resp, body)


def test_create_sheet_rejects_empty_title():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.create_sheet("")


def test_create_sheet_returns_response_on_success():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.create.return_value.execute.return_value = {
            "spreadsheetId": "abc123"
        }
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())
        response = service.create_sheet("Test Sheet")

    assert response == {"spreadsheetId": "abc123"}


def test_create_sheet_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.create.return_value.execute.side_effect = (
            _make_http_error(403, "The caller does not have permission")
        )
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.create_sheet("Test Sheet")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason


def test_get_values_rejects_empty_spreadsheet_id():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.get_values("", "Sheet1!A1:B2")


def test_get_values_rejects_empty_range_name():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.get_values("abc123", "")


def test_get_values_returns_response_on_success():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "Sheet1!A1:B2",
            "majorDimension": "ROWS",
            "values": [["a", "b"], ["c", "d"]],
        }
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())
        response = service.get_values("abc123", "Sheet1!A1:B2")

    assert response == [["a", "b"], ["c", "d"]]


def test_get_values_defaults_to_empty_list_when_no_values_key():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = {
            "range": "Sheet1!A1:B2",
            "majorDimension": "ROWS",
        }
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())
        response = service.get_values("abc123", "Sheet1!A1:B2")

    assert response == []


def test_get_values_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.get.return_value.execute.side_effect = (
            _make_http_error(404, "Requested entity was not found")
        )
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.get_values("abc123", "Sheet1!A1:B2")

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.reason


def test_update_values_rejects_empty_spreadsheet_id():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.update_values("", "Sheet1!A1", [["a"]])


def test_update_values_rejects_empty_range_name():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.update_values("abc123", "", [["a"]])


def test_update_values_rejects_empty_values():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.update_values("abc123", "Sheet1!A1", [])


def test_update_values_returns_response_on_success():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.update.return_value.execute.return_value = {
            "spreadsheetId": "abc123",
            "updatedRange": "Sheet1!A1",
            "updatedCells": 1,
        }
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())
        response = service.update_values("abc123", "Sheet1!A1", [["a"]])

    assert response == {
        "spreadsheetId": "abc123",
        "updatedRange": "Sheet1!A1",
        "updatedCells": 1,
    }


def test_update_values_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.update.return_value.execute.side_effect = (
            _make_http_error(400, "Invalid range")
        )
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.update_values("abc123", "Sheet1!A1", [["a"]])

    assert exc_info.value.status_code == 400
    assert "Invalid range" in exc_info.value.reason


def test_append_values_rejects_empty_spreadsheet_id():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.append_values("", "Sheet1!A1", [["a"]])


def test_append_values_rejects_empty_range_name():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.append_values("abc123", "", [["a"]])


def test_append_values_rejects_empty_values():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.append_values("abc123", "Sheet1!A1", [])


def test_append_values_returns_response_on_success():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = {
            "spreadsheetId": "abc123",
            "tableRange": "Sheet1!A1:B1",
            "updates": {"updatedCells": 2},
        }
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())
        response = service.append_values("abc123", "Sheet1!A1", [["a", "b"]])

    assert response == {
        "spreadsheetId": "abc123",
        "tableRange": "Sheet1!A1:B1",
        "updates": {"updatedCells": 2},
    }


def test_append_values_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.append.return_value.execute.side_effect = (
            _make_http_error(500, "Internal error")
        )
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.append_values("abc123", "Sheet1!A1", [["a"]])

    assert exc_info.value.status_code == 500
    assert "Internal error" in exc_info.value.reason


def test_clear_values_rejects_empty_spreadsheet_id():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.clear_values("", "Sheet1!A1:B2")


def test_clear_values_rejects_empty_range_name():
    with patch("conduit_py.google.workspace.sheets.service.build"):
        service = SheetsService(credentials=MagicMock())

    with pytest.raises(ValueError):
        service.clear_values("abc123", "")


def test_clear_values_returns_response_on_success():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.clear.return_value.execute.return_value = {
            "spreadsheetId": "abc123",
            "clearedRange": "Sheet1!A1:B2",
        }
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())
        response = service.clear_values("abc123", "Sheet1!A1:B2")

    assert response == {"spreadsheetId": "abc123", "clearedRange": "Sheet1!A1:B2"}


def test_clear_values_wraps_http_error_with_status_and_reason():
    with patch("conduit_py.google.workspace.sheets.service.build") as mock_build:
        mock_api = MagicMock()
        mock_api.spreadsheets.return_value.values.return_value.clear.return_value.execute.side_effect = (
            _make_http_error(403, "The caller does not have permission")
        )
        mock_build.return_value = mock_api

        service = SheetsService(credentials=MagicMock())

        with pytest.raises(GoogleAPIError) as exc_info:
            service.clear_values("abc123", "Sheet1!A1:B2")

    assert exc_info.value.status_code == 403
    assert "permission" in exc_info.value.reason
