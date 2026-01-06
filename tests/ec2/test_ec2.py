"""
Tests for EC2 client and factory methods.

Tests EC2 initialization, Instance factory, and Volume factory.
"""

import pytest

from antokel_cloud.aws.ec2 import EC2
from antokel_cloud.aws.ec2.instance import Instance
from antokel_cloud.aws.ec2.volume import Volume


class TestEC2Init:
    """Tests for EC2 client initialization."""

    def test_init_with_credentials(self, mock_ec2):
        """
        Test: Initialize EC2 with explicit credentials
        Input: region, access_key, secret_key
        Expected: Client created successfully
        """
        ec2 = EC2(
            region='us-west-2',
            access_key='test-key',
            secret_key='test-secret',
        )
        
        assert ec2._client is not None, \
            "Expected _client to be initialized"

    def test_init_without_credentials(self, mock_ec2):
        """
        Test: Initialize EC2 without explicit credentials
        Input: No parameters (uses env/config)
        Expected: Client created successfully
        """
        ec2 = EC2()
        
        assert ec2._client is not None, \
            "Expected _client to be initialized"


class TestEC2InstanceFactory:
    """Tests for the Instance factory method."""

    def test_instance_factory_minimal_params(self, mock_ec2):
        """
        Test: Instance() factory with minimal parameters
        Input: No parameters
        Expected: Returns Instance with _ec2 reference
        """
        ec2 = EC2()
        
        instance = ec2.Instance()
        
        assert isinstance(instance, Instance), \
            f"Expected Instance, got {type(instance)}"
        assert instance._ec2 is ec2, \
            "Expected Instance._ec2 to reference parent EC2"

    def test_instance_factory_with_id(self, mock_ec2):
        """
        Test: Instance() factory with existing instance ID
        Input: id='i-1234567890abcdef0'
        Expected: Instance with id set
        """
        ec2 = EC2()
        
        instance = ec2.Instance(id='i-1234567890abcdef0')
        
        assert instance.id == 'i-1234567890abcdef0', \
            f"Expected id='i-1234567890abcdef0', got id='{instance.id}'"

    def test_instance_factory_with_all_params(self, mock_ec2):
        """
        Test: Instance() factory with all parameters
        Input: All params provided
        Expected: Instance has all attributes set
        """
        ec2 = EC2()
        storage = [ec2.Volume(gib=20)]
        
        instance = ec2.Instance(
            id='i-existing',
            name='test-instance',
            machine='t4g.micro',
            mode='spot',
            key_pair='my-keypair',
            security_groups=['sg-12345'],
            ami='ami-12345678',
            storage=storage,
            user_data='#!/bin/bash\necho hello',
        )
        
        assert instance.id == 'i-existing', \
            f"Expected id='i-existing', got '{instance.id}'"
        assert instance.name == 'test-instance', \
            f"Expected name='test-instance', got '{instance.name}'"
        assert instance.machine == 't4g.micro', \
            f"Expected machine='t4g.micro', got '{instance.machine}'"
        assert instance.mode == 'spot', \
            f"Expected mode='spot', got '{instance.mode}'"
        assert instance.key_pair == 'my-keypair', \
            f"Expected key_pair='my-keypair', got '{instance.key_pair}'"
        assert instance.security_groups == ['sg-12345'], \
            f"Expected security_groups=['sg-12345'], got {instance.security_groups}"
        assert instance.ami == 'ami-12345678', \
            f"Expected ami='ami-12345678', got '{instance.ami}'"
        assert instance.storage == storage, \
            f"Expected storage={storage}, got {instance.storage}"
        assert instance.user_data == '#!/bin/bash\necho hello', \
            f"Expected user_data='#!/bin/bash\\necho hello', got '{instance.user_data}'"

    def test_instance_factory_default_mode(self, mock_ec2):
        """
        Test: Instance() factory default mode is 'on-demand'
        Input: No mode specified
        Expected: mode='on-demand'
        """
        ec2 = EC2()
        
        instance = ec2.Instance()
        
        assert instance.mode == 'on-demand', \
            f"Expected mode='on-demand', got mode='{instance.mode}'"


class TestEC2VolumeFactory:
    """Tests for the Volume factory method."""

    def test_volume_factory_defaults(self, mock_ec2):
        """
        Test: Volume() factory with default values
        Input: No parameters
        Expected: gib=8, mode='gp3'
        """
        ec2 = EC2()
        
        volume = ec2.Volume()
        
        assert isinstance(volume, Volume), \
            f"Expected Volume, got {type(volume)}"
        assert volume.gib == 8, \
            f"Expected gib=8, got gib={volume.gib}"
        assert volume.mode == 'gp3', \
            f"Expected mode='gp3', got mode='{volume.mode}'"

    def test_volume_factory_custom_size(self, mock_ec2):
        """
        Test: Volume() factory with custom size
        Input: gib=20
        Expected: Volume with gib=20
        """
        ec2 = EC2()
        
        volume = ec2.Volume(gib=20)
        
        assert volume.gib == 20, \
            f"Expected gib=20, got gib={volume.gib}"

    def test_volume_factory_gp2_mode(self, mock_ec2):
        """
        Test: Volume() factory with gp2 mode
        Input: mode='gp2'
        Expected: Volume with mode='gp2'
        """
        ec2 = EC2()
        
        volume = ec2.Volume(mode='gp2')
        
        assert volume.mode == 'gp2', \
            f"Expected mode='gp2', got mode='{volume.mode}'"

    def test_volume_factory_standard_mode(self, mock_ec2):
        """
        Test: Volume() factory with standard mode
        Input: mode='standard'
        Expected: Volume with mode='standard'
        """
        ec2 = EC2()
        
        volume = ec2.Volume(mode='standard')
        
        assert volume.mode == 'standard', \
            f"Expected mode='standard', got mode='{volume.mode}'"

    def test_volume_factory_with_snapshot_id(self, mock_ec2):
        """
        Test: Volume() factory with existing snapshot ID
        Input: id='snap-1234567890abcdef0'
        Expected: Volume with id set
        """
        ec2 = EC2()
        
        volume = ec2.Volume(id='snap-1234567890abcdef0')
        
        assert volume.id == 'snap-1234567890abcdef0', \
            f"Expected id='snap-1234567890abcdef0', got id='{volume.id}'"

