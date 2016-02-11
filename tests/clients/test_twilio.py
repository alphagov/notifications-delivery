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


def test_get_sms_status(delivery_config,
                        mock_twilio_get):
    with mock_twilio_get:
        from notifications_delivery.clients.sms.twilio import TwilioClient
        twilio_client = TwilioClient(delivery_config)
        msg_id = "123"
        status = twilio_client.status(msg_id)
        twilio_client.client.messages.get.assert_called_with(msg_id)


def test_get_sms_status_failed(delivery_config,
                               mock_twilio_get_exception):
    with mock_twilio_get_exception:
        from notifications_delivery.clients.sms.twilio import (
            TwilioClient, SmsClientException)
        twilio_client = TwilioClient(delivery_config)
        msg_id = "123"
        try:
            status = twilio_client.status(msg_id)
            pytest.fail("Failed to raise SmsClientException")
        except SmsClientException as e:
            pass


def test_send_sms_failed(delivery_config,
                         mock_twilio_create_exception,
                         sms_template_notification,
                         sms_content):
    with mock_twilio_create_exception:
        from notifications_delivery.clients.sms.twilio import (
            TwilioClient, SmsClientException)
        twilio_client = TwilioClient(delivery_config)
        from twilio.rest import TwilioRestClient
        try:
           message_id = twilio_client.send_sms(sms_template_notification, sms_content)
           pytest.fail("Failed to raise SmsClientException")
        except SmsClientException as e:
           pass
