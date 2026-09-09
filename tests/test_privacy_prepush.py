#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for PrivacyPrepushInspector.
Verifies detection and masking of API keys, tokens, and PII.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.analysis.privacy_prepush_inspector import (
    PrivacyPrepushInspector,
    inspect_text_content,
    mask_secret
)


class TestPrivacyPrepush(unittest.TestCase):

    def test_mask_secret(self):
        self.assertEqual(mask_secret("1234"), "****")
        masked = mask_secret("sk-1234567890abcdef1234567890")
        self.assertTrue(masked.startswith("sk-1"))
        self.assertTrue(masked.endswith("90"))
        self.assertIn("*", masked)

    def test_detect_openai_and_hf_tokens(self):
        sample = """
        OPENAI_API_KEY = "sk-proj-abcde12345abcde12345abcde12345"
        HF_TOKEN = "hf_0123456789012345678901234567890123"
        """
        violations = inspect_text_content(sample)
        rules = [v["rule"] for v in violations]
        self.assertIn("OpenAI API Key", rules)
        self.assertIn("Hugging Face Token", rules)

    def test_clean_code_passes(self):
        sample = """
        def fetch_data():
            token = os.environ.get("MY_TOKEN")
            return {"status": "ok"}
        """
        violations = inspect_text_content(sample)
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
