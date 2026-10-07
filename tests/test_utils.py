"""Unit tests for utility functions."""

import unittest
from ctfdownloader.utils import extract_urls, sanitize_name


class TestUtils(unittest.TestCase):
    def test_sanitize_name_normal(self):
        self.assertEqual(sanitize_name("Crypto 101"), "Crypto 101")

    def test_sanitize_name_forbidden_characters(self):
        self.assertEqual(sanitize_name("web: challenge <1> / test?"), "web_ challenge _1_ _ test")

    def test_sanitize_name_traversal_prevention(self):
        self.assertEqual(sanitize_name("../../etc/passwd"), "etc_passwd")
        self.assertEqual(sanitize_name(".."), "item")
        self.assertEqual(sanitize_name("."), "item")

    def test_sanitize_name_url_encoded(self):
        self.assertEqual(sanitize_name("chall%20name"), "chall name")

    def test_sanitize_name_fallback_empty(self):
        self.assertEqual(sanitize_name("", fallback="default_name"), "default_name")

    def test_extract_urls(self):
        text = "Visit https://challenge.ctf.example.com or http://10.0.0.1:8080/flag"
        urls = extract_urls(text)
        self.assertEqual(len(urls), 2)
        self.assertIn("https://challenge.ctf.example.com", urls)
        self.assertIn("http://10.0.0.1:8080/flag", urls)

    def test_extract_urls_empty(self):
        self.assertEqual(extract_urls("No urls here!"), [])


if __name__ == "__main__":
    unittest.main()
