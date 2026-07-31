"""Google Secret Manager API service wrapper."""

from google.api_core.exceptions import GoogleAPICallError
from google.auth.credentials import Credentials
from google.cloud import secretmanager
from google.cloud.secretmanager import Secret, SecretVersion

from conduit_py.google.exceptions import GoogleAPIError


class SecretManagerService:
    """Creates secrets and manages secret versions for a single GCP project.

    Args:
        credentials: Authenticated Google credentials with Secret Manager
            access.
        project_name: The GCP project secrets are created in and read from.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.project_name = project_name
        self.client = secretmanager.SecretManagerServiceClient(
            credentials=credentials
        )

    def create_secret(
        self,
        secret_id: str
    ) -> Secret:
        """Create an empty secret container with automatic replication.

        This only creates the secret resource; it has no versions/values
        until ``add_secret_version`` is called.

        Args:
            secret_id: The ID to create the secret under, unique within
                ``project_name``.

        Returns:
            The created ``Secret``.

        Raises:
            ValueError: If ``secret_id`` is empty.
            GoogleAPIError: If the secret cannot be created.
        """
        if not secret_id:
            raise ValueError("Secret ID cannot be empty")

        try:
            parent = f"projects/{self.project_name}"
            return self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create secret: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def add_secret_version(
        self,
        secret_id: str,
        payload: str | bytes
    ) -> SecretVersion:
        """Add a new version holding ``payload`` to an existing secret.

        Args:
            secret_id: The secret to add a version to. Must already exist
                (see ``create_secret``).
            payload: The secret value. ``str`` values are UTF-8 encoded.

        Returns:
            The created ``SecretVersion``.

        Raises:
            ValueError: If ``secret_id`` or ``payload`` is empty.
            GoogleAPIError: If the version cannot be added.
        """
        if not secret_id:
            raise ValueError("Secret ID cannot be empty")

        if not payload:
            raise ValueError("Payload cannot be empty")

        if isinstance(payload, str):
            payload = payload.encode("utf-8")

        try:
            parent = f"projects/{self.project_name}/secrets/{secret_id}"
            return self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": payload},
                }
            )
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to add secret version: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def access_secret_version(
        self,
        secret_id: str,
        version_id: str = "latest"
    ) -> bytes:
        """Fetch and decode the payload of a secret version.

        Args:
            secret_id: The secret to read from.
            version_id: The version to read, or ``"latest"`` for the most
                recently added enabled version.

        Returns:
            The raw secret payload bytes.

        Raises:
            ValueError: If ``secret_id`` is empty.
            GoogleAPIError: If the version cannot be accessed.
        """
        if not secret_id:
            raise ValueError("Secret ID cannot be empty")

        try:
            name = (
                f"projects/{self.project_name}/secrets/{secret_id}"
                f"/versions/{version_id}"
            )
            response = self.client.access_secret_version(
                request={"name": name}
            )

            return response.payload.data
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to access secret version: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
