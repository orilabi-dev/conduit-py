"""Enumerations identifying Google services conduit_py can work with."""

from enum import Enum


class GoogleService(str, Enum):
    """Identifiers for Google services conduit_py can authenticate against.

    Members double as plain strings (e.g. ``GoogleService.SHEETS == "sheets"``)
    so they can be used anywhere a raw service name is expected.
    """
    SHEETS = "sheets"
    DOCS = "docs"
    DRIVE = "drive"