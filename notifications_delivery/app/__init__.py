import os

from flask import Flask
from utils import logging

from notifications_delivery.clients.notify_client.api_client import ApiClient

api_client = ApiClient()


def create_app():
    application = Flask(__name__)

    application.config.from_object(os.environ['NOTIFY_DELIVERY_ENVIRONMENT'])
    logging.init_app(application)

    from notifications_delivery.app.main.views import main as main_blueprint
    application.register_blueprint(main_blueprint)

    from notifications_delivery.app.status.rest import status as status_blueprint
    application.register_blueprint(status_blueprint)

    register_error_handlers(application)

    api_client.init_app(application)

    init_scheduler(application)

    return application


def register_error_handlers(application):
    import notifications_delivery.app.errors as errors
    application.errorhandler(400)(errors.bad_request)
    application.errorhandler(404)(errors.not_found)
    application.errorhandler(500)(errors.internal_server_error)


def init_scheduler(application):
    import atexit
    from notifications_delivery.job.job_scheduler import JobScheduler
    scheduler = JobScheduler(application.config)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
