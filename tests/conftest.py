import pytest
import boto3
import boto
import moto

from botocore.exceptions import ClientError
from botocore.parsers import ResponseParserError
from flask import jsonify
from tests import (
    create_sqs_connection, create_sqs_resource, create_queue,
    create_email_notification, create_sms_content_notification,
    create_message, create_sms_template_notification, create_sms_job_notification)
from notifications_delivery.processor.sqs_processor import (
    ProcessingError, ExternalConnectionError)

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
def ses_client(region_name='eu-west-1'):
    return boto3.client('ses',
                        region_name=region_name,
                        aws_access_key_id='sample_key',
                        aws_secret_access_key='sample_secret')


@pytest.fixture(scope='function')
def sqs_client(region_name='eu-west-1'):
    return boto3.client('sqs',
                        region_name=region_name,
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
        'NOTIFICATION_QUEUE_PREFIX': 'notification',
        'NOTIFY_DATA_API_URL': '',
        'NOTIFY_DATA_API_AUTH_TOKEN': '',
        'API_HOST_NAME': '',
        'DELIVERY_CLIENT_USER_NAME': '',
        'DELIVERY_CLIENT_SECRET': '',
        'NOTIFICATION_ATTRIBUTES': ['type', 'message_id', 'service_id', 'template_id'],
        'SECRET_KEY': 'secret-key',
        'DANGEROUS_SALT': 'dangerous-salt',
        'TWILIO_ACCOUNT_SID': 'ACCOUNT_ID',
        'TWILIO_AUTH_TOKEN': 'AUTH_TOKEN'
    }


@pytest.fixture(scope='function')
def mock_get_all_queues_return_one(mocker, sqs_queue):

    def _get(config, queue_name_prefix=''):
        return [sqs_queue]
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)


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
    def _send_sms(number, service_id, template_id, job_id):
        return jsonify({}), 200
    return mocker.patch('notifications_delivery.job.jobs.api_client.send_sms', side_effect=_send_sms)


@pytest.fixture(scope='function')
def mock_alpha_send_sms(mocker):

    def _send_sms(to, content):
        return {'something': 'something'}
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.NotifyAPIClient.send_sms',
        side_effect=_send_sms)


@pytest.fixture(scope='function')
def mock_alpha_send_sms_processing_error(mocker):

    def _send_sms(to, content):
        raise ProcessingError("processing error")
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.NotifyAPIClient.send_sms',
        side_effect=_send_sms)


@pytest.fixture(scope='function')
def mock_alpha_send_sms_http_503(mocker):

    def _send_sms(to, content):
        raise ExternalConnectionError("processing error")
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.NotifyAPIClient.send_sms',
        side_effect=_send_sms)


@pytest.fixture(scope='function')
def mock_alpha_send_email(mocker):

    def _send_email(to, body, from_, subject):
        return {'something': 'something'}
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.NotifyAPIClient.send_email',
        side_effect=_send_email)


@pytest.fixture(scope='function')
def mock_beta_get_template(mocker):

    def _get_template(service_id, template_id):
        return {
            'id': template_id,
            'name': "Template name",
            'template_type': 'sms',
            'content': "Sample Template content",
            'service': service_id
        }
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.ApiClient.get_template',
        side_effect=_get_template)


@pytest.fixture(scope='function')
def mock_beta_create_notification(mocker):
    def _create_notification(service_id, template_id, job_id, to, status):
        return {
            'id': 123,
            'service': service_id,
            'template': template_id,
            'job': job_id,
            'to': to,
            'status': status
        }
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.ApiClient.create_notification',
        side_effect=_create_notification)


@pytest.fixture(scope='function')
def mock_twilio_create(mocker):
    def _create(body=None, to=None, from_=None):
        return "123"
    return mocker.patch(
        'notifications_delivery.sms.twilio.TwilioRestClient.messages.create',
        side_effect=_create)


@pytest.fixture(scope='function')
def create_queue_no_msgs(mocker, delivery_config, queue_name='test-queue'):
    boto3.setup_default_session(region_name=delivery_config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    queue = create_queue(sqs_connection, queue_name)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return []

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def populate_queue_with_sms_content_msg(mocker, delivery_config, queue_name='test-queue'):
    boto3.setup_default_session(region_name=delivery_config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(delivery_config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    notification = create_sms_content_notification()
    msg = create_message(delivery_config, sqs_resource, queue, "sms", notification)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return [msg]

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def populate_queue_with_sms_template_msg(mocker, delivery_config, queue_name='test-queue'):
    boto3.setup_default_session(region_name=delivery_config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(delivery_config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    notification = create_sms_template_notification()
    msg = create_message(delivery_config, sqs_resource, queue, "sms", notification)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return [msg]

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def populate_queue_with_sms_job_msg(mocker, delivery_config, queue_name='test-queue'):
    boto3.setup_default_session(region_name=delivery_config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(delivery_config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    notification = create_sms_job_notification()
    msg = create_message(delivery_config, sqs_resource, queue, "sms", notification)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return [msg]

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def populate_queue_with_email_msg(mocker, delivery_config, queue_name='test-queue'):
    boto3.setup_default_session(region_name=delivery_config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(delivery_config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    notification = create_email_notification()
    msg = create_message(delivery_config, sqs_resource, queue, "email", notification)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return [msg]

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def mock_update_job(mocker):
    def _update_job(job):
        return jsonify({}), 200
    return mocker.patch('notifications_delivery.job.jobs.api_client.update_job', side_effect=_update_job)
