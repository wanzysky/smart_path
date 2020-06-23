# smart_path

Dispatch to `pathlib.Path` if a local file system path is given,
or `s3path.S3Path` if the given path is prefixed with
`s3://`

## Example

### Basic

```python
from smart_path import smart_path
from pathlib import Path
from s3path import S3Path


# A local path on file system
path_local = smart_path("/tmp/t")
assert isinstance(path_local, Path)


# A s3 path on oss
path_brainpp_oss = smart_path("s3://public-datasets-contrib/", endpoint_url='s3.amazonaws.com')
assert isinstance(path_local, S3Path)
```

### Stub Mode

```python
from smart_path import smart_path


# Stub mode works like the symbolic link in Unix. The source path can be either
# on local file system or brain++ oss, so do the target path. Stub Mode is
# excepted to be helpful when we need to store a large file on oss and pretend 
# it is on local file system.
#
# In stub mode, smart_path writes to two destinations:
# 1. The string "hello-world" is written to `s3://somewhere/on/oss`
# 2. The path "s3://somewhere/on/oss" is written to `corresponding/local/path`
path = smart_path('s3://somewhere/on/oss', stub='corresponding/local/path')
path.write_text('hello-world')
# smart_path knows it is a stub file
stub = smart_path('corresponding/local/path')
print(stub.read_text())  # prints "hello-world"

```

## Installation

```bash
pip install -e git://github.com/wanzysky/smart_path.git#egg=smart_path
```

# Notice:

*The entire project is borrowed from EMTF: EMTF-at-megvii-dot-com.*
