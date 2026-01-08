from __future__ import annotations

from typing import Optional, Literal, List, Union, Pattern

import re

import boto3

from .volume import Volume
from .instance import Instance
from .user_data.base import BaseUserData
from .user_data.container_fleet import ContainerFleet


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
    self.region = region
    self.access_key = access_key
    self.secret_key = secret_key

    session_kwargs = {}
    if region:
      session_kwargs['region_name'] = region
    if access_key:
      session_kwargs['aws_access_key_id'] = access_key
    if secret_key:
      session_kwargs['aws_secret_access_key'] = secret_key
    
    self._client = boto3.client('ec2', **session_kwargs)
    self.user_data = _UserDataFactory(self)
  
  def Instance(
    self,
    id: Optional[str] = None,
    name: Optional[str] = None,
    machine: Optional[str] = None,
    mode: Literal['spot', 'on-demand'] = 'on-demand',
    key_pair: Optional[str] = None,
    security_groups: Optional[List[str]] = None,
    ami: Optional[str] = None,
    storage: Optional[List[Volume]] = None,
    user_data: Optional[Union[str, BaseUserData]] = None,
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

  def find_by_name(self, regex: Union[str, Pattern[str]]) -> List[Instance]:
    """
    Find EC2 instances by their Name tag, using a Python regular expression.

    Example:
      ec2.find_by_name(regex='safegraph-.+')

    Args:
      regex: A regex pattern (string or compiled pattern) matched against the
        instance Name tag value.

    Returns:
      List of Instance wrappers (with id and name populated).
    """
    pattern = re.compile(regex) if isinstance(regex, str) else regex

    matches: List[Instance] = []
    next_token: Optional[str] = None

    while True:
      kwargs = {}
      if next_token:
        kwargs["NextToken"] = next_token

      resp = self._client.describe_instances(**kwargs)
      for reservation in resp.get("Reservations", []):
        for inst in reservation.get("Instances", []):
          tags = inst.get("Tags", []) or []
          name_tag = next((t for t in tags if t.get("Key") == "Name"), None)
          name = name_tag.get("Value") if name_tag else None
          if not name:
            continue

          if pattern.search(name):
            matches.append(self.Instance(id=inst.get("InstanceId"), name=name))

      next_token = resp.get("NextToken")
      if not next_token:
        break

    return matches


class _UserDataFactory:
  def __init__(self, ec2: EC2):
    self._ec2 = ec2

  def ContainerFleet(self, *args, **kwargs) -> ContainerFleet:
    return ContainerFleet(*args, **kwargs, ec2=self._ec2)


EC2.BaseUserData = BaseUserData  # type: ignore[attr-defined]