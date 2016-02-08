from apscheduler.schedulers.background import BackgroundScheduler

from notifications_delivery.job.jobs import process_jobs
from notifications_delivery.processor.sqs_processor import process_notification_job


class JobScheduler(object):

    def __init__(self, interval_seconds=60):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(process_jobs, 'interval', seconds=interval_seconds, max_instances=1)
        self.scheduler.add_job(process_notification_job, 'interval', seconds=interval_seconds, max_instances=1)

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown(wait=True)
