"""Typed exception hierarchy for conduit_py.google.

Every exception here carries a ``docs_url`` pointing at the README section
with troubleshooting guidance for that failure mode, and that URL is
appended to the exception message so it shows up directly in stack traces.
"""

_DOCS_BASE = "https://github.com/orilabi-dev/conduit-py#"


class ConduitGoogleError(Exception):
    """Base class for all conduit_py.google errors.

    Args:
        message: Human-readable description of what went wrong.

    Attributes:
        docs_url: Link to the README section covering this error.
    """

    docs_url: str = f"{_DOCS_BASE}errors"

    def __init__(self, message: str):
        super().__init__(f"{message} (see: {self.docs_url})")


class GoogleAuthError(ConduitGoogleError):
    """Raised when Google authentication fails or is misconfigured.

    Covers cases like a missing/invalid credentials file, or an OAuth flow
    that has neither a cached token nor an ``oauth_client_path`` to start a
    new one from.
    """

    docs_url = f"{_DOCS_BASE}authentication-errors"


class GoogleAPIError(ConduitGoogleError):
    """Raised when a Google API request fails.

    Wraps ``googleapiclient.errors.HttpError`` so callers can depend on a
    single, stable exception type from this library instead of reaching
    into googleapiclient's own error classes.

    Args:
        message: Human-readable description of what went wrong.
        status_code: HTTP status code from the failed request, if available.
        reason: Reason string from the failed request, if available.

    Attributes:
        status_code: HTTP status code from the failed request, or ``None``.
        reason: Reason string from the failed request, or ``None``.
        docs_url: Link to the README section covering this error.
    """

    docs_url = f"{_DOCS_BASE}api-errors"

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        reason: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.reason = reason
