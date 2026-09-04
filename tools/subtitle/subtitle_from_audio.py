"""Audio-driven subtitle tool for OpenMontage — precise SRT from narration.

Transcribes a narration WAV with faster-whisper to get ACTUAL sentence-level
timestamps, then writes an SRT whose cues appear exactly when each sentence is
spoken. This syncs subtitles to the real TTS timecode (vs. fixed guesses).

Use before compositing so subtitles track the narration precisely.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    DependencyError,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)


def _fmt(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class SubtitleFromAudio(BaseTool):
    name = "subtitle_from_audio"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "subtitle"
    provider = "faster-whisper"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "Uses faster-whisper (offline). Model downloads on first use."
    agent_skills = ["speech-to-text"]

    capabilities = ["srt_from_audio", "narration_synced_subtitles"]

    input_schema = {
        "type": "object",
        "required": ["audio_path"],
        "properties": {
            "audio_path": {"type": "string", "description": "Narration audio to transcribe."},
            "output_path": {"type": "string", "description": "Output .srt path."},
            "script_lines": {
                "type": "array", "items": {"type": "string"},
                "description": "Original scripture/script lines (the accurate 대본). If provided, the SRT uses THIS text with transcription timestamps (text-aligned-to-audio). If omitted, uses the transcribed text.",
            },
            "model_size": {"type": "string", "default": "small"},
            "language": {"type": "string", "default": "ko"},
            "offset_seconds": {"type": "number", "default": 0.0,
                             "description": "Shift all cues by this many seconds (e.g., narration starts at 0.9s)."},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=2048, vram_mb=0, disk_mb=500)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["audio_path", "model_size"]
    side_effects = ["writes .srt to output_path"]
    user_visible_verification = [
        "Subtitle cues appear exactly when each sentence is spoken",
        "Times match the narration, not approximate guesses",
    ]

    def get_status(self) -> ToolStatus:
        try:
            from tools.analysis.transcriber import Transcriber  # noqa: F401
            return ToolStatus.AVAILABLE
        except Exception:
            return ToolStatus.UNAVAILABLE

    def check_dependencies(self) -> None:
        try:
            from tools.analysis.transcriber import Transcriber  # noqa: F401
        except Exception:
            raise DependencyError("faster-whisper/transcriber unavailable. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 15.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        audio = Path(inputs.get("audio_path", "")).resolve()
        if not audio.is_file():
            return ToolResult(success=False, error="audio_path required")
        out = Path(inputs.get("output_path", str(audio.with_suffix(".srt")))).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        offset = float(inputs.get("offset_seconds", 0.0))

        from tools.analysis.transcriber import Transcriber
        r = Transcriber().execute({
            "input_path": str(audio),
            "model_size": inputs.get("model_size", "small"),
            "language": inputs.get("language", "ko"),
        })
        if not r.success:
            return ToolResult(success=False, error=f"transcription failed: {r.error}")

        segments = r.data.get("segments", [])
        if not segments:
            return ToolResult(success=False, error="no segments transcribed")

        # Use timestamps from transcription, but text from the script (if provided).
        # Emit exactly len(script_lines) cues, all scripture text; extra segments
        # extend the last cue so nothing is cut or mis-transcribed.
        script = inputs.get("script_lines") or []
        lines = []
        if script:
            n = len(script)
            for i in range(n):
                s_idx = min(i, len(segments) - 1)
                t0 = segments[s_idx]["start"] + offset
                t1 = segments[s_idx]["end"] + offset
                if i == n - 1:
                    t1 = segments[-1]["end"] + offset
                text = script[i].strip()
                if not text:
                    continue
                lines += [str(len(lines) // 4 + 1), f"{_fmt(t0)} --> {_fmt(t1)}", text, ""]
        else:
            idx = 0
            for i, seg in enumerate(segments):
                t0 = seg["start"] + offset
                t1 = seg["end"] + offset
                text = seg["text"].strip()
                if not text:
                    continue
                idx += 1
                lines += [str(idx), f"{_fmt(t0)} --> {_fmt(t1)}", text, ""]
        out.write_text("\n".join(lines), encoding="utf-8")

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(out),
                  "segments": len(lines) // 4,
                  "text_source": "script" if script else "transcription",
                  "first_cue": (segments[0]["start"] + offset, segments[0]["end"] + offset)},
            artifacts=[str(out)], duration_seconds=round(time.time() - start, 2),
        )
