from notifications_delivery.clients.queue.aws_queue import get_messages
from notifications_delivery.clients.s3.aws_s3 import get_csv_from_s3

from config import Config

import boto3


def process_jobs():
    region = Config.AWS_REGION
    queue_name = Config.NOTIFY_JOB_QUEUE
    messages = get_messages(region, queue_name, message_attributes=['job_id', 'service_id'])
    for message in messages:
        try:
            upload_id = message.message_attributes.get('job_id').get('StringValue')
            service_id = message.message_attributes.get('service_id').get('StringValue')
            upload_file_data = get_csv_from_s3(service_id, upload_id)
            _process_csv_file(upload_file_data)
            # TODO message.delete()
        except Exception as e:
            print(e)


def _process_csv_file(upload_file_data):
    print('Process file contents:')
