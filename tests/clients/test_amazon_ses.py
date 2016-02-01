from moto import mock_ses
from clients.email.amazon_ses import AmazonSesClient


@mock_ses
def test_send_email(aws_client):
    ses_client = AmazonSesClient(aws_client)
    ses_client.send_email(
        "source@notify.gov.uk",
        "random@random.com",
        "Email subject",
        "Email body")
