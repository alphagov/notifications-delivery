import os
import json
import csv

from notifications_python_client.errors import HTTPError

from notifications_delivery.clients.queue.aws_queue import get_messages
from notifications_delivery.clients.s3.aws_s3 import get_csv_from_s3

from notifications_delivery.app import create_app
from notifications_delivery.app import api_client


def process_jobs():
    app = create_app(os.getenv('NOTIFICATIONS_DELIVERY_ENVIRONMENT', 'development'))
    with app.app_context():
        region = app.config['AWS_REGION']
        queue_name = app.config['NOTIFY_JOB_QUEUE']
        try:
            messages = get_messages(region,
                                    queue_name,
                                    message_attributes=['id', 'service', 'template', 'bucket_name'])
            for message in messages:
                bucket_name = message.message_attributes.get('bucket_name').get('StringValue')
                service_id = message.message_attributes.get('service').get('StringValue')
                template_id = message.message_attributes.get('template').get('StringValue')
                job_id = message.message_attributes.get('id').get('StringValue')

                update_job_status(message, 'in progress')

                errors = process_job(bucket_name, service_id, template_id, job_id)
                for error in errors:
                    # TODO - don't log errored numbers but report to api instead
                    err_msg = 'errored number {}'.format(error)
                    app.logger.error(err_msg)

                update_job_status(message, 'finished')
                message.delete()

        except Exception as e:
            # TODO log errors and report to api
            app.logger.error(e)


def process_job(bucket_name, service_id, template_id, job_id):
    app = create_app(os.getenv('NOTIFICATIONS_DELIVERY_ENVIRONMENT', 'development'))
    with app.app_context():
        upload_file_data = get_csv_from_s3(bucket_name, job_id)
        numbers = get_numbers(upload_file_data)
        errors = []
        # TODO report progress?
        for number in numbers:
            try:
                api_client.send_sms(number, service_id, template_id, job_id)
            except HTTPError as e:
                app.logger.error(e.message)
            except Exception as e:
                errors.append(number)
                app.logger.error(e)

        return errors


def update_job_status(message, status):
    app = create_app(os.getenv('NOTIFICATIONS_DELIVERY_ENVIRONMENT', 'development'))
    with app.app_context():
        try:
            job = json.loads(message.body)
            job['status'] = status
            api_client.update_job(job)
        except HTTPError as e:
            app.logger.error(e.message)
        except Exception as e:
            app.logger.error(e)


def get_numbers(upload_file_data):
    numbers = []
    reader = csv.DictReader(
        upload_file_data.splitlines(),
        lineterminator='\n',
        quoting=csv.QUOTE_NONE)
    for i, row in enumerate(reader):
        numbers.append(row['phone'].replace(' ', ''))
    return numbers
