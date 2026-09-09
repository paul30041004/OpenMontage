"""Batch speech processor and volume normalizer for OpenMontage narration.

Normalizes multiple scene voiceover segments (sec_01.wav .. sec_15.wav)
to a consistent EBU R128 (-14.0 LUFS) standard across an entire episode,
prevents inter-scene volume jumping, and provides Apple Silicon MPS memory hygiene.
"""

from __future__ import annotations

import gc
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolStability,
    ToolStatus,
    ToolTier,
)


def mps_garbage_collect() -> None:
    """Forces Python and PyTorch MPS garbage collection to free unified memory."""
    gc.collect()
    try:
        import torch
        if hasattr(torch, "mps") and hasattr(torch.mps, "empty_cache"):
            torch.mps.empty_cache()
    except Exception:
        pass


class BatchSpeechProcessor(BaseTool):
    name = "batch_speech_processor"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "audio_processing"
    provider = "ffmpeg"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "FFmpeg is required."
    agent_skills = ["ffmpeg", "tts-sample-unification"]

    input_schema = {
        "type": "object",
        "required": ["segments", "output_dir"],
        "properties": {
            "segments": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of audio file paths for all scenes in an episode."
            },
            "output_dir": {
                "type": "string",
                "description": "Output directory for normalized segments."
            },
            "concat_output": {
                "type": "string",
                "description": "Optional path to export a single unified full-narration WAV."
            },
            "target_lufs": {
                "type": "number",
                "default": -14.0,
                "description": "Integrated loudness target in LUFS (default: -14.0)."
            }
        }
    }

    def _get_ffmpeg(self) -> str:
        for c in ["ffmpeg", "/Users/paul/pinokio/bin/ffmpeg-env/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]:
            try:
                res = subprocess.run([c, "-version"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    return c
            except Exception:
                continue
        return "ffmpeg"

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        segments = params.get("segments", [])
        if not segments:
            return ToolResult(success=False, error="정규화할 오디오 세그먼트 목록(segments)이 비어있습니다.")

        out_dir = Path(params["output_dir"]).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        target_lufs = float(params.get("target_lufs", -14.0))
        ffmpeg_bin = self._get_ffmpeg()

        normalized_paths: List[str] = []

        # 1. Normalize each segment individually to target LUFS
        for i, seg_path in enumerate(segments, 1):
            p = Path(seg_path).resolve()
            if not p.exists():
                continue

            out_seg = out_dir / f"norm_{p.stem}.wav"
            cmd = [
                ffmpeg_bin, "-y",
                "-i", str(p),
                "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=9",
                "-c:a", "pcm_s16le",
                "-ar", "24000",
                str(out_seg)
            ]
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                normalized_paths.append(str(out_seg))
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to normalize {p.name}: {e.stderr}")
                normalized_paths.append(str(p))

        # 2. Optional concatenation into one master WAV
        concat_path = params.get("concat_output")
        concat_done = False
        if concat_path and normalized_paths:
            concat_file = Path(concat_path).resolve()
            concat_file.parent.mkdir(parents=True, exist_ok=True)

            list_txt = out_dir / "concat_list.txt"
            with open(list_txt, "w", encoding="utf-8") as f:
                for np in normalized_paths:
                    abs_p = str(Path(np).resolve())
                    f.write(f"file '{abs_p}'\n")

            codec_args = ["-c:a", "libmp3lame", "-b:a", "192k"] if str(concat_file).endswith(".mp3") else ["-c:a", "pcm_s16le"]
            cmd_concat = [
                ffmpeg_bin, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_txt)
            ] + codec_args + [str(concat_file)]
            try:
                subprocess.run(cmd_concat, capture_output=True, text=True, check=True)
                concat_done = True
            except subprocess.CalledProcessError as e:
                print(f"Concat failed: {e.stderr}")
            finally:
                if list_txt.exists():
                    list_txt.unlink()

        # Free Apple Silicon MPS memory cache
        mps_garbage_collect()

        return ToolResult(
            success=True,
            data={
                "normalized_count": len(normalized_paths),
                "normalized_segments": normalized_paths,
                "concat_output": str(concat_path) if concat_done else None,
                "target_lufs": target_lufs
            }
        )
