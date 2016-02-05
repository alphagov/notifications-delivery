import pytest
import boto3
import boto
import moto

from botocore.exceptions import ClientError
from botocore.parsers import ResponseParserError


@pytest.fixture(scope='function')
def ses_client():
    return boto3.client('ses',
                        region_name='eu-west-1',
                        aws_access_key_id='sample_key',
                        aws_secret_access_key='sample_secret')


@pytest.fixture(scope='function')
def sqs_client():
    return boto3.client('sqs',
                        region_name='eu-west-1',
                        aws_access_key_id='sample_key',
                        aws_secret_access_key='sample_secret')


@moto.mock_sqs
@pytest.fixture(scope='function')
def sqs_resource():
    return boto.connect_sqs('the_key', 'the_secret')


@pytest.fixture(scope='function')
def delivery_config():
    return {
        'TURN_OFF_LOGGING': True,
        'DELIVERY_LOG_PATH': '',
        'DELIVERY_LOG_LEVEL': 'DEBUG',
        'PROCESSOR_MAX_NUMBER_OF_MESSGAES': 1,
        'PROCESSOR_VISIBILITY_TIMEOUT': 60,
        'AWS_REGION': 'eu-west-1'
    }


@moto.mock_sqs
@pytest.fixture(scope='function')
def sqs_queue(sqs_resource, queue_name='test-queue'):
    queue = sqs_resource.get_queue(queue_name)
    if not queue:
        sqs_resource.create_queue(queue_name, visibility_timeout=60)
        queue = sqs_resource.get_queue(queue_name)

        def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60):
            return sqs_resource.receive_message(
                queue, number_messages=MaxNumberOfMessages)
        setattr(queue, 'receive_messages', _receive)
    # Why do we need to do this??
    queue.wait_time_seconds = 10
    return queue


@pytest.fixture(scope='function')
def mock_get_all_queues_return_one(mocker, sqs_queue):
    def _get(config, queue_name_prefix=''):
        return [sqs_queue]
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)


@moto.mock_sqs
@pytest.fixture(scope='function')
def populate_queue(sqs_resource, queue=None, message="Test Message"):
    if queue is None:
        queue = sqs_queue(sqs_resource)
    msg = queue.new_message(message)
    queue.write(msg)
    return msg  # queue.send_message(MessageBody=message)['MessageId']
