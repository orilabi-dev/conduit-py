"""Aggregate client exposing Google Cloud services (BigQuery, Secret Manager,
Cloud Storage, Pub/Sub, Firestore, Cloud Logging, IAM)."""

from google.auth.credentials import Credentials

from conduit_py.google.cloud.bigquery.service import BigQueryService
from conduit_py.google.cloud.firestore.service import FirestoreService
from conduit_py.google.cloud.iam.service import IAMService
from conduit_py.google.cloud.logging.service import CloudLoggingService
from conduit_py.google.cloud.pubsub.service import PubSubService
from conduit_py.google.cloud.secret_manager.service import SecretManagerService
from conduit_py.google.cloud.storage.service import CloudStorageService


class CloudClient:
    """Wires up Google Cloud service clients for a single GCP project.

    Args:
        credentials: Authenticated Google credentials with access to the
            requested Cloud services.
        project_name: The GCP project the wrapped services operate against.

    Attributes:
        bigquery: A ``BigQueryService`` wired up with ``credentials`` and
            ``project_name``.
        secret_manager: A ``SecretManagerService`` wired up with
            ``credentials`` and ``project_name``.
        storage: A ``CloudStorageService`` wired up with ``credentials``
            and ``project_name``.
        pubsub: A ``PubSubService`` wired up with ``credentials`` and
            ``project_name``.
        firestore: A ``FirestoreService`` wired up with ``credentials``
            and ``project_name``.
        logging: A ``CloudLoggingService`` wired up with ``credentials``
            and ``project_name``.
        iam: An ``IAMService`` wired up with ``credentials`` and
            ``project_name``.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.bigquery = BigQueryService(
            credentials=credentials,
            project_name=project_name
        )

        self.secret_manager = SecretManagerService(
            credentials=credentials,
            project_name=project_name
        )

        self.storage = CloudStorageService(
            credentials=credentials,
            project_name=project_name
        )

        self.pubsub = PubSubService(
            credentials=credentials,
            project_name=project_name
        )

        self.firestore = FirestoreService(
            credentials=credentials,
            project_name=project_name
        )

        self.logging = CloudLoggingService(
            credentials=credentials,
            project_name=project_name
        )

        self.iam = IAMService(
            credentials=credentials,
            project_name=project_name
        )
