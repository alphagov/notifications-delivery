from moto import mock_ses
from notify.clients.email.aws_ses import (AwsSesClient, AwsSesClientException)


@mock_ses
def test_send_email(aws_client):
    ses_client = AwsSesClient(aws_client)
    source = "source@notify.gov.uk"
    to_address = "random@random.com"
    subject = "Email subject"
    body = "Email body"
    # All source email addresses have to be verified before you
    # can send on behalf of them.
    aws_client.verify_email_identity(EmailAddress=source)
    message_id = ses_client.send_email(source, to_address, subject, body)
    assert message_id


@mock_ses
def test_send_email_not_verified(aws_client):
    ses_client = AwsSesClient(aws_client)
    source = "source@notify.gov.uk"
    to_address = "random@random.com"
    subject = "Email subject"
    body = "Email body"
    try:
        message_id = ses_client.send_email(source, to_address, subject, body)
    except AwsSesClientException as e:
        assert 'Did not have authority to send from email source@notify.gov.uk' in str(e)
