"""Unit tests for environment parsing logic."""

import os
import tempfile
import unittest

from ctfdownloader.env import _unquote, get_env, get_env_float, load_env


class TestEnv(unittest.TestCase):
    def test_unquote(self):
        self.assertEqual(_unquote('"hello"'), "hello")
        self.assertEqual(_unquote("'world'"), "world")
        self.assertEqual(_unquote("plain_value # inline comment"), "plain_value")
        self.assertEqual(_unquote("   spaced   "), "spaced")

    def test_load_env_file(self):
        content = (
            "# Comment line\n"
            "TEST_VAR1=hello\n"
            "TEST_VAR2=\"quoted string\"\n"
            "export TEST_VAR3=exported_val\n"
            "TEST_FLOAT=2.5\n"
        )
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name

        try:
            loaded = load_env(temp_path)
            self.assertEqual(loaded.get("TEST_VAR1"), "hello")
            self.assertEqual(loaded.get("TEST_VAR2"), "quoted string")
            self.assertEqual(loaded.get("TEST_VAR3"), "exported_val")
            self.assertEqual(get_env("TEST_VAR1"), "hello")
            self.assertEqual(get_env_float("TEST_FLOAT", 1.0), 2.5)
            self.assertEqual(get_env_float("NON_EXISTENT", 4.0), 4.0)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
