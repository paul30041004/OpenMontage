"""EchoMimic audio-driven avatar tool for OpenMontage.

Wraps antgroup/EchoMimic (infer_audio2vid.py) so a portrait image + an audio
file produce a talking-avatar MP4 entirely locally. Supports long-form via the
chunked context window (`context_frames` / `context_overlap`).

Setup + weights: see `skills/echomimic-avatar.md` (or
`tools/_echomimic/setup_echomimic.py`). The tool shells out to a dedicated venv.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

import yaml

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

REPO_DIR = Path(__file__).resolve().parent.parent / "_echomimic"
VENV_PY = REPO_DIR / "venv" / "bin" / "python"
INFER = REPO_DIR / "infer_audio2vid.py"
BASE_CONFIG = REPO_DIR / "configs" / "prompts" / "animation.yaml"
DEFAULT_WEIGHTS = REPO_DIR / "pretrained_weights"
DEFAULT_DEVICE = "cpu"  # reliable default; cuda/mps opt-in


class EchoMimicAvatar(BaseTool):
    name = "echomimic_avatar"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "avatar"
    provider = "echomimic"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "EchoMimic not ready. Run:\n"
        "  python tools/_echomimic/setup_echomimic.py\n"
        "This installs the inference venv and downloads the pretrained weights "
        "(denoising_unet, reference_unet, motion_module, face_locator, sd-vae, "
        "sd-image-variations, whisper). Large download."
    )
    agent_skills = ["echomimic-avatar"]

    capabilities = ["avatar_from_audio", "avatar_longform"]

    input_schema = {
        "type": "object",
        "required": ["reference_image", "audio_path"],
        "properties": {
            "reference_image": {"type": "string", "description": "Portrait PNG/JPG to animate."},
            "audio_path": {"type": "string", "description": "Audio file (WAV/MP3) to lip-sync to."},
            "output_path": {"type": "string", "description": "Output MP4 path."},
            "width": {"type": "integer", "default": 512},
            "height": {"type": "integer", "default": 512},
            "fps": {"type": "integer", "default": 24},
            "seed": {"type": "integer", "default": 420},
            "cfg": {"type": "number", "default": 2.5},
            "steps": {"type": "integer", "default": 30},
            "device": {"type": "string", "enum": ["cpu", "mps", "cuda"], "default": "cpu"},
            "context_frames": {
                "type": "integer", "default": 12,
                "description": "Chunk size for long-form; larger = longer context, more VRAM.",
            },
            "context_overlap": {"type": "integer", "default": 3},
            "weights_dir": {"type": "string", "description": "Override pretrained_weights dir."},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=8, ram_mb=16384, vram_mb=8192, disk_mb=12000)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["reference_image", "audio_path", "seed"]
    side_effects = ["writes MP4 to output_path", "loads local diffusion model (VRAM/RAM-heavy)"]
    user_visible_verification = [
        "Watch the talking-avatar clip for lip-sync and identity fidelity",
        "Long clips: verify no drift across chunk boundaries",
    ]

    def get_status(self) -> ToolStatus:
        if not (VENV_PY.exists() and INFER.exists()):
            return ToolStatus.UNAVAILABLE
        w = Path(DEFAULT_WEIGHTS)
        if not (w / "denoising_unet.pth").exists():
            return ToolStatus.DEGRADED
        return ToolStatus.AVAILABLE

    def check_dependencies(self) -> None:
        if not (VENV_PY.exists() and INFER.exists()):
            raise DependencyError("EchoMimic inference env missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        # 240 frames ~1min on V100; CPU is far slower. Model load dominates.
        return 600.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        ref = inputs.get("reference_image")
        audio = inputs.get("audio_path")
        if not ref or not audio:
            return ToolResult(success=False, error="reference_image and audio_path required")
        ref_path = Path(ref)
        audio_path = Path(audio)
        if not ref_path.is_file():
            return ToolResult(success=False, error=f"Reference image not found: {ref}")
        if not audio_path.is_file():
            return ToolResult(success=False, error=f"Audio not found: {audio}")

        weights = Path(inputs.get("weights_dir") or DEFAULT_WEIGHTS)
        for needed in ["denoising_unet.pth", "reference_unet.pth", "motion_module.pth",
                       "face_locator.pth", "sd-vae-ft-mse", "sd-image-variations-diffusers"]:
            if not (weights / needed).exists():
                return ToolResult(success=False, error=f"Missing EchoMimic weight: {needed}. " + self.install_instructions)

        if not BASE_CONFIG.exists():
            return ToolResult(success=False, error=f"Base config missing: {BASE_CONFIG}")

        # Build a per-call config with absolute paths + single test case.
        cfg = yaml.safe_load(BASE_CONFIG.read_text(encoding="utf-8"))
        cfg["pretrained_base_model_path"] = str((weights / "sd-image-variations-diffusers").resolve())
        cfg["pretrained_vae_path"] = str((weights / "sd-vae-ft-mse").resolve())
        cfg["audio_model_path"] = str((weights / "audio_processor" / "whisper_tiny.pt").resolve())
        for key in ("denoising_unet_path", "reference_unet_path", "face_locator_path", "motion_module_path"):
            cfg[key] = str((weights / (key.replace("_path", "") + ".pth")).resolve())
        cfg["test_cases"] = {str(ref_path.resolve()): [str(audio_path.resolve())]}

        import tempfile
        tmp = tempfile.mkdtemp(prefix="echomimic_")
        cfg_path = Path(tmp) / "animation.yaml"
        cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")

        output = Path(inputs.get("output_path", "echomimic_avatar.mp4"))
        output.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(VENV_PY), str(INFER),
            "--config", str(cfg_path),
            "--device", inputs.get("device", "cpu"),
            "-W", str(inputs.get("width", 512)),
            "-H", str(inputs.get("height", 512)),
            "--fps", str(inputs.get("fps", 24)),
            "--seed", str(inputs.get("seed", 420)),
            "--cfg", str(inputs.get("cfg", 2.5)),
            "--steps", str(inputs.get("steps", 30)),
            "--context_frames", str(inputs.get("context_frames", 12)),
            "--context_overlap", str(inputs.get("context_overlap", 3)),
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", cwd=str(REPO_DIR), timeout=7200)
        except subprocess.TimeoutExpired:
            shutil.rmtree(tmp, ignore_errors=True)
            return ToolResult(success=False, error="EchoMimic inference timed out after 2h")

        stderr = proc.stderr or ""
        stdout = proc.stdout or ""
        shutil.rmtree(tmp, ignore_errors=True)

        # Find the produced video under outputs/ and move it to output_path.
        produced: Path | None = None
        out_root = REPO_DIR / "outputs"
        if out_root.exists():
            candidates = sorted(out_root.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
            if candidates:
                produced = candidates[0]
        if produced is None:
            return ToolResult(success=False, error="EchoMimic produced no MP4.\n" + (stderr or stdout)[-1500:],
                              data={"full_stderr": stderr})

        shutil.copy2(str(produced), str(output))
        if "withaudio" not in produced.name:
            # Re-mux audio onto the generated clip if the script's second pass didn't run.
            out2 = output.with_suffix(".withaudio.mp4")
            ff = subprocess.run(
                ["ffmpeg", "-y", "-i", str(output), "-i", str(audio_path),
                 "-c:v", "copy", "-c:a", "aac", "-shortest", str(out2)],
                capture_output=True, text=True,
            )
            if ff.returncode == 0:
                shutil.move(str(out2), str(output))

        duration = None
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", str(output)], capture_output=True, text=True)
        if probe.returncode == 0:
            duration = float(probe.stdout.strip())

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(output),
                  "duration_seconds": duration, "chunked": inputs.get("context_frames", 12) > 0},
            artifacts=[str(output)],
            duration_seconds=round(time.time() - start, 2),
        )
