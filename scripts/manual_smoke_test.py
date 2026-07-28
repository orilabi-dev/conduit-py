"""Manual smoke test: creates a real spreadsheet via the live Google Sheets API.

Not part of the automated test suite (pytest only discovers tests/test_*.py).
Run directly:

    uv run python scripts/manual_smoke_test.py

Requires an OAuth client secret at credentials.json in the repo root (see
README for how to obtain one). On first run this opens a browser for
consent; the resulting token is cached at token.json in the repo root so
subsequent runs skip re-authenticating.
"""

from pathlib import Path

from conduit_py import Conduit
from conduit_py.google import GoogleScopes

REPO_ROOT = Path(__file__).resolve().parent.parent


def run() -> None:
    google = Conduit.google(
        scopes=[GoogleScopes.SLIDES.WRITE],
        oauth_client_path=REPO_ROOT / "conduit_py_credentials.json",
        token_path=REPO_ROOT / "token.json",
    )

    # sheet = google.workspace.sheets.create_sheet("Conduit Smoke Test")
    # sheet = google.workspace.sheets.get_sheet(spreadsheet_id="1DrN_ZKwSFH-iV5O-nLhrz4rGtg3T2Iz7fBGW7pQ3iGU")
    
    slides = google.workspace.slides.create_slide("Conduit Smoke Test")
    print(slides['presentationId'])
    # sheets = sheet["sheets"]
    
    # for s in sheets:
    #     print(s["properties"]["title"])


if __name__ == "__main__":
    run()
