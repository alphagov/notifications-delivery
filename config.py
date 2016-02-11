import os


class Config(object):
    DEBUG = False
    NOTIFY_LOG_LEVEL = 'DEBUG'
    NOTIFY_APP_NAME = 'delivery'
    NOTIFY_LOG_PATH = '/var/log/notify/application.log'
    DELIVERY_LOG_PATH = '/var/log/notify/delivery.log'
    DELIVERY_LOG_LEVEL = 'DEBUG'
    PROCESSOR_MAX_NUMBER_OF_MESSGAES = 1
    PROCESSOR_VISIBILITY_TIMEOUT = 5
    NOTIFY_DATA_API_URL = os.getenv('NOTIFY_API_URL', "http://localhost:6001")
    NOTIFY_DATA_API_AUTH_TOKEN = os.getenv('NOTIFY_API_TOKEN', "dev-token")
    # Notification Queue names are a combination of a prefx plus a name
    NOTIFICATION_QUEUE_PREFIX = 'notification'
    NOTIFICATION_ATTRIBUTES = ['type', 'message_id', 'service_id', 'template_id']

    AWS_REGION = 'eu-west-1'

    NOTIFY_JOB_QUEUE = os.getenv('NOTIFY_JOB_QUEUE', 'notify-jobs-queue')

    API_HOST_NAME = os.getenv('API_HOST_NAME')
    DELIVERY_CLIENT_USER_NAME = os.getenv('DELIVERY_CLIENT_USER_NAME')
    DELIVERY_CLIENT_SECRET = os.getenv('DELIVERY_CLIENT_SECRET')
    JOB_POLL_INTERVAL_SECONDS = int(os.getenv('JOB_POLL_INTERVAL_SECONDS', '5'))
    DELIVERY_POLL_INTERVAL_SECONDS = int(os.getenv('DELIVERY_POLL_INTERVAL_SECONDS', '2'))

    TWILIO_ACCOUNT_SID = 'ACCOUNT_ID'
    TWILIO_AUTH_TOKEN = 'AUTH_TOKEN'


class Development(Config):
    DEBUG = True
    API_HOST_NAME = 'http://localhost:6011'
    SECRET_KEY = 'secret-key'
    DANGEROUS_SALT = 'dangerous-salt'
    DELIVERY_CLIENT_USER_NAME = 'dev-notify-delivery'
    DELIVERY_CLIENT_SECRET = 'dev-notify-secret-key'
    DELIVERY_LOG_LEVEL = 'INFO'
    NOTIFICATION_QUEUE_PREFIX = 'notification_development'


class Preview(Config):
    NOTIFICATION_QUEUE_PREFIX = 'notification_preview'
    DELIVERY_LOG_LEVEL = 'ERROR'


class Staging(Config):
    NOTIFICATION_QUEUE_PREFIX = 'notification_staging'
    DELIVERY_LOG_LEVEL = 'ERROR'


class Test(Config):
    DEBUG = True
    SECRET_KEY = 'secret-key'
    DANGEROUS_SALT = 'dangerous-salt'
    NOTIFICATION_QUEUE_PREFIX = 'notification_test'
    DELIVERY_LOG_LEVEL = 'ERROR'


class Live(Config):
    NOTIFICATION_QUEUE_PREFIX = 'notification_live'
    DELIVERY_LOG_LEVEL = 'ERROR'


configs = {
    'development': Development,
    'preview': Preview,
    'staging': Staging,
    'test': Test,
    'live': Live,
}
