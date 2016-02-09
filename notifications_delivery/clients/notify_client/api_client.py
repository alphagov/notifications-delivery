from notifications_python_client.base import BaseAPIClient


class ApiClient(BaseAPIClient):
    def __init__(self, base_url=None, client_id=None, secret=None):
        super(self.__class__, self).__init__(base_url=base_url or 'base_url',
                                             client_id=client_id or 'client_id',
                                             secret=secret or 'secret')

    def init_app(self, app):
        self.base_url = app.config['API_HOST_NAME']
        self.client_id = app.config['DELIVERY_CLIENT_USER_NAME']
        self.secret = app.config['DELIVERY_CLIENT_SECRET']

    def send_sms(self, number, service_id, template_id, job_id):
        url = '/notifications/sms/service/{}'.format(service_id)
        notification = {"to": number,  "job": job_id, "template": template_id}
        return self.post(url, data=notification)

    def create_notification(self, service_id, template_id, job_id, to, status):
        url = '/service/{service_id}/job/{job_id}/notifications/'
        notification = {
            "to": to,
            'service': service_id,
            'template': template_id,
            'job': job_id,
            'status': status}
        return self.post(url, data=notification)

    def get_template(self, service_id, template_id):
        return self.get('/service/{}/template/{}'.format(service_id, template_id))['data']

    def update_job(self, job):
        service_id = job['service']
        job_id = job['id']
        url = '/service/{}/job/{}'.format(service_id, job_id)
        return self.put(url, data=job)
