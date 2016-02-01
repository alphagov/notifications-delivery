from clients.email.email_client import (
    EmailClient, EmailClientException)


class AmazonSesClient(EmailClient):
    '''
    Amazon SES email client.
    '''

    def __init__(self, client, *args, **kwargs):
        self._client = client
        super(AmazonSesClient, self).__init__(*args, **kwargs)

    def send_email(self,
                   source,
                   to_addresses,
                   subject,
                   body,
                   reply_to_addresses=None):
        try:
            if isinstance(to_addresses, str):
                to_addresses = [to_addresses]
            if reply_to_addresses and isinstance(reply_to_addresses, str):
                reply_to_addresses = [reply_to_addresses]
            elif reply_to_addresses is None:
                reply_to_addresses = []

            self._client.send_email(
                Source=source,
                Destination={
                    'ToAddresses': to_addresses,
                    'CcAddresses': [],
                    'BccAddresses': []
                },
                Message={
                    'Subject': {
                        'Data': subject,
                    },
                    'Body': {
                        'Text': {
                            'Data': body}}
                },
                ReplyToAddresses=reply_to_addresses)
        except Exception as e:
            import traceback
            traceback.print_exc()
            # TODO logging exceptions
            raise EmailClientException(str(e))
