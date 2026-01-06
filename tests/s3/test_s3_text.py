"""
Tests for S3Text text-based operations.

Tests read, write, and stream_lines functionality.
"""

import boto3
import pytest

from antokel_cloud.aws.s3 import S3


class TestS3TextRead:
    """Tests for the read method."""

    def test_read_text_file(self, mock_s3):
        """
        Test: read() returns file content as string
        Input: S3 contains 'Hello World'
        Expected: Returns 'Hello World'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='hello.txt', Body=b'Hello World')
        
        s3 = S3(bucket='test-bucket')
        
        result = s3.as_text.read('hello.txt')
        
        assert result == 'Hello World', \
            f"Expected 'Hello World', got '{result}'"

    def test_read_utf8_content(self, mock_s3):
        """
        Test: read() correctly decodes UTF-8 content
        Input: S3 contains unicode 'Héllo Wörld'
        Expected: Decodes correctly to 'Héllo Wörld'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='unicode.txt', Body='Héllo Wörld'.encode('utf-8'))
        
        s3 = S3(bucket='test-bucket')
        
        result = s3.as_text.read('unicode.txt')
        
        assert result == 'Héllo Wörld', \
            f"Expected 'Héllo Wörld', got '{result}'"

    def test_read_with_prefix(self, mock_s3):
        """
        Test: read() works with S3 prefix
        Input: prefix='data/', cloud='file.txt'
        Expected: Reads from 'data/file.txt'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='data/file.txt', Body=b'prefixed content')
        
        s3 = S3(bucket='test-bucket', prefix='data')
        
        result = s3.as_text.read('file.txt')
        
        assert result == 'prefixed content', \
            f"Expected 'prefixed content', got '{result}'"

    def test_read_multiline_content(self, mock_s3):
        """
        Test: read() preserves multiline content
        Input: S3 contains 'line1\nline2\nline3'
        Expected: Returns full multiline string
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        content = 'line1\nline2\nline3'
        client.put_object(Bucket='test-bucket', Key='multiline.txt', Body=content.encode('utf-8'))
        
        s3 = S3(bucket='test-bucket')
        
        result = s3.as_text.read('multiline.txt')
        
        assert result == content, \
            f"Expected '{content}', got '{result}'"


class TestS3TextWrite:
    """Tests for the write method."""

    def test_write_text_content(self, mock_s3):
        """
        Test: write() creates object with UTF-8 body
        Input: write('content', 'file.txt')
        Expected: Object created with UTF-8 encoded body
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        
        s3 = S3(bucket='test-bucket')
        
        s3.as_text.write('Hello from write!', 'written.txt')
        
        # Verify content
        response = client.get_object(Bucket='test-bucket', Key='written.txt')
        content = response['Body'].read().decode('utf-8')
        
        assert content == 'Hello from write!', \
            f"Expected 'Hello from write!', got '{content}'"

    def test_write_utf8_content(self, mock_s3):
        """
        Test: write() correctly encodes UTF-8 content
        Input: write('Héllo Wörld', 'file.txt')
        Expected: Object has correctly encoded UTF-8 body
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        
        s3 = S3(bucket='test-bucket')
        
        s3.as_text.write('Héllo Wörld', 'unicode.txt')
        
        response = client.get_object(Bucket='test-bucket', Key='unicode.txt')
        content = response['Body'].read().decode('utf-8')
        
        assert content == 'Héllo Wörld', \
            f"Expected 'Héllo Wörld', got '{content}'"

    def test_write_with_prefix(self, mock_s3):
        """
        Test: write() works with S3 prefix
        Input: prefix='data/', cloud='file.txt'
        Expected: Writes to 'data/file.txt'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        
        s3 = S3(bucket='test-bucket', prefix='data')
        
        s3.as_text.write('prefixed write', 'file.txt')
        
        response = client.get_object(Bucket='test-bucket', Key='data/file.txt')
        content = response['Body'].read().decode('utf-8')
        
        assert content == 'prefixed write', \
            f"Expected 'prefixed write', got '{content}'"

    def test_write_overwrites_existing(self, mock_s3):
        """
        Test: write() overwrites existing object
        Input: Object exists, then write() called
        Expected: Object content replaced
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='existing.txt', Body=b'old content')
        
        s3 = S3(bucket='test-bucket')
        
        s3.as_text.write('new content', 'existing.txt')
        
        response = client.get_object(Bucket='test-bucket', Key='existing.txt')
        content = response['Body'].read().decode('utf-8')
        
        assert content == 'new content', \
            f"Expected 'new content', got '{content}'"


class TestS3TextStreamLines:
    """Tests for the stream_lines method."""

    def test_stream_lines_single_line(self, mock_s3):
        """
        Test: stream_lines() yields single line
        Input: S3 contains 'line1'
        Expected: Yields ['line1']
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='single.txt', Body=b'line1')
        
        s3 = S3(bucket='test-bucket')
        
        lines = list(s3.as_text.stream_lines('single.txt'))
        
        assert lines == ['line1'], \
            f"Expected ['line1'], got {lines}"

    def test_stream_lines_multiple_lines(self, mock_s3):
        """
        Test: stream_lines() yields each line
        Input: S3 contains 'line1\nline2\nline3'
        Expected: Yields ['line1', 'line2', 'line3']
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        content = 'line1\nline2\nline3'
        client.put_object(Bucket='test-bucket', Key='multi.txt', Body=content.encode('utf-8'))
        
        s3 = S3(bucket='test-bucket')
        
        lines = list(s3.as_text.stream_lines('multi.txt'))
        
        assert lines == ['line1', 'line2', 'line3'], \
            f"Expected ['line1', 'line2', 'line3'], got {lines}"

    def test_stream_lines_no_trailing_newline(self, mock_s3):
        """
        Test: stream_lines() handles file without trailing newline
        Input: S3 contains 'line1\nline2' (no trailing newline)
        Expected: Yields both lines correctly
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        content = 'line1\nline2'
        client.put_object(Bucket='test-bucket', Key='no-trailing.txt', Body=content.encode('utf-8'))
        
        s3 = S3(bucket='test-bucket')
        
        lines = list(s3.as_text.stream_lines('no-trailing.txt'))
        
        assert lines == ['line1', 'line2'], \
            f"Expected ['line1', 'line2'], got {lines}"

    def test_stream_lines_with_trailing_newline(self, mock_s3):
        """
        Test: stream_lines() handles file with trailing newline
        Input: S3 contains 'line1\nline2\n' (with trailing newline)
        Expected: Yields ['line1', 'line2'] without empty line
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        content = 'line1\nline2\n'
        client.put_object(Bucket='test-bucket', Key='trailing.txt', Body=content.encode('utf-8'))
        
        s3 = S3(bucket='test-bucket')
        
        lines = list(s3.as_text.stream_lines('trailing.txt'))
        
        # The implementation yields remaining buffer if not empty
        # A trailing newline means buffer will be empty at the end
        assert lines == ['line1', 'line2'], \
            f"Expected ['line1', 'line2'], got {lines}"

    def test_stream_lines_empty_file(self, mock_s3):
        """
        Test: stream_lines() handles empty file
        Input: S3 contains ''
        Expected: Yields nothing (empty iterator)
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='empty.txt', Body=b'')
        
        s3 = S3(bucket='test-bucket')
        
        lines = list(s3.as_text.stream_lines('empty.txt'))
        
        assert lines == [], \
            f"Expected [], got {lines}"

    def test_stream_lines_with_prefix(self, mock_s3):
        """
        Test: stream_lines() works with S3 prefix
        Input: prefix='data/', cloud='file.txt'
        Expected: Streams from 'data/file.txt'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        content = 'prefixed\nlines'
        client.put_object(Bucket='test-bucket', Key='data/file.txt', Body=content.encode('utf-8'))
        
        s3 = S3(bucket='test-bucket', prefix='data')
        
        lines = list(s3.as_text.stream_lines('file.txt'))
        
        assert lines == ['prefixed', 'lines'], \
            f"Expected ['prefixed', 'lines'], got {lines}"

    def test_stream_lines_utf8_content(self, mock_s3):
        """
        Test: stream_lines() correctly handles UTF-8 content
        Input: S3 contains 'Héllo\nWörld'
        Expected: Yields ['Héllo', 'Wörld']
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        content = 'Héllo\nWörld'
        client.put_object(Bucket='test-bucket', Key='unicode.txt', Body=content.encode('utf-8'))
        
        s3 = S3(bucket='test-bucket')
        
        lines = list(s3.as_text.stream_lines('unicode.txt'))
        
        assert lines == ['Héllo', 'Wörld'], \
            f"Expected ['Héllo', 'Wörld'], got {lines}"

    def test_stream_lines_is_iterator(self, mock_s3):
        """
        Test: stream_lines() returns an iterator (memory-efficient)
        Input: Call stream_lines()
        Expected: Returns iterator, not list
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='iter.txt', Body=b'line1\nline2')
        
        s3 = S3(bucket='test-bucket')
        
        result = s3.as_text.stream_lines('iter.txt')
        
        # Check it's an iterator, not a list
        assert hasattr(result, '__iter__') and hasattr(result, '__next__'), \
            "Expected stream_lines to return an iterator"

