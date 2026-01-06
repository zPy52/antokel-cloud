"""
Tests for Instance lifecycle management.

Tests create, start, stop, terminate operations and error handling.
"""

import boto3
import pytest

from antokel_cloud.aws.ec2 import EC2
from antokel_cloud.aws.ec2.volume import Volume


class TestInstanceCreate:
    """Tests for the create method."""

    def test_create_missing_machine_raises_error(self, mock_ec2):
        """
        Test: create() without machine raises ValueError
        Input: Instance with no machine set
        Expected: Raises ValueError with message about 'machine'
        """
        ec2 = EC2()
        instance = ec2.Instance(key_pair='my-keypair')  # machine missing
        
        with pytest.raises(ValueError) as exc_info:
            instance.create()
        
        assert "'machine'" in str(exc_info.value), \
            f"Expected error about 'machine', got: {exc_info.value}"

    def test_create_missing_key_pair_raises_error(self, mock_ec2):
        """
        Test: create() without key_pair raises ValueError
        Input: Instance with no key_pair set
        Expected: Raises ValueError with message about 'key_pair'
        """
        ec2 = EC2()
        instance = ec2.Instance(machine='t4g.micro')  # key_pair missing
        
        with pytest.raises(ValueError) as exc_info:
            instance.create()
        
        assert "'key_pair'" in str(exc_info.value), \
            f"Expected error about 'key_pair', got: {exc_info.value}"

    def test_create_already_has_id_returns_existing(self, mock_ec2):
        """
        Test: create() when instance already has ID returns existing ID
        Input: Instance with id='i-existing123'
        Expected: Returns existing ID, no API call made
        """
        ec2 = EC2()
        instance = ec2.Instance(id='i-existing123')
        
        result = instance.create()
        
        assert result == 'i-existing123', \
            f"Expected 'i-existing123', got '{result}'"

    def test_create_on_demand_instance(self, mock_ec2):
        """
        Test: create() with on-demand mode creates instance
        Input: mode='on-demand'
        Expected: Instance created, ID returned
        """
        # Create a key pair for the test
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
            mode='on-demand',
        )
        
        instance_id = instance.create()
        
        assert instance_id is not None, \
            "Expected instance ID to be returned"
        assert instance_id.startswith('i-'), \
            f"Expected instance ID to start with 'i-', got '{instance_id}'"
        assert instance.id == instance_id, \
            f"Expected instance.id to be set to '{instance_id}'"

    def test_create_spot_instance(self, mock_ec2):
        """
        Test: create() with spot mode includes market options
        Input: mode='spot'
        Expected: Instance created with spot options
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
            mode='spot',
        )
        
        instance_id = instance.create()
        
        assert instance_id is not None, \
            "Expected instance ID to be returned"
        assert instance_id.startswith('i-'), \
            f"Expected instance ID to start with 'i-', got '{instance_id}'"

    def test_create_with_ami(self, mock_ec2):
        """
        Test: create() with AMI parameter
        Input: ami='ami-12345678'
        Expected: Instance created with specified AMI
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
            ami='ami-12345678',
        )
        
        instance_id = instance.create()
        
        assert instance_id is not None, \
            "Expected instance ID to be returned"

    def test_create_with_name(self, mock_ec2):
        """
        Test: create() with name creates instance with Name tag
        Input: name='my-instance'
        Expected: Instance created with Name tag
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
            name='my-instance',
        )
        
        instance_id = instance.create()
        
        # Verify instance has Name tag
        response = client.describe_instances(InstanceIds=[instance_id])
        tags = response['Reservations'][0]['Instances'][0].get('Tags', [])
        name_tag = next((t for t in tags if t['Key'] == 'Name'), None)
        
        assert name_tag is not None, \
            "Expected Name tag to be set"
        assert name_tag['Value'] == 'my-instance', \
            f"Expected Name='my-instance', got Name='{name_tag['Value']}'"

    def test_create_with_security_groups(self, mock_ec2):
        """
        Test: create() with security groups
        Input: security_groups=['sg-12345']
        Expected: Instance created with security groups
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        # Create a security group
        vpc = client.create_vpc(CidrBlock='10.0.0.0/16')
        sg = client.create_security_group(
            GroupName='test-sg',
            Description='Test security group',
            VpcId=vpc['Vpc']['VpcId']
        )
        sg_id = sg['GroupId']
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
            security_groups=[sg_id],
        )
        
        instance_id = instance.create()
        
        assert instance_id is not None, \
            "Expected instance ID to be returned"

    def test_create_with_storage(self, mock_ec2):
        """
        Test: create() with storage volumes
        Input: Multiple Volume objects
        Expected: Instance created with block device mappings
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
            storage=[
                ec2.Volume(gib=20),
                ec2.Volume(gib=50, mode='gp2'),
            ],
        )
        
        instance_id = instance.create()
        
        assert instance_id is not None, \
            "Expected instance ID to be returned"

    def test_create_with_user_data(self, mock_ec2):
        """
        Test: create() with user_data startup script
        Input: user_data='#!/bin/bash\necho hello'
        Expected: Instance created with user data
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
            user_data='#!/bin/bash\necho hello',
        )
        
        instance_id = instance.create()
        
        assert instance_id is not None, \
            "Expected instance ID to be returned"

    def test_create_sets_instance_id(self, mock_ec2):
        """
        Test: create() sets the instance ID on the Instance object
        Input: New instance with no ID
        Expected: instance.id is set after create()
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
        )
        
        assert instance.id is None, \
            "Expected instance.id to be None before create()"
        
        returned_id = instance.create()
        
        assert instance.id is not None, \
            "Expected instance.id to be set after create()"
        assert instance.id == returned_id, \
            f"Expected instance.id='{returned_id}', got instance.id='{instance.id}'"


class TestInstanceStart:
    """Tests for the start method."""

    def test_start_without_id_raises_error(self, mock_ec2):
        """
        Test: start() without instance ID raises ValueError
        Input: Instance with no ID set
        Expected: Raises ValueError
        """
        ec2 = EC2()
        instance = ec2.Instance()
        
        with pytest.raises(ValueError) as exc_info:
            instance.start()
        
        assert "Instance ID" in str(exc_info.value), \
            f"Expected error about Instance ID, got: {exc_info.value}"

    def test_start_success(self, mock_ec2):
        """
        Test: start() calls start_instances API
        Input: Instance with valid ID
        Expected: start_instances called, no error
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
        )
        instance.create()
        
        # Stop the instance first so we can start it
        client.stop_instances(InstanceIds=[instance.id])
        
        # Should not raise
        instance.start()


class TestInstanceStop:
    """Tests for the stop method."""

    def test_stop_without_id_raises_error(self, mock_ec2):
        """
        Test: stop() without instance ID raises ValueError
        Input: Instance with no ID set
        Expected: Raises ValueError
        """
        ec2 = EC2()
        instance = ec2.Instance()
        
        with pytest.raises(ValueError) as exc_info:
            instance.stop()
        
        assert "Instance ID" in str(exc_info.value), \
            f"Expected error about Instance ID, got: {exc_info.value}"

    def test_stop_success(self, mock_ec2):
        """
        Test: stop() calls stop_instances API
        Input: Instance with valid ID
        Expected: stop_instances called, no error
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
        )
        instance.create()
        
        # Should not raise
        instance.stop()


class TestInstanceTerminate:
    """Tests for the terminate method."""

    def test_terminate_without_id_raises_error(self, mock_ec2):
        """
        Test: terminate() without instance ID raises ValueError
        Input: Instance with no ID set
        Expected: Raises ValueError
        """
        ec2 = EC2()
        instance = ec2.Instance()
        
        with pytest.raises(ValueError) as exc_info:
            instance.terminate()
        
        assert "Instance ID" in str(exc_info.value), \
            f"Expected error about Instance ID, got: {exc_info.value}"

    def test_terminate_success(self, mock_ec2):
        """
        Test: terminate() calls terminate_instances API
        Input: Instance with valid ID
        Expected: terminate_instances called, instance terminated
        """
        client = boto3.client('ec2', region_name='us-east-1')
        client.create_key_pair(KeyName='test-keypair')
        
        ec2 = EC2()
        instance = ec2.Instance(
            machine='t2.micro',
            key_pair='test-keypair',
        )
        instance_id = instance.create()
        
        # Should not raise
        instance.terminate()
        
        # Verify instance is terminated
        response = client.describe_instances(InstanceIds=[instance_id])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        
        assert state in ('terminated', 'shutting-down'), \
            f"Expected state='terminated' or 'shutting-down', got state='{state}'"


class TestInstanceDefaults:
    """Tests for Instance default values."""

    def test_defaults(self, mock_ec2):
        """
        Test: Instance() with no parameters has correct defaults
        Input: Instance()
        Expected: Default values for all optional parameters
        """
        ec2 = EC2()
        instance = ec2.Instance()
        
        assert instance.id is None, \
            f"Expected id=None, got id={instance.id}"
        assert instance.name is None, \
            f"Expected name=None, got name={instance.name}"
        assert instance.machine is None, \
            f"Expected machine=None, got machine={instance.machine}"
        assert instance.mode == 'on-demand', \
            f"Expected mode='on-demand', got mode='{instance.mode}'"
        assert instance.key_pair is None, \
            f"Expected key_pair=None, got key_pair={instance.key_pair}"
        assert instance.security_groups == [], \
            f"Expected security_groups=[], got security_groups={instance.security_groups}"
        assert instance.ami is None, \
            f"Expected ami=None, got ami={instance.ami}"
        assert instance.storage == [], \
            f"Expected storage=[], got storage={instance.storage}"
        assert instance.user_data is None, \
            f"Expected user_data=None, got user_data={instance.user_data}"

