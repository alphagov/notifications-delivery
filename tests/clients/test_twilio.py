import pytest


def test_send_sms(delivery_config,
                  mock_twilio_create,
                  sms_template_notification,
                  sms_content):
    with mock_twilio_create:
        from notifications_delivery.clients.sms.twilio import TwilioClient
        twilio_client = TwilioClient(delivery_config)
        request_id = twilio_client.send_sms(sms_template_notification, sms_content)
        assert request_id
        twilio_client.client.messages.create.assert_called_with(
            to=sms_template_notification['to'],
            body=sms_content,
            from_=twilio_client.from_number)


def test_send_sms_failed(delivery_config,
                         mock_twilio_create_exception,
                         sms_template_notification,
                         sms_content):
    with mock_twilio_create_exception:
        from notifications_delivery.clients.sms.twilio import (TwilioClient, SmsClientException)
        twilio_client = TwilioClient(delivery_config)
        from twilio.rest import TwilioRestClient
        try:
           message_id = twilio_client.send_sms(sms_template_notification, sms_content)
           pytest.fail("Failed to raise SmsClientException")
        except SmsClientException as e:
           pass
