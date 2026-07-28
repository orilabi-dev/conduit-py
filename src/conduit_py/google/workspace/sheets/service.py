"""Google Sheets API service wrapper."""

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from conduit_py.google.exceptions import GoogleAPIError


class SheetsService:
    """Thin wrapper around the Google Sheets API (``sheets`` v4).

    Args:
        credentials: Authenticated Google credentials with Sheets scope(s).
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.service = build(
            "sheets",
            "v4",
            credentials=credentials
        )

    def create_sheet(
        self,
        title: str
    ) -> dict:
        """Create a new spreadsheet with the given title.

        Calls ``spreadsheets().create`` with ``fields="spreadsheetId"``, so
        only the new spreadsheet's ID is returned — no sheet/tab data, no
        formatting, nothing else from the created resource.

        Args:
            title: Title for the new spreadsheet. Must not be empty.

        Returns:
            A dict containing only the key ``spreadsheetId`` (the ID of the
            newly created spreadsheet).

        Raises:
            ValueError: If ``title`` is empty.
            GoogleAPIError: If the Sheets API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not title:
            raise ValueError("Sheet title cannot be empty")
        
        body = {
            "properties": {
                "title": title
            }
        }
        try:
            response = (
                self.service
                .spreadsheets()
                .create(body=body,fields="spreadsheetId")
                .execute()
            )
            
            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to create spreadsheet: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error
            
    def get_sheet(
        self,
        spreadsheet_id: str
    ) -> dict:
        """Fetch a spreadsheet's full data, including all grid/cell data.

        Calls ``spreadsheets().get`` with ``includeGridData=True``, so the
        response contains the complete spreadsheet resource: properties,
        every sheet's metadata, and all cell/grid data.

        Args:
            spreadsheet_id: ID of the spreadsheet to fetch. Must not be
                empty.

        Returns:
            A dict representing the full Google Sheets ``Spreadsheet``
            resource (properties, sheets, and grid data).

        Raises:
            ValueError: If ``spreadsheet_id`` is empty.
            GoogleAPIError: If the Sheets API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID cannot be empty")
        
        try:
            response = (
                self.service
                .spreadsheets()
                .get(
                    spreadsheetId=spreadsheet_id,
                    includeGridData=True
                )
                .execute()
            )
            
            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to get spreadsheet: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error