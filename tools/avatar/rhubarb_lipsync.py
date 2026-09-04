"""Rhubarb-driven 2D lip-sync avatar — precise phoneme-level time sync.

Uses Rhubarb Lip Sync's timecoded mouth shapes (A-H, X) to drive a 2D
line-art narrator's mouth, giving exact per-phoneme timing (vs. Wav2Lip's
neural output which can drift). Fits the book/ink series aesthetic.

Pipeline: audio -> rhubarb JSON (mouth cues) -> per-frame Pillow renders of the
face with the matching mouth shape -> ffmpeg encode with the source audio.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

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

RHUBARB = Path(__file__).resolve().parent.parent.parent / "tools" / "_rhubarb" / "rhubarb"
W, H = 1280, 720
FACE_CX, FACE_CY = 760, 320   # face center on the backdrop
FACE_R = 200                  # face radius
MOUTH_X, MOUTH_Y = 760, 380   # mouth anchor

PAPER = (245, 239, 223)
INK = (43, 38, 32)
RED = (179, 53, 46)
SKIN = (236, 224, 199)


def _mouth_draw(d: ImageDraw.ImageDraw, shape: str) -> None:
    """Draw one of rhubarb's mouth shapes (X,A-G) as simple line art."""
    x, y = MOUTH_X, MOUTH_Y
    lw = 5
    if shape == "X":  # closed line
        d.line([(x - 34, y), (x + 34, y)], fill=INK, width=lw)
    elif shape == "A":  # wide open
        d.ellipse([x - 40, y - 16, x + 40, y + 34], outline=INK, width=lw)
    elif shape == "B":  # open
        d.ellipse([x - 34, y - 12, x + 34, y + 26], outline=INK, width=lw)
    elif shape == "C":  # small open
        d.ellipse([x - 26, y - 8, x + 26, y + 18], outline=INK, width=lw)
    elif shape == "D":  # closed smile
        d.arc([x - 36, y - 6, x + 36, y + 26], start=0, end=180, fill=INK, width=lw)
    elif shape == "E":  # small smile
        d.arc([x - 24, y - 4, x + 24, y + 16], start=0, end=180, fill=INK, width=lw)
    elif shape == "F":  # wide smile
        d.arc([x - 42, y - 10, x + 42, y + 34], start=0, end=180, fill=INK, width=lw)
    elif shape == "G":  # puckered
        d.ellipse([x - 16, y - 10, x + 16, y + 12], outline=INK, width=lw)
    else:
        d.line([(x - 34, y), (x + 34, y)], fill=INK, width=lw)


def _mouth_draw(d: ImageDraw.ImageDraw, shape: str) -> None:
    """Draw one of rhubarb's mouth shapes (X,A-G) as refined line art."""
    x, y = MOUTH_X, MOUTH_Y
    lw = 6
    lip = (179, 53, 46, 255)
    if shape == "X":  # closed gentle line
        d.line([(x - 30, y), (x + 30, y)], fill=INK, width=lw)
    elif shape == "A":  # wide open
        d.ellipse([x - 36, y - 18, x + 36, y + 34], fill=(120, 40, 36, 255), outline=INK, width=lw)
        d.line([(x - 30, y + 2), (x + 30, y + 2)], fill=lip, width=3)  # upper lip hint
    elif shape == "B":  # open
        d.ellipse([x - 32, y - 13, x + 32, y + 26], fill=(120, 40, 36, 255), outline=INK, width=lw)
    elif shape == "C":  # small open
        d.ellipse([x - 24, y - 8, x + 24, y + 18], fill=(120, 40, 36, 255), outline=INK, width=lw)
    elif shape == "D":  # closed smile
        d.arc([x - 34, y - 8, x + 34, y + 24], start=0, end=180, fill=INK, width=lw)
    elif shape == "E":  # small smile
        d.arc([x - 22, y - 4, x + 22, y + 14], start=0, end=180, fill=INK, width=lw)
    elif shape == "F":  # wide warm smile
        d.arc([x - 40, y - 10, x + 40, y + 30], start=0, end=180, fill=INK, width=lw)
        d.line([(x - 34, y + 14), (x + 34, y + 14)], fill=lip, width=3)
    elif shape == "G":  # puckered
        d.ellipse([x - 15, y - 10, x + 15, y + 12], outline=INK, width=lw)
    else:
        d.line([(x - 30, y), (x + 30, y)], fill=INK, width=lw)


def _eye(d, ex, ey, r, highlight=True) -> None:
    """One elegant almond eye with a highlight dot."""
    d.ellipse([ex - r * 1.3, ey - r * 0.8, ex + r * 1.3, ey + r * 0.8], fill=INK)
    if highlight:
        d.ellipse([ex - r * 0.55, ey - r * 0.45, ex - r * 0.15, ey - r * 0.1], fill=(255, 255, 255, 230))
    d.ellipse([ex - r * 1.35, ey + r * 0.75, ex + r * 1.35, ey + r * 0.95], fill=(200, 200, 200, 120))


def render_face(shape: str) -> Image.Image:
    """A refined, symmetric line-art narrator face (red-thread series style)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # ---- series accent: red thread + knot ----
    d.line([46, 46, 200, 46], fill=RED, width=4)
    d.ellipse([188, 35, 212, 57], fill=RED)
    d.line([46, 46, 46, 66], fill=RED, width=4)

    # ---- face (symmetric) ----
    cx, cy, r = FACE_CX, FACE_CY, FACE_R
    # head (soft two-tone for depth: warm base + a subtle lighter highlight side)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SKIN, outline=INK, width=7)
    # subtle highlight arc on the left cheek for gentle depth (symmetric-neutral)
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 150, 270, fill=(247, 238, 220, 255))
    # blush marks (symmetric)
    for bx in (cx - 96, cx + 96):
        d.ellipse([bx - 22, cy + 26, bx + 22, cy + 52], fill=(232, 180, 158, 90))
    # eyes (almond, symmetric)
    for ex in (cx - 68, cx + 68):
        _eye(d, ex, cy - 60, 22)
    # brows (gentle arch, symmetric)
    for bx in (cx - 68, cx + 68):
        d.arc([bx - 26, cy - 100, bx + 26, cy - 74], 190, 350, fill=INK, width=6)
    # nose (subtle central line)
    d.arc([cx - 6, cy - 32, cx + 16, cy + 6], 40, 160, fill=(179, 53, 46, 220), width=4)
    # mouth
    _mouth_draw(d, shape)
    return img


def _probe_seconds(path: Path) -> float:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except Exception:
        return 0.0


class RhubarbLipsync(BaseTool):
    name = "rhubarb_lipsync"
    version = "0.1.0"
    tier = ToolTier.GENERATE
    capability = "avatar"
    provider = "rhubarb"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffmpeg"]
    install_instructions = (
        "Rhubarb Lip Sync binary missing. Download Rhubarb-Lip-Sync macOS zip from "
        "github.com/DanielSWolf/rhubarb-lip-sync/releases and place rhubarb + res/ "
        "under tools/_rhubarb/."
    )
    agent_skills = ["ffmpeg"]

    capabilities = ["rhubarb_lipsync", "2d_avatar"]

    input_schema = {
        "type": "object",
        "required": ["audio_path"],
        "properties": {
            "audio_path": {"type": "string", "description": "Audio to lip-sync."},
            "output_path": {"type": "string", "description": "Output MP4 path."},
            "fps": {"type": "integer", "default": 24},
            "size": {"type": "integer", "enum": [720, 1080], "default": 720},
        },
    }

    resource_profile = ResourceProfile(cpu_cores=2, ram_mb=1024, vram_mb=0, disk_mb=500)
    retry_policy = RetryPolicy(max_retries=0)
    idempotency_key_fields = ["audio_path"]
    side_effects = ["writes MP4 to output_path"]
    user_visible_verification = [
        "Mouth shapes must track phonemes exactly (this is the point vs Wav2Lip)",
        "Watch for natural mouth closure between words",
    ]

    def get_status(self) -> ToolStatus:
        if RHUBARB.exists():
            return ToolStatus.AVAILABLE
        return ToolStatus.UNAVAILABLE

    def check_dependencies(self) -> None:
        if not RHUBARB.exists():
            raise DependencyError("Rhubarb binary missing. " + self.install_instructions)

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def estimate_runtime(self, inputs: dict[str, Any]) -> float:
        audio_s = _probe_seconds(Path(inputs.get("audio_path", "")))
        return max(20.0, audio_s * 3)

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        start = time.time()
        audio = Path(inputs.get("audio_path", "")).resolve()
        if not audio.is_file():
            return ToolResult(success=False, error="audio_path required")
        if not RHUBARB.exists():
            return ToolResult(success=False, error="Rhubarb missing. " + self.install_instructions)

        fps = int(inputs.get("fps", 24))
        bg = inputs.get("bg_path")
        output = Path(inputs.get("output_path", "rhubarb_avatar.mp4")).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="rhubarb_") as tmp:
            tmp = Path(tmp)
            cues = self._rhubarb(audio, tmp)
            frames = self._render(cues, fps, audio, tmp)
            self._encode(frames, audio, output, fps, bg)

        return ToolResult(
            success=True,
            data={"provider": self.provider, "output": str(output),
                  "duration_seconds": _probe_seconds(output), "cues": len(cues)},
            artifacts=[str(output)], duration_seconds=round(time.time() - start, 2),
        )

    def _rhubarb(self, audio: Path, tmp: Path) -> list[dict]:
        j = tmp / "cues.json"
        subprocess.run([str(RHUBARB), "-o", str(j), "-f", "json", str(audio)],
                       capture_output=True, text=True, timeout=300, check=True)
        return json.loads(j.read_text(encoding="utf-8"))["mouthCues"]

    def _render(self, cues, fps, audio, tmp) -> list[Path]:
        dur = _probe_seconds(audio)
        n = max(1, int(round(dur * fps)))
        frames: list[Path] = []
        ci = 0
        for f in range(n):
            t = f / fps
            while ci < len(cues) - 1 and t > cues[ci + 1]["end"]:
                ci += 1
            shape = cues[ci]["value"] if cues else "X"
            img = render_face(shape)
            p = tmp / f"f{f:05d}.png"
            img.save(p)
            frames.append(p)
        return frames

    def _encode(self, frames, audio, output, fps, bg) -> None:
        tmp = frames[0].parent
        seq = str(tmp / "f%05d.png")
        if bg:
            # Composite the transparent face (scaled) over the backdrop + narration.
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(bg),
                "-framerate", str(fps), "-i", seq, "-i", str(audio),
                "-filter_complex",
                "[1:v]scale=-2:560,format=rgba,setsar=1[face];"
                "[0:v][face]overlay=x=main_w-overlay_w-50:y=(main_h-overlay_h)/2[v];"
                "[2:a]afade=t=in:st=0:d=0.3[an]",
                "-map", "[v]", "-map", "[an]",
                "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", str(output)],
                check=True, capture_output=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", seq,
                            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-i", str(audio), "-c:a", "aac", "-shortest", str(output)],
                           check=True, capture_output=True)
