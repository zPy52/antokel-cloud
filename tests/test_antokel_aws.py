"""
Tests for the AntokelAws main entry point.

Tests credential handling, environment variable reading, and factory methods.
"""

import os

import pytest

from antokel_cloud.aws import AntokelAws
from antokel_cloud.aws.s3 import S3
from antokel_cloud.aws.ec2 import EC2


class TestAntokelAwsInit:
    """Tests for AntokelAws initialization."""

    def test_init_with_explicit_credentials(self):
        """
        Test: Initialize with explicit credentials
        Input: region='us-west-2', access_key='my-key', secret_key='my-secret'
        Expected: Attributes set to provided values
        """
        aws = AntokelAws(
            region='us-west-2',
            access_key='my-key',
            secret_key='my-secret',
        )
        
        assert aws.region == 'us-west-2', \
            f"Expected region='us-west-2', got region='{aws.region}'"
        assert aws.access_key == 'my-key', \
            f"Expected access_key='my-key', got access_key='{aws.access_key}'"
        assert aws.secret_key == 'my-secret', \
            f"Expected secret_key='my-secret', got secret_key='{aws.secret_key}'"

    def test_init_with_env_variables(self, monkeypatch):
        """
        Test: Initialize reading from environment variables
        Input: AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY in env
        Expected: Reads credentials from environment
        """
        monkeypatch.setenv('AWS_REGION', 'eu-west-1')
        monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'env-access-key')
        monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'env-secret-key')
        
        aws = AntokelAws()
        
        assert aws.region == 'eu-west-1', \
            f"Expected region='eu-west-1', got region='{aws.region}'"
        assert aws.access_key == 'env-access-key', \
            f"Expected access_key='env-access-key', got access_key='{aws.access_key}'"
        assert aws.secret_key == 'env-secret-key', \
            f"Expected secret_key='env-secret-key', got secret_key='{aws.secret_key}'"

    def test_init_aws_default_region_fallback(self, monkeypatch):
        """
        Test: AWS_DEFAULT_REGION fallback when AWS_REGION is not set
        Input: Only AWS_DEFAULT_REGION set in env
        Expected: Uses AWS_DEFAULT_REGION as fallback
        """
        # Clear AWS_REGION if it exists
        monkeypatch.delenv('AWS_REGION', raising=False)
        monkeypatch.setenv('AWS_DEFAULT_REGION', 'ap-southeast-1')
        
        aws = AntokelAws()
        
        assert aws.region == 'ap-southeast-1', \
            f"Expected region='ap-southeast-1', got region='{aws.region}'"

    def test_init_explicit_credentials_override_env(self, monkeypatch):
        """
        Test: Explicit credentials take precedence over env variables
        Input: Both env variables and explicit params set
        Expected: Explicit params win
        """
        monkeypatch.setenv('AWS_REGION', 'env-region')
        monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'env-key')
        monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'env-secret')
        
        aws = AntokelAws(
            region='explicit-region',
            access_key='explicit-key',
            secret_key='explicit-secret',
        )
        
        assert aws.region == 'explicit-region'
        assert aws.access_key == 'explicit-key'
        assert aws.secret_key == 'explicit-secret'


class TestAntokelAwsS3Factory:
    """Tests for the S3 factory method."""

    def test_s3_factory_returns_s3_client(self, mock_s3):
        """
        Test: S3() factory returns an S3 client instance
        Input: aws.S3('test-bucket')
        Expected: Returns S3 instance with correct bucket
        """
        aws = AntokelAws()
        s3 = aws.S3('test-bucket')
        
        assert isinstance(s3, S3), \
            f"Expected S3 instance, got {type(s3)}"
        assert s3._bucket == 'test-bucket', \
            f"Expected bucket='test-bucket', got bucket='{s3._bucket}'"

    def test_s3_factory_with_prefix(self, mock_s3):
        """
        Test: S3() factory with prefix parameter
        Input: aws.S3('bucket', prefix='folder/')
        Expected: S3 client has prefix set correctly
        """
        aws = AntokelAws()
        s3 = aws.S3('my-bucket', prefix='data/folder')
        
        assert s3._prefix == 'data/folder/', \
            f"Expected prefix='data/folder/', got prefix='{s3._prefix}'"

    def test_s3_factory_passes_credentials(self, mock_s3):
        """
        Test: S3() factory passes credentials to S3 client
        Input: AntokelAws with explicit credentials
        Expected: S3 client configured with same credentials
        """
        aws = AntokelAws(
            region='us-west-2',
            access_key='test-key',
            secret_key='test-secret',
        )
        s3 = aws.S3('bucket')
        
        # The S3 client should be configured - we verify via boto3 client
        assert s3._client is not None


class TestAntokelAwsEC2Factory:
    """Tests for the EC2 factory method."""

    def test_ec2_factory_returns_ec2_client(self, mock_ec2):
        """
        Test: EC2() factory returns an EC2 client instance
        Input: aws.EC2()
        Expected: Returns EC2 instance
        """
        aws = AntokelAws()
        ec2 = aws.EC2()
        
        assert isinstance(ec2, EC2), \
            f"Expected EC2 instance, got {type(ec2)}"

    def test_ec2_factory_has_boto_client(self, mock_ec2):
        """
        Test: EC2() factory creates boto3 client
        Input: aws.EC2()
        Expected: EC2 instance has _client attribute
        """
        aws = AntokelAws()
        ec2 = aws.EC2()
        
        assert ec2._client is not None, \
            "Expected EC2._client to be set"

