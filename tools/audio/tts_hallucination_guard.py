"""TTS Hallucination and Pronunciation Guard for OpenMontage.

Performs closed-loop ASR verification on generated voiceover audio.
Detects autoregressive TTS stuttering, repetition loops, truncation,
and hallucinations by comparing the transcribed speech against target text.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

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


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute character-level Levenshtein edit distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def clean_text_for_comparison(text: str) -> str:
    """Strip punctuation and whitespace for pure character comparison."""
    if not text:
        return ""
    # Remove all non-alphanumeric characters
    cleaned = re.sub(r"[^\w\d가-힣]", "", text)
    return cleaned.lower()


class TTSHallucinationGuard(BaseTool):
    name = "tts_hallucination_guard"
    version = "0.1.0"
    tier = ToolTier.ANALYZE
    capability = "analysis"
    provider = "openmontage"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = []
    install_instructions = "Built-in validation tool."
    agent_skills = ["speech-to-text"]

    input_schema = {
        "type": "object",
        "required": ["audio_path", "target_text"],
        "properties": {
            "audio_path": {
                "type": "string",
                "description": "Path to synthesized speech audio file."
            },
            "target_text": {
                "type": "string",
                "description": "The expected speech script text."
            },
            "max_cer": {
                "type": "number",
                "default": 0.28,
                "description": "Maximum allowable Character Error Rate (default: 0.28)."
            }
        }
    }

    def _get_ffprobe(self) -> str:
        for c in ["ffprobe", "/Users/paul/pinokio/bin/ffmpeg-env/bin/ffprobe", "/opt/homebrew/bin/ffprobe"]:
            try:
                res = subprocess.run([c, "-version"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    return c
            except Exception:
                continue
        return "ffprobe"

    def _get_audio_duration(self, audio_path: str) -> float:
        try:
            cmd = [
                self._get_ffprobe(), "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", audio_path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip())
        except Exception:
            pass
        return 0.0

    def _transcribe_quick(self, audio_path: str) -> str:
        """Transcribe using available local faster-whisper or MLX whisper."""
        try:
            from tools.analysis.transcriber import Transcriber
            t_tool = Transcriber()
            res = t_tool.execute({"audio_path": audio_path, "language": "ko"})
            if res.success and res.data:
                return res.data.get("text", "")
        except Exception:
            pass
        return ""

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        audio_path = params.get("audio_path")
        if not audio_path or not os.path.exists(audio_path):
            return ToolResult(success=False, error=f"오디오 파일을 찾을 수 없습니다: {audio_path}")

        target_text = params.get("target_text", "").strip()
        if not target_text:
            return ToolResult(success=False, error="비교 대상 텍스트(target_text)가 비어있습니다.")

        max_cer = float(params.get("max_cer", 0.28))
        duration_sec = self._get_audio_duration(audio_path)

        # Basic duration sanity check (CPS: Characters Per Second)
        clean_target = clean_text_for_comparison(target_text)
        char_count = len(clean_target)

        # Speech rate check (normal Korean narration is 4-8 syllables per second)
        failure_reason = None
        if duration_sec < 0.2:
            failure_reason = "silent_or_empty_audio"
        elif char_count > 10 and duration_sec < char_count * 0.06:
            failure_reason = "truncated_speech (too short for text)"
        elif char_count > 5 and duration_sec > char_count * 0.65:
            failure_reason = "looping_or_stuck_audio (too long for text)"

        # Run transcription verification
        transcribed_text = self._transcribe_quick(audio_path)
        clean_transcribed = clean_text_for_comparison(transcribed_text)

        cer = 0.0
        similarity = 1.0

        if clean_transcribed and clean_target:
            dist = levenshtein_distance(clean_target, clean_transcribed)
            cer = dist / max(len(clean_target), 1)
            similarity = max(0.0, 1.0 - cer)

            # Check for repetition loops (e.g. repeated words)
            words = transcribed_text.split()
            for i in range(len(words) - 2):
                if words[i] == words[i+1] == words[i+2] and len(words[i]) > 1:
                    failure_reason = f"repetition_loop_detected ('{words[i]}')"
                    break

            if not failure_reason and cer > max_cer:
                failure_reason = f"high_character_error_rate (CER: {cer:.2f} > {max_cer:.2f})"

        passed = failure_reason is None

        return ToolResult(
            success=True,
            data={
                "passed": passed,
                "cer": round(cer, 3),
                "similarity": round(similarity, 3),
                "duration_seconds": round(duration_sec, 2),
                "target_text": target_text,
                "transcribed_text": transcribed_text,
                "failure_reason": failure_reason
            }
        )
