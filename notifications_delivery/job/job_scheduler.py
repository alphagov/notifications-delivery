from apscheduler.schedulers.background import BackgroundScheduler

from notifications_delivery.job.jobs import process_jobs
from notifications_delivery.processor.sqs_processor import process_notification_job


class JobScheduler(object):

    def __init__(self, config):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.job_process,
            'interval',
            seconds=config['JOB_POLL_INTERVAL_SECONDS'],
            max_instances=1)
        self.scheduler.add_job(
            self.notification_job_process,
            'interval',
            seconds=config['DELIVERY_POLL_INTERVAL_SECONDS'],
            max_instances=1)
        self.config = config

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=True)

    def job_process(self):
        process_jobs(self.config)

    def notification_job_process(self):
        process_notification_job(self.config)
