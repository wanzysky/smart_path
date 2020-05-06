import functools
import tempfile
import unittest
from pathlib import Path

import boto3
from moto import mock_s3
from s3path import S3Path

from smart_path import smart_path

boto3.setup_default_session()
smart_path = functools.partial(smart_path, endpoint_url=None)


class TestCallable(unittest.TestCase):
    @mock_s3
    def test_s3path(self):
        str_path = "s3://foo/bar"
        path = smart_path(str_path)
        self.assertIsInstance(path, S3Path)
        self.assertEqual(str(path), "/foo/bar")

        path = S3Path("s3://hahah")
        path = smart_path(path)
        self.assertIsInstance(path, S3Path)

        conn = boto3.resource("s3")
        conn.create_bucket(Bucket="tmp")
        path = S3Path("s3://tmp")
        path = smart_path(path)
        self.assertIsInstance(path, S3Path)

    def test_local_path(self):
        str_absolute_path = "/hahah/a"
        str_relative_path = "./a"
        absolute_path = smart_path(str_absolute_path)
        relative_path = smart_path(str_relative_path)
        self.assertIsInstance(absolute_path, Path)
        self.assertIsInstance(relative_path, Path)

        p = smart_path("./")
        self.assertIsInstance(p, Path)

    def test_stub_mode_local2local(self):
        with tempfile.TemporaryDirectory() as temp_dirname:
            link = "{}/link".format(temp_dirname)
            stub = "{}/stub".format(temp_dirname)
            p1 = smart_path(link, stub=stub)
            p2 = smart_path(stub)
            self.assertIsInstance(p1, Path)
            self.assertIsInstance(p2, Path)
            self.assertEqual(p1, p2)
            another_link = "{}/another_link".format(temp_dirname)
            with self.assertRaises(OSError):
                _ = smart_path(another_link, stub=stub)
            text = "hello world!"
            p1.write_text(text)
            self.assertEqual(p2.read_text(), text)
            text = "world hello!"
            p2.write_text(text)
            self.assertEqual(p1.read_text(), text)

    @mock_s3
    def test_stub_mode_local2oss(self):
        conn = boto3.resource("s3")
        conn.create_bucket(Bucket="tmp")
        with tempfile.TemporaryDirectory() as temp_dirname:
            link = "s3://tmp/link"
            stub = "{}/stub".format(temp_dirname)
            p1 = smart_path(link, stub=stub)
            p2 = smart_path(stub)
            self.assertIsInstance(p1, S3Path)
            self.assertIsInstance(p2, S3Path)
            self.assertEqual(p1, p2)
            another_link = "{}/another_link".format(temp_dirname)
            with self.assertRaises(OSError):
                _ = smart_path(another_link, stub=stub)

            text = "hello world!"
            p1.write_text(text)
            self.assertEqual(p2.read_text(), text)

            text = "world hello!"
            p2.write_text(text)
            self.assertEqual(p1.read_text(), text)

            another_stub = "{}/another_stub".format(temp_dirname)
            p3 = smart_path(another_stub)
            p3.write_text(link)
            p4 = smart_path(another_stub)
            self.assertIsInstance(p4, Path)

    @mock_s3
    def test_stub_mode_oss2oss(self):
        conn = boto3.resource("s3")
        conn.create_bucket(Bucket="tmp")
        link = "s3://tmp/link-s3"
        stub = "s3://tmp/stub-s3"
        p1 = smart_path(link, stub=stub)
        p2 = smart_path(stub)
        self.assertIsInstance(p1, S3Path)
        self.assertIsInstance(p2, S3Path)
        self.assertEqual(p1, p2)
        another_link = "s3://tmp/another_link-s3"
        with self.assertRaises(OSError):
            _ = smart_path(another_link, stub=stub)

        text = "hello world!"
        p1.write_text(text)
        self.assertEqual(p2.read_text(), text)

        text = "world hello!"
        p2.write_text(text)
        self.assertEqual(p1.read_text(), text)

    @mock_s3
    def test_stub_mode_oss2local(self):
        conn = boto3.resource("s3")
        conn.create_bucket(Bucket="tmp")
        with tempfile.TemporaryDirectory() as temp_dirname:
            link = "{}/link".format(temp_dirname)
            stub = "s3://tmp/stub"
            p1 = smart_path(link, stub=stub)
            p2 = smart_path(stub)
            self.assertIsInstance(p1, Path)
            self.assertIsInstance(p2, Path)
            self.assertEqual(p1, p2)
