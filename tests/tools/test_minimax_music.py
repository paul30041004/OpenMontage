import unittest
from tools.audio.minimax_music import MiniMaxMusic
from tools.base_tool import ToolStatus


class TestMiniMaxMusic(unittest.TestCase):
    def setUp(self):
        self.tool = MiniMaxMusic()

    def test_tool_metadata(self):
        self.assertEqual(self.tool.name, "minimax_music")
        self.assertEqual(self.tool.capability, "music_generation")
        self.assertEqual(self.tool.provider, "minimax")
        self.assertTrue(self.tool.supports.get("instrumental"))

    def test_cost_estimation(self):
        cost = self.tool.estimate_cost({"prompt": "Upbeat gaming BGM"})
        self.assertEqual(cost, 0.03)

    def test_status_without_env(self):
        import os
        old_val = os.environ.pop("MINIMAX_API_KEY", None)
        try:
            status = self.tool.get_status()
            self.assertEqual(status, ToolStatus.UNAVAILABLE)
        finally:
            if old_val:
                os.environ["MINIMAX_API_KEY"] = old_val


if __name__ == "__main__":
    unittest.main()
