"""Aggregate client exposing the Sheets, Docs, Slides, Drive, Gmail,
Calendar, Forms, and Tasks services."""

from google.auth.credentials import Credentials

from conduit_py.google.workspace.calendar.service import CalendarService
from conduit_py.google.workspace.docs.service import DocsService
from conduit_py.google.workspace.drive.service import DriveService
from conduit_py.google.workspace.forms.service import FormsService
from conduit_py.google.workspace.gmail.service import GmailService
from conduit_py.google.workspace.sheets.service import SheetsService
from conduit_py.google.workspace.slides.service import SlidesService
from conduit_py.google.workspace.tasks.service import TasksService


class WorkspaceClient:
    """Bundles the per-API Workspace service clients under one object.

    Args:
        credentials: Authenticated Google credentials, shared across all
            underlying services (Sheets, Docs, Slides, Drive, Gmail,
            Calendar, Forms, Tasks).

    Attributes:
        credentials: The credentials passed in, unchanged.
        sheets: A ``SheetsService`` for the Google Sheets API.
        slides: A ``SlidesService`` for the Google Slides API.
        docs: A ``DocsService`` for the Google Docs API.
        drive: A ``DriveService`` for the Google Drive API.
        gmail: A ``GmailService`` for the Gmail API.
        calendar: A ``CalendarService`` for the Google Calendar API.
        forms: A ``FormsService`` for the Google Forms API.
        tasks: A ``TasksService`` for the Google Tasks API.
    """
    def __init__(
        self,
        credentials: Credentials
    ):
        self.credentials = credentials

        self.sheets = SheetsService(self.credentials)

        self.slides = SlidesService(self.credentials)

        self.docs = DocsService(self.credentials)

        self.drive = DriveService(self.credentials)

        self.gmail = GmailService(self.credentials)

        self.calendar = CalendarService(self.credentials)

        self.forms = FormsService(self.credentials)

        self.tasks = TasksService(self.credentials)
