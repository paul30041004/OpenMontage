"""Qwen3-TTS local text-to-speech tool (Apple Silicon MLX).

Runs Qwen3-TTS (Qwen's state-of-the-art open-weight TTS) locally via mlx-audio
on Apple Silicon Metal GPU. Supports three modes:

- voice_clone: 3-second zero-shot voice cloning from reference audio (Base model)
- custom_voice: 9 premium timbres incl. Korean 'Sohee' (CustomVoice model)
- voice_design: natural-language voice design (VoiceDesign model)

Qwen3-TTS covers 10 languages (ko/en/ja/zh/de/fr/ru/pt/es/it) and ranks at the
top of open-weight TTS leaderboards (WER/SIM). Zero API cost, fully offline.
"""

from __future__ import annotations

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

PYTHON_BIN = "/Users/paul/fish-clean-venv/bin/python"

# Model variants (mlx-community quantized for Apple Silicon)
_MODELS = {
    "base_0.6b": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit",
    "base_1.7b": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
    "custom_0.6b": "mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit",
    "custom_1.7b": "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-8bit",
    "design_1.7b": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit",
}

_SPEAKERS = ["serena", "vivian", "uncle_fu", "ryan", "aiden", "ono_anna", "sohee", "eric", "dylan"]


class Qwen3TTS(BaseTool):
    name = "qwen3_tts"
    version = "1.0.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "qwen3"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.LOCAL_GPU

    dependencies = [f"path:{PYTHON_BIN}"]
    install_instructions = (
        "Requires mlx-audio in /Users/paul/fish-clean-venv. Model weights "
        "(mlx-community Qwen3-TTS quantized) download automatically on first use."
    )
    fallback = "fish_audio_local_tts"
    fallback_tools = ["fish_audio_local_tts", "voxcpm_tts", "edge_tts"]
    agent_skills = ["text-to-speech", "fish-audio-tts"]

    capabilities = [
        "text_to_speech",
        "voice_cloning",
        "voice_design",
        "custom_voice",
        "multilingual",
        "local_tts",
    ]
    supports = {
        "voice_cloning": True,
        "voice_design": True,
        "custom_voice": True,
        "multilingual": True,
        "offline": True,
        "apple_silicon_mlx": True,
        "korean": True,
    }
    best_for = [
        "state-of-the-art local voice cloning (3s reference)",
        "natural Korean speech via 'Sohee' premium timbre",
        "natural-language voice design",
        "10-language multilingual TTS",
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
            "mode": {
                "type": "string",
                "enum": ["voice_clone", "custom_voice", "voice_design"],
                "default": "voice_clone",
                "description": "voice_clone=zero-shot clone from reference audio; custom_voice=premium timbre; voice_design=natural-language voice design.",
            },
            "model": {
                "type": "string",
                "enum": list(_MODELS.keys()),
                "default": "base_0.6b",
                "description": "Model variant. base=voice clone, custom=premium timbres, design=voice design.",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to reference audio for voice cloning (mode=voice_clone).",
            },
            "reference_text": {
                "type": "string",
                "description": "Transcript of reference audio (improves clone fidelity).",
            },
            "voice": {
                "type": "string",
                "enum": _SPEAKERS,
                "description": "Premium speaker name for mode=custom_voice (e.g. 'sohee' for Korean female).",
            },
            "instruct": {
                "type": "string",
                "description": "Natural-language voice/emotion instruction (mode=voice_design, or to steer custom_voice).",
            },
            "lang_code": {
                "type": "string",
                "default": "auto",
                "description": "Language code (ko/en/ja/zh/...) or 'auto'.",
            },
            "speed": {
                "type": "number",
                "default": 1.0,
                "description": "Speech speed multiplier.",
            },
            "temperature": {
                "type": "number",
                "default": 0.9,
                "description": "Sampling temperature.",
            },
            "output_path": {
                "type": "string",
                "description": "Output WAV path.",
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
        return max(3.0, len(inputs.get("text", "")) * 0.1)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text is required")

        mode = inputs.get("mode", "voice_clone")
        model_key = inputs.get("model", "base_0.6b")
        model_id = _MODELS.get(model_key, _MODELS["base_0.6b"])
        lang = inputs.get("lang_code", "auto")
        speed = float(inputs.get("speed", 1.0))
        temperature = float(inputs.get("temperature", 0.9))
        output_path = Path(inputs.get("output_path", "qwen3_tts.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        gen_kwargs = [
            f"text={repr(text)}",
            f"lang_code={repr(lang)}",
            f"speed={speed}",
            f"temperature={temperature}",
            "verbose=False",
        ]

        if mode == "voice_clone":
            ref_audio = inputs.get("reference_audio")
            if not ref_audio or not Path(ref_audio).is_file():
                return ToolResult(
                    success=False,
                    error="mode=voice_clone requires a valid reference_audio path",
                )
            gen_kwargs.append(f"ref_audio={repr(str(ref_audio))}")
            ref_text = inputs.get("reference_text")
            if ref_text:
                gen_kwargs.append(f"ref_text={repr(ref_text)}")
        elif mode == "custom_voice":
            voice = inputs.get("voice", "sohee")
            gen_kwargs.append(f"voice={repr(voice)}")
            instruct = inputs.get("instruct")
            if instruct:
                gen_kwargs.append(f"instruct={repr(instruct)}")
        elif mode == "voice_design":
            instruct = inputs.get("instruct")
            if instruct:
                gen_kwargs.append(f"instruct={repr(instruct)}")

        kwargs_str = ", ".join(gen_kwargs)

        script = f"""
import mlx_audio.tts as tts
import soundfile as sf
import numpy as np

model = tts.load_model({repr(model_id)})
chunks = []
for chunk in model.generate({kwargs_str}):
    if hasattr(chunk, 'audio'):
        chunks.append(np.array(chunk.audio))
    else:
        chunks.append(np.array(chunk))
audio = np.concatenate(chunks) if chunks else np.array([])
sr = getattr(model, 'sample_rate', 24000)
sf.write({repr(str(output_path))}, audio, sr)
print('SUCCESS')
"""
        start = time.time()
        try:
            res = subprocess.run(
                [PYTHON_BIN, "-c", script],
                capture_output=True,
                text=True,
                check=True,
                timeout=300,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"Qwen3-TTS generation failed: {exc}",
            )

        if not output_path.exists() or output_path.stat().st_size < 1000:
            return ToolResult(success=False, error="Output audio not created")

        dur = None
        try:
            probe = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(output_path),
                ],
                capture_output=True, text=True,
            )
            if probe.returncode == 0 and probe.stdout.strip():
                dur = round(float(probe.stdout.strip()), 2)
        except Exception:
            dur = None

        elapsed = round(time.time() - start, 2)
        return ToolResult(
            success=True,
            data={
                "provider": "qwen3",
                "model": model_key,
                "mode": mode,
                "output": str(output_path),
                "duration_seconds": dur,
                "text_length": len(text),
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=elapsed,
        )
