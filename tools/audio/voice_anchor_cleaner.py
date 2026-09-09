"""Voice Reference Anchor Cleaner for OpenMontage Neural Voice Cloning.

Prepares raw voice clips (from YouTube, podcasts, or recordings) for zero-shot
voice cloning (VoxCPM2, Qwen3-TTS, Chatterbox). Performs voice activity detection
(VAD) silence trimming, noise filtering, duration clamping (5-15s), and audio normalization.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

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


class VoiceAnchorCleaner(BaseTool):
    name = "voice_anchor_cleaner"
    version = "0.1.0"
    tier = ToolTier.ENHANCE
    capability = "audio_processing"
    provider = "ffmpeg"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "FFmpeg is required for voice anchor cleaning."
    agent_skills = ["ffmpeg", "tts-sample-unification"]

    input_schema = {
        "type": "object",
        "required": ["input_audio", "output_path"],
        "properties": {
            "input_audio": {
                "type": "string",
                "description": "Path to raw input voice sample (WAV, MP3, M4A)."
            },
            "output_path": {
                "type": "string",
                "description": "Destination path for cleaned reference anchor WAV."
            },
            "max_duration_seconds": {
                "type": "number",
                "default": 12.0,
                "description": "Maximum reference duration (default: 12.0s, optimal for zero-shot embeddings)."
            },
            "min_duration_seconds": {
                "type": "number",
                "default": 3.0,
                "description": "Minimum required speech duration (default: 3.0s)."
            },
            "sample_rate": {
                "type": "integer",
                "default": 24000,
                "description": "Output sample rate in Hz (default: 24000Hz standard for TTS encoders)."
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

    def _get_ffprobe(self) -> str:
        for c in ["ffprobe", "/Users/paul/pinokio/bin/ffmpeg-env/bin/ffprobe", "/opt/homebrew/bin/ffprobe"]:
            try:
                res = subprocess.run([c, "-version"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    return c
            except Exception:
                continue
        return "ffprobe"

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        input_audio = params.get("input_audio")
        if not input_audio or not os.path.exists(input_audio):
            return ToolResult(success=False, error=f"입력 오디오 파일을 찾을 수 없습니다: {input_audio}")

        output_path = params.get("output_path")
        if not output_path:
            return ToolResult(success=False, error="출력 경로(output_path)가 필요합니다.")

        max_dur = float(params.get("max_duration_seconds", 12.0))
        min_dur = float(params.get("min_duration_seconds", 3.0))
        sr = int(params.get("sample_rate", 24000))

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        ffmpeg_bin = self._get_ffmpeg()

        # Audio filter chain:
        # 1. Silenceremove start: strip leading silence
        # 2. Silenceremove stop: strip trailing silence
        # 3. Highpass 80Hz + Lowpass 9000Hz (voice isolation band)
        # 4. Loudness normalization to -18 LUFS (ideal clean reference level)
        filters = [
            "silenceremove=start_periods=1:start_duration=0.08:start_threshold=-42dB",
            "areverse",
            "silenceremove=start_periods=1:start_duration=0.08:start_threshold=-42dB",
            "areverse",
            "highpass=f=80",
            "lowpass=f=9500",
            "loudnorm=I=-18:TP=-1.0:LRA=9"
        ]
        af_str = ",".join(filters)

        cmd = [
            ffmpeg_bin, "-y",
            "-i", input_audio,
            "-t", str(max_dur),
            "-af", af_str,
            "-ac", "1",
            "-ar", str(sr),
            "-c:a", "pcm_s16le",
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            return ToolResult(success=False, error=f"FFmpeg 정제 실패: {e.stderr}")

        # Check result duration
        try:
            probe_cmd = [
                self._get_ffprobe(), "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", output_path
            ]
            res = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=5)
            final_dur = float(res.stdout.strip())
        except Exception:
            final_dur = 0.0

        if final_dur < min_dur:
            return ToolResult(
                success=False,
                error=f"정제된 음성 길이가 너무 짧습니다 ({final_dur:.2f}초 < 최소 {min_dur}초). 음성이 포함된 구간을 선택해주세요."
            )

        return ToolResult(
            success=True,
            data={
                "output_path": output_path,
                "duration_seconds": round(final_dur, 2),
                "sample_rate": sr,
                "channels": 1,
                "file_size": os.path.getsize(output_path),
                "message": f"음성 복제용 앵커 정제 완료 ({final_dur:.1f}초, 24kHz Mono WAV)."
            }
        )
