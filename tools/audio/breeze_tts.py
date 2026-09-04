"""Breeze TTS 2 text-to-speech, voice design, and voice direction tool.

Breeze TTS 2 (Breezeblue AI) is a real-time, open-weight TTS model supporting:
- Voice Clone: Zero-shot speaker cloning from clean reference audio + transcript
- Voice Design: Creating distinctive voices from natural-language instructions
- Voice Direction: Steering tone, emotion, pace, and delivery of a reference voice
- Vocal Events: Inline events like (laugh), (sigh), (cough), (clears throat), [笑], [叹气]
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

import requests

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

DEFAULT_API_URL = "http://127.0.0.1:7860/v1/audio/speech"


class BreezeTTS(BaseTool):
    name = "breeze_tts"
    version = "0.1.0"
    tier = ToolTier.VOICE
    capability = "tts"
    provider = "breeze"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.HYBRID

    dependencies = []
    install_instructions = (
        "Run Breeze TTS 2 locally or start the local server:\n"
        "  git clone https://github.com/breezeblue-ai/breeze-tts.git\n"
        "  cd breeze-tts && pip install -r requirements.txt\n"
        "  python -m breeze_infer.api /path/to/breeze-tts-2 --host 0.0.0.0 --port 7860\n"
        "Or set BREEZE_TTS_API_URL in .env (default: http://127.0.0.1:7860/v1/audio/speech)."
    )
    agent_skills = ["breeze-tts", "text-to-speech"]

    capabilities = [
        "text_to_speech",
        "voice_design",
        "voice_direction",
        "voice_cloning",
        "vocal_events",
    ]
    supports = {
        "voice_cloning": True,
        "voice_design": True,
        "voice_direction": True,
        "vocal_events": True,
        "streaming_pcm": True,
        "cfg_scale": True,
        "seed": True,
    }
    best_for = [
        "natural English and Chinese speech synthesis with vocal events (laugh, sigh)",
        "reference-free voice design via natural-language descriptions",
        "voice direction to steer emotion, pace, and delivery of a cloned speaker",
        "ultra-low-latency real-time TTS streaming",
    ]
    not_good_for = [
        "native Korean/Japanese character acting (use VoxCPM2 or Audio8 TTS instead)",
    ]

    fallback_tools = ["voxcpm_tts", "audio8_tts", "edge_tts", "elevenlabs_tts"]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to synthesize. Can include vocal events like (laugh), (sigh), [笑], [叹气].",
            },
            "instruction": {
                "type": "string",
                "description": "Natural-language voice description or delivery direction (e.g. 'A warm, thoughtful young woman with a calm delivery' or 'Speak slowly with a serious tone').",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to clean reference audio file for voice cloning or voice direction.",
            },
            "reference_text": {
                "type": "string",
                "description": "Exact transcript of the reference audio.",
            },
            "cfg_scale": {
                "type": "number",
                "default": 4.0,
                "minimum": 1.0,
                "maximum": 10.0,
                "description": "Classifier-free guidance scale. Higher values (e.g. 4.0) strengthen instruction following.",
            },
            "seed": {
                "type": "integer",
                "description": "Random seed for reproducible generation.",
            },
            "api_url": {
                "type": "string",
                "default": DEFAULT_API_URL,
                "description": "Breeze TTS streaming server endpoint URL.",
            },
            "cli_script_path": {
                "type": "string",
                "description": "Path to breeze-tts infer.py if running directly via CLI instead of HTTP API.",
            },
            "model_path": {
                "type": "string",
                "description": "Path to the breeze-tts-2 model checkpoint directory.",
            },
            "output_path": {
                "type": "string",
                "description": "Output path where the generated audio file should be written (.wav or .mp3).",
            },
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=8192, vram_mb=8192, disk_mb=15000)
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["timeout", "connection_error"])

    def get_status(self) -> ToolStatus:
        api_url = os.environ.get("BREEZE_TTS_API_URL", DEFAULT_API_URL)
        try:
            r = requests.get(api_url.replace("/v1/audio/speech", "/health"), timeout=1.0)
            if r.status_code == 200:
                return ToolStatus.AVAILABLE
        except Exception:
            pass

        # Check if CLI infer.py exists locally
        cli_path = os.environ.get("BREEZE_TTS_CLI_PATH")
        if cli_path and Path(cli_path).is_file():
            return ToolStatus.AVAILABLE

        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 4.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text is required for speech synthesis")

        instruction = inputs.get("instruction", "").strip()
        ref_audio = inputs.get("reference_audio")
        ref_text = inputs.get("reference_text")
        cfg_scale = float(inputs.get("cfg_scale", 4.0))
        seed = inputs.get("seed")
        output_path = Path(inputs.get("output_path", "breeze_tts_output.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        api_url = inputs.get("api_url") or os.environ.get("BREEZE_TTS_API_URL", DEFAULT_API_URL)
        cli_script = inputs.get("cli_script_path") or os.environ.get("BREEZE_TTS_CLI_PATH")

        start_time = time.time()

        # Method 1: Try Streaming HTTP API
        try:
            files: dict[str, Any] = {}
            data: dict[str, Any] = {
                "text": text,
                "cfg_scale": str(cfg_scale),
            }
            if instruction:
                data["instruction"] = instruction
            if seed is not None:
                data["seed"] = str(seed)
            if ref_text:
                data["ref_text"] = ref_text

            opened_file = None
            if ref_audio and Path(ref_audio).is_file():
                opened_file = open(ref_audio, "rb")
                files["ref_audio"] = opened_file

            try:
                resp = requests.post(api_url, data=data, files=files if files else None, timeout=120)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    # Server returns raw PCM 24kHz 16-bit mono or WAV
                    if resp.content[:4] == b"RIFF":
                        with open(output_path, "wb") as f:
                            f.write(resp.content)
                    else:
                        # Convert raw PCM (24kHz s16le mono) to WAV
                        pcm_tmp = output_path.with_suffix(".pcm")
                        with open(pcm_tmp, "wb") as f:
                            f.write(resp.content)
                        subprocess.run(
                            [
                                "ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
                                "-i", str(pcm_tmp), str(output_path)
                            ],
                            capture_output=True,
                            check=True,
                        )
                        if pcm_tmp.exists():
                            pcm_tmp.unlink()

                    return self._build_result(output_path, start_time, mode="api")
            finally:
                if opened_file:
                    opened_file.close()

        except Exception as exc:
            log.debug("Breeze TTS HTTP API call failed, falling back to CLI if available: %s", exc)

        # Method 2: Fallback to CLI execution if script is provided
        if cli_script and Path(cli_script).is_file():
            model_path = inputs.get("model_path") or os.environ.get("BREEZE_TTS_MODEL_PATH", "breeze-tts-2")
            cmd = [
                "python", str(cli_script), str(model_path),
                "--text", text,
                "--cfg-scale", str(cfg_scale),
                "--output", str(output_path),
            ]
            if instruction:
                cmd += ["--instruction", instruction]
            if ref_audio and Path(ref_audio).is_file():
                cmd += ["--ref-audio", str(ref_audio)]
            if ref_text:
                cmd += ["--ref-text", ref_text]

            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
                if output_path.exists() and output_path.stat().st_size > 1000:
                    return self._build_result(output_path, start_time, mode="cli")
            except Exception as e:
                return ToolResult(success=False, error=f"Breeze TTS CLI execution failed: {e}")

        return ToolResult(
            success=False,
            error=(
                f"Breeze TTS 2 server is not reachable at {api_url} and no CLI script was found. "
                + self.install_instructions
            ),
        )

    def _build_result(self, out_path: Path, start_time: float, mode: str) -> ToolResult:
        dur = None
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)],
                capture_output=True,
                text=True,
            )
            if probe.returncode == 0 and probe.stdout.strip():
                dur = float(probe.stdout.strip())
        except Exception:
            dur = None

        elapsed = round(time.time() - start_time, 2)
        return ToolResult(
            success=True,
            data={
                "provider": "breeze",
                "mode": mode,
                "output": str(out_path),
                "duration_seconds": dur,
            },
            artifacts=[str(out_path)],
            cost_usd=0.0,
            duration_seconds=elapsed,
        )
