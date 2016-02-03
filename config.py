import os


class Config(object):
    DEBUG = False
    NOTIFY_LOG_LEVEL = 'DEBUG'
    NOTIFY_APP_NAME = 'delivery'
    NOTIFY_LOG_PATH = '/var/log/notify/application.log'

    AWS_REGION = 'eu-west-1'
    NOTIFY_JOB_QUEUE = os.getenv('NOTIFY_JOB_QUEUE', 'notify-jobs-queue')


class Development(Config):
    DEBUG = True


class Test(Config):
    DEBUG = True


class Live(Config):
    pass

configs = {
    'development': Development,
    'test': Test,
    'live': Live,
}
