import unittest

from rupert.assistant import AssistantEngine, TurnMode
from rupert.brain import BrainReply


class FakeClient:
    def __init__(self):
        self.calls = []

    def search(self, target):
        self.calls.append(("search", target))
        return [{"path": "Nota.md"}]

    def read(self, target):
        self.calls.append(("read", target))
        return "contenido"

    def open_note(self, target):
        self.calls.append(("open", target))

    def append(self, target, content):
        self.calls.append(("append", target, content))

    def write(self, target, content):
        self.calls.append(("write", target, content))


class FakeBrain:
    def __init__(self):
        self.calls = []

    def chat(self, text):
        self.calls.append(text)
        return BrainReply(text="respuesta razonada", model="fake")


class AssistantTests(unittest.TestCase):
    def test_known_command_bypasses_brain(self):
        client = FakeClient()
        brain = FakeBrain()
        turn = AssistantEngine(client, brain).handle("buscar Theo")
        self.assertEqual(turn.mode, TurnMode.LOCAL)
        self.assertEqual(brain.calls, [])
        self.assertEqual(client.calls, [("search", "Theo")])
        self.assertEqual(turn.payload, [{"path": "Nota.md"}])

    def test_unknown_language_goes_to_brain_only(self):
        client = FakeClient()
        brain = FakeBrain()
        turn = AssistantEngine(client, brain).handle("¿Cómo mejorarías esta idea?")
        self.assertEqual(turn.mode, TurnMode.BRAIN)
        self.assertEqual(turn.message, "respuesta razonada")
        self.assertEqual(brain.calls, ["¿Cómo mejorarías esta idea?"])
        self.assertEqual(client.calls, [])

    def test_exit_is_local(self):
        client = FakeClient()
        brain = FakeBrain()
        turn = AssistantEngine(client, brain).handle("salir")
        self.assertTrue(turn.should_exit)
        self.assertEqual(turn.mode, TurnMode.LOCAL)
        self.assertEqual(brain.calls, [])

    def test_dangerous_natural_language_is_not_implicitly_executed(self):
        client = FakeClient()
        brain = FakeBrain()
        turn = AssistantEngine(client, brain).handle("borra todas mis notas")
        self.assertEqual(turn.mode, TurnMode.BRAIN)
        self.assertEqual(client.calls, [])
        self.assertEqual(brain.calls, ["borra todas mis notas"])


if __name__ == "__main__":
    unittest.main()
