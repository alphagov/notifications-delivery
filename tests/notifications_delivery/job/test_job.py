import uuid
import json
import moto
import boto3

from notifications_delivery.job.jobs import process_jobs


@moto.mock_sqs
def test_process_jobs(mock_get_file_from_s3):
    q = _setup_job_mock_queue()
    process_jobs()
    assert mock_get_file_from_s3.called


def _setup_job_mock_queue():
    boto3.setup_default_session(region_name='eu-west-1')
    conn = boto3.resource('sqs')
    q = conn.create_queue(QueueName='notify-jobs-queue')

    job = {"job_id": str(uuid.uuid4()),  "service_id": str(uuid.uuid4())}
    job_json = json.dumps(job)
    q.send_message(
        MessageBody=job_json,
        MessageAttributes={'job_id': {'StringValue': job['job_id'], 'DataType': 'String'},
                           'service_id': {'StringValue': job['service_id'], 'DataType': 'String'}})

    return q
