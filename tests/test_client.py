"""Unit tests for CTFdClient."""

import unittest
from unittest.mock import MagicMock

from ctfdownloader.client import CTFdClient


class TestCTFdClient(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.client = CTFdClient(
            base_url="https://ctfd.example.com",
            session=self.mock_session,
        )

    def test_token_auth_headers(self):
        self.client.authenticate_with_token("secret_token_123")
        headers = self.mock_session.headers.update.call_args[0][0]
        self.assertEqual(headers["Authorization"], "Token secret_token_123")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_resolve_url(self):
        self.assertEqual(
            self.client.resolve_url("/files/test.zip"),
            "https://ctfd.example.com/files/test.zip",
        )
        self.assertEqual(
            self.client.resolve_url("https://external.com/file.zip"),
            "https://external.com/file.zip",
        )

    def test_extract_csrf_nonce_hidden_input(self):
        resp = MagicMock()
        resp.text = '<html><input type="hidden" name="nonce" value="token_hidden_1"></html>'
        self.mock_session.get.return_value = resp

        nonce = self.client.extract_csrf_nonce()
        self.assertEqual(nonce, "token_hidden_1")

    def test_extract_csrf_nonce_script_object(self):
        resp = MagicMock()
        resp.text = '<html><script>window.init = { "csrfNonce": "token_script_2" };</script></html>'
        self.mock_session.get.return_value = resp

        nonce = self.client.extract_csrf_nonce()
        self.assertEqual(nonce, "token_script_2")

    def test_extract_csrf_nonce_meta_tag(self):
        resp = MagicMock()
        resp.text = '<html><head><meta name="csrf-token" content="token_meta_3"></head></html>'
        self.mock_session.get.return_value = resp

        nonce = self.client.extract_csrf_nonce()
        self.assertEqual(nonce, "token_meta_3")


if __name__ == "__main__":
    unittest.main()
