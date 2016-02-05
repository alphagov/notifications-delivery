import os


class Config(object):
    DEBUG = False
    NOTIFY_LOG_LEVEL = 'DEBUG'
    NOTIFY_APP_NAME = 'delivery'
    NOTIFY_LOG_PATH = '/var/log/notify/application.log'
    DELIVERY_LOG_PATH = '/var/log/notify/delivery.log'
    DELIVERY_LOG_LEVEL = 'DEBUG'
    PROCESSOR_MAX_NUMBER_OF_MESSGAES = 1
    PROCESSOR_VISIBILITY_TIMEOUT = 60

    AWS_REGION = 'eu-west-1'

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


class Test(Config):
    DEBUG = True


class Live(Config):
    pass

configs = {
    'development': Development,
    'test': Test,
    'live': Live,
}
