import os

from notifications_delivery.clients.queue.aws_queue import get_messages
from notifications_delivery.clients.s3.aws_s3 import get_csv_from_s3

from notifications_delivery.app import create_app
from notifications_delivery.app import api_client


def process_jobs():
    application = create_app(os.getenv('NOTIFY_API_ENVIRONMENT', 'development'))
    with application.app_context():
        region = application.config['AWS_REGION']
        queue_name = application.config['NOTIFY_JOB_QUEUE']

        try:
            messages = get_messages(region,
                                    queue_name,
                                    message_attributes=['job_id', 'service_id', 'template_id', 'bucket_name'])
            for message in messages:
                bucket_name = message.message_attributes.get('bucket_name').get('StringValue')
                job_id = message.message_attributes.get('job_id').get('StringValue')
                template_id = message.message_attributes.get('template_id').get('StringValue')

                process_job(bucket_name, job_id, template_id)
                message.delete()

        except Exception as e:
            # TODO log errors and report to api
            print(e)


def process_job(bucket_name, job_id, template_id):
    upload_file_data = get_csv_from_s3(bucket_name, job_id)
    numbers = get_numbers(upload_file_data)
    for number in numbers:
        try:
            api_client.send_sms(number, template_id)
        except Exception as e:
            print(e)

        # TODO report progress, errors and outcome of job to api


def get_numbers(upload_file_data):
    lines = upload_file_data.split('\n')
    lines = [line.replace(' ', '') for line in lines if line and line != 'phone']
    return lines
