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

class GoogleScopes:
    """Namespace grouping the per-service scope enums.

    Lets callers write ``GoogleScopes.SHEETS.WRITE`` instead of importing
    ``SheetsScope`` directly.
    """
    SHEETS = SheetsScope
    DOCS = DocScopes
    SLIDES = SlideScopes
    BIGQUERY = BigQueryScopes
    SECRET_MANAGER = SecretManagerScopes
