import uuid
import json
import moto
import boto3

from notifications_delivery.job.jobs import (
    process_jobs,
    get_numbers
)

from notifications_delivery.clients.queue.aws_queue import get_messages


def test_process_jobs_gets_messages_from_queue(mock_get_messages, mock_post_notifications):
    process_jobs()
    mock_get_messages.assert_called_with('eu-west-1', 'notify-jobs-queue',
                                         message_attributes=['job_id', 'service_id', 'template_id', 'bucket_name'])


@moto.mock_sqs
def test_process_job_gets_file_from_s3(mock_get_file_from_s3, mock_post_notifications):
    job = setup_job_mock_queue()
    process_jobs()
    bucket_name = 'service-{}-notify'.format(job['service_id'])
    mock_get_file_from_s3.assert_called_with(bucket_name, job['job_id'])


@moto.mock_sqs
def test_process_job_gets_job_messages(mock_post_notifications):
    job = setup_job_mock_queue()
    messages = get_messages('eu-west-1',
                            'notify-jobs-queue',
                            message_attributes=['job_id', 'service_id', 'template_id', 'bucket_name'])
    assert len(messages) == 1
    message = messages[0]
    assert message.body == json.dumps(job)


@moto.mock_sqs
def test_process_job_posts_notification(app_, mock_get_file_from_s3, mock_post_notifications):
    job = setup_job_mock_queue()
    file_contents = mock_get_file_from_s3.side_effect(job['bucket_name'], job['job_id'])
    template_id = job['template_id']
    numbers = get_numbers(file_contents)

    with app_.test_request_context():

        process_jobs()

        from unittest.mock import call
        calls = [call(number, template_id) for number in numbers]

        assert mock_post_notifications.call_count == 9
        mock_post_notifications.assert_has_calls(calls)


def setup_job_mock_queue():
    boto3.setup_default_session(region_name='eu-west-1')
    conn = boto3.resource('sqs')
    q = conn.create_queue(QueueName='notify-jobs-queue')

    job_id = str(uuid.uuid4())
    service_id = str(uuid.uuid4())
    template_id = "1"
    bucket_name = 'service-{}-notify'.format(service_id)

    job = {"job_id": job_id,  "service_id": service_id, "template_id": template_id, "bucket_name": bucket_name}
    job_json = json.dumps(job)
    q.send_message(MessageBody=job_json,
                   MessageAttributes={'job_id': {'StringValue': job_id, 'DataType': 'String'},
                                      'service_id': {'StringValue': service_id, 'DataType': 'String'},
                                      'template_id': {'StringValue': template_id, 'DataType': 'String'},
                                      'bucket_name': {'StringValue': bucket_name, 'DataType': 'String'}})

    return job
