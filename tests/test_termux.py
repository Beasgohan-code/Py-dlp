"""Unit tests for Termux (Android) integration and setup."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pydlp.core.termux import (
    get_termux_download_dir,
    is_termux,
    send_termux_notification,
    setup_termux_environment,
)


class TestTermux(unittest.TestCase):
    """Test suite for Termux detection and configuration."""

    def test_termux_detection(self):
        with patch.dict(os.environ, {"TERMUX_VERSION": "0.118.0"}):
            self.assertTrue(is_termux())

        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(is_termux())

    def test_get_termux_download_dir(self):
        dl_dir = get_termux_download_dir()
        self.assertIsInstance(dl_dir, Path)

    def test_send_notification_mock(self):
        with patch("pydlp.core.termux.is_termux", return_value=True):
            with patch("shutil.which", return_value="/data/data/com.termux/files/usr/bin/termux-notification"):
                with patch("subprocess.run") as mock_run:
                    ret = send_termux_notification("Test Title", "Test Body")
                    self.assertTrue(ret)
                    mock_run.assert_called_once()

    def test_setup_termux_environment_mock(self):
        with tempfile.TemporaryDirectory() as temp_home:
            with patch.object(Path, "home", return_value=Path(temp_home)):
                with patch("subprocess.run"):
                    ret = setup_termux_environment()
                    self.assertEqual(ret, 0)
                    opener = Path(temp_home) / "bin" / "termux-url-opener"
                    self.assertTrue(opener.exists())
                    self.assertIn("Py-dlp", opener.read_text())


if __name__ == "__main__":
    unittest.main()
