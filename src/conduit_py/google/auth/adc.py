"""Application Default Credentials (ADC) authentication."""

from google.auth import default


class ADCAuthenticator:
    """Authenticates using Google Application Default Credentials."""

    @staticmethod
    def authenticate(
        scopes: list[str]
    ):
        """Resolve credentials via Application Default Credentials.

        Delegates to ``google.auth.default``, which looks for credentials in
        the environment (e.g. the ``GOOGLE_APPLICATION_CREDENTIALS``
        variable, gcloud's local ADC file, or the metadata server on GCP).

        Args:
            scopes: Google OAuth scopes to request.

        Returns:
            The default credentials object resolved by
            ``google.auth.default``.

        Raises:
            google.auth.exceptions.DefaultCredentialsError: If no ADC
                credentials can be found in the environment. Not wrapped in
                a conduit_py exception type.
        """
        credentials, _ = default(
            scopes=scopes
        )

        return credentials