"""Tests for policy service against the self-contained runtime in the skill package."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from leftman_skill_system.services.policy_service import PolicyService


BASE_DIR = RUNTIME_DIR / "leftman_skill_system"


class PolicyServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = PolicyService(BASE_DIR / "policies")

    def test_load_default_policy(self):
        policy = self.service.load("default")
        self.assertIn("requires_explicit_consent", policy)
        self.assertFalse(policy["requires_explicit_consent"])

    def test_load_high_risk_deceased_policy(self):
        policy = self.service.load("high_risk_deceased")
        self.assertTrue(policy["requires_explicit_consent"])
        self.assertIn("blocked_topics", policy)

    def test_load_nonexistent_policy_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            self.service.load("nonexistent_policy")

    def test_requires_explicit_consent_default(self):
        self.assertFalse(self.service.requires_explicit_consent("default"))

    def test_requires_explicit_consent_high_risk(self):
        self.assertTrue(self.service.requires_explicit_consent("high_risk_deceased"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
