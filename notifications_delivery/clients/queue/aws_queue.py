import boto3


def get_messages(region, queue_name, message_attributes=[]):
    q = boto3.resource('sqs', region_name=region).create_queue(QueueName=queue_name)
    return q.receive_messages(MessageAttributeNames=message_attributes, MaxNumberOfMessages=10)
