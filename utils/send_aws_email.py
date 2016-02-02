"""
Usage:
    utils/send_aws_email.py <aws_key> <aws_secret> <region>

"""

import boto3
from clients.email.aws_ses import AwsSesClient
from docopt import docopt


def send_test_email(aws_client):
    ses_client = AwsSesClient(aws_client)
    from_ = input("enter from address (nobody@digital.cabinet-office.gov.uk): ")
    to = input("enter to address (someone@digital.cabinet-office.gov.uk): ")
    subject = input("enter email subject: ")
    body = input("enter email body text: ")
    print(ses_client.send_email(from_, to, subject, body))


if __name__ == "__main__":
    arguments = docopt(__doc__)

    aws_client = boto3.client('ses',
                              region_name=arguments['<region>'],
                              aws_access_key_id=arguments['<aws_key>'],
                              aws_secret_access_key=arguments['<aws_secret>'])

    send_test_email(aws_client)
