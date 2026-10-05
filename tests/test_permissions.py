import unittest

from rupert.permissions import (
    ActionSource,
    ActionSpec,
    PermissionPolicy,
    RiskLevel,
    action_spec_for_intent,
)
from rupert.router import IntentKind


class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.policy = PermissionPolicy()

    def test_voice_can_append(self):
        spec = action_spec_for_intent(IntentKind.APPEND)
        self.assertIsNotNone(spec)
        decision = self.policy.evaluate(spec, source=ActionSource.VOICE)
        self.assertTrue(decision.allowed)

    def test_voice_cannot_overwrite(self):
        spec = action_spec_for_intent(IntentKind.WRITE)
        self.assertIsNotNone(spec)
        decision = self.policy.evaluate(spec, source=ActionSource.VOICE)
        self.assertFalse(decision.allowed)

    def test_brain_cannot_execute_even_read_action(self):
        spec = action_spec_for_intent(IntentKind.SEARCH)
        self.assertIsNotNone(spec)
        decision = self.policy.evaluate(spec, source=ActionSource.BRAIN)
        self.assertFalse(decision.allowed)
        self.assertIn("cerebro", decision.reason)

    def test_destructive_requires_confirmation(self):
        spec = ActionSpec("git.reset-hard", RiskLevel.DESTRUCTIVE)
        denied = self.policy.evaluate(spec, source=ActionSource.KEYBOARD, confirmed=False)
        allowed = self.policy.evaluate(spec, source=ActionSource.KEYBOARD, confirmed=True)
        self.assertFalse(denied.allowed)
        self.assertTrue(allowed.allowed)

    def test_brain_stays_denied_even_if_destructive_is_confirmed(self):
        spec = ActionSpec("files.delete", RiskLevel.DESTRUCTIVE)
        decision = self.policy.evaluate(spec, source=ActionSource.BRAIN, confirmed=True)
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
