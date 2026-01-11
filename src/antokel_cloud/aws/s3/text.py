from __future__ import annotations

from csv import DictReader
from codecs import getincrementaldecoder
from typing import TYPE_CHECKING, Iterator, Dict

if TYPE_CHECKING:
  from . import S3


class S3Text:
  """
  Text-based operations for S3 files.
  """
  
  def __init__(self, s3: S3):
    self._s3 = s3
  
  def read(self, cloud: str) -> str:
    key = self._s3._resolve_key(cloud)
    response = self._s3._client.get_object(Bucket=self._s3._bucket, Key=key)
    return response['Body'].read().decode('utf-8')
  
  def write(self, content: str, cloud: str) -> None:
    key = self._s3._resolve_key(cloud)
    self._s3._client.put_object(
      Bucket=self._s3._bucket,
      Key=key,
      Body=content.encode('utf-8'),
    )
  
  def stream_lines(self, cloud: str) -> Iterator[str]:
    """
    Stream a text file from S3 line by line.
    """
    key = self._s3._resolve_key(cloud)
    response = self._s3._client.get_object(Bucket=self._s3._bucket, Key=key)
    
    decoder = getincrementaldecoder("utf-8")(errors='strict')
    buffer = ""
    
    for chunk in response['Body'].iter_chunks():
      buffer += decoder.decode(chunk, final=False)
      
      while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)
        yield line
    
    buffer += decoder.decode(b"", final=True)
    if buffer:
      yield buffer

  def stream_csv(self, cloud: str, delimiter: str = ',') -> Iterator[Dict[str, str]]:
    """
    Stream a CSV file from S3 as a sequence of dictionaries.

    Args:
        cloud: The S3 key (path) to stream from.
        delimiter: The CSV separator (default: comma).

    Yields:
        A dictionary for each row mapping header names to values.
    """
    lines = self.stream_lines(cloud)
    reader = DictReader(lines, delimiter=delimiter)
    
    yield from reader