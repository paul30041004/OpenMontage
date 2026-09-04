"""Wav2Lip avatar tool for OpenMontage — runs on Mac (CPU/MPS).

Local lip-sync: a face (still photo or short video) + any audio -> the face
speaks the audio. Long audio (even 1h+) is handled by a **chunk pipeline**:
split into N-second pieces, lip-sync each, FFmpeg-concat the results.

Backed by the vendored Rudrabha/Wav2Lip at `tools/_wav2lip/` (weights:
wav2lip_gan.pth + s3fd.pth already downloaded) run through the shared local
venv. Fully local — no API key, no CUDA required.
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

WAV2LIP_DIR = Path(__file__).resolve().parent.parent / "_wav2lip"
VENV_PY = Path(__file__).resolve().parent.parent / "_bert_vits2" / "venv" / "bin" / "python"
INFER = WAV2LIP_DIR / "inference.py"
CKPT = WAV2LIP_DIR / "checkpoints" / "wav2lip_gan.pth"
S3FD = WAV2LIP_DIR / "face_detection" / "detection" / "sfd" / "s3fd.pth"


def _probe_seconds(path: Path) -> float:
    try:
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        return float(p.stdout.strip())
    except Exception:
        return 0.0


class Wav2LipAvatar(BaseTool):
    name = "wav2lip_avatar"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "avatar"
    provider = "wav2lip"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "Wav2Lip not ready. Weights live in tools/_wav2lip/checkpoints/"
        "(wav2lip_gan.pth + s3fd.pth). Model download via gdown from the "
        "Rudrabha/Wav2Lip Google Drive folder."
    )
    agent_skills = ["ffmpeg", "echomimic-avatar"]

    capabilities = ["avatar_from_audio", "longform_lipsync", "audio_video_alignment"]

    input_schema = {
        "type": "object",
        "required": ["face", "audio_path"],
        "properties": {
            "face": {"type": "string", "description": "Still photo (png/jpg) OR short video of the speaker's face."},
            "audio_path": {"type": "string", "description": "Audio to lip-sync (wav/mp3; any length)."},
            "output_path": {"type": "string", "description": "Output MP4 path."},
            "chunk_seconds": {"type": "integer", "default": 180,
                              "description": "Chunk size for long audio (default 3 min)."},
            "fps": {"type": "number", "default": 25},
            "device": {"type": "string", "enum": ["cpu", "mps"], "default": "cpu"},
            "resize_factor": {"type": "integer", "default": 1},
            "nosmooth": {"type": "boolean", "default": False},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=6144, vram_mb=0, disk_mb=2000)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["face", "audio_path"]
    side_effects = ["writes MP4 to output_path"]
    user_visible_verification = [
        "Watch the lip-sync clip: lips should track the audio",
        "Long clips: verify no drift at chunk boundaries after concat",
    ]

    def get_status(self) -> ToolStatus:
        if not (INFER.exists() and VENV_PY.exists()):
            return ToolStatus.UNAVAILABLE
        if not (CKPT.exists() and S3FD.exists()):
            return ToolStatus.DEGRADED
        return ToolStatus.AVAILABLE

    def check_dependencies(self) -> None:
        if not (INFER.exists() and VENV_PY.exists()):
            raise DependencyError("Wav2Lip env missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        audio_s = _probe_seconds(Path(inputs.get("audio_path", "")))
        # CPU ~ realtime-ish; rough
        return max(60.0, audio_s * 1.2)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        face = Path(inputs.get("face", "")).resolve()
        audio = Path(inputs.get("audio_path", "")).resolve()
        if not face.is_file() or not audio.is_file():
            return ToolResult(success=False, error="face and audio_path required (existing files)")
        if self.get_status() == ToolStatus.DEGRADED:
            return ToolResult(success=False, error="Wav2Lip weights missing. " + self.install_instructions)

        output = Path(inputs.get("output_path", "wav2lip_avatar.mp4"))
        output.parent.mkdir(parents=True, exist_ok=True)
        chunk_s = max(30, int(inputs.get("chunk_seconds", 180)))
        fps = inputs.get("fps", 25)
        device = inputs.get("device", "cpu")
        nosmooth = bool(inputs.get("nosmooth"))

        audio_dur = _probe_seconds(audio)
        if audio_dur <= chunk_s + 5:
            # short audio — single pass
            tmp = output.with_suffix(".tmp.mp4")
            rc = self._run_infer(face, audio, tmp, fps, device, nosmooth)
            if rc != 0:
                return ToolResult(success=False, error=f"Wav2Lip failed (exit {rc})")
            shutil.move(str(tmp), str(output))
        else:
            # chunk pipeline
            try:
                self._chunked(face, audio, output, chunk_s, fps, device, nosmooth)
            except Exception as exc:  # noqa: BLE001
                return ToolResult(success=False, error=f"chunked lipsync failed: {exc}")

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(output),
                  "duration_seconds": _probe_seconds(output),
                  "chunked": audio_dur > chunk_s + 5, "device": device},
            artifacts=[str(output)],
            duration_seconds=round(time.time() - start, 2),
        )

    def _run_infer(self, face: Path, audio: Path, out: Path, fps, device, nosmooth) -> int:
        static = str(face.suffix).lower() in (".png", ".jpg", ".jpeg")
        out = out.resolve()  # cwd is tools/_wav2lip; keep paths absolute
        cmd = [str(VENV_PY), str(INFER),
               "--checkpoint_path", str(CKPT),
               "--face", str(face), "--audio", str(audio),
               "--outfile", str(out),
               "--fps", str(fps),
               "--static", "True" if static else "False"]
        if nosmooth:
            cmd.append("--nosmooth")
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", cwd=str(WAV2LIP_DIR), timeout=7200)
        return proc.returncode if out.exists() else proc.returncode

    def _chunked(self, face, audio, output, chunk_s, fps, device, nosmooth) -> None:
        with tempfile.TemporaryDirectory(prefix="w2l_") as tmp:
            tmp = Path(tmp)
            # split audio
            audio_dur = _probe_seconds(audio)
            n = int(audio_dur // chunk_s) + (1 if audio_dur % chunk_s else 0)
            chunks: list[Path] = []
            for i in range(n):
                t0 = i * chunk_s
                seg = tmp / f"seg{i:03d}.wav"
                subprocess.run(["ffmpeg", "-y", "-ss", str(t0), "-t", str(chunk_s),
                                "-i", str(audio), "-ar", "16000", "-ac", "1",
                                str(seg)], check=True, capture_output=True)
                if not seg.exists() or _probe_seconds(seg) < 0.5:
                    continue
                chunks.append(seg)
            # lip-sync each chunk against the still face
            clips: list[Path] = []
            for i, seg in enumerate(chunks):
                clip = tmp / f"clip{i:03d}.mp4"
                rc = self._run_infer(face, seg, clip, fps, device, nosmooth)
                if rc != 0 or not clip.exists():
                    raise RuntimeError(f"chunk {i} failed (exit {rc})")
                clips.append(clip)
            # concat
            lst = tmp / "concat.txt"
            lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", str(output)], check=True, capture_output=True)
