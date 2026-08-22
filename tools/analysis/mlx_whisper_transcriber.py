"""Apple Silicon MLX Whisper transcription tool.

Utilizes Apple's MLX machine learning framework to run OpenAI Whisper models
natively on Apple Silicon unified memory (M1/M2/M3/M4) via Metal with
blazing-fast performance, low energy consumption, and zero cloud API costs.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
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


class MLXWhisperTranscriber(BaseTool):
    name = "mlx_whisper"
    version = "1.0.0"
    tier = ToolTier.CORE
    capability = "analysis"
    provider = "apple_mlx"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["python:mlx", "python:mlx_whisper"]
    install_instructions = (
        "pip install mlx mlx-whisper\n"
        "Requires: macOS with Apple Silicon (M1/M2/M3/M4) on macOS 13.5+"
    )
    agent_skills = ["speech-to-text", "video-understand"]

    capabilities = [
        "transcribe",
        "word_timestamps",
        "language_detection",
        "apple_silicon_metal",
    ]

    supports = {
        "apple_silicon_native": True,
        "metal_acceleration": True,
        "unified_memory": True,
        "offline": True,
        "word_level_timestamps": True,
    }

    best_for = [
        "Blazing-fast local speech-to-text on MacBooks / Mac Studio / Mac Mini",
        "Extracting word-level timestamps for Remotion viral karaoke subtitles",
        "100% offline, private, zero-cost audio transcription",
    ]

    input_schema = {
        "type": "object",
        "required": ["input_path"],
        "properties": {
            "input_path": {
                "type": "string",
                "description": "Path to audio or video file.",
            },
            "model_path": {
                "type": "string",
                "default": "mlx-community/whisper-large-v3-mlx",
                "description": (
                    "MLX Whisper model repository. Options: "
                    "mlx-community/whisper-tiny-mlx, "
                    "mlx-community/whisper-base-mlx, "
                    "mlx-community/whisper-small-mlx, "
                    "mlx-community/whisper-large-v3-mlx, "
                    "mlx-community/whisper-large-v3-turbo"
                ),
            },
            "language": {
                "type": "string",
                "description": "ISO language code (e.g. 'ko', 'en', 'ja', 'zh') or null for auto-detect.",
            },
            "word_timestamps": {
                "type": "boolean",
                "default": True,
                "description": "Extract precise word-level start/end timestamps.",
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the transcript JSON and SRT files.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=4096, vram_mb=0, disk_mb=1000, network_required=False
    )

    idempotency_key_fields = ["input_path", "model_path", "language"]
    side_effects = ["writes transcript.json and transcript.srt to output_dir"]
    user_visible_verification = [
        "Verify transcript accuracy and word timestamp sync against source audio",
    ]

    def get_status(self) -> ToolStatus:
        import platform

        if platform.system() != "Darwin" or platform.machine() != "arm64":
            return ToolStatus.UNAVAILABLE
        try:
            import mlx_whisper  # noqa: F401
            return ToolStatus.AVAILABLE
        except ImportError:
            return ToolStatus.UNAVAILABLE

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        input_path = Path(inputs["input_path"])
        if not input_path.exists():
            return ToolResult(
                success=False, error=f"Input file not found: {input_path}"
            )

        model_path = inputs.get(
            "model_path", "mlx-community/whisper-large-v3-turbo"
        )
        language = inputs.get("language")
        word_timestamps = inputs.get("word_timestamps", True)
        output_dir = Path(inputs.get("output_dir", input_path.parent))
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            import mlx_whisper

            t0 = time.time()
            transcribe_kwargs: dict[str, Any] = {
                "path_or_hf_repo": model_path,
                "word_timestamps": word_timestamps,
            }
            if language:
                transcribe_kwargs["language"] = language

            result = mlx_whisper.transcribe(str(input_path), **transcribe_kwargs)
            elapsed = time.time() - t0

            # Extract words and segments
            segments = result.get("segments", [])
            words_list = []
            for seg in segments:
                for w in seg.get("words", []):
                    words_list.append(
                        {
                            "word": w.get("word", "").strip(),
                            "start": round(w.get("start", 0.0), 3),
                            "end": round(w.get("end", 0.0), 3),
                            "confidence": round(w.get("probability", 1.0), 3),
                        }
                    )

            # Write transcript JSON
            json_out = output_dir / f"{input_path.stem}_mlx_transcript.json"
            with open(json_out, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "text": result.get("text", "").strip(),
                        "language": result.get("language", language),
                        "segments": segments,
                        "words": words_list,
                        "elapsed_seconds": round(elapsed, 2),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            # Generate standard SRT
            srt_out = output_dir / f"{input_path.stem}_mlx_subtitles.srt"
            with open(srt_out, "w", encoding="utf-8") as f:
                for i, seg in enumerate(segments, 1):
                    s_sec = seg.get("start", 0.0)
                    e_sec = seg.get("end", 0.0)

                    def fmt(sec: float) -> str:
                        hrs = int(sec // 3600)
                        mins = int((sec % 3600) // 60)
                        secs = int(sec % 60)
                        mils = int((sec - int(sec)) * 1000)
                        return f"{hrs:02d}:{mins:02d}:{secs:02d},{mils:03d}"

                    f.write(f"{i}\n")
                    f.write(f"{fmt(s_sec)} --> {fmt(e_sec)}\n")
                    f.write(f"{seg.get('text', '').strip()}\n\n")

            return ToolResult(
                success=True,
                data={
                    "provider": "apple_mlx",
                    "text": result.get("text", "").strip(),
                    "language": result.get("language"),
                    "segments_count": len(segments),
                    "word_count": len(words_list),
                    "transcript_json_path": str(json_out),
                    "subtitles_srt_path": str(srt_out),
                    "elapsed_seconds": round(elapsed, 2),
                },
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"MLX Whisper transcription failed: {exc}",
            )
