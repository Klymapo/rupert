import json
import unittest
from urllib.request import Request

from rupert.brain import BrainError, OllamaBackend, OllamaConfig, SYSTEM_PROMPT, brain_doctor


class FakeRequester:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, request: Request, timeout: float) -> bytes:
        self.calls.append((request, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return json.dumps(response).encode("utf-8")


class BrainTests(unittest.TestCase):
    def test_remote_endpoint_blocked_by_default(self):
        cfg = OllamaConfig(base_url="https://example.com", model="tiny")
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_remote_endpoint_can_be_explicitly_allowed(self):
        cfg = OllamaConfig(base_url="https://example.com", model="tiny", allow_remote=True)
        cfg.validate()

    def test_chat_posts_non_streaming_messages(self):
        requester = FakeRequester([
            {"model": "tiny", "message": {"role": "assistant", "content": "Hola."}, "done": True}
        ])
        backend = OllamaBackend(
            OllamaConfig(model="tiny", timeout=5),
            requester=requester,
        )
        reply = backend.chat("Hola Rupert")
        self.assertEqual(reply.text, "Hola.")
        request, timeout = requester.calls[0]
        self.assertEqual(timeout, 5)
        self.assertEqual(request.get_method(), "POST")
        self.assertTrue(request.full_url.endswith("/api/chat"))
        payload = json.loads(request.data.decode("utf-8"))
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["model"], "tiny")
        self.assertEqual(payload["messages"][0]["content"], SYSTEM_PROMPT)
        self.assertEqual(payload["messages"][1]["content"], "Hola Rupert")

    def test_list_models(self):
        requester = FakeRequester([
            {"models": [{"name": "qwen:small"}, {"name": "gemma:small"}]}
        ])
        backend = OllamaBackend(OllamaConfig(model="qwen:small"), requester=requester)
        self.assertEqual(backend.list_models(), ["qwen:small", "gemma:small"])
        request, _ = requester.calls[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertTrue(request.full_url.endswith("/api/tags"))

    def test_bad_json_raises(self):
        def bad_json(request, timeout):
            return b"not-json"

        backend = OllamaBackend(OllamaConfig(model="tiny"), requester=bad_json)
        with self.assertRaises(BrainError):
            backend.chat("hola")

    def test_doctor_succeeds_when_selected_model_exists(self):
        requester = FakeRequester([
            {"models": [{"name": "tiny"}]}
        ])
        result = brain_doctor(OllamaConfig(model="tiny"), requester=requester)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
