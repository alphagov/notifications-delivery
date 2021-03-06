import pytest
import boto3
import boto
import moto
from unittest.mock import (Mock, patch)

from botocore.exceptions import ClientError
from botocore.parsers import ResponseParserError
from flask import jsonify
from tests import (
    create_sqs_connection, create_sqs_resource, create_queue, create_message)
from notifications_delivery.processor.sqs_processor import (
    ProcessingError, ExternalConnectionError)

from notifications_delivery.app import create_app


@pytest.fixture(scope='session')
def app_(request):
    app = create_app()

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
def sms_template_notification(to=None, template=None, id_=None):
    if to is None:
        to = "447700900986"
    if template is None:
        template = "1234"
    if id_ is None:
        id_ = '123'
    return {'to': to, 'template': template, 'id': id_}


@pytest.fixture(scope='function')
def sms_job_notification(to=None, template=None, job=None, id_=None):
    if to is None:
        to = "447700900986"
    if template is None:
        template = "1234"
    if job is None:
        job = '4567'
    if id_ is None:
        id_ = '123'
    return {'to': to, 'template': template, 'job': job, 'id': id_}


@pytest.fixture(scope='function')
def sms_content_notification(to=None, content=None, id_=None):
    if to is None:
        to = "447700900986"
    if content is None:
        content = "Test content"
    if id_ is None:
        id_ = '123'
    return {'to': to, 'content': content, 'id': id_}


@pytest.fixture(scope='function')
def email_notification(to=None, body=None, from_=None, subject=None, id_=None):
    if to is None:
        to = "test@digital.cabinet-office.gov.uk"
    if body is None:
        body = "<Insert email content here>"
    if from_ is None:
        from_ = "notify@digital.cabinet-office.gov.uk"
    if subject is None:
        subject = "Email subject"
    return {
        'to_address': to,
        'from_address': from_,
        'body': body,
        'subject': subject,
        'id': id_}


@pytest.fixture(scope='function')
def sms_content():
    return "sms content"


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
def mock_alpha_send_sms_http_503(mocker):

    def _send_sms(to, content):
        raise ExternalConnectionError("processing error")
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.NotifyAPIClient.send_sms',
        side_effect=_send_sms)


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
def mock_ses_send_email(mocker):
    def _send_email(from_, to_, subject, body):
        return None
    return mocker.patch(
        'notifications_delivery.processor.sqs_processor.AwsSesClient.send_email',
        side_effect=_send_email)


@pytest.fixture(scope='function')
def mock_beta_create_notification(mocker):
    def _create_notification(service_id, template_id, job_id, to, status, notification_id):
        return {
            'id': notification_id,
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
        return Mock(sid="123")
    create_mock = Mock(**{'create.side_effect': _create})
    msgs_mock = Mock(messages=create_mock)
    cls_mock = patch(
        'notifications_delivery.clients.sms.twilio.TwilioRestClient',
        messages=msgs_mock)
    return cls_mock


@pytest.fixture(scope='function')
def mock_twilio_create_exception(mocker):
    def _except(body=None, to=None, from_=None):
        from notifications_delivery.clients.sms.twilio import TwilioRestException
        raise TwilioRestException("http://www.google.com", "Exception")
    create_mock = Mock(**{'create.side_effect': _except})
    msgs_mock = Mock(messages=create_mock)
    cls_mock = patch(
        'notifications_delivery.clients.sms.twilio.TwilioRestClient',
        return_value=msgs_mock)
    return cls_mock


@pytest.fixture(scope='function')
def mock_twilio_get(mocker):
    def _get(message_id):
        return Mock(status='delivered')
    get_mock = Mock(**{'get.side_effect': _get})
    msgs_mock = Mock(messages=get_mock)
    cls_mock = patch(
        'notifications_delivery.clients.sms.twilio.TwilioRestClient',
        return_value=msgs_mock)
    return cls_mock


@pytest.fixture(scope='function')
def mock_twilio_get_exception(mocker):
    def _except(message_id):
        from notifications_delivery.clients.sms.twilio import TwilioRestException
        raise TwilioRestException("http://www.google.com", "Exception")
    get_mock = Mock(**{'get.side_effect': _except})
    msgs_mock = Mock(messages=get_mock)
    cls_mock = patch(
        'notifications_delivery.clients.sms.twilio.TwilioRestClient',
        return_value=msgs_mock)
    return cls_mock


@pytest.fixture(scope='function')
def create_queue_no_msgs(mocker, app_, queue_name='test-queue'):
    boto3.setup_default_session(region_name=app_.config['AWS_REGION'])
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
def populate_queue_with_sms_content_msg(mocker,
                                        app_,
                                        sms_content_notification,
                                        queue_name='test-queue'):
    boto3.setup_default_session(region_name=app_.config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(app_.config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    msg = create_message(app_.config, sqs_resource, queue, "sms", sms_content_notification)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return [msg]

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def populate_queue_with_sms_template_msg(mocker,
                                         app_,
                                         sms_template_notification,
                                         queue_name='test-queue'):
    boto3.setup_default_session(region_name=app_.config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(app_.config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    msg = create_message(app_.config, sqs_resource, queue, "sms", sms_template_notification)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return [msg]

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def populate_queue_with_sms_job_msg(mocker,
                                    app_,
                                    sms_job_notification,
                                    queue_name='test-queue'):
    boto3.setup_default_session(region_name=app_.config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(app_.config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    msg = create_message(app_.config, sqs_resource, queue, "sms", sms_job_notification)

    def _receive(MaxNumberOfMessages=1, VisibilityTimeout=60, MessageAttributeNames=[]):
        return [msg]

    setattr(queue, 'receive_messages', _receive)

    def _get(config, queue_name_prefix=''):
        return [queue]

    mocker.patch(
        'notifications_delivery.processor.sqs_processor._get_all_queues', side_effect=_get)
    return queue


@pytest.fixture(scope='function')
def populate_queue_with_email_msg(mocker,
                                  app_,
                                  email_notification,
                                  queue_name='test-queue'):
    boto3.setup_default_session(region_name=app_.config['AWS_REGION'])
    sqs_connection = create_sqs_connection()
    sqs_resource = create_sqs_resource(app_.config['AWS_REGION'])
    queue = create_queue(sqs_connection, queue_name)
    msg = create_message(app_.config, sqs_resource, queue, "email", email_notification)

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
