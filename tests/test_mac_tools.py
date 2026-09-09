#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for lightweight Mac-native tools in OpenMontage:
1. AssKaraokeBurner (ASS format generation & VideoToolbox burning)
2. ScriptureHymnRAG (Offline Bible & Hymn verification)
3. OBSController (WebSocket remote actions)
4. SocialMetadataPackager (Release bundle and thumbnail frame extraction)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.subtitle.ass_karaoke_burner import AssKaraokeBurner, format_ass_time
from tools.analysis.scripture_hymn_rag import ScriptureHymnRAG
from tools.video.obs_controller import OBSController
from tools.publish.social_metadata_packager import SocialMetadataPackager


class TestMacTools(unittest.TestCase):

    def test_ass_time_formatting(self):
        self.assertEqual(format_ass_time(0.0), "0:00:00.00")
        self.assertEqual(format_ass_time(65.5), "0:01:05.50")
        self.assertEqual(format_ass_time(3600.0), "1:00:00.00")

    def test_scripture_hymn_rag(self):
        rag = ScriptureHymnRAG()
        res_hymn = rag.execute({"query": "115장", "mode": "hymn_info"})
        self.assertTrue(res_hymn.success)
        self.assertEqual(res_hymn.data["hymn_number"], 115)
        self.assertIn("기쁘다 구주 오셨네", res_hymn.data["metadata"]["title"])

        res_bible = rag.execute({"query": "창세기 4장"})
        self.assertTrue(res_bible.success)
        self.assertIn("가인", res_bible.data["characters"])

    def test_obs_controller_initialization(self):
        obs = OBSController()
        self.assertEqual(obs.name, "obs_controller")
        self.assertEqual(obs.capability, "video_post")

    def test_social_metadata_packager_initialization(self):
        packager = SocialMetadataPackager()
        self.assertEqual(packager.name, "social_metadata_packager")
        self.assertEqual(packager.capability, "publish")


if __name__ == "__main__":
    unittest.main()
