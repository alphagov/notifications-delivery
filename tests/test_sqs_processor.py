import moto
import pytest
from notifications_delivery.processor.sqs_processor import process_all_queues
from tests import decrypt_content


@moto.mock_sqs
def test_empty_queue(mocker,
                     delivery_config,
                     create_queue_no_msgs):
    process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])


@moto.mock_sqs
def test_process_sms_content_message(mocker,
                                     delivery_config,
                                     mock_twilio_create,
                                     populate_queue_with_sms_content_msg):
    with mock_twilio_create:
        process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
        msg = populate_queue_with_sms_content_msg.receive_messages()[0]
        content = decrypt_content(delivery_config, msg.body)
        assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_email_message(mocker,
                               delivery_config,
                               mock_ses_send_email,
                               populate_queue_with_email_msg):
    process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
    msg = populate_queue_with_email_msg.receive_messages()[0]
    content = decrypt_content(delivery_config, msg.body)
    mock_ses_send_email.assert_called_with(
        content['from_address'], content['to_address'], content['subject'], content['body'])
    assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_sms_template_message(mocker,
                                      delivery_config,
                                      mock_twilio_create,
                                      mock_beta_get_template,
                                      populate_queue_with_sms_template_msg):
    with mock_twilio_create:
        process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
        msg = populate_queue_with_sms_template_msg.receive_messages()[0]
        content = decrypt_content(delivery_config, msg.body)
        service_id = msg.message_attributes.get('service_id').get('StringValue')
        template_id = msg.message_attributes.get('template_id').get('StringValue')
        mock_beta_get_template.assert_called_with(service_id, template_id)
        template_json = mock_beta_get_template(service_id, template_id)
        assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_sms_processing_error(mocker,
                                      delivery_config,
                                      populate_queue_with_sms_content_msg,
                                      mock_twilio_create_exception):
    with mock_twilio_create_exception:
        process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
        msg = populate_queue_with_sms_content_msg.receive_messages()[0]
        content = decrypt_content(delivery_config, msg.body)
        assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_sms_job_notification(mocker,
                                      delivery_config,
                                      mock_twilio_create,
                                      mock_beta_get_template,
                                      mock_beta_create_notification,
                                      populate_queue_with_sms_job_msg):
    with mock_twilio_create:
        process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
        msg = populate_queue_with_sms_job_msg.receive_messages()[0]
        content = decrypt_content(delivery_config, msg.body)
        service_id = msg.message_attributes.get('service_id').get('StringValue')
        template_id = msg.message_attributes.get('template_id').get('StringValue')
        notification_id = msg.message_attributes.get('notification_id').get('StringValue')
        mock_beta_get_template.assert_called_with(service_id, template_id)
        template_json = mock_beta_get_template(service_id, template_id)
        mock_beta_create_notification.assert_called_with(
            service_id=service_id, template_id=template_id, job_id=content['job'],
            to=content['to'], status='sent',
            notification_id=notification_id)
        assert msg.delete.call_count == 1
