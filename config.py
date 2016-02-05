
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
