import os

from flask._compat import string_types
from flask import Flask
from config import configs
from utils import logging

from notifications_delivery.clients.notify_client.api_client import ApiClient

api_client = ApiClient()


def create_app(config_name, config_overrides=None):
    application = Flask(__name__)

    application.config['NOTIFICATIONS_DELIVERY_ENVIRONMENT'] = config_name
    application.config.from_object(configs[config_name])

    init_app(application, config_overrides)

    logging.init_app(application)

    from notifications_delivery.app.main.views import main as main_blueprint
    application.register_blueprint(main_blueprint)

    from notifications_delivery.app.status.rest import status as status_blueprint
    application.register_blueprint(status_blueprint)

    register_error_handlers(application)

    api_client.init_app(application)

    init_scheduler(application)

    return application


def init_app(app, config_overrides=None):
    for key, value in app.config.items():
        if key in os.environ:
            app.config[key] = convert_to_boolean(os.environ[key])

    if config_overrides:
        for key in app.config.keys():
            if key in config_overrides:
                app.config[key] = config_overrides[key]


def convert_to_boolean(value):
    """Turn strings to bools if they look like them

    Truthy things should be True
    >>> for truthy in ['true', 'on', 'yes', '1']:
    ...   assert convert_to_boolean(truthy) == True

    Falsey things should be False
    >>> for falsey in ['false', 'off', 'no', '0']:
    ...   assert convert_to_boolean(falsey) == False

    Other things should be unchanged
    >>> for value in ['falsey', 'other', True, 0]:
    ...   assert convert_to_boolean(value) == value
    """
    if isinstance(value, string_types):
        if value.lower() in ['t', 'true', 'on', 'yes', '1']:
            return True
        elif value.lower() in ['f', 'false', 'off', 'no', '0']:
            return False

    return value


def convert_to_number(value):
    """Turns numeric looking things into floats or ints

    Integery things should be integers
    >>> for inty in ['0', '1', '2', '99999']:
    ...   assert isinstance(convert_to_number(inty), int)

    Floaty things should be floats
    >>> for floaty in ['0.99', '1.1', '1000.0000001']:
    ...   assert isinstance(convert_to_number(floaty), float)

    Other things should be unchanged
    >>> for value in [0, 'other', True, 123]:
    ...   assert convert_to_number(value) == value
    """
    try:
        return float(value) if "." in value else int(value)
    except (TypeError, ValueError):
        return value


def register_error_handlers(application):
    import notifications_delivery.app.errors as errors
    application.errorhandler(400)(errors.bad_request)
    application.errorhandler(404)(errors.not_found)
    application.errorhandler(500)(errors.internal_server_error)


def init_scheduler(application):
    import atexit
    from notifications_delivery.job.job_scheduler import JobScheduler
    interval_seconds = application.config['JOB_POLL_INTERVAL_SECONDS']
    scheduler = JobScheduler(application.config, interval_seconds=interval_seconds)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
