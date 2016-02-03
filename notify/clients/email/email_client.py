from notify.clients.client import (Client, ClientException)


class EmailClientException(ClientException):
    '''
    Base Exception for EmailClients
    '''
    pass


class EmailClient(Client):
    '''
    Base Email client for sending emails.
    '''

    def send_email(self, *args, **kwargs):
        raise NotImplemented('TODO Need to implement.')
