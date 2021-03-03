"""Dispatch to pathlib.Path if a local file system path is given,
or S3Path if the given path is prefixed with 's3://'.
"""

from pathlib import Path
from typing import Union

import boto3
import s3path
from s3path import S3Path
OSS_ENDPOINT = 'https://s3.amazonaws.com'

__all__ = ["smart_path"]

STUB_TAG = "[STUB]\n"
STUB_TAG_ENCODE = str.encode(STUB_TAG)


def _convert_path_to_str(path: Union[Path, S3Path]) -> str:
    """Convert smart_path to commonly used format
    """
    if isinstance(path, S3Path):
        text = path.as_uri()
    elif isinstance(path, Path):
        text = str(path.absolute())
    return text


def _try_parse_stub(*args, endpoint_url: str) -> Union[Path, S3Path]:
    """Try to convert a path to non-stub format if
    1. this path exists
    2. container starts with `STUB_TAG`
    return None otherwise
    """
    path = _route_path(*args, endpoint_url=endpoint_url)
    if not path.exists():
        return None

    if not path.is_file():
        return None

    with path.open("rb") as f:
        PREFIX = f.read(len(STUB_TAG_ENCODE))
        if PREFIX != STUB_TAG_ENCODE:
            return None

    with path.open("r") as f:
        path = f.read()[len(STUB_TAG) :]

    return _route_path(path, endpoint_url=endpoint_url)


def _route_path(*args, endpoint_url: str) -> Union[Path, S3Path]:
    """use S3Path or Path depending on the input.
    """
    if str(args[0]).startswith("s3://"):
        s3path._s3_accessor.s3 = boto3.resource("s3", endpoint_url=endpoint_url)
        return S3Path.from_uri(*args)
    elif isinstance(args[0], S3Path):
        s3path._s3_accessor.s3 = boto3.resource("s3", endpoint_url=endpoint_url)
        return S3Path(*args)
    else:
        return Path(*args)


def smart_path(*args, endpoint_url: str = OSS_ENDPOINT, stub=None) -> Union[Path, S3Path]:
    """Dispatch to pathlib.Path if a local file system path is given,
    or s3path.S3Path if the given path is prefixed with 's3://'.

    Support stub mode, i.e. create a file which contains a path pointing
    to real target location, expected useful to save a big file in local
    file system.

    :param args: parts of paths
    :param endpoint_url: endpoint url for s3path, OSS_ENDPOINT by default
    :param stub: stub path for stub mode, raise IOError if conflict happens
    :return: a Path object or an S3Path object.
    """

    if stub is not None:
        stub_path = _route_path(stub, endpoint_url=endpoint_url)
        if stub_path.exists():
            link_path_from_stub = _try_parse_stub(stub, endpoint_url=endpoint_url)
            link_path = _route_path(*args, endpoint_url=endpoint_url)

            # check if there exists a conflict, i.e present links is different from previous link
            link_text_from_stub = _convert_path_to_str(link_path_from_stub)
            link_text = _convert_path_to_str(link_path)
            if link_text_from_stub != link_text:
                raise OSError(
                    "ERROR: path from stub and input path should be same: {} and {}".format(
                        link_text_from_stub, link_text
                    )
                )
        else:
            link_path = _route_path(*args, endpoint_url=endpoint_url)
            link_text = _convert_path_to_str(link_path)
            stub_path.write_text("{}{}".format(STUB_TAG, link_text))
        return link_path
    else:
        stub_path = _try_parse_stub(*args, endpoint_url=endpoint_url)
        if stub_path:
            return stub_path
        else:
            return _route_path(*args, endpoint_url=endpoint_url)
