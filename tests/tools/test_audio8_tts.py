import unittest
from tools.audio.audio8_tts import Audio8TTS
from tools.base_tool import ToolStatus


class TestAudio8TTS(unittest.TestCase):
    def setUp(self):
        self.tool = Audio8TTS()

    def test_tool_metadata(self):
        self.assertEqual(self.tool.name, "audio8_tts")
        self.assertEqual(self.tool.capability, "tts")
        self.assertEqual(self.tool.provider, "audio8")
        self.assertTrue(self.tool.supports.get("voice_cloning"))
        self.assertTrue(self.tool.supports.get("zero_shot"))

    def test_cost_estimation(self):
        cost = self.tool.estimate_cost({"text": "테스트 문장입니다."})
        self.assertEqual(cost, 0.0)

    def test_input_schema(self):
        schema = self.tool.input_schema
        self.assertIn("text", schema["required"])
        self.assertIn("reference_audio", schema["properties"])
        self.assertIn("reference_text", schema["properties"])


if __name__ == "__main__":
    unittest.main()
