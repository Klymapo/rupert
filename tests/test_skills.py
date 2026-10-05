import unittest

from rupert.permissions import ActionSource, ActionSpec, RiskLevel
from rupert.skills import SkillDefinition, SkillRegistry, SkillResult, build_obsidian_registry


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


class SkillRegistryTests(unittest.TestCase):
    def test_unknown_skill_is_denied(self):
        result = SkillRegistry().invoke("missing", source=ActionSource.KEYBOARD)
        self.assertFalse(result.ok)

    def test_duplicate_skill_is_rejected(self):
        registry = SkillRegistry()
        spec = ActionSpec("demo.read", RiskLevel.READ)
        definition = SkillDefinition("demo.read", "demo", spec, lambda: SkillResult(True, "ok"))
        registry.register(definition)
        with self.assertRaises(ValueError):
            registry.register(definition)

    def test_policy_runs_before_handler(self):
        called = []
        registry = SkillRegistry()
        spec = ActionSpec("demo.write", RiskLevel.WRITE)

        def handler():
            called.append(True)
            return SkillResult(True, "executed")

        registry.register(SkillDefinition("demo.write", "demo", spec, handler))
        result = registry.invoke("demo.write", source=ActionSource.BRAIN)
        self.assertFalse(result.ok)
        self.assertEqual(called, [])

    def test_obsidian_registry_exposes_expected_skills(self):
        registry = build_obsidian_registry(FakeClient())
        self.assertEqual(
            registry.names(),
            [
                "obsidian.append",
                "obsidian.open",
                "obsidian.overwrite",
                "obsidian.read",
                "obsidian.search",
            ],
        )

    def test_obsidian_search_executes_through_registry(self):
        client = FakeClient()
        registry = build_obsidian_registry(client)
        result = registry.invoke(
            "obsidian.search",
            source=ActionSource.KEYBOARD,
            target="Theo",
            content="",
        )
        self.assertTrue(result.ok)
        self.assertEqual(client.calls, [("search", "Theo")])
        self.assertEqual(result.payload, [{"path": "Nota.md"}])

    def test_voice_overwrite_never_reaches_handler(self):
        client = FakeClient()
        registry = build_obsidian_registry(client)
        result = registry.invoke(
            "obsidian.overwrite",
            source=ActionSource.VOICE,
            target="Nota.md",
            content="nuevo",
        )
        self.assertFalse(result.ok)
        self.assertEqual(client.calls, [])


if __name__ == "__main__":
    unittest.main()
