from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class Volume:
  """
  EBS Volume configuration for EC2 instances.
  
  If `id` is provided, it references an existing volume snapshot to attach.
  Otherwise, a new volume will be created with the specified configuration.
  
  Args:
    id: Optional existing volume/snapshot ID to attach
    gib: Size in GiB (required if id not provided)
    mode: Volume type - 'gp3', 'gp2', or 'standard' (default: 'gp3')
  """
  id: Optional[str] = None
  gib: int = 8
  mode: Literal['gp3', 'gp2', 'standard'] = 'gp3'
  
  def to_block_device_mapping(self, device_name: str = '/dev/xvda') -> dict:
    """
    Convert to boto3 BlockDeviceMapping format.
    
    Args:
      device_name: The device name (e.g., '/dev/xvda')
      
    Returns:
      BlockDeviceMapping dictionary for boto3
    """
    if self.id:
      # Reference existing snapshot
      return {
        'DeviceName': device_name,
        'Ebs': {
          'SnapshotId': self.id,
          'DeleteOnTermination': False,
          'VolumeType': self.mode,
        }
      }
    else:
      # Create new volume
      return {
        'DeviceName': device_name,
        'Ebs': {
          'VolumeSize': self.gib,
          'DeleteOnTermination': True,
          'VolumeType': self.mode,
        }
      }

