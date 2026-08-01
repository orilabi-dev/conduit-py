from unittest.mock import MagicMock, patch

from conduit_py.google.cloud.client import CloudClient


def test_init_builds_bigquery_service_with_credentials_and_project():
    credentials = MagicMock()

    with patch("conduit_py.google.cloud.client.BigQueryService") as mock_bigquery_cls, patch(
        "conduit_py.google.cloud.client.SecretManagerService"
    ), patch("conduit_py.google.cloud.client.CloudStorageService"), patch(
        "conduit_py.google.cloud.client.PubSubService"
    ):
        client = CloudClient(credentials=credentials, project_name="test-project")

    mock_bigquery_cls.assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.bigquery is mock_bigquery_cls.return_value


def test_init_builds_secret_manager_service_with_credentials_and_project():
    credentials = MagicMock()

    with patch("conduit_py.google.cloud.client.BigQueryService"), patch(
        "conduit_py.google.cloud.client.SecretManagerService"
    ) as mock_secret_manager_cls, patch(
        "conduit_py.google.cloud.client.CloudStorageService"
    ), patch("conduit_py.google.cloud.client.PubSubService"):
        client = CloudClient(credentials=credentials, project_name="test-project")

    mock_secret_manager_cls.assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.secret_manager is mock_secret_manager_cls.return_value


def test_init_builds_storage_service_with_credentials_and_project():
    credentials = MagicMock()

    with patch("conduit_py.google.cloud.client.BigQueryService"), patch(
        "conduit_py.google.cloud.client.SecretManagerService"
    ), patch("conduit_py.google.cloud.client.CloudStorageService") as mock_storage_cls, patch(
        "conduit_py.google.cloud.client.PubSubService"
    ):
        client = CloudClient(credentials=credentials, project_name="test-project")

    mock_storage_cls.assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.storage is mock_storage_cls.return_value


def test_init_builds_pubsub_service_with_credentials_and_project():
    credentials = MagicMock()

    with patch("conduit_py.google.cloud.client.BigQueryService"), patch(
        "conduit_py.google.cloud.client.SecretManagerService"
    ), patch("conduit_py.google.cloud.client.CloudStorageService"), patch(
        "conduit_py.google.cloud.client.PubSubService"
    ) as mock_pubsub_cls:
        client = CloudClient(credentials=credentials, project_name="test-project")

    mock_pubsub_cls.assert_called_once_with(
        credentials=credentials, project_name="test-project"
    )
    assert client.pubsub is mock_pubsub_cls.return_value
