from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from conduit_py.google.cloud.bigquery.service import BigQueryService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[BigQueryService, MagicMock]:
    with patch("conduit_py.google.cloud.bigquery.service.bigquery.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        service = BigQueryService(credentials=MagicMock(), project_name="test-project")
    return service, mock_client


def test_init_builds_client_with_project_and_credentials():
    credentials = MagicMock()
    with patch("conduit_py.google.cloud.bigquery.service.bigquery.Client") as mock_client_cls:
        BigQueryService(credentials=credentials, project_name="test-project")

    mock_client_cls.assert_called_once_with(project="test-project", credentials=credentials)


def test_query_and_wait_rejects_empty_query():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.query_and_wait("")


def test_query_and_wait_returns_rows_on_success():
    service, mock_client = _make_service()
    mock_client.query_and_wait.return_value = ["row1", "row2"]

    result = service.query_and_wait("SELECT 1")

    mock_client.query_and_wait.assert_called_once_with("SELECT 1")
    assert result == ["row1", "row2"]


def test_query_and_wait_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.query_and_wait.side_effect = NotFound("table not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.query_and_wait("SELECT 1")

    assert exc_info.value.status_code == 404
    assert "table not found" in exc_info.value.reason


def test_query_rejects_empty_query():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.query("")


def test_query_returns_job_without_waiting():
    service, mock_client = _make_service()
    fake_job = MagicMock(name="QueryJob")
    mock_client.query.return_value = fake_job

    result = service.query("SELECT 1")

    mock_client.query.assert_called_once_with("SELECT 1")
    assert result is fake_job


def test_query_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.query.side_effect = NotFound("bad query")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.query("SELECT 1")

    assert exc_info.value.status_code == 404
    assert "bad query" in exc_info.value.reason


def test_get_table_rejects_empty_dataset_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_table("", "my_table")


def test_get_table_rejects_empty_table_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_table("my_dataset", "")


def test_get_table_calls_client_with_fully_qualified_table_ref():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    fake_table = MagicMock(name="Table")
    mock_client.get_table.return_value = fake_table

    result = service.get_table("my_dataset", "my_table")

    mock_client.get_table.assert_called_once_with("test-project.my_dataset.my_table")
    assert result is fake_table


def test_get_table_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    mock_client.get_table.side_effect = NotFound("table not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.get_table("my_dataset", "my_table")

    assert exc_info.value.status_code == 404
    assert "table not found" in exc_info.value.reason


def test_list_datasets_returns_iterator_from_client():
    service, mock_client = _make_service()
    mock_client.list_datasets.return_value = ["dataset1", "dataset2"]

    result = service.list_datasets()

    mock_client.list_datasets.assert_called_once_with()
    assert result == ["dataset1", "dataset2"]


def test_list_datasets_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.list_datasets.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_datasets()

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_list_tables_rejects_empty_dataset_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.list_tables("")


def test_list_tables_calls_client_with_dataset_id():
    service, mock_client = _make_service()
    mock_client.list_tables.return_value = ["table1", "table2"]

    result = service.list_tables("my_dataset")

    mock_client.list_tables.assert_called_once_with("my_dataset")
    assert result == ["table1", "table2"]


def test_list_tables_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.list_tables.side_effect = NotFound("dataset not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_tables("my_dataset")

    assert exc_info.value.status_code == 404
    assert "dataset not found" in exc_info.value.reason


def test_create_dataset_rejects_empty_dataset_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_dataset("")


def test_create_dataset_calls_client_with_dataset_id():
    service, mock_client = _make_service()
    fake_dataset = MagicMock(name="Dataset")
    mock_client.create_dataset.return_value = fake_dataset

    result = service.create_dataset("my_dataset")

    mock_client.create_dataset.assert_called_once_with("my_dataset")
    assert result is fake_dataset


def test_create_dataset_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.create_dataset.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_dataset("my_dataset")

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_insert_rows_json_rejects_empty_dataset_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.insert_rows_json("", "my_table", [{"col": "val"}])


def test_insert_rows_json_rejects_empty_table_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.insert_rows_json("my_dataset", "", [{"col": "val"}])


def test_insert_rows_json_rejects_empty_rows():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.insert_rows_json("my_dataset", "my_table", [])


def test_insert_rows_json_calls_client_with_fully_qualified_table_and_rows():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    mock_client.insert_rows_json.return_value = []

    service.insert_rows_json("my_dataset", "my_table", [{"col": "val"}])

    mock_client.insert_rows_json.assert_called_once_with(
        table="test-project.my_dataset.my_table",
        json_rows=[{"col": "val"}],
    )


def test_insert_rows_json_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    mock_client.insert_rows_json.side_effect = NotFound("table not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.insert_rows_json("my_dataset", "my_table", [{"col": "val"}])

    assert exc_info.value.status_code == 404
    assert "table not found" in exc_info.value.reason


def test_insert_rows_json_raises_on_partial_row_failures():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    row_errors = [{"index": 0, "errors": [{"reason": "invalid"}]}]
    mock_client.insert_rows_json.return_value = row_errors

    with pytest.raises(GoogleAPIError) as exc_info:
        service.insert_rows_json("my_dataset", "my_table", [{"col": "val"}])

    assert exc_info.value.status_code is None
    assert str(row_errors) in exc_info.value.reason


def test_load_table_from_uri_rejects_empty_dataset_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.load_table_from_uri("", "my_table", "gs://my-bucket/data.csv")


def test_load_table_from_uri_rejects_empty_table_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.load_table_from_uri("my_dataset", "", "gs://my-bucket/data.csv")


def test_load_table_from_uri_rejects_empty_source_uri():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.load_table_from_uri("my_dataset", "my_table", "")


def test_load_table_from_uri_calls_client_and_waits_for_job():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    fake_result = MagicMock(name="LoadJobResult")
    mock_job = MagicMock()
    mock_job.result.return_value = fake_result
    mock_client.load_table_from_uri.return_value = mock_job

    result = service.load_table_from_uri("my_dataset", "my_table", "gs://my-bucket/data.csv")

    args, kwargs = mock_client.load_table_from_uri.call_args
    assert args[0] == "gs://my-bucket/data.csv"
    assert args[1] == "test-project.my_dataset.my_table"
    assert "job_config" in kwargs
    assert result is fake_result


def test_load_table_from_uri_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    mock_client.load_table_from_uri.return_value.result.side_effect = NotFound(
        "dataset not found"
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.load_table_from_uri("my_dataset", "my_table", "gs://my-bucket/data.csv")

    assert exc_info.value.status_code == 404
    assert "dataset not found" in exc_info.value.reason


def test_export_table_to_gcs_rejects_empty_dataset_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.export_table_to_gcs("", "my_table", "gs://my-bucket/export-*.csv")


def test_export_table_to_gcs_rejects_empty_table_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.export_table_to_gcs("my_dataset", "", "gs://my-bucket/export-*.csv")


def test_export_table_to_gcs_rejects_empty_destination_uri():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.export_table_to_gcs("my_dataset", "my_table", "")


def test_export_table_to_gcs_calls_client_and_waits_for_job():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    fake_result = MagicMock(name="ExtractJobResult")
    mock_job = MagicMock()
    mock_job.result.return_value = fake_result
    mock_client.extract_table.return_value = mock_job

    result = service.export_table_to_gcs(
        "my_dataset", "my_table", "gs://my-bucket/export-*.csv"
    )

    mock_client.extract_table.assert_called_once_with(
        "test-project.my_dataset.my_table", "gs://my-bucket/export-*.csv"
    )
    assert result is fake_result


def test_export_table_to_gcs_wraps_api_call_error_with_code_and_reason():
    service, mock_client = _make_service()
    mock_client.project = "test-project"
    mock_client.extract_table.return_value.result.side_effect = NotFound(
        "table not found"
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.export_table_to_gcs("my_dataset", "my_table", "gs://my-bucket/export-*.csv")

    assert exc_info.value.status_code == 404
    assert "table not found" in exc_info.value.reason
