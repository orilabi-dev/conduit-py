from unittest.mock import MagicMock, patch

import pytest
from google.api_core.exceptions import NotFound

from conduit_py.google.cloud.pubsub.service import PubSubService
from conduit_py.google.exceptions import GoogleAPIError


def _make_service() -> tuple[PubSubService, MagicMock, MagicMock]:
    with patch("conduit_py.google.cloud.pubsub.service.PublisherClient") as mock_pub_cls, patch(
        "conduit_py.google.cloud.pubsub.service.SubscriberClient"
    ) as mock_sub_cls:
        mock_publisher = MagicMock()
        mock_subscriber = MagicMock()
        mock_pub_cls.return_value = mock_publisher
        mock_sub_cls.return_value = mock_subscriber
        mock_publisher.topic_path.side_effect = (
            lambda project, topic: f"projects/{project}/topics/{topic}"
        )
        mock_subscriber.subscription_path.side_effect = (
            lambda project, sub: f"projects/{project}/subscriptions/{sub}"
        )
        service = PubSubService(credentials=MagicMock(), project_name="test-project")
    return service, mock_publisher, mock_subscriber


def test_init_builds_publisher_and_subscriber_with_credentials():
    credentials = MagicMock()
    with patch("conduit_py.google.cloud.pubsub.service.PublisherClient") as mock_pub_cls, patch(
        "conduit_py.google.cloud.pubsub.service.SubscriberClient"
    ) as mock_sub_cls:
        service = PubSubService(credentials=credentials, project_name="test-project")

    mock_pub_cls.assert_called_once_with(credentials=credentials)
    mock_sub_cls.assert_called_once_with(credentials=credentials)
    assert service.project_name == "test-project"


def test_create_topic_rejects_empty_topic_id():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_topic("")


def test_create_topic_calls_publisher_with_topic_path():
    service, mock_publisher, _ = _make_service()
    fake_topic = MagicMock(name="Topic")
    mock_publisher.create_topic.return_value = fake_topic

    result = service.create_topic("my-topic")

    mock_publisher.create_topic.assert_called_once_with(
        name="projects/test-project/topics/my-topic"
    )
    assert result is fake_topic


def test_create_topic_wraps_api_call_error():
    service, mock_publisher, _ = _make_service()
    mock_publisher.create_topic.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_topic("my-topic")

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_list_topics_calls_publisher_with_project_path():
    service, mock_publisher, _ = _make_service()
    mock_publisher.list_topics.return_value = ["topic1", "topic2"]

    result = service.list_topics()

    mock_publisher.list_topics.assert_called_once_with(project="projects/test-project")
    assert result == ["topic1", "topic2"]


def test_list_topics_wraps_api_call_error():
    service, mock_publisher, _ = _make_service()
    mock_publisher.list_topics.side_effect = NotFound("project not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.list_topics()

    assert exc_info.value.status_code == 404
    assert "project not found" in exc_info.value.reason


def test_publish_message_rejects_empty_topic_id():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.publish_message("", "data")


def test_publish_message_rejects_empty_data():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.publish_message("my-topic", "")


def test_publish_message_encodes_str_data_and_returns_message_id():
    service, mock_publisher, _ = _make_service()
    mock_future = MagicMock()
    mock_future.result.return_value = "message-id-123"
    mock_publisher.publish.return_value = mock_future

    result = service.publish_message("my-topic", "hello world")

    mock_publisher.publish.assert_called_once_with(
        "projects/test-project/topics/my-topic", b"hello world"
    )
    assert result == "message-id-123"


def test_publish_message_passes_bytes_data_through_unchanged():
    service, mock_publisher, _ = _make_service()
    mock_future = MagicMock()
    mock_future.result.return_value = "message-id-123"
    mock_publisher.publish.return_value = mock_future

    service.publish_message("my-topic", b"raw-bytes")

    args, _ = mock_publisher.publish.call_args
    assert args[1] == b"raw-bytes"


def test_publish_message_wraps_api_call_error_from_future_result():
    service, mock_publisher, _ = _make_service()
    mock_future = MagicMock()
    mock_future.result.side_effect = NotFound("topic not found")
    mock_publisher.publish.return_value = mock_future

    with pytest.raises(GoogleAPIError) as exc_info:
        service.publish_message("my-topic", "data")

    assert exc_info.value.status_code == 404
    assert "topic not found" in exc_info.value.reason


def test_create_subscription_rejects_empty_topic_id():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_subscription("", "my-sub")


def test_create_subscription_rejects_empty_subscription_id():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.create_subscription("my-topic", "")


def test_create_subscription_calls_subscriber_with_expected_paths():
    service, _, mock_subscriber = _make_service()
    fake_subscription = MagicMock(name="Subscription")
    mock_subscriber.create_subscription.return_value = fake_subscription

    result = service.create_subscription("my-topic", "my-sub")

    mock_subscriber.create_subscription.assert_called_once_with(
        name="projects/test-project/subscriptions/my-sub",
        topic="projects/test-project/topics/my-topic",
    )
    assert result is fake_subscription


def test_create_subscription_wraps_api_call_error():
    service, _, mock_subscriber = _make_service()
    mock_subscriber.create_subscription.side_effect = NotFound("topic not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.create_subscription("my-topic", "my-sub")

    assert exc_info.value.status_code == 404
    assert "topic not found" in exc_info.value.reason


def test_pull_messages_rejects_empty_subscription_id():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.pull_messages("")


def test_pull_messages_calls_subscriber_with_subscription_and_max_messages():
    service, _, mock_subscriber = _make_service()
    fake_response = MagicMock(name="PullResponse")
    mock_subscriber.pull.return_value = fake_response

    result = service.pull_messages("my-sub", max_messages=5)

    mock_subscriber.pull.assert_called_once_with(
        subscription="projects/test-project/subscriptions/my-sub",
        max_messages=5,
    )
    assert result is fake_response


def test_pull_messages_defaults_max_messages_to_ten():
    service, _, mock_subscriber = _make_service()
    mock_subscriber.pull.return_value = MagicMock()

    service.pull_messages("my-sub")

    _, kwargs = mock_subscriber.pull.call_args
    assert kwargs["max_messages"] == 10


def test_pull_messages_wraps_api_call_error():
    service, _, mock_subscriber = _make_service()
    mock_subscriber.pull.side_effect = NotFound("subscription not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.pull_messages("my-sub")

    assert exc_info.value.status_code == 404
    assert "subscription not found" in exc_info.value.reason


def test_acknowledge_messages_rejects_empty_subscription_id():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.acknowledge_messages("", ["ack1"])


def test_acknowledge_messages_rejects_empty_ack_ids():
    service, _, _ = _make_service()

    with pytest.raises(ValueError):
        service.acknowledge_messages("my-sub", [])


def test_acknowledge_messages_calls_subscriber_with_subscription_and_ack_ids():
    service, _, mock_subscriber = _make_service()

    result = service.acknowledge_messages("my-sub", ["ack1", "ack2"])

    mock_subscriber.acknowledge.assert_called_once_with(
        subscription="projects/test-project/subscriptions/my-sub",
        ack_ids=["ack1", "ack2"],
    )
    assert result is None


def test_acknowledge_messages_wraps_api_call_error():
    service, _, mock_subscriber = _make_service()
    mock_subscriber.acknowledge.side_effect = NotFound("subscription not found")

    with pytest.raises(GoogleAPIError) as exc_info:
        service.acknowledge_messages("my-sub", ["ack1"])

    assert exc_info.value.status_code == 404
    assert "subscription not found" in exc_info.value.reason
