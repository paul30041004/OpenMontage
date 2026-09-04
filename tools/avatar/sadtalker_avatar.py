"""SadTalker avatar tool for OpenMontage — photo→talking head on Mac (CPU).

Turns a single portrait photo + audio into a talking-head video (head motion
+ lip-sync) using OpenTalker/SadTalker. Runs on Mac CPU (`--cpu`). Long audio
is handled by a chunk pipeline: split into N-second pieces, render each, concat.

Backed by the vendored clone at `tools/_sadtalker/` (models already downloaded:
SadTalker_V0.0.2_256/512.safetensors, mapping_*, facexlib detection weights).
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

REPO = Path(__file__).resolve().parent.parent / "_sadtalker"
VENV_PY = REPO / "venv" / "bin" / "python"
INFER = REPO / "inference.py"


def _probe_seconds(path: Path) -> float:
    try:
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        return float(p.stdout.strip())
    except Exception:
        return 0.0


class SadTalkerAvatar(BaseTool):
    name = "sadtalker_avatar"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "avatar"
    provider = "sadtalker"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.SEEDED
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "SadTalker not ready. Run:\n"
        "  python tools/_sadtalker/scripts/download_models.sh  (weights)\n"
        "and set up the venv (see .agents/skills/sadtalker-avatar/SKILL.md)."
    )
    agent_skills = ["ffmpeg", "echomimic-avatar", "wav2lip-avatar"]

    capabilities = ["photo_talking_head", "longform_talking_head"]

    input_schema = {
        "type": "object",
        "required": ["source_image", "driven_audio"],
        "properties": {
            "source_image": {"type": "string", "description": "Portrait photo of the speaker."},
            "driven_audio": {"type": "string", "description": "Audio to speak (any length)."},
            "output_path": {"type": "string", "description": "Output MP4 path."},
            "still": {"type": "boolean", "default": True, "description": "Static-photo mode (no ref video)."},
            "preprocess": {"type": "string", "enum": ["crop", "resize", "full", "extcrop"], "default": "crop"},
            "size": {"type": "integer", "enum": [256, 512], "default": 256,
              "description": "Renderer resolution / model size."},
            "chunk_seconds": {"type": "integer", "default": 180,
                              "description": "Chunk size for long audio (default 3 min)."},
            "device": {"type": "string", "enum": ["cpu", "mps"], "default": "cpu"},
            "enhancer": {"type": "string", "enum": ["none", "gfpgan"], "default": "none"},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=8192, vram_mb=0, disk_mb=3000)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["source_image", "driven_audio", "size"]
    side_effects = ["writes MP4 to output_path"]
    user_visible_verification = [
        "Watch head motion + lip-sync fidelity; 256 vs 512 model tradeoff",
        "Long clips: verify continuity at chunk boundaries",
    ]

    def get_status(self) -> ToolStatus:
        if not (VENV_PY.exists() and INFER.exists()):
            return ToolStatus.UNAVAILABLE
        ck = REPO / "checkpoints"
        if not (ck / "SadTalker_V0.0.2_256.safetensors").exists():
            return ToolStatus.DEGRADED
        return ToolStatus.AVAILABLE

    def check_dependencies(self) -> None:
        if not (VENV_PY.exists() and INFER.exists()):
            raise DependencyError("SadTalker env missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        audio_s = _probe_seconds(Path(inputs.get("driven_audio", "")))
        # CPU render ~4s/frame @ ~12.5fps -> ~50x realtime
        return max(120.0, audio_s * 8)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        img = Path(inputs.get("source_image", "")).resolve()
        audio = Path(inputs.get("driven_audio", "")).resolve()
        if not img.is_file() or not audio.is_file():
            return ToolResult(success=False, error="source_image and driven_audio required")
        if self.get_status() == ToolStatus.DEGRADED:
            return ToolResult(success=False, error="SadTalker weights missing. " + self.install_instructions)

        output = Path(inputs.get("output_path", "sadtalker_avatar.mp4"))
        output.parent.mkdir(parents=True, exist_ok=True)
        chunk_s = max(30, int(inputs.get("chunk_seconds", 180)))
        audio_dur = _probe_seconds(audio)

        if audio_dur <= chunk_s + 5:
            ok = self._run(img, audio, output, inputs)
            if not ok:
                return ToolResult(success=False, error="SadTalker render failed")
        else:
            try:
                self._chunked(img, audio, output, chunk_s, inputs)
            except Exception as exc:  # noqa: BLE001
                return ToolResult(success=False, error=f"chunked sadtalker failed: {exc}")

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(output),
                  "duration_seconds": _probe_seconds(output),
                  "chunked": audio_dur > chunk_s + 5},
            artifacts=[str(output)],
            duration_seconds=round(time.time() - start, 2),
        )

    def _run(self, img: Path, audio: Path, out: Path, inputs: dict[str, Any]) -> bool:
        cmd = [str(VENV_PY), str(INFER),
               "--driven_audio", str(audio),
               "--source_image", str(img),
               "--result_dir", str(out.parent),
               "--preprocess", inputs.get("preprocess", "crop"),
               "--size", str(inputs.get("size", 256)),
               "--cpu",
               ]
        if inputs.get("still", True):
            cmd.append("--still")
        if inputs.get("enhancer", "none") == "gfpgan":
            cmd.append("--enhancer")
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", cwd=str(REPO), timeout=7200)
        # inference.py writes into <result_dir>/<timestamp>/...mp4 and a
        # combined <result_dir>/<timestamp>.mp4; find the newest mp4.
        import re
        m = re.search(r"named:\s*(\S+\.mp4)", proc.stdout or "")
        if m and Path(m.group(1)).exists():
            shutil.copy2(m.group(1), str(out))
            return True
        cands = sorted(out.parent.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        for c in cands:
            if c.resolve() != out.resolve():
                shutil.copy2(str(c), str(out))
                return True
        return out.exists()

    def _chunked(self, img, audio, output, chunk_s, inputs) -> None:
        with tempfile.TemporaryDirectory(prefix="sadtk_") as tmp:
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
                sub_in = dict(inputs)
                if not self._run(img, seg, clip, sub_in):
                    raise RuntimeError(f"chunk {i} failed")
                clips.append(clip)
            lst = tmp / "concat.txt"
            lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", str(output)], check=True, capture_output=True)
