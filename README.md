# Antokel Cloud SDK

## Example usage for S3

```python
from antokel_cloud.aws import AntokelAws

aws = AntokelAws() # ... optional parameters for the region, access key and secret key. They're obtained from the env variables by default
# cloud = AntokelAws(region=..., access_key=..., secret_key=...)

s3 = aws.S3(bucket='bucket-name') # it can be positional too.
# s3 = aws.S3('bucket-name') 
# s3 = aws.S3('bucket-name', prefix='folder1/route/2') ... we can add an optional "prefix" that essentially establishes a folder/subfolder.
# s3 = aws.S3('bucket-name', prefix='folder1/route/2/')

s3.upload('path/to/local/file.pdf', 'path/without-prefix/on/s3.pdf')
# s3.upload(local='path/to/local/file.pdf', cloud='path/without-prefix/on/s3.pdf')
s3.remove('path/without-prefix/on/s3.pdf')
# s3.remove(cloud='path/without-prefix/on/s3.pdf')
s3.move('original/s3/path.pdf', 'new/s3/path.pdf') # this removes the original file and moves it to the new path.
# s3.move(local='original/s3/path.pdf', cloud='new/s3/path.pdf')

s3.download('path/without-prefix/on/s3.pdf', 'path/to/local/file.pdf')
# s3.download(cloud='path/without-prefix/on/s3.pdf', local='path/to/local/file.pdf')

s3.as_text.read('path/without-prefix/on/s3.txt') # this returns a string which reads the text from S3.
# s3.as_text.read(cloud='path/without-prefix/on/s3.txt')
content = 'example'
s3.as_text.write(content, 'path/without-prefix/on/s3.txt') # this returns a string which reads the text from S3.
# s3.as_text.write(content=content, cloud='path/without-prefix/on/s3.txt')

lines = s3.as_text.stream_lines('path/without-prefix/on/s3.csv') # this one streams, reading little by little, a file like a csv or a txt or similar as lines, which can be obtained from iterating it.
# lines = s3.as_text.stream_lines(cloud='path/without-prefix/on/s3.csv')
for line in lines:
  print(line) # for example, a .CSV line
```


## Example usage for EC2
```python
from antokel_cloud.aws import AntokelAws

aws = AntokelAws()

ec2 = aws.EC2()

instances = ec2.find_by_name(regex=r"safegraph-.+") # this is a list of instances

bootup_script = '''
echo "hello world"
'''.strip()

script = ec2.user_data.ContainerFleet(
  ecr='112233445566.dkr.ecr.us-east-1.amazonaws.com/repo-tag',
  os='amazon_linux', # 'amazon_linux' by default. Can also be debian, ubuntu, macos, windows, red_hat, suse_linux.
  env={ # optional; empty by default. 
    "OPENAI_API_KEY": "...",
    "DEBUG": "true",
    ...
  },
  cmd='python main.py --concurrency 5'
)

instance = ec2.Instance(
  id='...', # optional; if not given, it'll create one using `instance.create()` and update the id. Otherwise, the programmer means the instance already exists and wants to communicate with it. In that case, the programmer should only have to give the instance id and not need to specify any of the other fields.
  name='my-machine', # optional
  machine='t4g.micro', # required if id not given; otherwise optional
  mode='spot', # optional, can be 'spot' or 'on-demand'. It's 'on-demand' by default 
  key_pair='keypair-name', # required if id not given; otherwise optional
  security_groups=['sg-01234', 'sg-98123'], # optional
  ami='ami_13290193013' # optional
  storage=[
    ec2.Volume(
      id='...', # optional; if given, it's referring to an existing volume snapshot that the ec2 instance should attach to. In that case, all other kwargs become optional. Otherwise, if not provided, it'll create a volume that will be destroyed on instance's termination
      gib=8, 
      mode='gp3', # optional, gp3 by default. It can be gp2 and standard as well.
    ),
    ...
  ], # optional; it'll create one volume that'll be deleted on instance termination with 8 GB and gp3 mode.
  user_data=bootup_script # optional; it can also be an `ec2.BaseUserData` object, which would be the `script` variable.
)

instance.create()
instance.start()
instance.stop()
instance.terminate()
```