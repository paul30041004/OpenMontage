"""Edge TTS provider tool wrapping edge-tts.

Provides 100% free, high-quality Microsoft Neural text-to-speech without
requiring any API keys or paid cloud accounts. Supports 70+ languages,
300+ voices, rate/pitch adjustments, and word-level timestamp extraction.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import time
from pathlib import Path
from typing import Any, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


class EdgeTTS(BaseTool):
    name = "edge_tts"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "edge_tts"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.API

    dependencies = ["python:edge_tts"]
    install_instructions = "pip install edge-tts"
    agent_skills = ["text-to-speech"]

    capabilities = [
        "text_to_speech",
        "multilingual",
        "voice_selection",
        "speed_control",
        "pitch_control",
        "word_timestamps",
    ]

    supports = {
        "voice_cloning": False,
        "multilingual": True,
        "offline": False,
        "free": True,
        "no_api_key_required": True,
    }

    best_for = [
        "100% free high-quality neural voiceover without API keys",
        "Korean, English, Japanese, Chinese, and 70+ languages",
        "Fast synthesis with natural human-like cadence",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to synthesize into speech.",
            },
            "voice": {
                "type": "string",
                "default": "ko-KR-InJoonNeural",
                "description": (
                    "Voice identifier. Examples: "
                    "ko-KR-InJoonNeural (Korean Male, deep/narrative), "
                    "ko-KR-SunHiNeural (Korean Female, warm/clear), "
                    "ko-KR-HyunsuNeural (Korean Male, energetic), "
                    "en-US-ChristopherNeural (English Male, documentary), "
                    "en-US-AriaNeural (English Female, professional), "
                    "en-US-GuyNeural (English Male, conversational), "
                    "ja-JP-NanamiNeural (Japanese Female), "
                    "zh-CN-YunxiNeural (Chinese Male)."
                ),
            },
            "rate": {
                "type": "string",
                "default": "+0%",
                "description": "Speaking rate modifier (e.g. '+10%', '-5%').",
            },
            "pitch": {
                "type": "string",
                "default": "+0Hz",
                "description": "Pitch modifier (e.g. '+5Hz', '-5Hz').",
            },
            "volume": {
                "type": "string",
                "default": "+0%",
                "description": "Volume modifier (e.g. '+0%', '-10%').",
            },
            "output_path": {
                "type": "string",
                "description": "Path to write the generated audio file (.mp3).",
            },
            "write_subtitles": {
                "type": "boolean",
                "default": False,
                "description": "Whether to extract word-level VTT subtitles alongside audio.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50, network_required=True
    )

    idempotency_key_fields = ["text", "voice", "rate", "pitch"]
    side_effects = ["writes audio file to output_path"]
    user_visible_verification = [
        "Listen to generated audio for natural neural inflection and pacing",
    ]

    def get_status(self) -> ToolStatus:
        try:
            import edge_tts  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    async def _synthesize_async(
        self,
        text: str,
        voice: str,
        rate: str,
        pitch: str,
        volume: str,
        output_path: str,
        write_subtitles: bool,
    ) -> dict[str, Any]:
        import edge_tts

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
        )

        sub_path = None
        if write_subtitles:
            sub_path = str(Path(output_path).with_suffix(".srt"))
            sub_maker = edge_tts.SubMaker()
            with open(output_path, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        sub_maker.feed(chunk)

            with open(sub_path, "w", encoding="utf-8") as f:
                f.write(sub_maker.get_srt())
        else:
            await communicate.save(output_path)

        return {"output_path": output_path, "subtitle_path": sub_path}

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        try:
            import edge_tts  # noqa: F401
        except ImportError:
            return ToolResult(
                success=False,
                error="edge-tts package not installed. Run: pip install edge-tts",
            )

        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="Text input cannot be empty.")

        voice = inputs.get("voice", "ko-KR-InJoonNeural")
        rate = inputs.get("rate", "+0%")
        pitch = inputs.get("pitch", "+0Hz")
        volume = inputs.get("volume", "+0%")
        write_subtitles = inputs.get("write_subtitles", False)

        output_path = inputs.get("output_path")
        if not output_path:
            output_path = f"assets/audio/edge_tts_{int(time.time())}.mp3"

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            result_meta = asyncio.run(
                self._synthesize_async(
                    text=text,
                    voice=voice,
                    rate=rate,
                    pitch=pitch,
                    volume=volume,
                    output_path=str(out_file),
                    write_subtitles=write_subtitles,
                )
            )

            # Probe duration
            duration_seconds = 0.0
            if shutil.which("ffprobe"):
                import subprocess

                try:
                    cmd = [
                        "ffprobe",
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        str(out_file),
                    ]
                    duration_seconds = float(
                        subprocess.check_output(cmd).decode().strip()
                    )
                except Exception:
                    pass

            return ToolResult(
                success=True,
                data={
                    "provider": "edge_tts",
                    "voice": voice,
                    "output": str(out_file),
                    "duration_seconds": duration_seconds,
                    "subtitle_path": result_meta.get("subtitle_path"),
                    "cost_usd": 0.0,
                    "license": "Free Microsoft Neural TTS",
                },
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"EdgeTTS synthesis failed: {exc}",
            )
