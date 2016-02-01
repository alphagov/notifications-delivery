import pytest
import boto3


@pytest.fixture(scope='session')
def aws_client():
    return boto3.client('ses', region_name='eu-west-1')
