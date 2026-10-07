"""Unit tests for the CLI module."""

import unittest
from unittest.mock import patch

from ctfdownloader.cli import _build_parser, _resolve_configuration


class TestCLI(unittest.TestCase):
    def test_parser_list(self):
        parser = _build_parser()
        args = parser.parse_args(["-u", "https://demo.ctfd.io", "list"])
        self.assertEqual(args.command, "list")
        self.assertEqual(args.url, "https://demo.ctfd.io")

    def test_parser_download(self):
        parser = _build_parser()
        args = parser.parse_args([
            "-u", "https://demo.ctfd.io",
            "-t", "test_token",
            "download",
            "-o", "my_challenges",
            "-c", "Web",
            "--force"
        ])
        self.assertEqual(args.command, "download")
        self.assertEqual(args.token, "test_token")
        self.assertEqual(args.output, "my_challenges")
        self.assertEqual(args.category, "Web")
        self.assertTrue(args.force)

    def test_resolve_configuration_valid_url(self):
        parser = _build_parser()
        args = parser.parse_args(["-u", "https://demo.ctfd.io", "list"])
        config = _resolve_configuration(args)
        self.assertEqual(config["base_url"], "https://demo.ctfd.io")
        self.assertEqual(config["min_delay"], 1.0)
        self.assertEqual(config["max_delay"], 3.0)

    def test_resolve_configuration_invalid_url_scheme(self):
        parser = _build_parser()
        args = parser.parse_args(["-u", "ftp://demo.ctfd.io", "list"])
        with self.assertRaises(SystemExit):
            _resolve_configuration(args)

    def test_resolve_configuration_missing_url(self):
        parser = _build_parser()
        args = parser.parse_args(["list"])
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(SystemExit):
                _resolve_configuration(args)


if __name__ == "__main__":
    unittest.main()
