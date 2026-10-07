"""Unit tests for challenge downloader organization and atomic saving."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

from ctfdownloader.client import CTFdClient
from ctfdownloader.downloader import CTFDownloader


class TestCTFDownloader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_client = MagicMock(spec=CTFdClient)
        self.mock_client.session = MagicMock()
        self.mock_client.timeout = 10.0
        self.mock_client.resolve_url.side_effect = lambda u: f"https://ctf.example.com/{u.lstrip('/')}"
        self.downloader = CTFDownloader(
            client=self.mock_client,
            output_dir=self.temp_dir,
            logger=lambda msg: None,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_filename_from_url(self):
        fn = self.downloader._extract_filename_from_url("/files/34a5d/challenge.pcap?token=xyz")
        self.assertEqual(fn, "challenge.pcap")

    def test_build_description_content(self):
        detail = {
            "name": "Secret Service",
            "category": "Web",
            "value": 150,
            "description": "Exploit the service at http://secret.ctf.example.com",
            "connection_info": "nc 10.10.10.10 1337",
            "tags": ["web", "easy"],
        }
        content = self.downloader._build_description_content(detail, ["http://secret.ctf.example.com"])
        self.assertIn("Title: Secret Service", content)
        self.assertIn("Category: Web", content)
        self.assertIn("Points: 150", content)
        self.assertIn("Connection Info: nc 10.10.10.10 1337", content)
        self.assertIn("Tags: web, easy", content)
        self.assertIn("http://secret.ctf.example.com", content)

    def test_download_challenge_structure(self):
        self.mock_client.get_challenge_detail.return_value = {
            "id": 42,
            "name": "Buffer Overflow",
            "category": "Pwn",
            "value": 200,
            "description": "Get a shell.",
            "files": ["/files/binary.elf"],
        }

        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Length": "12"}
        mock_resp.iter_content.return_value = [b"test_payload"]
        mock_resp.__enter__.return_value = mock_resp

        self.mock_client.session.get.return_value = mock_resp

        success = self.downloader.download_challenge(42)
        self.assertTrue(success)

        expected_folder = os.path.join(self.temp_dir, "Pwn", "Buffer Overflow")
        self.assertTrue(os.path.isdir(expected_folder))

        desc_file = os.path.join(expected_folder, "description.txt")
        self.assertTrue(os.path.isfile(desc_file))

        binary_file = os.path.join(expected_folder, "binary.elf")
        self.assertTrue(os.path.isfile(binary_file))
        with open(binary_file, "rb") as f:
            self.assertEqual(f.read(), b"test_payload")


if __name__ == "__main__":
    unittest.main()
