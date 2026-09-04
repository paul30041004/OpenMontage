"""VoxCPM2 emotional TTS tool for OpenMontage — local, character acting.

VoxCPM2 (OpenBMB) supports **Voice Design** — synthesize with a natural-language
voice + emotion description, no reference audio needed. This is the
"캐릭터 감정연기" tier: pass an emotion like "잔잔하고 따뜻하게" or
"슬프고 절절하게" and the model acts it.

It ALSO supports **voice cloning** via the `clone` subcommand — pass a
`reference_audio` (a WAV of the target voice) plus `prompt_text` (what the
reference says) and VoxCPM2 reproduces that speaker consistently. Use this for
documentary/narrator voices that must stay identical across a long video.

Fully local (MPS/CPU), free. Model (~5GB) lives under the HF cache at
`~/.cache/huggingface/hub/models--openbmb--VoxCPM2/snapshots/__dl__`.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    DependencyError,
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

TTS_VENV = Path(__file__).resolve().parent.parent.parent / "projects" / "_shared" / "tts-venv"
VOXCPM_BIN = TTS_VENV / "bin" / "voxcpm"
MODEL_DIR = Path.home() / ".cache" / "huggingface" / "hub" / "models--openbmb--VoxCPM2" / "snapshots" / "__dl__"


class VoxCPMTTS(BaseTool):
    name = "voxcpm_tts"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "tts"
    provider = "voxcpm"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "VoxCPM2 model missing. Download ~5GB via tools/_bert_vits2/download_model.py "
        "(openbmb/VoxCPM2: model.safetensors, audiovae.pth, tokenizer.json + small files)."
    )
    agent_skills = ["voxcpm-tts", "tts-sample-unification", "text-to-speech"]

    capabilities = ["tts_ko_emotional", "voice_design", "tts_ko", "voice_clone"]

    input_schema = {
        "type": "object",
        "required": ["text"],
        "properties": {
            "text": {"type": "string", "description": "Text to synthesize (Korean)."},
            "emotion": {
                "type": "string",
                "description": "Natural-language emotion/style, e.g. '잔잔하고 따뜻하게', '슬프고 절절하게'. Also pass inside ( ) in text.",
            },
            "voice_design": {
                "type": "string",
                "description": "Voice description prefix, e.g. '(부드러운 중년 여성 목소리로)'.",
            },
            "reference_audio": {
                "type": "string",
                "description": "Path to a WAV of the target voice. When set, uses `clone` mode for consistent voice cloning. `prompt_text` should describe what the reference says.",
            },
            "prompt_text": {
                "type": "string",
                "description": "Text the reference_audio speaks (clone mode). Improves clone fidelity.",
            },
            "device": {"type": "string", "enum": ["mps", "cpu"], "default": "mps"},
            "timesteps": {"type": "integer", "default": 8},
            "model_path": {"type": "string", "description": "Override model dir."},
            "output_path": {"type": "string", "description": "Output WAV path."},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=8192, vram_mb=0, disk_mb=5000)
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout"])
    idempotency_key_fields = ["text", "emotion"]
    side_effects = ["writes WAV to output_path"]
    user_visible_verification = [
        "Listen for the requested emotional delivery (not flat read)",
        "Verify Korean pronunciation + prosody match the emotion cue",
    ]

    def get_status(self) -> ToolStatus:
        if not TTS_VENV.exists():
            return ToolStatus.UNAVAILABLE
        if not (MODEL_DIR / "model.safetensors").exists():
            return ToolStatus.DEGRADED
        return ToolStatus.AVAILABLE

    def check_dependencies(self) -> None:
        if not (TTS_VENV.exists() and (MODEL_DIR / "model.safetensors").exists()):
            raise DependencyError("VoxCPM2 env/model missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 30.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        text = inputs.get("text", "").strip()
        if not text:
            return ToolResult(success=False, error="text required")
        model = Path(inputs.get("model_path") or MODEL_DIR)
        if not (model / "model.safetensors").exists():
            return ToolResult(success=False, error="VoxCPM2 model missing. " + self.install_instructions)

        # Build the design text: voice_design prefix + emotion + text
        prefix = ""
        if inputs.get("voice_design"):
            prefix += f"({inputs['voice_design']})"
        design_text = f"{prefix}{text}"

        out = Path(inputs.get("output_path", "voxcpm_tts.wav"))
        out.parent.mkdir(parents=True, exist_ok=True)

        ref_audio = inputs.get("reference_audio")
        if ref_audio:
            ref = Path(ref_audio)
            if not ref.is_file():
                return ToolResult(success=False, error=f"reference_audio not found: {ref}")
            cmd = [str(VOXCPM_BIN), "clone",
                   "--text", text,
                   "--reference-audio", str(ref),
                   "--model-path", str(model),
                   "--output", str(out),
                   "--device", inputs.get("device", "mps"),
                   "--inference-timesteps", str(inputs.get("timesteps", 8))]
            if inputs.get("prompt_text"):
                cmd += ["--prompt-text", inputs["prompt_text"]]
            if inputs.get("emotion"):
                cmd += ["--control", inputs["emotion"]]
        else:
            cmd = [str(VOXCPM_BIN), "design",
                   "--text", design_text,
                   "--model-path", str(model),
                   "--output", str(out),
                   "--device", inputs.get("device", "mps"),
                   "--inference-timesteps", str(inputs.get("timesteps", 8))]
            if inputs.get("emotion"):
                cmd += ["--control", inputs["emotion"]]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="VoxCPM timed out after 15min")

        if not out.exists() or out.stat().st_size < 1000:
            return ToolResult(success=False, error="VoxCPM produced no audio:\n" + (proc.stdout or proc.stderr)[-600:])

        dur = None
        pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "csv=p=0", str(out)], capture_output=True, text=True)
        if pr.returncode == 0:
            dur = float(pr.stdout.strip())

        return ToolResult(
            success=True,
            data={"provider": self.provider, "language": "ko", "emotion": inputs.get("emotion"),
                  "output": str(out), "duration_seconds": dur},
            artifacts=[str(out)], duration_seconds=round(time.time() - start, 2),
        )
