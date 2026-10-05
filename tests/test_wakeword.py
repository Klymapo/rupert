import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rupert.wakeword import WakeWordConfig, _prediction_score, wait_for_activation


class FakeDetector:
    def __init__(self):
        self.config = WakeWordConfig(model=Path("ignored.onnx"), threshold=0.5)
        self.calls = 0

    def detected_pcm16(self, pcm):
        self.calls += 1
        return (self.calls >= 2, 0.8 if self.calls >= 2 else 0.1)


class FakeStream:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, chunk_size):
        return (b"\x00\x00" * chunk_size, False)


class WakeWordTests(unittest.TestCase):
    def test_prediction_score(self):
        self.assertEqual(_prediction_score({"rupert": 0.2, "other": 0.75}), 0.75)

    def test_invalid_threshold(self):
        cfg = WakeWordConfig(model=Path("x.onnx"), threshold=1.2)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_config_from_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "rupert.onnx"
            with patch.dict(
                os.environ,
                {
                    "WAKEWORD_MODEL": str(model),
                    "WAKEWORD_THRESHOLD": "0.61",
                    "WAKEWORD_FRAMEWORK": "onnx",
                    "WAKEWORD_CHUNK_SIZE": "1280",
                },
                clear=False,
            ):
                cfg = WakeWordConfig.from_env()
                self.assertEqual(cfg.model, model.resolve())
                self.assertEqual(cfg.threshold, 0.61)
                self.assertEqual(cfg.chunk_size, 1280)

    def test_wait_for_activation_with_fake_stream(self):
        detector = FakeDetector()
        score = wait_for_activation(detector, stream_factory=lambda **kwargs: FakeStream(**kwargs))
        self.assertEqual(score, 0.8)
        self.assertEqual(detector.calls, 2)


if __name__ == "__main__":
    unittest.main()
