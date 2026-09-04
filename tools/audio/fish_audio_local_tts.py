"""Local MLX Fish Audio S2-Pro text-to-speech provider tool.

Runs the local open-weights Fish Audio S2-Pro model (mlx-community/fish-audio-s2-pro-8bit)
accelerated by Apple Silicon MLX GPU via fish-clean-venv. Zero API cost, fully offline.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
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

log = logging.getLogger(__name__)

PYTHON_BIN = "/Users/paul/fish-clean-venv/bin/python"


class FishAudioLocalTTS(BaseTool):
    name = "fish_audio_local_tts"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "fish_audio_local"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL_GPU

    dependencies = [f"path:{PYTHON_BIN}"]
    install_instructions = (
        "Requires mlx-audio in /Users/paul/fish-clean-venv and the local "
        "mlx-community/fish-audio-s2-pro-8bit model in ~/.cache/huggingface/hub/."
    )
    fallback = "voxcpm_tts"
    fallback_tools = ["voxcpm_tts", "bert_vits2_tts", "google_tts"]
    agent_skills = ["fish-audio-tts", "text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_cloning",
        "multilingual",
        "local_tts",
    ]
    supports = {
        "voice_cloning": True,
        "multilingual": True,
        "offline": True,
        "native_audio": True,
        "apple_silicon_mlx": True,
    }
    best_for = [
        "high-quality local Korean, English, Japanese, Chinese speech synthesis",
        "fast Apple Silicon MLX GPU acceleration",
        "zero API cost fully offline production",
    ]
    not_good_for = [
        "SSML markup control",
    ]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to synthesize.",
            },
            "speed": {
                "type": "number",
                "default": 1.1,
                "description": "Speech speed multiplier (1.0 = normal, 1.2 = fast).",
            },
            "temperature": {
                "type": "number",
                "default": 0.7,
                "description": "Sampling temperature for voice expression.",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to local reference audio WAV for voice cloning / anchor unification.",
            },
            "reference_text": {
                "type": "string",
                "description": "Transcript of reference audio (sharpens clone pronunciation).",
            },
            "instruct": {
                "type": "string",
                "description": "Natural-language emotion/style instruction (e.g. '매우 긴박하고 흥분된 목소리로 빠르게').",
            },
            "emotion": {
                "type": "string",
                "description": "Alias for instruct.",
            },
            "output_path": {
                "type": "string",
                "description": "Output path for the generated WAV/MP3 file.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=8192, vram_mb=4096, disk_mb=3000, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])

    def get_status(self) -> ToolStatus:
        if Path(PYTHON_BIN).exists():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        text_len = len(inputs.get("text", ""))
        return max(1.5, round(text_len * 0.04, 2))

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text is required")

        speed = float(inputs.get("speed", 1.1))
        temperature = float(inputs.get("temperature", 0.7))
        instruct = inputs.get("instruct") or inputs.get("emotion") or ""
        ref_audio = inputs.get("reference_audio")
        ref_text = inputs.get("reference_text", "")
        output_path = Path(inputs.get("output_path", "output_fish_local.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        ref_load_code = ""
        gen_kwargs = []
        gen_kwargs.append(f"text={repr(text)}")
        gen_kwargs.append(f"speed={speed}")
        gen_kwargs.append(f"temperature={temperature}")
        gen_kwargs.append("verbose=False")

        if instruct:
            gen_kwargs.append(f"instruct={repr(instruct)}")

        if ref_audio and Path(ref_audio).is_file():
            ref_load_code = f"""
data, sr = sf.read({repr(str(ref_audio))})
ref_arr = mx.array(data, dtype=mx.float32)
"""
            gen_kwargs.append("ref_audio=ref_arr")
            if ref_text:
                gen_kwargs.append(f"ref_text={repr(ref_text)}")

        kwargs_str = ", ".join(gen_kwargs)

        script = f"""
import mlx_audio.tts as tts
import soundfile as sf
import mlx.core as mx
import numpy as np

model = tts.load_model('mlx-community/fish-audio-s2-pro-8bit')
{ref_load_code}

chunks = []
for chunk in model.generate({kwargs_str}):
    if hasattr(chunk, 'audio'):
        chunks.append(np.array(chunk.audio))
    else:
        chunks.append(np.array(chunk))

audio_data = np.concatenate(chunks) if chunks else np.array([])
sr = getattr(model, 'sample_rate', 44100)
sf.write({repr(str(output_path))}, audio_data, sr)
print('SUCCESS')
"""
        start = time.time()
        try:
            res = subprocess.run(
                [PYTHON_BIN, "-c", script],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Fish Audio Local MLX generation failed: {exc}",
            )

        if not output_path.exists() or output_path.stat().st_size < 1000:
            return ToolResult(
                success=False,
                error="Output audio file was not created properly",
            )

        dur = None
        try:
            probe = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )
            if probe.returncode == 0 and probe.stdout.strip():
                dur = round(float(probe.stdout.strip()), 2)
        except Exception:
            dur = None

        elapsed = round(time.time() - start, 2)
        return ToolResult(
            success=True,
            data={
                "provider": "fish_audio_local",
                "model": "fish-audio-s2-pro-8bit-mlx",
                "output": str(output_path),
                "duration_seconds": dur,
                "text_length": len(text),
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=elapsed,
        )
