import pytest
import boto3

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


@pytest.fixture(scope='session')
def aws_client():
    return boto3.client('ses',
                        region_name='eu-west-1',
                        aws_access_key_id='sample_key',
                        aws_secret_access_key='sample_key')


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
