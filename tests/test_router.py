import unittest
from rupert.router import IntentKind, parse_intent


class RouterTests(unittest.TestCase):
    def test_search_spanish(self):
        intent = parse_intent("buscar Theo")
        self.assertEqual(intent.kind, IntentKind.SEARCH)
        self.assertEqual(intent.target, "Theo")

    def test_append(self):
        intent = parse_intent("añadir AlasTheo/Ideas.md :: Nueva idea")
        self.assertEqual(intent.kind, IntentKind.APPEND)
        self.assertEqual(intent.target, "AlasTheo/Ideas.md")
        self.assertEqual(intent.content, "Nueva idea")

    def test_unknown_write_without_separator(self):
        self.assertEqual(parse_intent("escribir Nota.md contenido").kind, IntentKind.UNKNOWN)

    def test_exit(self):
        self.assertEqual(parse_intent("salir").kind, IntentKind.EXIT)


if __name__ == "__main__":
    unittest.main()
