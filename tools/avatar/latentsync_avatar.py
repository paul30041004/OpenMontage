"""LatentSync-MLX avatar tool for OpenMontage — Apple Silicon native lip-sync.

Audio-conditioned latent diffusion lip-sync running natively on Apple MLX
(~2.3x faster than PyTorch MPS). Portrait photo or face video + audio -> the
face speaks. Long audio uses a chunk pipeline (split -> render each -> concat).

Backed by `tools/_latentsync_mlx/` (sb1992/latentsync-mlx port of ByteDance
LatentSync) + the upstream `latentsync/` preprocessing package. MLX UNet + VAE
weights already converted.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
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

REPO = Path(__file__).resolve().parent.parent / "_latentsync_mlx"
UPSTREAM = REPO / "upstream"
VENV_PY = REPO / "venv" / "bin" / "python"
INFER = REPO / "scripts" / "inference.py"
UNET = REPO / "checkpoints" / "latentsync_unet_mlx.safetensors"
VAE = REPO / "checkpoints" / "vae_mlx.safetensors"


def _probe_seconds(path: Path) -> float:
    try:
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        return float(p.stdout.strip())
    except Exception:
        return 0.0


class LatentSyncAvatar(BaseTool):
    name = "latentsync_avatar"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "avatar"
    provider = "latentsync"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "LatentSync-MLX not ready. Weights + MLX venv live under tools/_latentsync_mlx/ "
        "(see .agents/skills/latentsync-mlx/SKILL.md)."
    )
    agent_skills = ["ffmpeg", "wav2lip-avatar", "sadtalker-avatar"]

    capabilities = ["mlx_lipsync", "longform_mlx_lipsync"]

    input_schema = {
        "type": "object",
        "required": ["face", "audio_path"],
        "properties": {
            "face": {"type": "string", "description": "Portrait photo OR a face video."},
            "audio_path": {"type": "string", "description": "Audio to lip-sync (any length)."},
            "output_path": {"type": "string", "description": "Output MP4 path."},
            "resolution": {"type": "integer", "enum": [256, 512], "default": 256},
            "inference_steps": {"type": "integer", "default": 20},
            "guidance_scale": {"type": "number", "default": 1.5},
            "chunk_seconds": {"type": "integer", "default": 120,
                              "description": "Chunk size for long audio (default 2 min)."},
            "seed": {"type": "integer", "default": 1247},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=12288, vram_mb=0, disk_mb=6000)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["face", "audio_path", "seed"]
    side_effects = ["writes MP4 to output_path"]
    user_visible_verification = [
        "Watch lip-sync + face consistency (MLX diffusion, higher quality than Wav2Lip)",
        "Long clips: verify continuity at chunk boundaries",
    ]

    def get_status(self) -> ToolStatus:
        if not (VENV_PY.exists() and INFER.exists()):
            return ToolStatus.UNAVAILABLE
        if not (UNET.exists() and VAE.exists()):
            return ToolStatus.DEGRADED
        return ToolStatus.AVAILABLE

    def check_dependencies(self) -> None:
        if not (VENV_PY.exists() and INFER.exists()):
            raise DependencyError("LatentSync-MLX env missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        audio_s = _probe_seconds(Path(inputs.get("audio_path", "")))
        return max(180.0, audio_s * 30)  # MLX ~ 30x realtime observed

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        face = Path(inputs.get("face", "")).resolve()
        audio = Path(inputs.get("audio_path", "")).resolve()
        if not face.is_file() or not audio.is_file():
            return ToolResult(success=False, error="face and audio_path required")
        if self.get_status() == ToolStatus.DEGRADED:
            return ToolResult(success=False, error="LatentSync weights missing. " + self.install_instructions)

        output = Path(inputs.get("output_path", "latentsync_avatar.mp4"))
        output.parent.mkdir(parents=True, exist_ok=True)
        chunk_s = max(30, int(inputs.get("chunk_seconds", 120)))
        audio_dur = _probe_seconds(audio)

        if audio_dur <= chunk_s + 5:
            ok = self._run(face, audio, output, inputs)
            if not ok:
                return ToolResult(success=False, error="LatentSync render failed")
        else:
            try:
                self._chunked(face, audio, output, chunk_s, inputs)
            except Exception as exc:  # noqa: BLE001
                return ToolResult(success=False, error=f"chunked latentsync failed: {exc}")

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(output),
                  "duration_seconds": _probe_seconds(output),
                  "chunked": audio_dur > chunk_s + 5},
            artifacts=[str(output)],
            duration_seconds=round(time.time() - start, 2),
        )

    def _run(self, face: Path, audio: Path, out: Path, inputs: dict[str, Any]) -> bool:
        # LatentSync needs a video; if given a photo, synthesize a static video.
        vid = face
        if face.suffix.lower() in (".png", ".jpg", ".jpeg"):
            tmp_vid = out.parent / f"_static_{out.stem}.mp4"
            dur = max(_probe_seconds(audio), 1.0) + 0.5
            subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", str(face), "-t", str(dur),
                            "-r", "25", "-pix_fmt", "yuv420p", str(tmp_vid)],
                           check=True, capture_output=True)
            vid = tmp_vid

        cmd = [str(VENV_PY), str(INFER),
               "--video_path", str(vid),
               "--audio_path", str(audio),
               "--video_out_path", str(out),
               "--resolution", str(inputs.get("resolution", 256)),
               "--inference_steps", str(inputs.get("inference_steps", 20)),
               "--guidance_scale", str(inputs.get("guidance_scale", 1.5)),
               "--seed", str(inputs.get("seed", 1247)),
               "--unet_weights", str(UNET),
               "--vae_weights", str(VAE)]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", cwd=str(UPSTREAM), timeout=7200,
                              env={**__import__("os").environ, "PYTHONPATH": f"{REPO}:{UPSTREAM}"})
        return out.exists()

    def _chunked(self, face, audio, output, chunk_s, inputs) -> None:
        with tempfile.TemporaryDirectory(prefix="lsmlx_") as tmp:
            tmp = Path(tmp)
            audio_dur = _probe_seconds(audio)
            n = int(audio_dur // chunk_s) + (1 if audio_dur % chunk_s else 0)
            clips: list[Path] = []
            for i in range(n):
                t0 = i * chunk_s
                seg = tmp / f"seg{i:03d}.wav"
                subprocess.run(["ffmpeg", "-y", "-ss", str(t0), "-t", str(chunk_s),
                                "-i", str(audio), "-ar", "16000", "-ac", "1",
                                str(seg)], check=True, capture_output=True)
                if _probe_seconds(seg) < 0.5:
                    continue
                clip = tmp / f"clip{i:03d}.mp4"
                if not self._run(face, seg, clip, inputs):
                    raise RuntimeError(f"chunk {i} failed")
                clips.append(clip)
            lst = tmp / "concat.txt"
            lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", str(output)], check=True, capture_output=True)
