"""OAuth scope enums for the Google Workspace and Google Cloud APIs.

Pass members of these enums (or their string ``.value``) to ``Conduit.google``
to request read-only or read/write access to the corresponding API.
"""

from enum import Enum


class SheetsScope(str, Enum):
    """OAuth scopes for the Google Sheets API."""
    READ = "https://www.googleapis.com/auth/spreadsheets.readonly"
    WRITE = "https://www.googleapis.com/auth/spreadsheets"

class DocScopes(str, Enum):
    """OAuth scopes for the Google Docs API."""
    READ = "https://www.googleapis.com/auth/documents.readonly"
    WRITE = "https://www.googleapis.com/auth/documents"

class SlideScopes(str, Enum):
    """OAuth scopes for the Google Slides API."""
    READ = "https://www.googleapis.com/auth/presentations.readonly"
    WRITE = "https://www.googleapis.com/auth/presentations"

class DriveScopes(str, Enum):
    """OAuth scopes for the Google Drive API."""
    READ = "https://www.googleapis.com/auth/drive.readonly"
    WRITE = "https://www.googleapis.com/auth/drive"

class GmailScopes(str, Enum):
    """OAuth scopes for the Gmail API.

    Gmail's granular scopes don't map cleanly to a plain READ/WRITE split:
    reading mail, sending mail, and modifying mail (e.g. trashing a
    message) are each gated by a distinct scope.
    """
    READ = "https://www.googleapis.com/auth/gmail.readonly"
    SEND = "https://www.googleapis.com/auth/gmail.send"
    MODIFY = "https://www.googleapis.com/auth/gmail.modify"

class CalendarScopes(str, Enum):
    """OAuth scopes for the Google Calendar API, scoped to events only
    (this service only reads/writes events, not calendar list management)."""
    READ = "https://www.googleapis.com/auth/calendar.events.readonly"
    WRITE = "https://www.googleapis.com/auth/calendar.events"

class FormsScopes(str, Enum):
    """OAuth scopes for the Google Forms API.

    Reading/editing a form's structure and reading its responses are
    gated by separate scopes.
    """
    READ = "https://www.googleapis.com/auth/forms.body.readonly"
    WRITE = "https://www.googleapis.com/auth/forms.body"
    RESPONSES_READ = "https://www.googleapis.com/auth/forms.responses.readonly"

class BigQueryScopes(str, Enum):
    """OAuth scopes for the Google BigQuery API."""
    READ = "https://www.googleapis.com/auth/bigquery.readonly"
    WRITE = "https://www.googleapis.com/auth/bigquery"
    INSERT_DATA = "https://www.googleapis.com/auth/bigquery.insertdata"

class SecretManagerScopes(str, Enum):
    """OAuth scopes for the Google Secret Manager API.

    Secret Manager is a gRPC-based Cloud API gated by IAM permissions
    rather than granular OAuth scopes, so the broad ``cloud-platform``
    scope is the only one available here.
    """
    CLOUD_PLATFORM = "https://www.googleapis.com/auth/cloud-platform"

class CloudStorageScopes(str, Enum):
    """OAuth scopes for the Google Cloud Storage API."""
    READ = "https://www.googleapis.com/auth/devstorage.read_only"
    WRITE = "https://www.googleapis.com/auth/devstorage.read_write"

class PubSubScopes(str, Enum):
    """OAuth scopes for the Google Cloud Pub/Sub API."""
    PUBSUB = "https://www.googleapis.com/auth/pubsub"

class FirestoreScopes(str, Enum):
    """OAuth scopes for the Google Cloud Firestore API."""
    DATASTORE = "https://www.googleapis.com/auth/datastore"

class CloudLoggingScopes(str, Enum):
    """OAuth scopes for the Google Cloud Logging API."""
    READ = "https://www.googleapis.com/auth/logging.read"
    WRITE = "https://www.googleapis.com/auth/logging.write"

class GoogleScopes:
    """Namespace grouping the per-service scope enums.

    Lets callers write ``GoogleScopes.SHEETS.WRITE`` instead of importing
    ``SheetsScope`` directly.
    """
    SHEETS = SheetsScope
    DOCS = DocScopes
    SLIDES = SlideScopes
    DRIVE = DriveScopes
    GMAIL = GmailScopes
    CALENDAR = CalendarScopes
    FORMS = FormsScopes
    BIGQUERY = BigQueryScopes
    SECRET_MANAGER = SecretManagerScopes
    CLOUD_STORAGE = CloudStorageScopes
    PUBSUB = PubSubScopes
    FIRESTORE = FirestoreScopes
    CLOUD_LOGGING = CloudLoggingScopes
