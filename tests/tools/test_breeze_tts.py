import unittest
from tools.audio.breeze_tts import BreezeTTS
from tools.base_tool import ToolStatus


class TestBreezeTTS(unittest.TestCase):
    def setUp(self):
        self.tool = BreezeTTS()

    def test_tool_metadata(self):
        self.assertEqual(self.tool.name, "breeze_tts")
        self.assertEqual(self.tool.capability, "tts")
        self.assertEqual(self.tool.provider, "breeze")
        self.assertTrue(self.tool.supports.get("voice_design"))
        self.assertTrue(self.tool.supports.get("voice_direction"))
        self.assertTrue(self.tool.supports.get("vocal_events"))

    def test_cost_estimation(self):
        cost = self.tool.estimate_cost({"text": "(laugh) Hello world!"})
        self.assertEqual(cost, 0.0)

    def test_input_schema(self):
        schema = self.tool.input_schema
        self.assertIn("text", schema["required"])
        self.assertIn("instruction", schema["properties"])
        self.assertIn("cfg_scale", schema["properties"])
        self.assertIn("reference_audio", schema["properties"])


if __name__ == "__main__":
    unittest.main()
