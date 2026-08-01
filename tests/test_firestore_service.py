from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from conduit_py.google.cloud.firestore.service import FirestoreService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[FirestoreService, MagicMock]:
    with patch(
        "conduit_py.google.cloud.firestore.service.firestore.Client"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        service = FirestoreService(credentials=MagicMock(), project_name="test-project")
    return service, mock_client


def test_init_builds_client_with_project_and_credentials():
    credentials = MagicMock()
    with patch(
        "conduit_py.google.cloud.firestore.service.firestore.Client"
    ) as mock_client_cls:
        FirestoreService(credentials=credentials, project_name="test-project")

    mock_client_cls.assert_called_once_with(project="test-project", credentials=credentials)


def test_create_document_rejects_empty_collection():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_document("", "doc1", {"field": "value"})


def test_create_document_rejects_empty_document_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_document("my-collection", "", {"field": "value"})


def test_create_document_rejects_empty_data():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_document("my-collection", "doc1", {})


def test_create_document_sets_data_via_collection_and_document():
    service, mock_client = _make_service()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document

    result = service.create_document("my-collection", "doc1", {"field": "value"})

    mock_client.collection.assert_called_once_with("my-collection")
    mock_collection.document.assert_called_once_with("doc1")
    mock_document.set.assert_called_once_with({"field": "value"})
    assert result is None


def test_create_document_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.collection.return_value.document.return_value.set.side_effect = (
        NotFound("collection not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_document("my-collection", "doc1", {"field": "value"})

    assert exc_info.value.status_code == 404
    assert "collection not found" in exc_info.value.reason


def test_get_document_rejects_empty_collection():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_document("", "doc1")


def test_get_document_rejects_empty_document_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.get_document("my-collection", "")


def test_get_document_returns_dict_on_success():
    service, mock_client = _make_service()
    mock_snapshot = MagicMock()
    mock_snapshot.to_dict.return_value = {"field": "value"}
    mock_client.collection.return_value.document.return_value.get.return_value = mock_snapshot

    result = service.get_document("my-collection", "doc1")

    mock_client.collection.assert_called_once_with("my-collection")
    mock_client.collection.return_value.document.assert_called_once_with("doc1")
    assert result == {"field": "value"}


def test_get_document_returns_none_when_document_missing():
    service, mock_client = _make_service()
    mock_snapshot = MagicMock()
    mock_snapshot.to_dict.return_value = None
    mock_client.collection.return_value.document.return_value.get.return_value = mock_snapshot

    result = service.get_document("my-collection", "doc1")

    assert result is None


def test_get_document_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.collection.return_value.document.return_value.get.side_effect = (
        NotFound("collection not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.get_document("my-collection", "doc1")

    assert exc_info.value.status_code == 404
    assert "collection not found" in exc_info.value.reason


def test_update_document_rejects_empty_collection():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.update_document("", "doc1", {"field": "value"})


def test_update_document_rejects_empty_document_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.update_document("my-collection", "", {"field": "value"})


def test_update_document_rejects_empty_data():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.update_document("my-collection", "doc1", {})


def test_update_document_updates_via_collection_and_document():
    service, mock_client = _make_service()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document

    result = service.update_document("my-collection", "doc1", {"field": "new-value"})

    mock_document.update.assert_called_once_with({"field": "new-value"})
    assert result is None


def test_update_document_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.collection.return_value.document.return_value.update.side_effect = (
        NotFound("document not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.update_document("my-collection", "doc1", {"field": "value"})

    assert exc_info.value.status_code == 404
    assert "document not found" in exc_info.value.reason


def test_delete_document_rejects_empty_collection():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_document("", "doc1")


def test_delete_document_rejects_empty_document_id():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.delete_document("my-collection", "")


def test_delete_document_deletes_via_collection_and_document():
    service, mock_client = _make_service()
    mock_collection = MagicMock()
    mock_document = MagicMock()
    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document

    result = service.delete_document("my-collection", "doc1")

    mock_document.delete.assert_called_once_with()
    assert result is None


def test_delete_document_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.collection.return_value.document.return_value.delete.side_effect = (
        NotFound("document not found")
    )

    with pytest.raises(GoogleAPIError) as exc_info:
        service.delete_document("my-collection", "doc1")

    assert exc_info.value.status_code == 404
    assert "document not found" in exc_info.value.reason


def test_list_documents_rejects_empty_collection():
    service, _ = _make_service()

    with pytest.raises(ValueError):
        service.list_documents("")


def test_list_documents_calls_client_with_collection():
    service, mock_client = _make_service()
    fake_stream = iter(["doc1", "doc2"])
    mock_client.collection.return_value.stream.return_value = fake_stream

    result = service.list_documents("my-collection")

    mock_client.collection.assert_called_once_with("my-collection")
    assert result is fake_stream


def test_list_documents_wraps_api_call_error():
    service, mock_client = _make_service()
    mock_client.collection.return_value.stream.side_effect = NotFound("collection not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_documents("my-collection")

    assert exc_info.value.status_code == 404
    assert "collection not found" in exc_info.value.reason
