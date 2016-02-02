import pytest
import boto3


@pytest.fixture(scope='session')
def aws_client():
    return boto3.client('ses',
                        region_name='eu-west-1',
                        aws_access_key_id='sample_key',
                        aws_secret_access_key='sample_key')
