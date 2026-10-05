import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rupert import voice


class VoiceTests(unittest.TestCase):
    def test_detect_explicit_executable(self):
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d) / "whisper-cli.exe"
            exe.write_text("x", encoding="utf-8")
            with patch.dict(os.environ, {"WHISPER_CPP_EXE": str(exe)}, clear=False):
                self.assertEqual(voice.detect_whisper_executable(), exe.resolve())

    def test_detect_explicit_model(self):
        with tempfile.TemporaryDirectory() as d:
            model = Path(d) / "ggml-base.bin"
            model.write_bytes(b"x")
            with patch.dict(os.environ, {"WHISPER_MODEL": str(model)}, clear=False):
                self.assertEqual(voice.detect_model(), model.resolve())


if __name__ == "__main__":
    unittest.main()
