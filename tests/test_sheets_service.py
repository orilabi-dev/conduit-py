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
