from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
  from . import S3


class S3Text:
  """
  Text-based operations for S3 files.
  
  Provides methods to read, write, and stream text content from S3.
  """
  
  def __init__(self, s3: S3):
    self._s3 = s3
  
  def read(self, cloud: str) -> str:
    """
    Read the content of a text file from S3.
    
    Args:
      cloud: The S3 key (path) to read from
      
    Returns:
      The file content as a string
    """
    key = self._s3._resolve_key(cloud)
    response = self._s3._client.get_object(Bucket=self._s3._bucket, Key=key)
    return response['Body'].read().decode('utf-8')
  
  def write(self, content: str, cloud: str) -> None:
    """
    Write text content to an S3 file.
    
    Args:
      content: The text content to write
      cloud: The S3 key (path) to write to
    """
    key = self._s3._resolve_key(cloud)
    self._s3._client.put_object(
      Bucket=self._s3._bucket,
      Key=key,
      Body=content.encode('utf-8'),
    )
  
  def stream_lines(self, cloud: str) -> Iterator[str]:
    """
    Stream a text file from S3 line by line.
    
    This is memory-efficient for large files like CSVs.
    
    Args:
      cloud: The S3 key (path) to stream from
      
    Yields:
      Each line from the file as a string (without newline characters)
    """
    key = self._s3._resolve_key(cloud)
    response = self._s3._client.get_object(Bucket=self._s3._bucket, Key=key)
    
    buffer = ''
    for chunk in response['Body'].iter_chunks():
      buffer += chunk.decode('utf-8')
      while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)
        yield line
    
    # Yield any remaining content (last line without newline)
    if buffer:
      yield buffer

