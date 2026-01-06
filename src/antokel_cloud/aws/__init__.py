from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
  from .s3 import S3
  from .ec2 import EC2


class AntokelAws:
  """
  Main entry point for AWS services.
  
  Credentials are read from environment variables by default:
  - AWS_REGION (or AWS_DEFAULT_REGION)
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  
  Usage:
    aws = AntokelAws()
    s3 = aws.S3('my-bucket')
    ec2 = aws.EC2()
  """
  
  def __init__(
    self,
    region: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
  ):
    self.region = region or os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION')
    self.access_key = access_key or os.environ.get('AWS_ACCESS_KEY_ID')
    self.secret_key = secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
  
  def S3(self, bucket: str, prefix: Optional[str] = None) -> S3:
    """
    Create an S3 client for the specified bucket.
    
    Args:
      bucket: The S3 bucket name
      prefix: Optional prefix (folder path) to prepend to all operations
      
    Returns:
      S3 client instance
    """
    from .s3 import S3 as S3Client
    return S3Client(
      bucket=bucket,
      prefix=prefix,
      region=self.region,
      access_key=self.access_key,
      secret_key=self.secret_key,
    )
  
  def EC2(self) -> EC2:
    """
    Create an EC2 client.
    
    Returns:
      EC2 client instance
    """
    from .ec2 import EC2 as EC2Client
    return EC2Client(
      region=self.region,
      access_key=self.access_key,
      secret_key=self.secret_key,
    )

