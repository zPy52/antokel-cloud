from __future__ import annotations

import shlex
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
  from .. import EC2


@dataclass
class AwsRuntimeCredentials:
  region: Optional[str] = None
  access_key: Optional[str] = None
  secret_key: Optional[str] = None


class BaseUserData(ABC):
  """
  Base class for EC2 UserData renderers.

  Instances are meant to be passed to `ec2.Instance(..., user_data=...)`.
  The EC2 `Instance` will pass `str(user_data)` to AWS, which calls `render()`.
  """

  def __init__(self, ec2: Optional["EC2"] = None):
    self._ec2 = ec2

  def bind(self, ec2: "EC2") -> "BaseUserData":
    self._ec2 = ec2
    return self

  def _parse_ecr_registry(self, image: str) -> str:
    # image like: 6695....dkr.ecr.us-east-1.amazonaws.com/repo[:tag]
    return image.split("/", 1)[0]
  
  def _shell_quote(self, v: str) -> str:
    return shlex.quote(v)

  def _aws_creds(self) -> AwsRuntimeCredentials:
    if not self._ec2:
      return AwsRuntimeCredentials()

    # EC2 is created by AntokelAws and may have region + keys in its boto session kwargs.
    # We keep a lightweight copy on the EC2 object (added in EC2.__init__).
    region = getattr(self._ec2, "region", None)
    access_key = getattr(self._ec2, "access_key", None)
    secret_key = getattr(self._ec2, "secret_key", None)
    return AwsRuntimeCredentials(region=region, access_key=access_key, secret_key=secret_key)

  @abstractmethod
  def render(self) -> str:
    raise NotImplementedError

  def __str__(self) -> str:
    return self.render().strip() + "\n"


