"""Google Cloud Pub/Sub API service wrapper."""

from google.api_core.exceptions import GoogleAPICallError
from google.auth.credentials import Credentials
from google.cloud.pubsub_v1 import PublisherClient, SubscriberClient
from google.cloud.pubsub_v1.types import Subscription, Topic
from google.pubsub_v1.services.publisher.pagers import ListTopicsPager
from google.pubsub_v1.types import PullResponse

from conduit_py.google.exceptions import GoogleAPIError


class PubSubService:
    """Publishes and consumes messages using a publisher and subscriber
    client for a single GCP project.

    Args:
        credentials: Authenticated Google credentials with Pub/Sub access.
        project_name: The GCP project topics and subscriptions belong to.
    """

    def __init__(
        self,
        credentials: Credentials,
        project_name: str
    ):
        self.project_name = project_name
        self.publisher = PublisherClient(credentials=credentials)
        self.subscriber = SubscriberClient(credentials=credentials)

    def create_topic(
        self,
        topic_id: str
    ) -> Topic:
        """Create a new topic in the client's project.

        Args:
            topic_id: The ID to create the topic under.

        Returns:
            The created ``Topic``.

        Raises:
            ValueError: If ``topic_id`` is empty.
            GoogleAPIError: If the topic cannot be created.
        """
        if not topic_id:
            raise ValueError("Topic ID cannot be empty")

        try:
            topic_path = self.publisher.topic_path(self.project_name, topic_id)
            return self.publisher.create_topic(name=topic_path)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create topic: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def list_topics(self) -> ListTopicsPager:
        """List the topics in the client's project.

        Returns:
            An iterator over the project's ``Topic`` objects.

        Raises:
            GoogleAPIError: If the topics cannot be listed.
        """
        try:
            project_path = f"projects/{self.project_name}"
            return self.publisher.list_topics(project=project_path)
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to list topics: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def publish_message(
        self,
        topic_id: str,
        data: str | bytes
    ) -> str:
        """Publish a message to a topic and wait for it to be accepted.

        Calls ``publisher.publish``, which returns a ``Future``; this
        method blocks on that future's result so callers get a plain
        message ID back (or a raised ``GoogleAPIError``) rather than
        having to manage the future themselves.

        Args:
            topic_id: The topic to publish to.
            data: The message payload. ``str`` values are UTF-8 encoded.

        Returns:
            The ID of the published message.

        Raises:
            ValueError: If ``topic_id`` or ``data`` is empty.
            GoogleAPIError: If the message cannot be published.
        """
        if not topic_id:
            raise ValueError("Topic ID cannot be empty")

        if not data:
            raise ValueError("Data cannot be empty")

        if isinstance(data, str):
            data = data.encode("utf-8")

        try:
            topic_path = self.publisher.topic_path(self.project_name, topic_id)
            future = self.publisher.publish(topic_path, data)
            return future.result()
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to publish message: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def create_subscription(
        self,
        topic_id: str,
        subscription_id: str
    ) -> Subscription:
        """Create a new pull subscription on an existing topic.

        Args:
            topic_id: The topic to subscribe to. Must already exist.
            subscription_id: The ID to create the subscription under.

        Returns:
            The created ``Subscription``.

        Raises:
            ValueError: If ``topic_id`` or ``subscription_id`` is empty.
            GoogleAPIError: If the subscription cannot be created.
        """
        if not topic_id:
            raise ValueError("Topic ID cannot be empty")

        if not subscription_id:
            raise ValueError("Subscription ID cannot be empty")

        try:
            topic_path = self.publisher.topic_path(self.project_name, topic_id)
            subscription_path = self.subscriber.subscription_path(
                self.project_name, subscription_id
            )
            return self.subscriber.create_subscription(
                name=subscription_path, topic=topic_path
            )
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to create subscription: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def pull_messages(
        self,
        subscription_id: str,
        max_messages: int = 10
    ) -> PullResponse:
        """Pull up to ``max_messages`` from a subscription.

        This does not acknowledge the pulled messages — call
        ``acknowledge_messages`` with each message's ``ack_id`` once
        you've finished processing it, or it will be redelivered after
        the subscription's ack deadline elapses.

        Args:
            subscription_id: The subscription to pull from.
            max_messages: Maximum number of messages to pull. Defaults
                to ``10``.

        Returns:
            A ``PullResponse`` whose ``received_messages`` list holds
            the pulled messages (each with ``.ack_id`` and
            ``.message.data``).

        Raises:
            ValueError: If ``subscription_id`` is empty.
            GoogleAPIError: If the pull request fails.
        """
        if not subscription_id:
            raise ValueError("Subscription ID cannot be empty")

        try:
            subscription_path = self.subscriber.subscription_path(
                self.project_name, subscription_id
            )
            return self.subscriber.pull(
                subscription=subscription_path, max_messages=max_messages
            )
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to pull messages: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error

    def acknowledge_messages(
        self,
        subscription_id: str,
        ack_ids: list[str]
    ) -> None:
        """Acknowledge messages so they aren't redelivered.

        Args:
            subscription_id: The subscription the messages were pulled
                from.
            ack_ids: The ``ack_id`` of each message to acknowledge (see
                ``pull_messages``).

        Raises:
            ValueError: If ``subscription_id`` or ``ack_ids`` is empty.
            GoogleAPIError: If the acknowledge request fails.
        """
        if not subscription_id:
            raise ValueError("Subscription ID cannot be empty")

        if not ack_ids:
            raise ValueError("Ack IDs cannot be empty")

        try:
            subscription_path = self.subscriber.subscription_path(
                self.project_name, subscription_id
            )
            self.subscriber.acknowledge(
                subscription=subscription_path, ack_ids=ack_ids
            )
        except GoogleAPICallError as error:
            raise GoogleAPIError(
                f"Failed to acknowledge messages: {error.message}",
                status_code=error.code,
                reason=error.message,
            ) from error
