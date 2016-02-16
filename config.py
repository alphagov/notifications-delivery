import os


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    DANGEROUS_SALT = os.environ['DANGEROUS_SALT']
    NOTIFY_LOG_LEVEL = os.environ['NOTIFY_LOG_LEVEL']
    DELIVERY_LOG_LEVEL = os.environ['DELIVERY_LOG_LEVEL']
    API_HOST_NAME = os.environ['API_HOST_NAME']
    DELIVERY_CLIENT_USER_NAME = os.environ['DELIVERY_CLIENT_USER_NAME']
    DELIVERY_CLIENT_SECRET = os.environ['DELIVERY_CLIENT_SECRET']
    JOB_POLL_INTERVAL_SECONDS = int(os.environ['JOB_POLL_INTERVAL_SECONDS'])
    DELIVERY_POLL_INTERVAL_SECONDS = int(os.environ['DELIVERY_POLL_INTERVAL_SECONDS'])
    AWS_REGION = os.environ['AWS_REGION']
    NOTIFY_JOB_QUEUE = os.environ['NOTIFY_JOB_QUEUE']
    NOTIFY_DATA_API_URL = os.environ['NOTIFY_DATA_API_URL']
    NOTIFY_DATA_API_AUTH_TOKEN = os.environ['NOTIFY_DATA_API_AUTH_TOKEN']
    PROCESSOR_MAX_NUMBER_OF_MESSAGES = int(os.environ['PROCESSOR_MAX_NUMBER_OF_MESSAGES'])
    PROCESSOR_VISIBILITY_TIMEOUT = int(os.environ['PROCESSOR_VISIBILITY_TIMEOUT'])
    NOTIFICATION_QUEUE_PREFIX = os.environ['NOTIFICATION_QUEUE_PREFIX']
    TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
    TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
    TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

    # the following do not change per environment so can be set here
    NOTIFY_APP_NAME = 'delivery'
    NOTIFY_LOG_PATH = '/var/log/notify/application.log'
    DELIVERY_LOG_PATH = '/var/log/notify/delivery.log'
    NOTIFICATION_ATTRIBUTES = ['type', 'notification_id', 'service_id', 'template_id']


class Development(Config):
    DEBUG = True


class Test(Development):
    TURN_OFF_LOGGING = True
