from contextlib import ExitStack
from unittest.mock import MagicMock, patch

from conduit_py.google.cloud.client import CloudClient

_SERVICE_CLASS_NAMES = [
    "BigQueryService",
    "SecretManagerService",
    "CloudStorageService",
    "PubSubService",
    "FirestoreService",
    "CloudLoggingService",
    "IAMService",
]


def _patch_all_services() -> tuple[ExitStack, dict[str, MagicMock]]:
    stack = ExitStack()
    mocks = {
        name: stack.enter_context(patch(f"conduit_py.google.cloud.client.{name}"))
        for name in _SERVICE_CLASS_NAMES
    }
    return stack, mocks


def test_init_builds_bigquery_service_with_credentials_and_project():
    credentials = MagicMock()

    stack, mocks = _patch_all_services()
    with stack:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mocks["BigQueryService"].assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.bigquery is mocks["BigQueryService"].return_value


def test_init_builds_secret_manager_service_with_credentials_and_project():
    credentials = MagicMock()

    stack, mocks = _patch_all_services()
    with stack:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mocks["SecretManagerService"].assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.secret_manager is mocks["SecretManagerService"].return_value


def test_init_builds_storage_service_with_credentials_and_project():
    credentials = MagicMock()

    stack, mocks = _patch_all_services()
    with stack:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mocks["CloudStorageService"].assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.storage is mocks["CloudStorageService"].return_value


def test_init_builds_pubsub_service_with_credentials_and_project():
    credentials = MagicMock()

    stack, mocks = _patch_all_services()
    with stack:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mocks["PubSubService"].assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.pubsub is mocks["PubSubService"].return_value


def test_init_builds_firestore_service_with_credentials_and_project():
    credentials = MagicMock()

    stack, mocks = _patch_all_services()
    with stack:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mocks["FirestoreService"].assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.firestore is mocks["FirestoreService"].return_value


def test_init_builds_logging_service_with_credentials_and_project():
    credentials = MagicMock()

    stack, mocks = _patch_all_services()
    with stack:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mocks["CloudLoggingService"].assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.logging is mocks["CloudLoggingService"].return_value


def test_init_builds_iam_service_with_credentials_and_project():
    credentials = MagicMock()

    stack, mocks = _patch_all_services()
    with stack:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mocks["IAMService"].assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.iam is mocks["IAMService"].return_value
