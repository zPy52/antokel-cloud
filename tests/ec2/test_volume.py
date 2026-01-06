"""
Tests for Volume configuration dataclass.

Tests default values and to_block_device_mapping conversion.
"""

import pytest

from antokel_cloud.aws.ec2.volume import Volume


class TestVolumeDefaults:
    """Tests for Volume default values."""

    def test_default_values(self):
        """
        Test: Volume() with no arguments uses defaults
        Input: Volume()
        Expected: id=None, gib=8, mode='gp3'
        """
        volume = Volume()
        
        assert volume.id is None, \
            f"Expected id=None, got id={volume.id}"
        assert volume.gib == 8, \
            f"Expected gib=8, got gib={volume.gib}"
        assert volume.mode == 'gp3', \
            f"Expected mode='gp3', got mode='{volume.mode}'"

    def test_custom_gib(self):
        """
        Test: Volume() with custom gib
        Input: Volume(gib=100)
        Expected: gib=100
        """
        volume = Volume(gib=100)
        
        assert volume.gib == 100, \
            f"Expected gib=100, got gib={volume.gib}"

    def test_gp2_mode(self):
        """
        Test: Volume() with gp2 mode
        Input: Volume(mode='gp2')
        Expected: mode='gp2'
        """
        volume = Volume(mode='gp2')
        
        assert volume.mode == 'gp2', \
            f"Expected mode='gp2', got mode='{volume.mode}'"

    def test_standard_mode(self):
        """
        Test: Volume() with standard mode
        Input: Volume(mode='standard')
        Expected: mode='standard'
        """
        volume = Volume(mode='standard')
        
        assert volume.mode == 'standard', \
            f"Expected mode='standard', got mode='{volume.mode}'"

    def test_with_snapshot_id(self):
        """
        Test: Volume() with snapshot ID
        Input: Volume(id='snap-abc123')
        Expected: id='snap-abc123'
        """
        volume = Volume(id='snap-abc123')
        
        assert volume.id == 'snap-abc123', \
            f"Expected id='snap-abc123', got id='{volume.id}'"


class TestVolumeToBlockDeviceMapping:
    """Tests for to_block_device_mapping method."""

    def test_new_volume_default_device(self):
        """
        Test: to_block_device_mapping() for new volume with default device
        Input: Volume(gib=20), no device_name
        Expected: Dict with VolumeSize=20, DeleteOnTermination=True, default device
        """
        volume = Volume(gib=20)
        
        result = volume.to_block_device_mapping()
        
        expected = {
            'DeviceName': '/dev/xvda',
            'Ebs': {
                'VolumeSize': 20,
                'DeleteOnTermination': True,
                'VolumeType': 'gp3',
            }
        }
        
        assert result == expected, \
            f"Expected {expected}, got {result}"

    def test_new_volume_custom_device(self):
        """
        Test: to_block_device_mapping() with custom device name
        Input: Volume(gib=10), device_name='/dev/xvdb'
        Expected: Dict with DeviceName='/dev/xvdb'
        """
        volume = Volume(gib=10)
        
        result = volume.to_block_device_mapping('/dev/xvdb')
        
        assert result['DeviceName'] == '/dev/xvdb', \
            f"Expected DeviceName='/dev/xvdb', got DeviceName='{result['DeviceName']}'"

    def test_new_volume_gp2_mode(self):
        """
        Test: to_block_device_mapping() with gp2 volume type
        Input: Volume(gib=8, mode='gp2')
        Expected: VolumeType='gp2'
        """
        volume = Volume(gib=8, mode='gp2')
        
        result = volume.to_block_device_mapping()
        
        assert result['Ebs']['VolumeType'] == 'gp2', \
            f"Expected VolumeType='gp2', got VolumeType='{result['Ebs']['VolumeType']}'"

    def test_new_volume_standard_mode(self):
        """
        Test: to_block_device_mapping() with standard volume type
        Input: Volume(gib=8, mode='standard')
        Expected: VolumeType='standard'
        """
        volume = Volume(gib=8, mode='standard')
        
        result = volume.to_block_device_mapping()
        
        assert result['Ebs']['VolumeType'] == 'standard', \
            f"Expected VolumeType='standard', got VolumeType='{result['Ebs']['VolumeType']}'"

    def test_snapshot_volume(self):
        """
        Test: to_block_device_mapping() for existing snapshot
        Input: Volume(id='snap-123')
        Expected: Dict with SnapshotId, DeleteOnTermination=False
        """
        volume = Volume(id='snap-123')
        
        result = volume.to_block_device_mapping()
        
        expected = {
            'DeviceName': '/dev/xvda',
            'Ebs': {
                'SnapshotId': 'snap-123',
                'DeleteOnTermination': False,
                'VolumeType': 'gp3',
            }
        }
        
        assert result == expected, \
            f"Expected {expected}, got {result}"

    def test_snapshot_volume_custom_device(self):
        """
        Test: to_block_device_mapping() for snapshot with custom device
        Input: Volume(id='snap-456'), device_name='/dev/xvdc'
        Expected: DeviceName='/dev/xvdc', SnapshotId set
        """
        volume = Volume(id='snap-456')
        
        result = volume.to_block_device_mapping('/dev/xvdc')
        
        assert result['DeviceName'] == '/dev/xvdc', \
            f"Expected DeviceName='/dev/xvdc', got '{result['DeviceName']}'"
        assert result['Ebs']['SnapshotId'] == 'snap-456', \
            f"Expected SnapshotId='snap-456', got '{result['Ebs']['SnapshotId']}'"

    def test_snapshot_volume_delete_on_termination_false(self):
        """
        Test: Snapshot volumes have DeleteOnTermination=False
        Input: Volume(id='snap-789')
        Expected: DeleteOnTermination=False
        """
        volume = Volume(id='snap-789')
        
        result = volume.to_block_device_mapping()
        
        assert result['Ebs']['DeleteOnTermination'] is False, \
            f"Expected DeleteOnTermination=False, got {result['Ebs']['DeleteOnTermination']}"

    def test_new_volume_delete_on_termination_true(self):
        """
        Test: New volumes have DeleteOnTermination=True
        Input: Volume(gib=10)
        Expected: DeleteOnTermination=True
        """
        volume = Volume(gib=10)
        
        result = volume.to_block_device_mapping()
        
        assert result['Ebs']['DeleteOnTermination'] is True, \
            f"Expected DeleteOnTermination=True, got {result['Ebs']['DeleteOnTermination']}"

    def test_snapshot_preserves_volume_type(self):
        """
        Test: Snapshot volume preserves mode as VolumeType
        Input: Volume(id='snap-123', mode='gp2')
        Expected: VolumeType='gp2'
        """
        volume = Volume(id='snap-123', mode='gp2')
        
        result = volume.to_block_device_mapping()
        
        assert result['Ebs']['VolumeType'] == 'gp2', \
            f"Expected VolumeType='gp2', got '{result['Ebs']['VolumeType']}'"

