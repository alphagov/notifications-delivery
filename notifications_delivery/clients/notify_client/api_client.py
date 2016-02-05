from notifications_python_client.base import BaseAPIClient


class ApiClient(BaseAPIClient):
    def __init__(self, base_url=None, client_id=None, secret=None):
        super(self.__class__, self).__init__(base_url=base_url or 'base_url',
                                             client_id=client_id or 'client_id',
                                             secret=secret or 'secret')

    def init_app(self, app):
        self.base_url = app.config['API_HOST_NAME']
        self.client_id = app.config['ADMIN_CLIENT_USER_NAME']
        self.secret = app.config['ADMIN_CLIENT_SECRET']

    def send_sms(self, number, template_id):
        notification = {"to": number,  "template": template_id}
        return self.post('/notifications/sms', data=notification)

    def get_template(self, service_id, template_id):
        return self.get('/service/{}/template/{}'.format(service_id, template_id))
