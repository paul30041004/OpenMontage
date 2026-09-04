"""MiniMax Music 3 local music generation tool (Apple Silicon MLX).

Runs MiniMax Music 3 (open-weight, 8B Global LLM + 0.6B Local LLM + Flow
Matching) locally via mlx-audio on Apple Silicon Metal GPU. Generates complete
songs up to 5 minutes with lyrics + structured captions, 32kHz stereo WAV.

Zero API cost, fully offline. This is the local counterpart to the API-based
`minimax_music` tool (which requires MINIMAX_API_KEY).
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

_MODELS = {
    "4bit": "mlx-community/MiniMax-Music3-4bit",
    "8bit": "mlx-community/MiniMax-Music3-8bit",
    "6bit": "mlx-community/MiniMax-Music3-6bit",
    "bf16": "mlx-community/MiniMax-Music3-bf16",
}


class MiniMaxMusicLocal(BaseTool):
    name = "minimax_music_local"
    version = "1.0.0"
    tier = ToolTier.GENERATE
    capability = "music_generation"
    provider = "minimax_local"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL_GPU

    dependencies = [f"path:{PYTHON_BIN}"]
    install_instructions = (
        "Requires mlx-audio in /Users/paul/fish-clean-venv. Model weights "
        "(mlx-community/MiniMax-Music3-4bit) download automatically on first use."
    )
    fallback = "google_music"
    fallback_tools = ["google_music", "pixabay_music", "minimax_music"]
    agent_skills = ["music", "minimax-h3"]

    capabilities = [
        "generate_background_music",
        "generate_song",
        "generate_instrumental",
        "local_music",
    ]
    supports = {
        "instrumental": True,
        "vocals": True,
        "custom_lyrics": True,
        "style_control": True,
        "offline": True,
        "apple_silicon_mlx": True,
        "long_form": True,
    }
    best_for = [
        "local open-weight music generation without API cost",
        "complete songs with lyrics and structured captions",
        "long-form music up to 5 minutes",
    ]
    not_good_for = [
        "sound effects (use ElevenLabs SFX)",
        "very fast generation (local MLX is slower than API)",
    ]

    input_schema = {
        "type": "object",
        "required": ["prompt"],
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Music description (genre, mood, instruments, vocal style, arrangement).",
            },
            "lyrics": {
                "type": "string",
                "default": "",
                "description": "Optional lyrics with section tags like [Verse]/[Chorus]/[Bridge]. Empty = instrumental.",
            },
            "model": {
                "type": "string",
                "enum": list(_MODELS.keys()),
                "default": "4bit",
                "description": "Quantization variant.",
            },
            "duration_seconds": {
                "type": "number",
                "default": 30.0,
                "description": "Target duration in seconds (up to ~300).",
            },
            "steps": {
                "type": "integer",
                "default": 30,
                "description": "Flow-matching sampling steps.",
            },
            "seed": {
                "type": "integer",
                "default": 0,
                "description": "Random seed for reproducible generation.",
            },
            "output_path": {
                "type": "string",
                "description": "Output WAV path.",
            },
        },
    }

    resource_profile = ResourceProfile(
        cpu_cores=4, ram_mb=16384, vram_mb=8192, disk_mb=7000, network_required=False
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])

    def get_status(self) -> ToolStatus:
        if Path(PYTHON_BIN).exists():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 120.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        prompt = inputs.get("prompt", "").strip()
        if not prompt:
            return ToolResult(success=False, error="prompt is required")

        lyrics = inputs.get("lyrics", "")
        if not lyrics.strip():
            lyrics = "[instrumental]"
        model_key = inputs.get("model", "4bit")
        model_id = _MODELS.get(model_key, _MODELS["4bit"])
        duration = float(inputs.get("duration_seconds", 30.0))
        steps = int(inputs.get("steps", 30))
        seed = int(inputs.get("seed", 0))
        output_path = Path(inputs.get("output_path", "minimax_music_local.wav"))
        output_path.parent.mkdir(parents=True, exist_ok=True)

        script = f"""
import mlx_audio.music.generate as g
out = g.generate_music(
    caption={repr(prompt)},
    lyrics={repr(lyrics)},
    model={repr(model_id)},
    duration={duration},
    steps={steps},
    seed={seed},
    output_path={repr(str(output_path))},
    verbose=False,
)
print('SUCCESS')
"""
        start = time.time()
        try:
            res = subprocess.run(
                [PYTHON_BIN, "-c", script],
                capture_output=True,
                text=True,
                check=True,
                timeout=1800,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                error=f"MiniMax Music 3 local generation failed: {exc}",
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
                "provider": "minimax_local",
                "model": model_key,
                "prompt": prompt,
                "output": str(output_path),
                "duration_seconds": dur,
                "instrumental": not bool(lyrics),
            },
            artifacts=[str(output_path)],
            cost_usd=0.0,
            duration_seconds=elapsed,
            seed=seed,
            model=model_key,
        )
