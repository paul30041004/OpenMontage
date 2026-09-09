"""Vocal Mastering and Audio Engine for OpenMontage.

Applies broadcast-grade vocal mastering, surgical EQ (high-pass, presence, air),
sibilance de-essing, lush room/church reverb, intelligent backing track ducking,
and EBU R128 (-14 LUFS) loudness normalization using FFmpeg.
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


class VocalMastering(BaseTool):
    name = "vocal_mastering"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "audio_processing"
    provider = "ffmpeg"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "FFmpeg is required for vocal mastering."
    agent_skills = ["ffmpeg"]

    input_schema = {
        "type": "object",
        "required": ["vocal_audio", "output_path"],
        "properties": {
            "vocal_audio": {
                "type": "string",
                "description": "Path to primary vocal audio file (WAV or MP3)."
            },
            "instrumental_audio": {
                "type": "string",
                "description": "Optional path to backing accompaniment track (piano, strings, band)."
            },
            "output_path": {
                "type": "string",
                "description": "Destination file path for the final mastered audio (.mp3 or .wav)."
            },
            "reverb_preset": {
                "type": "string",
                "enum": ["church", "hall", "room", "plate", "none"],
                "default": "church",
                "description": "Reverb acoustic environment (church is ideal for hymns/worship, hall for classical)."
            },
            "reverb_wet": {
                "type": "number",
                "default": 0.22,
                "description": "Reverb wet mix ratio (0.0 to 1.0, default 0.22)."
            },
            "vocal_eq": {
                "type": "boolean",
                "default": True,
                "description": "Applies 80Hz rumble cut, 3.5kHz vocal presence, and 10kHz air boost."
            },
            "de_esser": {
                "type": "boolean",
                "default": True,
                "description": "Tames harsh sibilance around 6.5kHz."
            },
            "ducking": {
                "type": "boolean",
                "default": True,
                "description": "Automatically ducks accompaniment when vocals sing."
            },
            "target_lufs": {
                "type": "number",
                "default": -14.0,
                "description": "EBU R128 integrated loudness target (default: -14.0 LUFS for YouTube/streaming)."
            }
        }
    }

    REVERB_FILTERS = {
        "church": "aecho=0.8:0.7:60|120|180:0.3|0.2|0.12",
        "hall": "aecho=0.8:0.65:40|80:0.25|0.15",
        "plate": "aecho=0.8:0.5:30|55:0.2|0.1",
        "room": "aecho=0.8:0.4:20|35:0.15|0.08",
        "none": None
    }

    def _get_ffmpeg(self) -> str:
        candidates = [
            "ffmpeg",
            "/Users/paul/pinokio/bin/ffmpeg-env/bin/ffmpeg",
            "/Users/paul/pinokio/bin/miniforge/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg"
        ]
        for c in candidates:
            try:
                res = subprocess.run([c, "-version"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    return c
            except Exception:
                continue
        return "ffmpeg"

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        vocal_path = params.get("vocal_audio")
        if not vocal_path or not os.path.exists(vocal_path):
            return ToolResult(success=False, error=f"보컬 오디오 파일을 찾을 수 없습니다: {vocal_path}")

        output_path = params.get("output_path")
        if not output_path:
            return ToolResult(success=False, error="출력 경로(output_path)가 지정되지 않았습니다.")

        inst_path = params.get("instrumental_audio")
        has_inst = inst_path is not None and os.path.exists(inst_path)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        reverb_preset = params.get("reverb_preset", "church").lower()
        reverb_str = self.REVERB_FILTERS.get(reverb_preset)
        reverb_wet = float(params.get("reverb_wet", 0.22))
        vocal_eq = params.get("vocal_eq", True)
        de_esser = params.get("de_esser", True)
        ducking = params.get("ducking", True) and has_inst
        target_lufs = float(params.get("target_lufs", -14.0))

        # Build vocal filter chain
        vocal_filters = []
        if vocal_eq:
            vocal_filters.append("highpass=f=80")
            vocal_filters.append("equalizer=f=3500:t=q:w=1.2:g=2.5")
            vocal_filters.append("equalizer=f=10000:t=q:w=1.0:g=2.0")
        if de_esser:
            vocal_filters.append("equalizer=f=6500:t=q:w=2.0:g=-3.0")

        # Gentle vocal leveling
        vocal_filters.append("acompressor=threshold=0.15:ratio=3:attack=10:release=200")

        # Add reverb
        if reverb_str:
            vocal_filters.append(reverb_str)

        vocal_chain = ",".join(vocal_filters) if vocal_filters else "anull"

        cmd = [self._get_ffmpeg(), "-y", "-i", vocal_path]

        if has_inst:
            cmd.extend(["-i", inst_path])
            if ducking:
                filter_complex = (
                    f"[0:a]{vocal_chain}[voc];"
                    f"[1:a][voc]sidechaincompress=threshold=0.12:ratio=3.5:attack=15:release=250[inst_ducked];"
                    f"[voc][inst_ducked]amix=inputs=2:duration=longest:weights=1.1 0.85[mixed];"
                    f"[mixed]loudnorm=I={target_lufs}:TP=-1.5:LRA=11[out]"
                )
            else:
                filter_complex = (
                    f"[0:a]{vocal_chain}[voc];"
                    f"[voc][1:a]amix=inputs=2:duration=longest:weights=1.1 0.85[mixed];"
                    f"[mixed]loudnorm=I={target_lufs}:TP=-1.5:LRA=11[out]"
                )
            cmd.extend(["-filter_complex", filter_complex, "-map", "[out]"])
        else:
            filter_chain = f"{vocal_chain},loudnorm=I={target_lufs}:TP=-1.5:LRA=11"
            cmd.extend(["-af", filter_chain])

        # Bitrate / Encoding
        if output_path.endswith(".mp3"):
            cmd.extend(["-b:a", "320k"])
        elif output_path.endswith(".wav"):
            cmd.extend(["-c:a", "pcm_s24le", "-ar", "48000"])

        cmd.append(output_path)

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return ToolResult(
                success=True,
                data={
                    "output_path": output_path,
                    "target_lufs": target_lufs,
                    "reverb_preset": reverb_preset,
                    "instrumental_present": has_inst,
                    "ducking_applied": ducking,
                    "file_size": os.path.getsize(output_path)
                }
            )
        except subprocess.CalledProcessError as e:
            return ToolResult(
                success=False,
                error=f"FFmpeg 마스터링 실패: {e.stderr}"
            )
