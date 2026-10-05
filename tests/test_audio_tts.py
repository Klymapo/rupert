import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rupert.audio import record_push_to_talk
from rupert.tts import piper_data_dir, piper_voice, synthesize


class AudioTtsTests(unittest.TestCase):
    def test_audio_rejects_invalid_samplerate_before_loading_device(self):
        with self.assertRaises(ValueError):
            record_push_to_talk("x.wav", samplerate=0)

    def test_piper_voice_env_override(self):
        with patch.dict(os.environ, {"PIPER_VOICE": "es_MX-claude-high"}, clear=False):
            self.assertEqual(piper_voice(), "es_MX-claude-high")

    def test_piper_data_dir_env_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"PIPER_DATA_DIR": tmp}, clear=False):
                self.assertEqual(piper_data_dir(), Path(tmp).resolve())

    @patch("rupert.tts.piper_available", return_value=False)
    def test_synthesize_requires_piper(self, mocked):
        with self.assertRaises(RuntimeError):
            synthesize("hola")


if __name__ == "__main__":
    unittest.main()
