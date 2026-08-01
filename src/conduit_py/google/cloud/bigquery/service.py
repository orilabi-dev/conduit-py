"""Google BigQuery API service wrapper."""

from google.api_core.exceptions import GoogleAPICallError
from google.api_core.page_iterator import HTTPIterator
from google.auth.credentials import Credentials
from google.cloud import bigquery
from google.cloud.bigquery import Dataset
from google.cloud.bigquery.job import QueryJob
from google.cloud.bigquery.table import RowIterator, Table

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

    def get_table(
        self,
        dataset_id: str,
        table_id: str
    ) -> Table:
        """Fetch metadata for a single table.

        Args:
            dataset_id: The dataset containing the table.
            table_id: The table to fetch.

        Returns:
            The ``Table`` metadata.

        Raises:
            ValueError: If ``dataset_id`` or ``table_id`` is empty.
            GoogleAPIError: If the table cannot be fetched.
        """
        if not dataset_id:
            raise ValueError("Dataset ID cannot be empty")

        if not table_id:
            raise ValueError("Table ID cannot be empty")

        try:
            table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
            return self.client.get_table(table_ref)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to get table: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_datasets(self) -> HTTPIterator:
        """List the datasets in the client's project.

        Returns:
            An iterator over the project's ``DatasetListItem`` objects.

        Raises:
            GoogleAPIError: If the datasets cannot be listed.
        """
        try:
            return self.client.list_datasets()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list datasets: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_tables(
        self,
        dataset_id: str
    ) -> HTTPIterator:
        """List the tables in a dataset.

        Args:
            dataset_id: The dataset to list tables from.

        Returns:
            An iterator over the dataset's ``TableListItem`` objects.

        Raises:
            ValueError: If ``dataset_id`` is empty.
            GoogleAPIError: If the tables cannot be listed.
        """
        if not dataset_id:
            raise ValueError("Dataset ID cannot be empty")

        try:
            return self.client.list_tables(dataset_id)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list tables: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def create_dataset(
        self,
        dataset_id: str
    ) -> Dataset:
        """Create a new dataset in the client's project.

        Args:
            dataset_id: The ID to create the dataset under.

        Returns:
            The created ``Dataset``.

        Raises:
            ValueError: If ``dataset_id`` is empty.
            GoogleAPIError: If the dataset cannot be created.
        """
        if not dataset_id:
            raise ValueError("Dataset ID cannot be empty")

        try:
            return self.client.create_dataset(dataset_id)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create dataset: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def insert_rows_json(
        self,
        dataset_id: str,
        table_id: str,
        rows: list[dict]
    ) -> None:
        """Stream-insert rows into a table without a load job.

        Unlike other BigQuery client methods, ``insert_rows_json`` does not
        raise on a failed row insert -- it returns a list of per-row error
        dicts instead (an empty list means every row succeeded). This method
        checks that return value and raises ``GoogleAPIError`` if any row
        failed, so callers can rely on the usual raise-on-failure contract.

        Args:
            dataset_id: The dataset containing the table.
            table_id: The table to insert rows into.
            rows: The rows to insert, as JSON-serializable dicts.

        Raises:
            ValueError: If ``dataset_id``, ``table_id``, or ``rows`` is
                empty.
            GoogleAPIError: If the request fails outright, or if one or
                more rows are rejected.
        """
        if not dataset_id:
            raise ValueError("Dataset ID cannot be empty")

        if not table_id:
            raise ValueError("Table ID cannot be empty")

        if not rows:
            raise ValueError("Rows cannot be empty")

        try:
            table_ref = f"{self.client.project}.{dataset_id}.{table_id}"
            errors = self.client.insert_rows_json(table=table_ref, json_rows=rows)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to insert rows: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

        if errors:
            raise GoogleAPIError(
                f"Failed to insert rows: {errors}",
                status_code=None,
                reason=str(errors),
            )
