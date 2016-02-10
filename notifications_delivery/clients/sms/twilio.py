import logging
from notifications_delivery.clients.sms import (
    SmsClient, SmsClientException)
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException


logger = logging.getLogger(__name__)


class TwilioClientException(SmsClientException):
    pass


class TwilioClient(SmsClient):
    '''
    Twilio sms client.
    '''
    def __init__(self, config, *args, **kwargs):
        super(TwilioClient, self).__init__(*args, **kwargs)
        self.client = TwilioRestClient(
            config.get('TWILIO_ACCOUNT_SID'),
            config.get('TWILIO_AUTH_TOKEN'))
        self.from_number = config.get('FROM_NUMBER')

    def send_sms(self, notification, content):
        try:
            response = self.client.messages.create(
                body=content,
                to=notification['to'],
                from_=self.from_number
            )
            msg = (
                "SMS notification (id={}, to={}, body={}) has been queued to"
                " be sent with request id of {}.").format(
                    notification['id'],
                    notification['to'],
                    content,
                    response.sid)
            logger.debug(msg)
            return response.sid
        except TwilioRestException as e:
            logger.exception(e)
            raise SmsClientException(self.identifier)
