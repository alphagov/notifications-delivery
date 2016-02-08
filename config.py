import os


class Config(object):
    DEBUG = False
    NOTIFY_LOG_LEVEL = 'DEBUG'
    NOTIFY_APP_NAME = 'delivery'
    NOTIFY_LOG_PATH = '/var/log/notify/application.log'
    DELIVERY_LOG_PATH = '/tmp/delivery.log'  # '/var/log/notify/delivery.log'
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
    ADMIN_CLIENT_USER_NAME = os.getenv('ADMIN_CLIENT_USER_NAME')
    ADMIN_CLIENT_SECRET = os.getenv('ADMIN_CLIENT_SECRET')
    JOB_POLL_INTERVAL_SECONDS = os.getenv('JOB_POLL_INTERVAL_SECONDS', 30)


class Development(Config):
    DEBUG = True
    API_HOST_NAME = 'http://localhost:6011'
    ADMIN_CLIENT_USER_NAME = 'dev-notify-admin'
    ADMIN_CLIENT_SECRET = 'dev-notify-secret-key'
    SECRET_KEY = 'secret-key'
    DANGEROUS_SALT = 'dangerous-salt'


class Test(Config):
    DEBUG = True
    SECRET_KEY = 'secret-key'
    DANGEROUS_SALT = 'dangerous-salt'


class Live(Config):
    pass

configs = {
    'development': Development,
    'test': Test,
    'live': Live,
}
