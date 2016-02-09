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
                                     mock_alpha_send_sms,
                                     populate_queue_with_sms_content_msg):
    process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
    msg = populate_queue_with_sms_content_msg.receive_messages()[0]
    content = decrypt_content(delivery_config, msg.body)
    mock_alpha_send_sms.assert_called_with(content['to'], content['content'])
    assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_email_message(mocker,
                               delivery_config,
                               mock_alpha_send_email,
                               populate_queue_with_email_msg):
    process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
    msg = populate_queue_with_email_msg.receive_messages()[0]
    content = decrypt_content(delivery_config, msg.body)
    mock_alpha_send_email.assert_called_with(content['to_address'],
                                             content['body'],
                                             content['from_address'],
                                             content['subject'])
    assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_sms_template_message(mocker,
                                      delivery_config,
                                      mock_alpha_send_sms,
                                      mock_beta_get_template,
                                      populate_queue_with_sms_template_msg):
    process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
    msg = populate_queue_with_sms_template_msg.receive_messages()[0]
    content = decrypt_content(delivery_config, msg.body)
    service_id = msg.message_attributes.get('service_id').get('StringValue')
    template_id = msg.message_attributes.get('template_id').get('StringValue')
    mock_beta_get_template.assert_called_with(service_id, template_id)
    template_json = mock_beta_get_template(service_id, template_id)
    mock_alpha_send_sms.assert_called_with(content['to'], template_json['content'])
    assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_sms_processing_error(mocker,
                                      delivery_config,
                                      populate_queue_with_sms_content_msg,
                                      mock_alpha_send_sms_processing_error):
    process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
    msg = populate_queue_with_sms_content_msg.receive_messages()[0]
    content = decrypt_content(delivery_config, msg.body)
    mock_alpha_send_sms_processing_error.assert_called_with(content['to'], content['content'])
    assert msg.delete.call_count == 1


@moto.mock_sqs
def test_process_sms_http_503(mocker,
                              delivery_config,
                              populate_queue_with_sms_content_msg,
                              mock_alpha_send_sms_http_503):
    process_all_queues(delivery_config, delivery_config['NOTIFICATION_QUEUE_PREFIX'])
    msg = populate_queue_with_sms_content_msg.receive_messages()[0]
    content = decrypt_content(delivery_config, msg.body)
    mock_alpha_send_sms_http_503.assert_called_with(content['to'], content['content'])
    assert msg.delete.call_count == 0
