import unittest
from unittest.mock import patch

from rupert.pipeline import process_audio_file, process_transcript


class FakeClient:
    def __init__(self):
        self.writes = []

    def search(self, target):
        return [{"path": "Nota.md", "target": target}]

    def read(self, target):
        return "contenido"

    def open_note(self, target):
        return None

    def append(self, target, content):
        return None

    def write(self, target, content):
        self.writes.append((target, content))


class PipelineTests(unittest.TestCase):
    def test_process_transcript(self):
        turn = process_transcript(FakeClient(), " buscar Theo ")
        self.assertEqual(turn.transcript, "buscar Theo")
        self.assertTrue(turn.result.ok)
        self.assertEqual(turn.result.payload[0]["target"], "Theo")

    def test_voice_overwrite_is_blocked(self):
        client = FakeClient()
        turn = process_transcript(client, "escribir Nota.md :: reemplazar todo")
        self.assertFalse(turn.result.ok)
        self.assertEqual(client.writes, [])
        self.assertIn("no sobrescribo", turn.result.message)

    @patch("rupert.pipeline.speak")
    @patch("rupert.pipeline.transcribe_file", return_value="abrir Nota.md")
    def test_process_audio_can_speak(self, mocked_transcribe, mocked_speak):
        turn = process_audio_file(FakeClient(), "fake.wav", speak_response=True)
        self.assertTrue(turn.result.ok)
        mocked_transcribe.assert_called_once_with("fake.wav", language="es")
        mocked_speak.assert_called_once_with("Abrí Nota.md.", cuda=False)


if __name__ == "__main__":
    unittest.main()
