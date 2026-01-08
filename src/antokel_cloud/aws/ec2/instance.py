from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union, List, Literal

if TYPE_CHECKING:
  from . import EC2
  from .volume import Volume
  from .user_data import BaseUserData


class Instance:
  """
  EC2 Instance wrapper for simplified instance management.
  
  If `id` is provided, it references an existing instance.
  Otherwise, a new instance will be created when `create()` is called.
  
  Usage:
    ec2 = aws.EC2()
    instance = ec2.Instance(
      machine='t4g.micro',
      key_pair='my-keypair',
      mode='spot',
    )
    instance.create()
    instance.stop()
    instance.start()
    instance.terminate()
  """
  
  def __init__(
    self,
    ec2: EC2,
    id: Optional[str] = None,
    name: Optional[str] = None,
    machine: Optional[str] = None,
    mode: Literal['spot', 'on-demand'] = 'on-demand',
    key_pair: Optional[str] = None,
    security_groups: Optional[List[str]] = None,
    ami: Optional[str] = None,
    storage: Optional[List[Volume]] = None,
    user_data: Optional[Union[str, BaseUserData]] = None,
  ):
    self._ec2 = ec2
    self.id = id
    self.name = name
    self.machine = machine
    self.mode = mode
    self.key_pair = key_pair
    self.security_groups = security_groups or []
    self.ami = ami
    self.storage = storage or []
    self.user_data = user_data
  
  def create(self) -> str:
    """
    Create the EC2 instance.
    
    Returns:
      The instance ID
      
    Raises:
      ValueError: If required parameters are missing
    """
    if self.id:
      # Instance already exists
      return self.id
    
    if not self.machine:
      raise ValueError("'machine' is required to create an instance")
    if not self.key_pair:
      raise ValueError("'key_pair' is required to create an instance")
    
    # Build run_instances parameters
    params = {
      'InstanceType': self.machine,
      'KeyName': self.key_pair,
      'MinCount': 1,
      'MaxCount': 1,
    }
    
    if self.ami:
      params['ImageId'] = self.ami
    
    if self.security_groups:
      params['SecurityGroupIds'] = self.security_groups
    
    if self.name:
      params['TagSpecifications'] = [{
        'ResourceType': 'instance',
        'Tags': [{'Key': 'Name', 'Value': self.name}]
      }]
    
    if self.user_data:
      params['UserData'] = str(self.user_data)
    
    # Handle storage/volumes
    if self.storage:
      device_names = ['/dev/xvda', '/dev/xvdb', '/dev/xvdc', '/dev/xvdd', '/dev/xvde']
      block_devices = []
      for i, volume in enumerate(self.storage):
        if i < len(device_names):
          block_devices.append(volume.to_block_device_mapping(device_names[i]))
      if block_devices:
        params['BlockDeviceMappings'] = block_devices
    
    # Handle spot vs on-demand
    if self.mode == 'spot':
      params['InstanceMarketOptions'] = {
        'MarketType': 'spot',
        'SpotOptions': {
          'SpotInstanceType': 'one-time',
        }
      }
    
    response = self._ec2._client.run_instances(**params)
    self.id = response['Instances'][0]['InstanceId']
    return self.id
  
  def start(self) -> None:
    """
    Start the instance.
    
    Raises:
      ValueError: If instance ID is not set
    """
    if not self.id:
      raise ValueError("Instance ID is not set. Call create() first or provide an ID.")
    
    self._ec2._client.start_instances(InstanceIds=[self.id])
  
  def stop(self) -> None:
    """
    Stop the instance.
    
    Raises:
      ValueError: If instance ID is not set
    """
    if not self.id:
      raise ValueError("Instance ID is not set. Call create() first or provide an ID.")
    
    self._ec2._client.stop_instances(InstanceIds=[self.id])
  
  def terminate(self) -> None:
    """
    Terminate the instance.
    
    Raises:
      ValueError: If instance ID is not set
    """
    if not self.id:
      raise ValueError("Instance ID is not set. Call create() first or provide an ID.")
    
    self._ec2._client.terminate_instances(InstanceIds=[self.id])