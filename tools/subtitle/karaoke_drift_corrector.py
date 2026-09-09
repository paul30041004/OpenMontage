"""Acoustic Energy Peak-Snapped Karaoke Subtitle Drift Corrector for OpenMontage.

Corrects whisper/transcriber timestamp drift by analyzing physical vocal acoustic
energy envelopes and onset strength peaks via Librosa.
Snaps word-level subtitles to the exact microsecond of speech attacks,
producing frame-accurate karaoke highlight captions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

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


class KaraokeDriftCorrector(BaseTool):
    name = "karaoke_drift_corrector"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "subtitle"
    provider = "librosa"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["python:librosa"]
    install_instructions = "Install librosa:\n  pip install librosa"
    agent_skills = ["remotion-best-practices", "ffmpeg"]

    input_schema = {
        "type": "object",
        "required": ["audio_path", "words"],
        "properties": {
            "audio_path": {
                "type": "string",
                "description": "Path to the vocal audio file (WAV or MP3)."
            },
            "words": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["text", "start", "end"],
                    "properties": {
                        "text": {"type": "string"},
                        "start": {"type": "number"},
                        "end": {"type": "number"}
                    }
                },
                "description": "List of word-level timestamp objects from Whisper."
            },
            "output_json": {
                "type": "string",
                "description": "Optional destination path to save calibrated karaoke JSON."
            },
            "snap_window_ms": {
                "type": "number",
                "default": 200,
                "description": "Search window in milliseconds to snap to the nearest acoustic onset."
            }
        }
    }

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        import librosa

        audio_path = params.get("audio_path")
        if not audio_path or not os.path.exists(audio_path):
            return ToolResult(success=False, error=f"오디오 파일을 찾을 수 없습니다: {audio_path}")

        raw_words = params.get("words", [])
        if not raw_words:
            return ToolResult(success=False, error="단어 타임스탬프 목록(words)이 비어있습니다.")

        snap_window_sec = float(params.get("snap_window_ms", 200)) / 1000.0

        # 1. Load Audio and compute onset strength envelope
        y, sr = librosa.load(audio_path, sr=22050, mono=True)
        hop_length = 256
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        times = librosa.times_like(onset_env, sr=sr, hop_length=hop_length)

        # Detect physical onset peaks
        peaks = librosa.util.peak_pick(
            onset_env,
            pre_max=3,
            post_max=3,
            pre_avg=3,
            post_avg=3,
            delta=0.08,
            wait=3
        )
        peak_times = times[peaks]

        # 2. Calibrate each word timestamp
        calibrated_words: List[Dict[str, Any]] = []

        for w in raw_words:
            orig_start = float(w.get("start", 0.0))
            orig_end = float(w.get("end", orig_start + 0.3))
            text = str(w.get("text", "")).strip()

            # Find nearest acoustic peak within snap window
            candidate_peaks = peak_times[
                (peak_times >= orig_start - snap_window_sec) &
                (peak_times <= orig_start + snap_window_sec)
            ]

            if len(candidate_peaks) > 0:
                # Snap to the closest physical energy attack
                closest_peak = candidate_peaks[np.argmin(np.abs(candidate_peaks - orig_start))]
                calibrated_start = round(float(closest_peak), 3)
            else:
                calibrated_start = round(orig_start, 3)

            # Ensure minimum duration and forward progression
            calibrated_end = max(round(orig_end, 3), calibrated_start + 0.08)

            calibrated_words.append({
                "text": text,
                "start": calibrated_start,
                "end": calibrated_end,
                "duration": round(calibrated_end - calibrated_start, 3),
                "original_start": round(orig_start, 3),
                "snapped": calibrated_start != round(orig_start, 3)
            })

        # Save to JSON if requested
        out_json_path = params.get("output_json")
        if out_json_path:
            out_file = Path(out_json_path).resolve()
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(calibrated_words, f, indent=2, ensure_ascii=False)

        snapped_count = sum(1 for x in calibrated_words if x["snapped"])

        return ToolResult(
            success=True,
            data={
                "total_words": len(calibrated_words),
                "snapped_count": snapped_count,
                "calibrated_words": calibrated_words,
                "output_json": out_json_path
            }
        )
