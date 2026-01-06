# Antokel Cloud SDK

**Antokel Cloud SDK** is a simplified Python SDK for AWS services, designed specifically for Antokel engineers. It provides clean, easy-to-use interfaces for common cloud operations while maintaining full compatibility with boto3 under the hood.

## Features

- **Simplified S3 operations**: Upload, download, move, and remove files with automatic prefix handling
- **Text file operations**: Read, write, and stream text files from S3
- **EC2 instance management**: Launch, start, stop, and terminate EC2 instances
- **Automatic credential management**: Uses AWS environment variables by default
- **Type-safe**: Full type hints and modern Python support

Project status: **alpha** (API may change).

## Installation

From PyPI:

```bash
pip install antokel-cloud
```

From source (this repo):

```bash
pip install -e .
```

**Requirements**: Python 3.8+, boto3

## Quick Start

```python
from antokel_cloud.aws import AntokelAws

# Initialize with automatic credential detection
aws = AntokelAws()

# S3 operations
s3 = aws.S3('my-bucket')
s3.upload('local/file.pdf', 'remote/file.pdf')
s3.download('remote/file.pdf', 'local/file.pdf')

# EC2 operations
ec2 = aws.EC2()
instance = ec2.Instance(machine='t4g.micro', key_pair='my-keypair')
instance.create()
```

## S3 Usage

### Basic File Operations

```python
from antokel_cloud.aws import AntokelAws

aws = AntokelAws()
s3 = aws.S3('my-bucket')

# Upload a file
s3.upload('path/to/local/file.pdf', 'remote/path/file.pdf')

# Download a file
s3.download('remote/path/file.pdf', 'path/to/local/file.pdf')

# Move a file within S3
s3.move('old/path/file.pdf', 'new/path/file.pdf')

# Delete a file
s3.remove('remote/path/file.pdf')
```

### Working with Prefixes

You can set a prefix to organize files in a specific "folder":

```python
# All operations will be scoped to 'data/reports/'
s3 = aws.S3('my-bucket', prefix='data/reports/')

s3.upload('local/report.pdf', 'monthly.pdf')  # -> data/reports/monthly.pdf
s3.download('monthly.pdf', 'local/report.pdf')  # <- data/reports/monthly.pdf
```

### Text File Operations

```python
from antokel_cloud.aws import AntokelAws

aws = AntokelAws()
s3 = aws.S3('my-bucket')

# Read text content
content = s3.as_text.read('config/settings.json')
print(content)

# Write text content
s3.as_text.write('{"setting": "value"}', 'config/settings.json')

# Stream large files line by line (memory efficient)
for line in s3.as_text.stream_lines('data/large-file.csv'):
    print(line)
```

## EC2 Usage

### Creating and Managing Instances

```python
from antokel_cloud.aws import AntokelAws

aws = AntokelAws()
ec2 = aws.EC2()

# Create a new instance
instance = ec2.Instance(
    name='my-server',
    machine='t4g.micro',
    mode='on-demand',  # or 'spot'
    key_pair='my-keypair',
    security_groups=['sg-01234567'],
    storage=[
        ec2.Volume(gib=16, mode='gp3'),  # 16GB GP3 volume
    ],
    user_data='''#!/bin/bash
echo "Instance started"
'''
)

# Launch the instance
instance.create()
print(f"Instance created: {instance.id}")

# Control the instance
instance.start()
instance.stop()
instance.terminate()
```

### Working with Existing Instances

```python
# Reference an existing instance by ID
instance = ec2.Instance(id='i-0123456789abcdef0')
instance.start()
instance.stop()
```

### Volume Configuration

```python
# Different volume types
volumes = [
    ec2.Volume(gib=8, mode='gp3'),      # General purpose SSD (default)
    ec2.Volume(gib=100, mode='gp2'),    # Previous generation GP SSD
    ec2.Volume(gib=500, mode='standard'), # Magnetic
]

# Use existing volume snapshot
volume_from_snapshot = ec2.Volume(id='snap-0123456789abcdef0')
```

## Configuration

### AWS Credentials

The SDK automatically reads AWS credentials from environment variables:

```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

You can also pass credentials explicitly:

```python
aws = AntokelAws(
    region='us-west-2',
    access_key='your-access-key',
    secret_key='your-secret-key'
)
```

## API Reference

### AntokelAws

Main entry point for all AWS services.

```python
class AntokelAws:
    def __init__(
        self,
        region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ): ...

    def S3(self, bucket: str, prefix: Optional[str] = None) -> S3: ...

    def EC2(self) -> EC2: ...
```

### S3

Simplified S3 client with prefix support.

```python
class S3:
    def upload(self, local: str, cloud: str) -> None: ...
    def download(self, cloud: str, local: str) -> None: ...
    def remove(self, cloud: str) -> None: ...
    def move(self, original: str, new: str) -> None: ...

    @property
    def as_text(self) -> S3Text: ...
```

### S3Text

Text-based operations for S3 files.

```python
class S3Text:
    def read(self, cloud: str) -> str: ...
    def write(self, content: str, cloud: str) -> None: ...
    def stream_lines(self, cloud: str) -> Iterator[str]: ...
```

### EC2

EC2 client for instance management.

```python
class EC2:
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
    ) -> Instance: ...

    def Volume(
        self,
        id: Optional[str] = None,
        gib: int = 8,
        mode: Literal['gp3', 'gp2', 'standard'] = 'gp3',
    ) -> Volume: ...
```

### Instance

EC2 instance management.

```python
class Instance:
    @property
    def id(self) -> Optional[str]: ...

    def create(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def terminate(self) -> None: ...
```

## Notes

- **Prefix handling**: S3 prefixes are automatically normalized (leading/trailing slashes)
- **Credential precedence**: Explicit parameters override environment variables
- **Instance lifecycle**: New instances get a default 8GB GP3 root volume if none specified
- **Spot instances**: Use `mode='spot'` for cost savings, but instances may be terminated
- **Volume attachment**: Volumes are automatically attached during instance creation

## License

Apache-2.0. See `LICENSE`.
