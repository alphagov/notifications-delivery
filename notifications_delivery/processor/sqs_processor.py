import boto3
import logging


def _set_up_logger(config):
    turn_off = config.get('TURN_OFF_LOGGING', False)
    logger = logging.getLogger(__name__)
    if not turn_off:
        logger = logging.getLogger('delivery_notification')
        logger.setLevel(config['DELIVERY_LOG_LEVEL'])
        fh = logging.FileHandler(config['DELIVERY_LOG_PATH'])
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger


def _get_all_queues(config, queue_name_prefix=''):
        """
        Returns a list of all queues for a aws account.
        """
        client = boto3.client('sqs', region_name=config['AWS_REGION'])
        sqs = boto3.resource('sqs', region_name=config['AWS_REGION'])
        return [sqs.Queue(x) for x in client.list_queues(QueueNamePrefix=queue_name_prefix)['QueueUrls']]


def _get_message_id(message):
    # TODO needed because tests and live api return different type objects
    return message.id if getattr(message, 'id', None) else getattr(message, 'message_id', 'n/a')


def process_all_queues(config):
    """
    For each queue on the aws account process one message.
    """
    logger = _set_up_logger(config)
    queues = _get_all_queues(config)
    logger.debug("Pulling off {} queues.".format(len(queues)))
    for queue in queues:
        try:
            logger.info("Pulling from queue {}".format(queue.url))
            messages = queue.receive_messages(
                MaxNumberOfMessages=config['PROCESSOR_MAX_NUMBER_OF_MESSGAES'],
                VisibilityTimeout=config['PROCESSOR_VISIBILITY_TIMEOUT'])
            for message in messages:
                logger.info("Processing message {}".format(_get_message_id(message)))
                # TODO process message id
                message.delete()
                logger.info("Deleted message {}".format(_get_message_id(message)))
        except Exception as e:
            logger.error("Failed processing message from queue {}".format(queue.url))
            logger.exception(e)
