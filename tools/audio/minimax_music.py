"""MiniMax AI Music generation tool (Music-01 / Music-2.0 / Music 3).

Generates high-fidelity instrumental background tracks, beats, and songs with vocals
through MiniMax's first-party Music Generation API.
"""

from __future__ import annotations

import binascii
import json
import logging
import os
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

MODELS = ["music-01", "music-02", "music-2.0"]
DEFAULT_MODEL = "music-01"
DEFAULT_REGION = "global"
PRICE_PER_GENERATION_USD = 0.03

REGION_BASE_URLS = {
    "global": "https://api.minimax.io",
    "global_en": "https://api.minimax.io",
    "cn": "https://api.minimaxi.com",
    "cn_zh": "https://api.minimaxi.com",
}


class MiniMaxMusic(BaseTool):
    name = "minimax_music"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "music_generation"
    provider = "minimax"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.STOCHASTIC
    runtime = ToolRuntime.API

    dependencies = ["env:MINIMAX_API_KEY"]
    install_instructions = (
        "Set MINIMAX_API_KEY to your MiniMax API key in .env.\n"
        "Get a key at https://platform.minimax.io/ (Global) or https://platform.minimaxi.com/ (CN).\n"
        "Optionally set MINIMAX_REGION to 'global' or 'cn'."
    )
    agent_skills = ["music", "minimax-h3"]

    capabilities = [
        "generate_background_music",
        "generate_song",
        "generate_instrumental",
    ]
    supports = {
        "instrumental": True,
        "vocals": True,
        "custom_lyrics": True,
        "style_control": True,
        "tempo_control": True,
    }
    best_for = [
        "high-energy electronic and pop background music",
        "instrumental BGM for short-form and explainer videos",
        "songs with customized lyrics and vocal styling",
        "low-latency first-party MiniMax API generation",
    ]
    not_good_for = [
        "offline music generation",
        "sound effects (use ElevenLabs SFX instead)",
    ]

    fallback_tools = ["google_music", "pixabay_music", "fal_elevenlabs_music"]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Music description (style, genre, mood, tempo, instruments).",
            },
            "lyrics": {
                "type": "string",
                "description": "Optional lyrics for vocal songs. Leave empty for pure instrumental.",
            },
            "instrumental": {
                "type": "boolean",
                "default": True,
                "description": "If true, generates pure instrumental background music with no vocals.",
            },
            "model": {
                "type": "string",
                "enum": MODELS,
                "default": DEFAULT_MODEL,
                "description": "MiniMax Music model variant.",
            },
            "duration_seconds": {
                "type": "number",
                "default": 30,
                "description": "Target duration in seconds.",
            },
            "output_path": {
                "type": "string",
                "description": "Path where the generated MP3 should be saved.",
            },
        },
    }

    resource_profile = ResourceProfile(cpu_cores=1, ram_mb=256, vram_mb=0, disk_mb=50)
    retry_policy = RetryPolicy(max_retries=2, retryable_errors=["timeout", "rate_limit", "502", "503"])

    def get_status(self) -> ToolStatus:
        api_key = os.environ.get("MINIMAX_API_KEY", "").strip()
        if not api_key:
            return ToolStatus.UNAVAILABLE
        return ToolStatus.AVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return PRICE_PER_GENERATION_USD

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 15.0

    def _resolve_endpoint(self) -> str:
        region = os.environ.get("MINIMAX_REGION", DEFAULT_REGION).strip().lower()
        base_url = os.environ.get("MINIMAX_BASE_URL") or REGION_BASE_URLS.get(region, REGION_BASE_URLS["global"])
        return f"{base_url.rstrip('/')}/v1/music_generation"

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        api_key = os.environ.get("MINIMAX_API_KEY", "").strip()
        if not api_key:
            return ToolResult(
                success=False,
                error="MINIMAX_API_KEY environment variable is not set. " + self.install_instructions,
            )

        prompt = inputs.get("prompt", "").strip()
        if not prompt:
            return ToolResult(success=False, error="prompt is required for music generation")

        instrumental = inputs.get("instrumental", True)
        lyrics = inputs.get("lyrics", "").strip()
        model = inputs.get("model", DEFAULT_MODEL)
        output_path = inputs.get("output_path", "minimax_music.mp3")

        endpoint = self._resolve_endpoint()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "prompt": prompt,
            "is_pure_music": instrumental or not bool(lyrics),
            "model": model,
            "stream": False,
        }
        if lyrics:
            payload["lyrics"] = lyrics

        start_time = time.time()
        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=90)
        except requests.RequestException as e:
            return ToolResult(success=False, error=f"MiniMax Music request failed: {e}")

        if resp.status_code != 200:
            return ToolResult(
                success=False,
                error=f"MiniMax API error {resp.status_code}: {resp.text[:400]}",
            )

        try:
            data = resp.json()
        except json.JSONDecodeError:
            return ToolResult(success=False, error=f"MiniMax returned non-JSON: {resp.text[:200]}")

        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code", 0) != 0:
            return ToolResult(
                success=False,
                error=f"MiniMax Music error {base_resp.get('status_code')}: {base_resp.get('status_msg')}",
            )

        audio_hex = data.get("data", {}).get("audio")
        audio_url = data.get("data", {}).get("audio_url") or data.get("data", {}).get("url")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if audio_hex:
            try:
                audio_bytes = binascii.unhexlify(audio_hex)
                with open(out, "wb") as f:
                    f.write(audio_bytes)
            except Exception as e:
                return ToolResult(success=False, error=f"Failed to decode audio hex payload: {e}")
        elif audio_url:
            try:
                dl_resp = requests.get(audio_url, timeout=60)
                if dl_resp.status_code == 200:
                    with open(out, "wb") as f:
                        f.write(dl_resp.content)
                else:
                    return ToolResult(success=False, error=f"Failed to download audio from url: {audio_url}")
            except Exception as e:
                return ToolResult(success=False, error=f"Failed to download audio from {audio_url}: {e}")
        else:
            return ToolResult(success=False, error=f"No audio data returned by MiniMax: {data}")

        # Measure real duration
        dur = None
        try:
            import subprocess
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)],
                capture_output=True,
                text=True,
            )
            if probe.returncode == 0 and probe.stdout.strip():
                dur = float(probe.stdout.strip())
        except Exception:
            dur = inputs.get("duration_seconds", 30.0)

        elapsed = round(time.time() - start_time, 2)
        return ToolResult(
            success=True,
            data={
                "provider": "minimax",
                "model": model,
                "prompt": prompt,
                "output": str(out),
                "duration_seconds": dur,
                "instrumental": instrumental,
            },
            artifacts=[str(out)],
            cost_usd=PRICE_PER_GENERATION_USD,
            duration_seconds=elapsed,
        )
