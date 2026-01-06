from __future__ import annotations

from typing import Optional, Literal

import boto3

from .volume import Volume
from .instance import Instance


class EC2:
  """
  Simplified EC2 client for instance management.
  
  Usage:
    aws = AntokelAws()
    ec2 = aws.EC2()
    
    instance = ec2.Instance(
      machine='t4g.micro',
      key_pair='my-keypair',
    )
    instance.create()
  """
  
  def __init__(
    self,
    region: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
  ):
    session_kwargs = {}
    if region:
      session_kwargs['region_name'] = region
    if access_key:
      session_kwargs['aws_access_key_id'] = access_key
    if secret_key:
      session_kwargs['aws_secret_access_key'] = secret_key
    
    self._client = boto3.client('ec2', **session_kwargs)
  
  def Instance(
    self,
    id: Optional[str] = None,
    name: Optional[str] = None,
    machine: Optional[str] = None,
    mode: Literal['spot', 'on-demand'] = 'on-demand',
    key_pair: Optional[str] = None,
    security_groups: Optional[list[str]] = None,
    ami: Optional[str] = None,
    storage: Optional[list[Volume]] = None,
    user_data: Optional[str] = None,
  ) -> Instance:
    """
    Create an Instance configuration.
    
    If `id` is provided, it references an existing instance.
    Otherwise, use `instance.create()` to launch a new instance.
    
    Args:
      id: Optional existing instance ID
      name: Optional instance name tag
      machine: Instance type (e.g., 't4g.micro')
      mode: 'spot' or 'on-demand' (default: 'on-demand')
      key_pair: SSH key pair name
      security_groups: List of security group IDs
      ami: AMI ID to use
      storage: List of Volume configurations
      user_data: Startup script (user data)
      
    Returns:
      Instance configuration object
    """
    return Instance(
      ec2=self,
      id=id,
      name=name,
      machine=machine,
      mode=mode,
      key_pair=key_pair,
      security_groups=security_groups,
      ami=ami,
      storage=storage,
      user_data=user_data,
    )
  
  def Volume(
    self,
    id: Optional[str] = None,
    gib: int = 8,
    mode: Literal['gp3', 'gp2', 'standard'] = 'gp3',
  ) -> Volume:
    """
    Create a Volume configuration.
    
    If `id` is provided, it references an existing volume snapshot.
    Otherwise, a new volume will be created with the instance.
    
    Args:
      id: Optional existing volume/snapshot ID
      gib: Size in GiB (default: 8)
      mode: Volume type - 'gp3', 'gp2', or 'standard' (default: 'gp3')
      
    Returns:
      Volume configuration object
    """
    return Volume(id=id, gib=gib, mode=mode)

