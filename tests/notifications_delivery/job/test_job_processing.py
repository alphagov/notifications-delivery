import uuid
import json
import moto
import boto3

from notifications_delivery.job.jobs import process_jobs
from notifications_delivery.clients.queue.aws_queue import get_messages


def test_process_jobs_gets_messages_from_queue(mock_get_messages):
    process_jobs()
    mock_get_messages.assert_called_with('eu-west-1', 'notify-jobs-queue', message_attributes=['job_id', 'service_id'])


@moto.mock_sqs
def test_process_jobs_gets_file_from_s3(mock_get_file_from_s3):
    job = setup_job_mock_queue()
    process_jobs()
    mock_get_file_from_s3.assert_called_with(job['service_id'], job['job_id'])


@moto.mock_sqs
def test_process_job_gets_job_messages():
    job = setup_job_mock_queue()
    messages = get_messages('eu-west-1', 'notify-jobs-queue', message_attributes=['job_id', 'service_id'])
    assert len(messages) == 1
    message = messages[0]
    assert message.body == json.dumps(job)


def setup_job_mock_queue():
    boto3.setup_default_session(region_name='eu-west-1')
    conn = boto3.resource('sqs')
    q = conn.create_queue(QueueName='notify-jobs-queue')

    job = {"job_id": str(uuid.uuid4()),  "service_id": str(uuid.uuid4())}
    job_json = json.dumps(job)
    q.send_message(
        MessageBody=job_json,
        MessageAttributes={'job_id': {'StringValue': job['job_id'], 'DataType': 'String'},
                           'service_id': {'StringValue': job['service_id'], 'DataType': 'String'}})

    return job
