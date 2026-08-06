# conduit-py

A unified, opinionated Python client for authenticating and working with Google APIs.

Currently supported:

- **Auth**: Application Default Credentials (ADC), OAuth client (installed-app flow with token
  caching), and service account credentials.
- **Google Workspace**:
  - Sheets: `create_sheet`, `get_sheet`, `get_values`, `update_values`, `append_values`,
    `clear_values`, `add_chart`.
  - Docs: `create_doc`, `get_document`, `append_text`, `insert_image`.
  - Slides: `create_slide`, `get_presentation`, `add_slide`, `add_sheets_chart`.
  - Drive: `upload_file`, `download_file`, `list_files`, `delete_file`, `share_file`.
  - Gmail: `send_message`, `list_messages`, `get_message`, `trash_message`.
  - Calendar: `create_event`, `list_events`, `get_event`, `delete_event`.
  - Forms: `create_form`, `get_form`, `add_text_question`, `list_responses`.
  - Tasks: `create_task`, `list_tasks`, `complete_task`, `delete_task`.
- **Google Cloud**: Requires `project_name` (see [Google Cloud](#google-cloud) below).
  - BigQuery: `query`, `query_and_wait`, `get_table`, `list_datasets`, `list_tables`,
    `create_dataset`, `insert_rows_json`, `load_table_from_uri`, `export_table_to_gcs`.
  - Secret Manager: `create_secret`, `add_secret_version`, `access_secret_version`,
    `list_secrets`, `list_secret_versions`, `delete_secret`, `secret_exists`.
  - Cloud Storage: `create_bucket`, `list_buckets`, `upload_blob`, `download_blob`,
    `list_blobs`, `delete_blob`, `create_bucket_notification`.
  - Pub/Sub: `create_topic`, `list_topics`, `publish_message`, `create_subscription`,
    `pull_messages`, `acknowledge_messages`.
  - Firestore: `create_document`, `get_document`, `update_document`, `delete_document`,
    `list_documents`.
  - Cloud Logging: `write_log`, `list_entries`.
  - IAM: `create_service_account`, `list_service_accounts`, `delete_service_account`,
    `create_service_account_key` (service account/key lifecycle — not resource-level access
    grants; see [Google Cloud](#google-cloud) below).

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
spreadsheet_id = sheet["spreadsheetId"]

google.workspace.sheets.update_values(spreadsheet_id, "Sheet1!A1", [["Hello", "World"]])
rows = google.workspace.sheets.get_values(spreadsheet_id, "Sheet1!A1:B1")
print(rows)  # [["Hello", "World"]]
```

`update_values`/`append_values` default to `value_input_option="USER_ENTERED"`, so values are
parsed as if typed by a user (e.g. `"=SUM(A1:A2)"` becomes a real formula, not a literal string).

Docs and Slides follow the same create-then-operate shape:

```python
doc = google.workspace.docs.create_doc("My Doc")
google.workspace.docs.append_text(doc["documentId"], "Hello, world!")
google.workspace.docs.insert_image(doc["documentId"], "https://example.com/chart.png")

deck = google.workspace.slides.create_slide("My Deck")
slide = google.workspace.slides.add_slide(deck["presentationId"])
```

`insert_image`'s `image_uri` must be a URL Google's servers can fetch (a public GCS object, a
Drive file shared as "anyone with the link", or a signed URL) — raw bytes aren't accepted.

Drive manages files directly (no create-an-empty-resource step):

```python
file = google.workspace.drive.upload_file("report.txt", b"Hello, world!")
content = google.workspace.drive.download_file(file["id"])
google.workspace.drive.share_file(file["id"], "teammate@example.com", role="writer")
```

Gmail sends/reads mail as the authenticated user (`GoogleScopes.GMAIL` has `READ`, `SEND`, and
`MODIFY` variants, since Gmail gates reading, sending, and modifying mail with separate scopes):

```python
google.workspace.gmail.send_message("teammate@example.com", "Report ready", "See attached.")
unread = google.workspace.gmail.list_messages(query="is:unread")
for stub in unread:
    message = google.workspace.gmail.get_message(stub["id"])
    print(message["snippet"])
```

Calendar times are RFC3339 timestamps, and `GoogleScopes.CALENDAR` is scoped to events only (not
calendar list management):

```python
event = google.workspace.calendar.create_event(
    "primary", "Standup", "2026-01-15T09:00:00-05:00", "2026-01-15T09:15:00-05:00"
)
upcoming = google.workspace.calendar.list_events("primary", time_min="2026-01-01T00:00:00Z")
google.workspace.calendar.delete_event("primary", event["id"])
```

Forms only accepts a title on creation — add questions afterward with `add_text_question`, which
appends to the end of the form (it fetches the form first to compute the correct insertion index):

```python
form = google.workspace.forms.create_form("Feedback Survey")
google.workspace.forms.add_text_question(form["formId"], "What's your name?")
responses = google.workspace.forms.list_responses(form["formId"])
```

```python
task = google.workspace.tasks.create_task("@default", "Buy milk")
google.workspace.tasks.complete_task("@default", task["id"])
```

### Google Cloud

Pass `project_name` to `Conduit.google(...)` to also get a `.cloud` client exposing `.bigquery`,
`.secret_manager`, `.storage`, `.pubsub`, `.firestore`, `.logging`, and `.iam`. If `project_name`
is omitted, `.cloud` is `None`.

```python
from conduit_py import Conduit
from conduit_py.google import GoogleScopes

google = Conduit.google(
    scopes=[
        GoogleScopes.BIGQUERY.WRITE,
        GoogleScopes.SECRET_MANAGER.CLOUD_PLATFORM,
        GoogleScopes.CLOUD_STORAGE.WRITE,
        GoogleScopes.PUBSUB.PUBSUB,
        GoogleScopes.FIRESTORE.DATASTORE,
        GoogleScopes.CLOUD_LOGGING.WRITE,
        GoogleScopes.IAM.CLOUD_PLATFORM,
    ],
    oauth_client_path="path/to/client_secret.json",
    token_path="path/to/token.json",
    project_name="my-gcp-project",
)

# BigQuery
rows = google.cloud.bigquery.query_and_wait("SELECT 1 AS value")
for row in rows:
    print(row.value)

google.cloud.bigquery.create_dataset("my_dataset")
google.cloud.bigquery.insert_rows_json("my_dataset", "my_table", [{"col": "val"}])
table = google.cloud.bigquery.get_table("my_dataset", "my_table")
for dataset in google.cloud.bigquery.list_datasets():
    print(dataset.dataset_id)

google.cloud.bigquery.load_table_from_uri("my_dataset", "my_table", "gs://my-bucket/data.csv")
google.cloud.bigquery.export_table_to_gcs("my_dataset", "my_table", "gs://my-bucket/export-*.csv")

# Secret Manager
google.cloud.secret_manager.create_secret("my-secret")
google.cloud.secret_manager.add_secret_version("my-secret", payload="hunter2")
value = google.cloud.secret_manager.access_secret_version("my-secret")
print(value.decode())

if google.cloud.secret_manager.secret_exists("my-secret"):
    google.cloud.secret_manager.delete_secret("my-secret")

# Cloud Storage
google.cloud.storage.create_bucket("my-bucket")
google.cloud.storage.upload_blob("my-bucket", "report.txt", "Hello, world!")
content = google.cloud.storage.download_blob("my-bucket", "report.txt")
for blob in google.cloud.storage.list_blobs("my-bucket"):
    print(blob.name)
google.cloud.storage.create_bucket_notification("my-bucket", "my-topic")

# Pub/Sub
google.cloud.pubsub.create_topic("my-topic")
google.cloud.pubsub.create_subscription("my-topic", "my-subscription")
google.cloud.pubsub.publish_message("my-topic", "hello world")

response = google.cloud.pubsub.pull_messages("my-subscription", max_messages=5)
ack_ids = [msg.ack_id for msg in response.received_messages]
for msg in response.received_messages:
    print(msg.message.data)
if ack_ids:
    google.cloud.pubsub.acknowledge_messages("my-subscription", ack_ids)

# Firestore
google.cloud.firestore.create_document("users", "user123", {"name": "Ada"})
user = google.cloud.firestore.get_document("users", "user123")
google.cloud.firestore.update_document("users", "user123", {"name": "Ada Lovelace"})
for doc in google.cloud.firestore.list_documents("users"):
    print(doc.id, doc.to_dict())

# Cloud Logging
google.cloud.logging.write_log("my-log", "Job finished successfully", severity="INFO")
for entry in google.cloud.logging.list_entries(log_name="my-log", max_results=10):
    print(entry.payload)

# IAM
sa = google.cloud.iam.create_service_account("my-app-sa", "My App Service Account")
key = google.cloud.iam.create_service_account_key(sa.email)
google.cloud.iam.delete_service_account(sa.email)
```

`GoogleScopes.BIGQUERY` has `READ`, `WRITE`, and `INSERT_DATA` variants for narrower access.
`GoogleScopes.CLOUD_STORAGE` and `GoogleScopes.CLOUD_LOGGING` each have `READ`/`WRITE`.
`GoogleScopes.SECRET_MANAGER`, `GoogleScopes.PUBSUB`, `GoogleScopes.FIRESTORE`, and
`GoogleScopes.IAM` each only have one variant (`CLOUD_PLATFORM`, `PUBSUB`, `DATASTORE`, and
`CLOUD_PLATFORM` respectively) — all four are gRPC-based Cloud APIs gated by IAM permissions
rather than granular OAuth scopes.

`IAMService` manages service account and key *lifecycle* (create/list/delete a service account,
create a key for one) — it does not grant that service account access to other resources (e.g.
a Secret Manager secret or Storage bucket). Resource-level access grants live on each resource's
own IAM policy and aren't covered by this package yet.

`BigQueryService.query` starts a query job and returns immediately without waiting for it to
finish (call `.result()` on the returned job yourself); `query_and_wait` blocks until the query
completes and returns the result rows directly. `insert_rows_json` streams rows into a table
without a load job; unlike other BigQuery methods it doesn't raise on a per-row failure by
default, so this wrapper checks the returned error list itself and raises `GoogleAPIError` if any
row was rejected. `load_table_from_uri` and `export_table_to_gcs` both block until their job
completes (like `query_and_wait`, not `query`) and are the idiomatic way to move data between GCS
and BigQuery — `load_table_from_uri` parses the source file itself (with schema autodetection),
unlike `insert_rows_json`, which only accepts already-parsed Python dicts.

`PubSubService.pull_messages` does not acknowledge the messages it pulls — call
`acknowledge_messages` with each message's `ack_id` once you've finished processing it, or it will
be redelivered after the subscription's ack deadline elapses.

`FirestoreService.create_document` creates or fully overwrites a document; `update_document`
merges fields into an existing document and fails if it doesn't exist. `get_document` returns
`None` rather than raising when the document doesn't exist, since Firestore itself doesn't treat
a missing document as an error.

### Cross-service workflows

The services above are designed to compose. Two common patterns:

**A file lands in a bucket → gets loaded into BigQuery → an alert goes out.**
`create_bucket_notification` is what makes "a file landed" externally observable — it configures
the bucket to publish a Pub/Sub message on every new object, which some external trigger (a Cloud
Function, a polling worker using `pull_messages`, etc.) picks up and reacts to by calling this
library:

```python
# One-time setup
google.cloud.pubsub.create_topic("csv-landed")
google.cloud.storage.create_bucket_notification("my-bucket", "csv-landed")

# Triggered handler, run once per new file (uri comes from the Pub/Sub message)
def handle_new_csv(uri: str) -> None:
    google.cloud.bigquery.load_table_from_uri("my_dataset", "my_table", uri)
    google.workspace.gmail.send_message(
        "team@example.com", "New data loaded", f"Loaded {uri} into my_table."
    )
```

**Query data → put it in a spreadsheet → chart it → drop that chart into a slide deck.**
`add_chart`'s response gives you the `chartId` that `add_sheets_chart` needs — the chart it
creates is *linked*, so it can be refreshed later to reflect updated sheet data rather than being
a static snapshot:

```python
rows = google.cloud.bigquery.query_and_wait("SELECT month, revenue FROM my_dataset.sales")

sheet = google.workspace.sheets.create_sheet("Sales Report")
spreadsheet_id = sheet["spreadsheetId"]
values = [["Month", "Revenue"]] + [[row.month, row.revenue] for row in rows]
google.workspace.sheets.update_values(spreadsheet_id, "Sheet1!A1", values)

chart = google.workspace.sheets.add_chart(
    spreadsheet_id, sheet_id=0, chart_type="COLUMN", title="Revenue by Month",
    start_row_index=0, end_row_index=len(values), start_column_index=0, end_column_index=2,
)
chart_id = chart["replies"][0]["addChart"]["chart"]["chartId"]

deck = google.workspace.slides.create_slide("Q1 Review")
slide = google.workspace.slides.add_slide(deck["presentationId"])
slide_id = slide["replies"][0]["createSlide"]["objectId"]
google.workspace.slides.add_sheets_chart(deck["presentationId"], slide_id, spreadsheet_id, chart_id)
```

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
