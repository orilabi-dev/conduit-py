"""Service account authentication."""

from pathlib import Path

from google.oauth2.service_account import Credentials


class ServiceAccountAuthenticator:
    """Authenticates using a service account key file."""

    @staticmethod
    def authenticate(
        service_account_path: Path,
        scopes: list[str]
    ):
        """Load credentials from a service account key file.

        Args:
            service_account_path: Path to the service account JSON key file.
            scopes: Google OAuth scopes to request.

        Returns:
            A ``google.oauth2.service_account.Credentials`` instance.

        Raises:
            ValueError: If the file at ``service_account_path`` is not a
                valid service account key.
            FileNotFoundError: If ``service_account_path`` does not exist.
        """
        return Credentials.from_service_account_file(
            service_account_path,
            scopes=scopes
        )