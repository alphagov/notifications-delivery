import moto
import boto
from notifications_delivery.processor.sqs_processor import process_all_queues


@moto.mock_sqs
def test_process_message_from_queue(mocker,
                                    delivery_config,
                                    ):
    queue = _populate_queue_with_one_message(mocker)
    assert queue.count() == 1
    process_all_queues(delivery_config)
    assert queue.count() == 0


@moto.mock_sqs
def test_empty_queue(mocker,
                     delivery_config):
    queue = _create_queue_no_messages(mocker)
    assert queue.count() == 0
    process_all_queues(delivery_config)
    assert queue.count() == 0


def _create_queue_no_messages(mocker, queue_name='test-queue'):
    # TODO why doesn't this work in pytest fixtures?
    sqs_resource = boto.connect_sqs('the_key', 'the_secret')
    sqs_resource.create_queue(queue_name, visibility_timeout=60)
    queue = sqs_resource.get_queue(queue_name)
    queue.wait_time_seconds = 10

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60):
        return sqs_resource.receive_message(
            queue, number_messages=MaxNumberOfMessages)

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


def _populate_queue_with_one_message(mocker, queue_name='test-queue', test_message="Test Message"):
    # TODO why doesn't this work in pytest fixtures?
    sqs_resource = boto.connect_sqs('the_key', 'the_secret')
    sqs_resource.create_queue(queue_name, visibility_timeout=60)
    queue = sqs_resource.get_queue(queue_name)
    queue.wait_time_seconds = 10

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60):
        return sqs_resource.receive_message(
            queue, number_messages=MaxNumberOfMessages)

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    msg = queue.new_message(test_message)
    setattr(msg, 'message_id', msg.id)
    queue.write(msg)
    return queue
