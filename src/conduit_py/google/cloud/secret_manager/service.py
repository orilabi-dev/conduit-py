"""Google Secret Manager API service wrapper."""

from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.auth.credentials import Credentials
from google.cloud import secretmanager
from google.cloud.secretmanager import Secret, SecretVersion
from google.cloud.secretmanager_v1.services.secret_manager_service.pagers import (
    ListSecretsPager,
    ListSecretVersionsPager,
)

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

    def list_secrets(self) -> ListSecretsPager:
        """List the secrets in ``project_name``.

        Returns:
            An iterator over the project's ``Secret`` objects.

        Raises:
            GoogleAPIError: If the secrets cannot be listed.
        """
        try:
            parent = f"projects/{self.project_name}"
            return self.client.list_secrets(request={"parent": parent})
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list secrets: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_secret_versions(
        self,
        secret_id: str
    ) -> ListSecretVersionsPager:
        """List the versions of a secret.

        Args:
            secret_id: The secret to list versions for.

        Returns:
            An iterator over the secret's ``SecretVersion`` objects.

        Raises:
            ValueError: If ``secret_id`` is empty.
            GoogleAPIError: If the versions cannot be listed.
        """
        if not secret_id:
            raise ValueError("Secret ID cannot be empty")

        try:
            parent = f"projects/{self.project_name}/secrets/{secret_id}"
            return self.client.list_secret_versions(request={"parent": parent})
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list secret versions: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def delete_secret(
        self,
        secret_id: str
    ) -> None:
        """Permanently delete a secret and all of its versions.

        This is irreversible: once deleted, the secret and every version
        of its payload are gone for good.

        Args:
            secret_id: The secret to delete.

        Raises:
            ValueError: If ``secret_id`` is empty.
            GoogleAPIError: If the secret cannot be deleted.
        """
        if not secret_id:
            raise ValueError("Secret ID cannot be empty")

        try:
            name = f"projects/{self.project_name}/secrets/{secret_id}"
            self.client.delete_secret(request={"name": name})
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to delete secret: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def secret_exists(
        self,
        secret_id: str
    ) -> bool:
        """Check whether a secret exists.

        Args:
            secret_id: The secret to check for.

        Returns:
            ``True`` if the secret exists, ``False`` if it does not.

        Raises:
            ValueError: If ``secret_id`` is empty.
            GoogleAPIError: If the check fails for a reason other than the
                secret not existing (e.g. a permission error).
        """
        if not secret_id:
            raise ValueError("Secret ID cannot be empty")

        try:
            name = f"projects/{self.project_name}/secrets/{secret_id}"
            self.client.get_secret(request={"name": name})
            return True
        except NotFound:
            return False
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to check whether secret exists: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
