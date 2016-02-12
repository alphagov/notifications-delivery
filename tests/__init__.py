import boto
import boto3
import moto
from unittest.mock import Mock
from itsdangerous import URLSafeSerializer


def encrypt_content(config, content):
    serializer = URLSafeSerializer(config.get('SECRET_KEY'))
    return serializer.dumps(content, salt=config.get('DANGEROUS_SALT'))


def decrypt_content(config, encrypted_content):
    serializer = URLSafeSerializer(config.get('SECRET_KEY'))
    return serializer.loads(encrypted_content, salt=config.get('DANGEROUS_SALT'))


@moto.mock_sqs
def create_sqs_connection():
    return boto.connect_sqs('the_key', 'the_secret')


@moto.mock_sqs
def create_sqs_resource(region_name):
    return boto3.resource('sqs', region_name=region_name)


@moto.mock_sqs
def create_queue(sqs_connection, queue_name):
    sqs_connection.create_queue(queue_name, visibility_timeout=60)
    queue = sqs_connection.get_queue(queue_name)
    queue.wait_time_seconds = 10
    return queue


def create_msg_str_attr(content):
    return {'StringValue': content}


def create_message(config,
                   sqs_resource,
                   queue,
                   type_,
                   notification,
                   msg_id=None,
                   service_id=None,
                   template_id=None):
    if msg_id is None:
        msg_id = '1234'
    if service_id is None:
        service_id = '5678'
    if template_id is None:
        template_id = '3456'
    msg = Mock()
    encrypted_content = encrypt_content(config, notification)
    setattr(msg, 'body', encrypted_content)
    msg_attrs = {}
    msg_attrs['type'] = create_msg_str_attr(type_)
    msg_attrs['notification_id'] = create_msg_str_attr(msg_id)
    msg_attrs['service_id'] = create_msg_str_attr(service_id)
    msg_attrs['template_id'] = create_msg_str_attr(template_id)
    setattr(msg, 'message_attributes', msg_attrs)
    setattr(msg, 'delete', Mock())
    return msg
