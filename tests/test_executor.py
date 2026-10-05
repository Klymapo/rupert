import unittest

from rupert.executor import execute_text


class FakeClient:
    def __init__(self):
        self.calls = []

    def search(self, target):
        self.calls.append(("search", target))
        return [{"path": "AlasTheo/Ideas.md"}]

    def read(self, target):
        self.calls.append(("read", target))
        return "contenido"

    def open_note(self, target):
        self.calls.append(("open", target))

    def append(self, target, content):
        self.calls.append(("append", target, content))

    def write(self, target, content):
        self.calls.append(("write", target, content))


class ExecutorTests(unittest.TestCase):
    def test_search(self):
        client = FakeClient()
        result = execute_text(client, "buscar Theo")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload, [{"path": "AlasTheo/Ideas.md"}])
        self.assertIn("1 resultado", result.message)
        self.assertEqual(client.calls, [("search", "Theo")])

    def test_append(self):
        client = FakeClient()
        result = execute_text(client, "añadir Ideas.md :: hola")
        self.assertTrue(result.ok)
        self.assertEqual(client.calls, [("append", "Ideas.md", "hola")])

    def test_unknown(self):
        result = execute_text(FakeClient(), "haz magia")
        self.assertFalse(result.ok)

    def test_exit(self):
        result = execute_text(FakeClient(), "salir")
        self.assertTrue(result.should_exit)


if __name__ == "__main__":
    unittest.main()
