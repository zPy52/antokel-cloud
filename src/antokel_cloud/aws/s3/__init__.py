from __future__ import annotations

from typing import Optional

import boto3

from .text import S3Text


class S3:
  """
  Simplified S3 client for common file operations.
  
  Supports an optional prefix that will be prepended to all cloud paths.
  
  Usage:
    aws = AntokelAws()
    s3 = aws.S3('my-bucket', prefix='folder1/route/2')
    s3.upload('local/file.pdf', 'remote/file.pdf')
    s3.download('remote/file.pdf', 'local/file.pdf')
  """
  
  def __init__(
    self,
    bucket: str,
    prefix: Optional[str] = None,
    region: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
  ):
    self._bucket = bucket
    self._prefix = self._normalize_prefix(prefix)
    
    session_kwargs = {}
    if region:
      session_kwargs['region_name'] = region
    if access_key:
      session_kwargs['aws_access_key_id'] = access_key
    if secret_key:
      session_kwargs['aws_secret_access_key'] = secret_key
    
    self._client = boto3.client('s3', **session_kwargs)
    self._text = S3Text(self)
  
  @staticmethod
  def _normalize_prefix(prefix: Optional[str]) -> str:
    """Normalize prefix to ensure consistent path handling."""
    if not prefix:
      return ''
    # Remove leading slash, ensure trailing slash
    prefix = prefix.lstrip('/')
    if prefix and not prefix.endswith('/'):
      prefix += '/'
    return prefix
  
  def _resolve_key(self, cloud: str) -> str:
    """Resolve a cloud path to a full S3 key with prefix."""
    cloud = cloud.lstrip('/')
    return f"{self._prefix}{cloud}"
  
  @property
  def as_text(self) -> S3Text:
    """
    Access text-based operations.
    
    Returns:
      S3Text instance for read/write/stream operations
    """
    return self._text
  
  def upload(self, local: str, cloud: str) -> None:
    """
    Upload a local file to S3.
    
    Args:
      local: Path to the local file
      cloud: S3 key (path) to upload to
    """
    key = self._resolve_key(cloud)
    self._client.upload_file(local, self._bucket, key)
  
  def download(self, cloud: str, local: str) -> None:
    """
    Download a file from S3 to local filesystem.
    
    Args:
      cloud: S3 key (path) to download from
      local: Path to save the file locally
    """
    key = self._resolve_key(cloud)
    self._client.download_file(self._bucket, key, local)
  
  def remove(self, cloud: str) -> None:
    """
    Delete a file from S3.
    
    Args:
      cloud: S3 key (path) to delete
    """
    key = self._resolve_key(cloud)
    self._client.delete_object(Bucket=self._bucket, Key=key)
  
  def move(self, original: str, new: str) -> None:
    """
    Move a file within S3 (copy then delete original).
    
    Args:
      original: Source S3 key (path)
      new: Destination S3 key (path)
    """
    original_key = self._resolve_key(original)
    new_key = self._resolve_key(new)
    
    # Copy to new location
    self._client.copy_object(
      Bucket=self._bucket,
      CopySource={'Bucket': self._bucket, 'Key': original_key},
      Key=new_key,
    )
    
    # Delete original
    self._client.delete_object(Bucket=self._bucket, Key=original_key)

