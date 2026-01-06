"""
Shared pytest fixtures for antokel_cloud tests.

Provides AWS mocking using moto and dotenv loading.
"""

import os

import pytest
from moto import mock_aws
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def load_env():
    """Load environment variables from .env file."""
    load_dotenv()


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def mock_s3(aws_credentials):
    """Mock S3 service using moto."""
    with mock_aws():
        yield


@pytest.fixture
def mock_ec2(aws_credentials):
    """Mock EC2 service using moto."""
    with mock_aws():
        yield


@pytest.fixture
def mock_aws_all(aws_credentials):
    """Mock all AWS services using moto."""
    with mock_aws():
        yield

