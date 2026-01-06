"""
Tests for S3 client file operations.

Tests upload, download, remove, move, and prefix handling.
"""

import os
import tempfile

import boto3
import pytest

from antokel_cloud.aws.s3 import S3


class TestS3NormalizePrefix:
    """Tests for the _normalize_prefix static method."""

    def test_normalize_prefix_with_none(self):
        """
        Test: _normalize_prefix with None input
        Input: None
        Expected: Returns empty string ''
        """
        result = S3._normalize_prefix(None)
        
        assert result == '', \
            f"Expected '', got '{result}'"

    def test_normalize_prefix_with_empty_string(self):
        """
        Test: _normalize_prefix with empty string
        Input: ''
        Expected: Returns empty string ''
        """
        result = S3._normalize_prefix('')
        
        assert result == '', \
            f"Expected '', got '{result}'"

    def test_normalize_prefix_with_leading_slash(self):
        """
        Test: _normalize_prefix strips leading slash and adds trailing
        Input: '/folder'
        Expected: Returns 'folder/'
        """
        result = S3._normalize_prefix('/folder')
        
        assert result == 'folder/', \
            f"Expected 'folder/', got '{result}'"

    def test_normalize_prefix_without_trailing_slash(self):
        """
        Test: _normalize_prefix adds trailing slash
        Input: 'folder'
        Expected: Returns 'folder/'
        """
        result = S3._normalize_prefix('folder')
        
        assert result == 'folder/', \
            f"Expected 'folder/', got '{result}'"

    def test_normalize_prefix_already_correct(self):
        """
        Test: _normalize_prefix with already correct format
        Input: 'folder/'
        Expected: Returns 'folder/' unchanged
        """
        result = S3._normalize_prefix('folder/')
        
        assert result == 'folder/', \
            f"Expected 'folder/', got '{result}'"

    def test_normalize_prefix_nested_path(self):
        """
        Test: _normalize_prefix with nested path
        Input: '/data/subdir/folder'
        Expected: Returns 'data/subdir/folder/'
        """
        result = S3._normalize_prefix('/data/subdir/folder')
        
        assert result == 'data/subdir/folder/', \
            f"Expected 'data/subdir/folder/', got '{result}'"


class TestS3ResolveKey:
    """Tests for the _resolve_key method."""

    def test_resolve_key_no_prefix(self, mock_s3):
        """
        Test: _resolve_key without prefix
        Input: cloud='file.txt', prefix=''
        Expected: Returns 'file.txt'
        """
        s3 = S3(bucket='test-bucket', prefix=None)
        result = s3._resolve_key('file.txt')
        
        assert result == 'file.txt', \
            f"Expected 'file.txt', got '{result}'"

    def test_resolve_key_with_prefix(self, mock_s3):
        """
        Test: _resolve_key with prefix
        Input: cloud='file.txt', prefix='data/'
        Expected: Returns 'data/file.txt'
        """
        s3 = S3(bucket='test-bucket', prefix='data')
        result = s3._resolve_key('file.txt')
        
        assert result == 'data/file.txt', \
            f"Expected 'data/file.txt', got '{result}'"

    def test_resolve_key_strips_leading_slash(self, mock_s3):
        """
        Test: _resolve_key strips leading slash from cloud path
        Input: cloud='/file.txt', prefix='data/'
        Expected: Returns 'data/file.txt'
        """
        s3 = S3(bucket='test-bucket', prefix='data')
        result = s3._resolve_key('/file.txt')
        
        assert result == 'data/file.txt', \
            f"Expected 'data/file.txt', got '{result}'"

    def test_resolve_key_nested_path(self, mock_s3):
        """
        Test: _resolve_key with nested cloud path
        Input: cloud='subdir/file.txt', prefix='data/'
        Expected: Returns 'data/subdir/file.txt'
        """
        s3 = S3(bucket='test-bucket', prefix='data')
        result = s3._resolve_key('subdir/file.txt')
        
        assert result == 'data/subdir/file.txt', \
            f"Expected 'data/subdir/file.txt', got '{result}'"


class TestS3Upload:
    """Tests for the upload method."""

    def test_upload_success(self, mock_s3):
        """
        Test: upload() successfully uploads a file
        Input: Local file exists
        Expected: File uploaded to S3 with correct key
        """
        # Create mock bucket
        boto3.client('s3').create_bucket(Bucket='test-bucket')
        
        s3 = S3(bucket='test-bucket')
        
        # Create a temporary file to upload
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('Hello, S3!')
            temp_path = f.name
        
        try:
            s3.upload(temp_path, 'uploaded-file.txt')
            
            # Verify file was uploaded
            response = boto3.client('s3').get_object(
                Bucket='test-bucket', 
                Key='uploaded-file.txt'
            )
            content = response['Body'].read().decode('utf-8')
            
            assert content == 'Hello, S3!', \
                f"Expected 'Hello, S3!', got '{content}'"
        finally:
            os.unlink(temp_path)

    def test_upload_with_prefix(self, mock_s3):
        """
        Test: upload() with prefix prepends prefix to key
        Input: prefix='data/', cloud='file.txt'
        Expected: File uploaded to 'data/file.txt'
        """
        boto3.client('s3').create_bucket(Bucket='test-bucket')
        
        s3 = S3(bucket='test-bucket', prefix='data')
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('prefixed content')
            temp_path = f.name
        
        try:
            s3.upload(temp_path, 'file.txt')
            
            # Verify file was uploaded with prefix
            response = boto3.client('s3').get_object(
                Bucket='test-bucket', 
                Key='data/file.txt'
            )
            content = response['Body'].read().decode('utf-8')
            
            assert content == 'prefixed content', \
                f"Expected 'prefixed content', got '{content}'"
        finally:
            os.unlink(temp_path)


class TestS3Download:
    """Tests for the download method."""

    def test_download_success(self, mock_s3):
        """
        Test: download() successfully downloads a file
        Input: S3 object exists
        Expected: File downloaded to local path
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='remote-file.txt', Body=b'S3 content')
        
        s3 = S3(bucket='test-bucket')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = os.path.join(tmpdir, 'downloaded.txt')
            
            s3.download('remote-file.txt', local_path)
            
            with open(local_path, 'r') as f:
                content = f.read()
            
            assert content == 'S3 content', \
                f"Expected 'S3 content', got '{content}'"

    def test_download_with_prefix(self, mock_s3):
        """
        Test: download() with prefix resolves correct key
        Input: prefix='data/', cloud='file.txt'
        Expected: Downloads from 'data/file.txt'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='data/file.txt', Body=b'prefixed file')
        
        s3 = S3(bucket='test-bucket', prefix='data')
        
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = os.path.join(tmpdir, 'downloaded.txt')
            
            s3.download('file.txt', local_path)
            
            with open(local_path, 'r') as f:
                content = f.read()
            
            assert content == 'prefixed file', \
                f"Expected 'prefixed file', got '{content}'"


class TestS3Remove:
    """Tests for the remove method."""

    def test_remove_success(self, mock_s3):
        """
        Test: remove() deletes an object from S3
        Input: S3 object exists
        Expected: Object deleted from S3
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='to-delete.txt', Body=b'delete me')
        
        s3 = S3(bucket='test-bucket')
        
        s3.remove('to-delete.txt')
        
        # Verify object was deleted
        response = client.list_objects_v2(Bucket='test-bucket', Prefix='to-delete.txt')
        
        assert response.get('KeyCount', 0) == 0, \
            "Expected object to be deleted"

    def test_remove_with_prefix(self, mock_s3):
        """
        Test: remove() with prefix resolves correct key
        Input: prefix='data/', cloud='file.txt'
        Expected: Deletes 'data/file.txt'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='data/file.txt', Body=b'delete this')
        
        s3 = S3(bucket='test-bucket', prefix='data')
        
        s3.remove('file.txt')
        
        response = client.list_objects_v2(Bucket='test-bucket', Prefix='data/file.txt')
        
        assert response.get('KeyCount', 0) == 0, \
            "Expected object to be deleted"


class TestS3Move:
    """Tests for the move method."""

    def test_move_success(self, mock_s3):
        """
        Test: move() copies to new location and deletes original
        Input: Source object exists
        Expected: Object at new key, original deleted
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='original.txt', Body=b'move me')
        
        s3 = S3(bucket='test-bucket')
        
        s3.move('original.txt', 'new-location.txt')
        
        # Verify new location has content
        response = client.get_object(Bucket='test-bucket', Key='new-location.txt')
        content = response['Body'].read().decode('utf-8')
        
        assert content == 'move me', \
            f"Expected 'move me', got '{content}'"
        
        # Verify original is deleted
        original_response = client.list_objects_v2(Bucket='test-bucket', Prefix='original.txt')
        
        assert original_response.get('KeyCount', 0) == 0, \
            "Expected original object to be deleted"

    def test_move_with_prefix(self, mock_s3):
        """
        Test: move() with prefix applies prefix to both paths
        Input: prefix='data/', original='a.txt', new='b.txt'
        Expected: Moves from 'data/a.txt' to 'data/b.txt'
        """
        client = boto3.client('s3')
        client.create_bucket(Bucket='test-bucket')
        client.put_object(Bucket='test-bucket', Key='data/a.txt', Body=b'prefixed move')
        
        s3 = S3(bucket='test-bucket', prefix='data')
        
        s3.move('a.txt', 'b.txt')
        
        # Verify new location
        response = client.get_object(Bucket='test-bucket', Key='data/b.txt')
        content = response['Body'].read().decode('utf-8')
        
        assert content == 'prefixed move', \
            f"Expected 'prefixed move', got '{content}'"
        
        # Verify original deleted
        original_response = client.list_objects_v2(Bucket='test-bucket', Prefix='data/a.txt')
        
        assert original_response.get('KeyCount', 0) == 0, \
            "Expected original object to be deleted"


class TestS3AsTextProperty:
    """Tests for the as_text property."""

    def test_as_text_returns_s3text_instance(self, mock_s3):
        """
        Test: as_text property returns S3Text instance
        Input: Access s3.as_text
        Expected: Returns S3Text instance
        """
        from antokel_cloud.aws.s3.text import S3Text
        
        s3 = S3(bucket='test-bucket')
        
        text = s3.as_text
        
        assert isinstance(text, S3Text), \
            f"Expected S3Text instance, got {type(text)}"

    def test_as_text_returns_same_instance(self, mock_s3):
        """
        Test: as_text property returns the same instance each time
        Input: Access s3.as_text multiple times
        Expected: Same S3Text instance returned
        """
        s3 = S3(bucket='test-bucket')
        
        text1 = s3.as_text
        text2 = s3.as_text
        
        assert text1 is text2, \
            "Expected as_text to return the same instance"

