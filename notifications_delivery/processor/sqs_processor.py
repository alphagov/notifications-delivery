import boto3
import logging
from itsdangerous import URLSafeSerializer
from notify_client import NotifyAPIClient
from notify_client.errors import HTTPError as alphaHTTPError
from notify_client.errors import InvalidResponse as alphaInvalidResponse
from notifications_delivery.clients.notify_client.api_client import ApiClient
from notifications_python_client.errors import (HTTP503Error, HTTPError, InvalidResponse)


class ProcessingError(Exception):
    '''
    Exception used for messages where the content cannot be processed.
    The message will not be returned to the queue.
    '''
    pass


class ExternalConnectionError(Exception):
    '''
    Exception used for messages where connection error occurs with an
    external api.
    The message will be returned to the queue.
    '''
    pass


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


def _decrypt_message(config, encrypted_content):
    serializer = URLSafeSerializer(config.get('SECRET_KEY'))
    return serializer.loads(encrypted_content, salt=config.get('DANGEROUS_SALT'))


def _process_message(config, message, notify_alpha_client, notify_beta_client):
    content = _decrypt_message(config, message.body)
    type_ = message.message_attributes.get('type').get('StringValue')
    service_id = message.message_attributes.get('service_id').get('StringValue')
    template_id = message.message_attributes.get('template_id').get('StringValue')
    response = None
    if type_ == 'email':
        try:
            response = notify_alpha_client.send_email(
                content['to_address'],
                content['body'],
                content['from_address'],
                content['subject'])
        except alphaHTTPError as e:
            if e.status_code == 503:
                raise ExternalConnectionError(e)
            else:
                raise ProcessingError(e)
        except alphaInvalidResponse as e:
            raise ProcessingError(e)
    elif type_ == 'sms':
        if 'content' in content:
            try:
                response = notify_alpha_client.send_sms(
                    content['to'], content['content'])
            except alphaHTTPError as e:
                if e.status_code == 503:
                    raise ExternalConnectionError(e)
                else:
                    raise ProcessingError(e)
            except alphaInvalidResponse as e:
                raise ProcessingError(e)
        elif 'template' in content:
            try:
                template_response = notify_beta_client.get_template(service_id, template_id)
            except HTTP503Error as e:
                raise ExternalConnectionError(e)
            except HTTPError as e:
                raise ProcessingError(e)
            except InvalidResponse as e:
                raise InvalidResponse(e)
            try:
                response = notify_alpha_client.send_sms(content['to'], template_response['content'])
            except alphaHTTPError as e:
                if e.status_code == 503:
                    raise ExternalConnectionError(e)
                else:
                    raise ProcessingError(e)
            except alphaInvalidResponse as e:
                raise ProcessingError(e)
    else:
        error_msg = "Invalid type {} for message id {}".format(
            type_, message.message_attributes.get('message_id').get('StringValue'))
        raise ProcessingError(error_msg)


def _get_message_id(message):
    # TODO needed because tests and live api return different type objects
    return message.id if getattr(message, 'id', None) else getattr(message, 'message_id', 'n/a')


def process_all_queues(config, queue_name_prefix):
    """
    For each queue on the aws account process one message.
    """
    logger = _set_up_logger(config)
    notify_alpha_client = NotifyAPIClient(base_url=config['NOTIFY_DATA_API_URL'],
                                          auth_token=config['NOTIFY_DATA_API_AUTH_TOKEN'])
    notify_beta_client = ApiClient(base_url=config['API_HOST_NAME'],
                                   client_id=config['DELIVERY_CLIENT_USER_NAME'],
                                   secret=config['DELIVERY_CLIENT_SECRET'])
    queues = _get_all_queues(config, queue_name_prefix)
    logger.debug("Pulling off {} queues.".format(len(queues)))
    for queue in queues:
        try:
            logger.info("Pulling from queue {}".format(queue.url))
            messages = queue.receive_messages(
                MaxNumberOfMessages=config['PROCESSOR_MAX_NUMBER_OF_MESSGAES'],
                VisibilityTimeout=config['PROCESSOR_VISIBILITY_TIMEOUT'],
                MessageAttributeNames=config['NOTIFICATION_ATTRIBUTES'])
            for message in messages:
                logger.info("Processing message {}".format(_get_message_id(message)))
                to_delete = True
                try:
                    _process_message(config, message, notify_alpha_client, notify_beta_client)
                except ProcessingError as e:
                    msg = (
                        "Failed prcessing message from queue {}."
                        " The message will not be returned to the queue.").format(queue.url)
                    logger.error(msg)
                    logger.exception(e)
                    to_delete = True
                except ExternalConnectionError as e:
                    msg = (
                        "Failed prcessing message from queue {}."
                        " The message will be returned to the queue.").format(queue.url)
                    logger.error(msg)
                    logger.exception(e)
                    to_delete = False
                if to_delete:
                    message.delete()
                    logger.info("Deleted message {}".format(_get_message_id(message)))
        except Exception as e:
            logger.error("Unexpected exception processing message from queue {}".format(queue.url))
            logger.exception(e)


def process_notification_job():
    from notifications_delivery.app import create_app
    app = create_app(os.getenv('NOTIFICATIONS_DELIVERY_ENVIRONMENT', 'development'))
    with app.app_context():
        try:
            process_all_queues(app.config, app.config['NOTIFICATION_QUEUE_PREFIX'])
        except Exception as e:
            # TODO log errors and report to api
            app.logger.error(e)
