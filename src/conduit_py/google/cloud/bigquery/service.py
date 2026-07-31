"""Google BigQuery API service wrapper."""

from google.api_core.exceptions import GoogleAPICallError
from google.auth.credentials import Credentials
from google.cloud import bigquery
from google.cloud.bigquery.job import QueryJob
from google.cloud.bigquery.table import RowIterator

from conduit_py.google.exceptions import GoogleAPIError


class BigQueryService:
    """Runs BigQuery SQL queries using a shared ``bigquery.Client``.

    Args:
        credentials: Authenticated Google credentials with BigQuery access.
        project_name: The GCP project to bill queries and resolve
            unqualified table references against.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.client = bigquery.Client(
            project=project_name,
            credentials=credentials
        )

    def query_and_wait(
        self,
        query: str
    ) -> RowIterator:
        """Run a query and block until it completes.

        Args:
            query: The SQL query to run.

        Returns:
            A ``RowIterator`` over the query's result rows.

        Raises:
            ValueError: If ``query`` is empty.
            GoogleAPIError: If the query fails.
        """
        if not query:
            raise ValueError("Query cannot be empty")

        try:
            return self.client.query_and_wait(query)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to run query: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def query(
        self,
        query: str
    ) -> QueryJob:
        """Start a query job without waiting for it to complete.

        Unlike ``query_and_wait``, this returns immediately with a job
        handle; call ``.result()`` on it to block for and fetch the rows.

        Args:
            query: The SQL query to run.

        Returns:
            The ``QueryJob`` tracking the running query.

        Raises:
            ValueError: If ``query`` is empty.
            GoogleAPIError: If the query fails to start.
        """
        if not query:
            raise ValueError("Query cannot be empty")

        try:
            return self.client.query(query)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to run query: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
