from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from conduit_py.google.cloud.storage.service import CloudStorageService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[CloudStorageService, MagicMock]:
    with patch(
        "conduit_py.google.cloud.storage.service.storage.Client"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        service = CloudStorageService(credentials=MagicMock(), project_name="test-project")
    return service, mock_client


def test_init_builds_client_with_project_and_credentials():
    credentials = MagicMock()
    with patch(
        "conduit_py.google.cloud.storage.service.storage.Client"
    ) as mock_client_cls:
        CloudStorageService(credentials=credentials, project_name="test-project")

    mock_client_cls.assert_called_once_with(project="test-project", credentials=credentials)


def test_create_bucket_rejects_empty_bucket_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_bucket("")


def test_create_bucket_calls_client_with_bucket_name():
    service, mock_client = _make_service()
    fake_bucket = MagicMock(name="Bucket")
    mock_client.create_bucket.return_value = fake_bucket

    result = service.create_bucket("my-bucket")

    mock_client.create_bucket.assert_called_once_with("my-bucket")
    assert result is fake_bucket


def test_create_bucket_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.create_bucket.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_bucket("my-bucket")

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_list_buckets_returns_iterator_from_client():
    service, mock_client = _make_service()
    mock_client.list_buckets.return_value = ["bucket1", "bucket2"]

    result = service.list_buckets()

    mock_client.list_buckets.assert_called_once_with()
    assert result == ["bucket1", "bucket2"]


def test_list_buckets_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.list_buckets.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_buckets()

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_upload_blob_rejects_empty_bucket_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.upload_blob("", "my-blob", "data")


def test_upload_blob_rejects_empty_blob_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.upload_blob("my-bucket", "", "data")


def test_upload_blob_rejects_empty_data():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.upload_blob("my-bucket", "my-blob", "")


def test_upload_blob_uploads_via_bucket_and_blob():
    service, mock_client = _make_service()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    service.upload_blob("my-bucket", "my-blob", "hello world")

    mock_client.bucket.assert_called_once_with("my-bucket")
    mock_bucket.blob.assert_called_once_with("my-blob")
    mock_blob.upload_from_string.assert_called_once_with("hello world")


def test_upload_blob_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.bucket.return_value.blob.return_value.upload_from_string.side_effect = (
        NotFound("bucket not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.upload_blob("my-bucket", "my-blob", "data")

    assert exc_info.value.status_code == 404
    assert "bucket not found" in exc_info.value.reason


def test_download_blob_rejects_empty_bucket_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.download_blob("", "my-blob")


def test_download_blob_rejects_empty_blob_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.download_blob("my-bucket", "")


def test_download_blob_returns_bytes_from_blob():
    service, mock_client = _make_service()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.download_as_bytes.return_value = b"file contents"

    result = service.download_blob("my-bucket", "my-blob")

    mock_client.bucket.assert_called_once_with("my-bucket")
    mock_bucket.blob.assert_called_once_with("my-blob")
    assert result == b"file contents"


def test_download_blob_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.bucket.return_value.blob.return_value.download_as_bytes.side_effect = (
        NotFound("blob not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.download_blob("my-bucket", "my-blob")

    assert exc_info.value.status_code == 404
    assert "blob not found" in exc_info.value.reason


def test_list_blobs_rejects_empty_bucket_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.list_blobs("")


def test_list_blobs_calls_client_with_bucket_name():
    service, mock_client = _make_service()
    mock_client.list_blobs.return_value = ["blob1", "blob2"]

    result = service.list_blobs("my-bucket")

    mock_client.list_blobs.assert_called_once_with("my-bucket")
    assert result == ["blob1", "blob2"]


def test_list_blobs_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.list_blobs.side_effect = NotFound("bucket not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_blobs("my-bucket")

    assert exc_info.value.status_code == 404
    assert "bucket not found" in exc_info.value.reason


def test_delete_blob_rejects_empty_bucket_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_blob("", "my-blob")


def test_delete_blob_rejects_empty_blob_name():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_blob("my-bucket", "")


def test_delete_blob_deletes_via_bucket_and_blob():
    service, mock_client = _make_service()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    result = service.delete_blob("my-bucket", "my-blob")

    mock_client.bucket.assert_called_once_with("my-bucket")
    mock_bucket.blob.assert_called_once_with("my-blob")
    mock_blob.delete.assert_called_once_with()
    assert result is None


def test_delete_blob_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.bucket.return_value.blob.return_value.delete.side_effect = (
        NotFound("blob not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.delete_blob("my-bucket", "my-blob")

    assert exc_info.value.status_code == 404
    assert "blob not found" in exc_info.value.reason
