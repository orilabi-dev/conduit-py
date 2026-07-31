# conduit-py

A unified, opinionated Python client for authenticating and working with Google APIs.

Currently supported:

- **Auth**: Application Default Credentials (ADC), OAuth client (installed-app flow with token
  caching), and service account credentials.
- **Google Workspace**: Sheets (`create_sheet`). Docs and Drive scopes are defined but the
  corresponding services are not yet implemented.
- **Google Cloud**: BigQuery (`query_and_wait`, `query`) and Secret Manager (`create_secret`,
  `add_secret_version`, `access_secret_version`). Requires `project_name` (see
  [Google Cloud](#google-cloud) below).

## Install

```bash
pip install conduit-py
```

## Usage

```python
from conduit_py import Conduit
from conduit_py.google import GoogleScopes

google = Conduit.google(
    scopes=[GoogleScopes.SHEETS.WRITE],
    oauth_client_path="path/to/client_secret.json",
    token_path="path/to/token.json",  # optional: cache/reuse the OAuth token
)

sheet = google.workspace.sheets.create_sheet("My Sheet")
print(sheet["spreadsheetId"])
```

### Google Cloud

Pass `project_name` to `Conduit.google(...)` to also get a `.cloud` client exposing `.bigquery` and
`.secret_manager`. If `project_name` is omitted, `.cloud` is `None`.

```python
from conduit_py import Conduit

google = Conduit.google(
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
    oauth_client_path="path/to/client_secret.json",
    token_path="path/to/token.json",
    project_name="my-gcp-project",
)

# BigQuery
rows = google.cloud.bigquery.query_and_wait("SELECT 1 AS value")
for row in rows:
    print(row.value)

# Secret Manager
google.cloud.secret_manager.create_secret("my-secret")
google.cloud.secret_manager.add_secret_version("my-secret", payload="hunter2")
value = google.cloud.secret_manager.access_secret_version("my-secret")
print(value.decode())
```

Cloud services aren't covered by the `GoogleScopes` enum yet — pass the raw scope string(s) your
project needs (e.g. the broad `cloud-platform` scope above, or narrower BigQuery/Secret Manager
scopes if you want to limit access).

`BigQueryService.query` starts a query job and returns immediately without waiting for it to
finish (call `.result()` on the returned job yourself); `query_and_wait` blocks until the query
completes and returns the result rows directly.

### Authentication

`Conduit.google(...)` picks an authentication strategy based on which arguments you pass, in this
order of precedence:

1. `service_account_path` — service account credentials.
2. `oauth_client_path` and/or `token_path` — OAuth installed-app flow. If `token_path` points to an
   existing, valid cached token, no browser flow is triggered. If `token_path` is provided, the
   token is written there after a successful flow so future runs can skip re-authenticating.
3. Neither is provided — falls back to Application Default Credentials (ADC).

Note that constructing a client may perform a live network call and, for a fresh OAuth flow, open a
browser window for consent.

### Errors

All exceptions this package raises inherit from `conduit_py.google.exceptions.ConduitGoogleError`
and carry a `docs_url` attribute pointing back to the relevant section below — that same URL is
appended to the exception message, so it's visible directly in tracebacks.

#### Authentication errors

`conduit_py.google.exceptions.GoogleAuthError` is raised when authentication fails or is
misconfigured before any API call is made — for example, an OAuth flow with no cached token at
`token_path` and no `oauth_client_path` to start a new one from, or a `service_account_path` /
`oauth_client_path` that doesn't exist on disk. Check that the path arguments you passed to
`Conduit.google(...)` point at real files, and that at least one of `service_account_path`,
`token_path`, or `oauth_client_path` is provided (see [Authentication](#authentication) above for
precedence).

#### API errors

`conduit_py.google.exceptions.GoogleAPIError` wraps a failed Google API request. It carries:

- `status_code` — the HTTP status code from the failed request (e.g. `403`, `404`).
- `reason` — the reason string from the failed request.

A `403` usually means the authenticated identity lacks permission on the target resource, or the
scopes passed to `Conduit.google(...)` don't cover the operation being called. A `404` usually
means the resource ID (e.g. `spreadsheet_id`) doesn't exist or isn't accessible to the
authenticated identity.

## Development

```bash
uv sync
uv run pytest
```

### Manual smoke test

`scripts/manual_smoke_test.py` exercises the real Google Sheets API (not part of the automated
suite). It expects an OAuth client secret at `credentials.json` in the repo root and caches the
resulting token at `token.json` (both gitignored):

```bash
uv run python scripts/manual_smoke_test.py
```
