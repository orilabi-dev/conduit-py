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

    def get_values(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> list:
        """Fetch cell values from a range in a spreadsheet.

        Calls ``spreadsheets().values().get``, which returns a response
        containing only spreadsheet-range metadata plus a ``"values"`` key
        with the row data. The API omits the ``"values"`` key entirely when
        the range has no data, so this returns ``[]`` in that case instead
        of raising or returning a missing key.

        Args:
            spreadsheet_id: ID of the spreadsheet to read from. Must not
                be empty.
            range_name: A1 notation range to read (e.g. ``"Sheet1!A1:C10"``).
                Must not be empty.

        Returns:
            A list of rows, each a list of cell values. Empty list if the
            range contains no data.

        Raises:
            ValueError: If ``spreadsheet_id`` or ``range_name`` is empty.
            GoogleAPIError: If the Sheets API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID cannot be empty")
        if not range_name:
            raise ValueError("Range name cannot be empty")

        try:
            response = (
                self.service
                .spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                )
                .execute()
            )

            return response.get("values", [])
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to get values: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error

    def update_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: list[list],
        value_input_option: str = "USER_ENTERED"
    ) -> dict:
        """Overwrite cell values in a range of a spreadsheet.

        Calls ``spreadsheets().values().update``. With the default
        ``value_input_option`` of ``"USER_ENTERED"``, values are parsed as
        if typed by a user in the Sheets UI (e.g. ``"=SUM(A1:A2)"`` becomes
        a real formula rather than a literal string).

        Args:
            spreadsheet_id: ID of the spreadsheet to update. Must not be
                empty.
            range_name: A1 notation range to write (e.g. ``"Sheet1!A1"``).
                Must not be empty.
            values: Rows of cell values to write. Must not be empty.
            value_input_option: How input data should be interpreted.
                Defaults to ``"USER_ENTERED"``.

        Returns:
            A dict representing the Sheets API ``UpdateValuesResponse``
            (spreadsheet ID, updated range, and counts of updated rows/
            columns/cells).

        Raises:
            ValueError: If ``spreadsheet_id`` or ``range_name`` is empty,
                or if ``values`` is empty.
            GoogleAPIError: If the Sheets API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID cannot be empty")
        if not range_name:
            raise ValueError("Range name cannot be empty")
        if not values:
            raise ValueError("Values cannot be empty")

        try:
            response = (
                self.service
                .spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body={"values": values}
                )
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to update values: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error

    def append_values(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: list[list],
        value_input_option: str = "USER_ENTERED"
    ) -> dict:
        """Append rows of values after the last row of data in a range.

        Calls ``spreadsheets().values().append``. With the default
        ``value_input_option`` of ``"USER_ENTERED"``, values are parsed as
        if typed by a user in the Sheets UI (e.g. ``"=SUM(A1:A2)"`` becomes
        a real formula rather than a literal string).

        Args:
            spreadsheet_id: ID of the spreadsheet to append to. Must not
                be empty.
            range_name: A1 notation range identifying the table to append
                after (e.g. ``"Sheet1!A1"``). Must not be empty.
            values: Rows of cell values to append. Must not be empty.
            value_input_option: How input data should be interpreted.
                Defaults to ``"USER_ENTERED"``.

        Returns:
            A dict representing the Sheets API ``AppendValuesResponse``
            (spreadsheet ID, the table range that was found, and an
            ``updates`` object describing the newly written range).

        Raises:
            ValueError: If ``spreadsheet_id`` or ``range_name`` is empty,
                or if ``values`` is empty.
            GoogleAPIError: If the Sheets API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID cannot be empty")
        if not range_name:
            raise ValueError("Range name cannot be empty")
        if not values:
            raise ValueError("Values cannot be empty")

        try:
            response = (
                self.service
                .spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body={"values": values}
                )
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to append values: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error

    def clear_values(
        self,
        spreadsheet_id: str,
        range_name: str
    ) -> dict:
        """Clear cell values from a range, leaving formatting intact.

        Calls ``spreadsheets().values().clear``.

        Args:
            spreadsheet_id: ID of the spreadsheet to clear values from.
                Must not be empty.
            range_name: A1 notation range to clear (e.g.
                ``"Sheet1!A1:C10"``). Must not be empty.

        Returns:
            A dict representing the Sheets API ``ClearValuesResponse``
            (spreadsheet ID and the range that was cleared).

        Raises:
            ValueError: If ``spreadsheet_id`` or ``range_name`` is empty.
            GoogleAPIError: If the Sheets API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID cannot be empty")
        if not range_name:
            raise ValueError("Range name cannot be empty")

        try:
            response = (
                self.service
                .spreadsheets()
                .values()
                .clear(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                )
                .execute()
            )

            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to clear values: {error.reason}",
                status_code=error.status_code,
                reason=error.reason
            ) from error

    def add_chart(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        chart_type: str,
        title: str,
        start_row_index: int,
        end_row_index: int,
        start_column_index: int,
        end_column_index: int
    ) -> dict:
        """Create a chart from a data range, placed on a new sheet tab.

        Calls ``spreadsheets().batchUpdate`` with an ``addChart`` request.
        The first column of the given range (``start_column_index`` to
        ``start_column_index + 1``) is used as the chart's domain (labels);
        the remaining columns (``start_column_index + 1`` to
        ``end_column_index``) are used as data series.

        Args:
            spreadsheet_id: ID of the spreadsheet containing the source data.
                Must not be empty.
            sheet_id: The numeric ID of the sheet (tab) the source range is
                on.
            chart_type: The chart type, e.g. ``"COLUMN"``, ``"LINE"``,
                ``"BAR"``, ``"PIE"``. Must not be empty.
            title: Title for the chart. Must not be empty.
            start_row_index: Start row of the source range (0-indexed,
                inclusive).
            end_row_index: End row of the source range (0-indexed,
                exclusive).
            start_column_index: Start column of the source range (0-indexed,
                inclusive).
            end_column_index: End column of the source range (0-indexed,
                exclusive).

        Returns:
            A dict representing the Sheets API ``BatchUpdateSpreadsheetResponse``.
            ``replies[0]["addChart"]["chart"]["chartId"]`` gives the new
            chart's ID, needed to embed it in a slide via
            ``SlidesService.add_sheets_chart``.

        Raises:
            ValueError: If ``spreadsheet_id``, ``chart_type``, or ``title``
                is empty.
            GoogleAPIError: If the Sheets API request fails; carries the
                original ``status_code`` and ``reason`` from the failed
                request.
        """
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID cannot be empty")
        if not chart_type:
            raise ValueError("Chart type cannot be empty")
        if not title:
            raise ValueError("Title cannot be empty")

        source_range = {
            "sheetId": sheet_id,
            "startRowIndex": start_row_index,
            "endRowIndex": end_row_index,
        }
        domain_range = {
            **source_range,
            "startColumnIndex": start_column_index,
            "endColumnIndex": start_column_index + 1,
        }
        series_range = {
            **source_range,
            "startColumnIndex": start_column_index + 1,
            "endColumnIndex": end_column_index,
        }

        body = {
            "requests": [
                {
                    "addChart": {
                        "chart": {
                            "spec": {
                                "title": title,
                                "basicChart": {
                                    "chartType": chart_type,
                                    "legendPosition": "BOTTOM_LEGEND",
                                    "domains": [
                                        {"domain": {"sourceRange": {"sources": [domain_range]}}}
                                    ],
                                    "series": [
                                        {"series": {"sourceRange": {"sources": [series_range]}}}
                                    ],
                                },
                            },
                            "position": {"newSheet": True},
                        }
                    }
                }
            ]
        }

        try:
            response = (
                self.service
                .spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                .execute()
            )
            return response
        except HttpError as error:
            raise GoogleAPIError(
                f"Failed to add chart: {error.reason}",
                status_code=error.status_code,
                reason=error.reason,
            ) from error