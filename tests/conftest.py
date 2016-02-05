import pytest
import boto3
import boto
import moto

from botocore.exceptions import ClientError
from botocore.parsers import ResponseParserError
from flask import jsonify

from notifications_delivery.app import create_app


@pytest.fixture(scope='session')
def app_(request):
    app = create_app('test')

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


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
        'AWS_REGION': 'eu-west-1',
        'NOTIFICATION_QUEUE_PREFIX': 'notification'
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


@pytest.fixture(scope='function')
def mock_get_messages(mocker):

    def _get_messages(region, queue_name, **kwargs):
        return []

    return mocker.patch('notifications_delivery.job.jobs.get_messages', side_effect=_get_messages)


@pytest.fixture(scope='function')
def mock_get_file_from_s3(mocker):
    contents = 'phone\n+44 7700 900981\n+44 7700 900982\n+44 7700 900983\n+44 7700 900984\n+44 7700 900985\n+44 7700 900986\n+44 7700 900987\n+44 7700 900988\n+44 7700 900989'  # noqa

    def _get_file_from_s3(bucket_name, upload_id):
        return contents

    return mocker.patch('notifications_delivery.job.jobs.get_csv_from_s3', side_effect=_get_file_from_s3)


@pytest.fixture(scope='function')
def mock_post_notifications(mocker):
    def _send_sms(application, number, template_id):
        return jsonify({}), 200
    return mocker.patch('notifications_delivery.job.jobs.api_client.send_sms', side_effect=_send_sms)
