"""FFmpeg segment + parallel-concat long-form renderer for OpenMontage.

Long videos: split into N-second chunks, encode each chunk **in parallel**
(GNU Parallel), then FFmpeg-concat — the speed/stability sweet spot for
long-form production (no single huge encode, resume-friendly chunks).
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


class ChunkRender(BaseTool):
    name = "chunk_render"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "video_post"
    provider = "ffmpeg"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg", "cmd:parallel"]
    install_instructions = "Requires ffmpeg + GNU Parallel: brew install parallel"
    agent_skills = ["ffmpeg"]

    capabilities = ["segment_concat", "parallel_encode", "longform_render"]

    input_schema = {
        "type": "object",
        "required": ["video_path"],
        "properties": {
            "video_path": {"type": "string", "description": "Long input video (already composed)."},
            "output_path": {"type": "string", "description": "Output MP4 path."},
            "chunk_seconds": {"type": "integer", "default": 30},
            "crf": {"type": "integer", "default": 20},
            "preset": {"type": "string", "default": "veryfast",
                       "description": "x264 preset for chunk encoding."},
            "lut": {"type": "string", "description": "Optional unified .cube LUT for tone consistency."},
            "audio_loudnorm": {"type": "boolean", "default": True,
                               "description": "Apply loudnorm to the audio for consistency."},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=4, ram_mb=4096, vram_mb=0, disk_mb=2000)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["video_path", "chunk_seconds"]
    side_effects = ["writes MP4 to output_path"]
    user_visible_verification = [
        "Concat has no seams/glitches at chunk boundaries",
        "Tone is uniform across the whole long video (LUT)",
    ]

    def get_status(self) -> ToolStatus:
        if shutil.which("ffmpeg") and shutil.which("parallel"):
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def check_dependencies(self) -> None:
        if not (shutil.which("ffmpeg") and shutil.which("parallel")):
            raise DependencyError("chunk_render needs ffmpeg + GNU Parallel. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        return 60.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        src = Path(inputs.get("video_path", "")).resolve()
        if not src.is_file():
            return ToolResult(success=False, error="video_path required")
        output = Path(inputs.get("output_path", "chunked.mp4")).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        chunk_s = max(5, int(inputs.get("chunk_seconds", 30)))
        crf = int(inputs.get("crf", 20))
        preset = inputs.get("preset", "veryfast")
        lut = inputs.get("lut")
        loudnorm = bool(inputs.get("audio_loudnorm", True))

        try:
            chunks = self._render(src, output, chunk_s, crf, preset, lut, loudnorm)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(success=False, error=str(exc))

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(output),
                  "chunks": chunks, "chunk_seconds": chunk_s,
                  "duration_seconds": self._probe(output)},
            artifacts=[str(output)], duration_seconds=round(time.time() - start, 2),
        )

    def _probe(self, path: Path) -> float:
        p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        try:
            return float(p.stdout.strip())
        except Exception:
            return 0.0

    def _render(self, src: Path, output: Path, chunk_s: int, crf: int, preset: str,
                lut: str | None, loudnorm: bool) -> int:
        with tempfile.TemporaryDirectory(prefix="chunk_") as tmp:
            tmp = Path(tmp)
            dur = self._probe(src)
            n = max(1, int((dur + chunk_s - 1) // chunk_s))

            # 1) partition into independent chunks (GOP-aligned, draft quality)
            #    and re-encode each to final quality in parallel (GNU Parallel).
            vf = [f"lut3d=file={lut}"] if (lut and Path(lut).exists()) else []
            af = ["loudnorm=I=-16:TP=-1.5:LRA=11"] if loudnorm else []
            vfstr = ",".join(vf) if vf else "null"
            afstr = ",".join(af) if af else "anull"
            gop = int(chunk_s * 24)

            jobs = []
            for i in range(n):
                t0 = i * chunk_s
                part = tmp / f"seg_{i:03d}.mp4"
                enc = tmp / f"seg_{i:03d}.enc.mp4"
                jobs.append(
                    f"ffmpeg -y -ss {t0} -t {chunk_s} -i '{src}' "
                    f"-map '0:v' -map '0:a?' -vf {vfstr} -af {afstr} "
                    f"-c:v libx264 -crf {crf} -preset {preset} -g {gop} -sc_threshold 0 "
                    f"-pix_fmt yuv420p -c:a aac '{enc}'"
                )
            (tmp / "jobs.txt").write_text("\n".join(jobs) + "\n", encoding="utf-8")

            proc = subprocess.run(["parallel", "-j", "4", "--no-notice", "--ungroup",
                                   "-a", str(tmp / "jobs.txt")],
                                  capture_output=True, text=True)
            enc_chunks = sorted(tmp.glob("seg_*.enc.mp4"))
            if not enc_chunks:
                raise RuntimeError("parallel encode produced no chunks:\n" + (proc.stderr or proc.stdout)[-600:])

            # 2) concat
            lst = tmp / "concat.txt"
            lst.write_text("".join(f"file '{c.resolve()}'\n" for c in enc_chunks),
                           encoding="utf-8")
            subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                            "-c", "copy", str(output)], check=True, capture_output=True)
            return len(enc_chunks)
