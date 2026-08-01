"""Google Cloud IAM API service wrapper.

Covers service account and service account key lifecycle management.
Granting/revoking a service account's access to a specific resource
(e.g. a Secret Manager secret or Storage bucket) is a separate concern,
handled via each resource's own IAM policy — not this service.
"""

from google.api_core.exceptions import GoogleAPICallError
from google.auth.credentials import Credentials
from google.cloud import iam_admin_v1
from google.cloud.iam_admin_v1.services.iam.pagers import ListServiceAccountsPager
from google.cloud.iam_admin_v1.types import ServiceAccount, ServiceAccountKey

from conduit_py.google.exceptions import GoogleAPIError


class IAMService:
    """Manages service accounts and their keys for a single GCP project.

    Args:
        credentials: Authenticated Google credentials with IAM access.
        project_name: The GCP project service accounts belong to.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.project_name = project_name
        self.client = iam_admin_v1.IAMClient(credentials=credentials)

    def create_service_account(
        self,
        account_id: str,
        display_name: str
    ) -> ServiceAccount:
        """Create a new service account in the client's project.

        Args:
            account_id: The service account's ID, unique within the
                project (becomes the local part of its email address).
            display_name: A human-readable name for the service account.

        Returns:
            The created ``ServiceAccount`` (has ``.email``, used to
            address it in the other methods here).

        Raises:
            ValueError: If ``account_id`` or ``display_name`` is empty.
            GoogleAPIError: If the service account cannot be created.
        """
        if not account_id:
            raise ValueError("Account ID cannot be empty")

        if not display_name:
            raise ValueError("Display name cannot be empty")

        try:
            parent = self.client.common_project_path(self.project_name)
            return self.client.create_service_account(
                name=parent,
                account_id=account_id,
                service_account=ServiceAccount(display_name=display_name),
            )
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create service account: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_service_accounts(self) -> ListServiceAccountsPager:
        """List the service accounts in the client's project.

        Returns:
            An iterator over the project's ``ServiceAccount`` objects.

        Raises:
            GoogleAPIError: If the service accounts cannot be listed.
        """
        try:
            parent = self.client.common_project_path(self.project_name)
            return self.client.list_service_accounts(name=parent)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list service accounts: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def delete_service_account(
        self,
        email: str
    ) -> None:
        """Permanently delete a service account.

        Args:
            email: The service account's email address (e.g. as
                returned by ``create_service_account(...).email``).

        Raises:
            ValueError: If ``email`` is empty.
            GoogleAPIError: If the service account cannot be deleted.
        """
        if not email:
            raise ValueError("Email cannot be empty")

        try:
            name = self.client.service_account_path(self.project_name, email)
            self.client.delete_service_account(name=name)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to delete service account: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def create_service_account_key(
        self,
        email: str
    ) -> ServiceAccountKey:
        """Create a new key for a service account.

        The returned key's private key material is only ever available
        in this response — Google does not retain a copy to hand back
        later, so callers must persist it themselves if needed.

        Args:
            email: The service account's email address to create a key
                for.

        Returns:
            The created ``ServiceAccountKey``.

        Raises:
            ValueError: If ``email`` is empty.
            GoogleAPIError: If the key cannot be created.
        """
        if not email:
            raise ValueError("Email cannot be empty")

        try:
            name = self.client.service_account_path(self.project_name, email)
            return self.client.create_service_account_key(name=name)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create service account key: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
