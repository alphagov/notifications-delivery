import pytest
from notifications_delivery.clients.sms.twilio import (TwilioClient, TwilioClientException)


def test_send_sms(delivery_config,
                  mock_twilio_client_send_sms,
                  sms_notification,
                  sms_content):
    twilio_client = TwilioClient(delivery_config)
    request_id = twilio_client.send_sms(sms_notification, sms_content)
    assert request_id


def test_send_sms_failed(delivery_config,
                         mock_twilio_client_send_sms_exception,
                         sms_notification,
                         sms_content):
    twilio_client = TwilioClient(delivery_config)
    try:
        message_id = twilio_client.send_sms(sms_notification, sms_content)
        pytest.fail("Failed to raise TwilioClientException")
    except TwilioClientException as e:
        pass
