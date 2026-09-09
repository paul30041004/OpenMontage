"""Viral Shorts / TikTok Style Karaoke ASS Subtitle Burner for OpenMontage.

Generates Advanced SubStation Alpha (.ass) subtitles with word-by-word
highlighting (Word-Pop), glowing border outlines, and drop shadows,
and hard-burns them into video using Apple Silicon VideoToolbox acceleration.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolStability,
    ToolStatus,
    ToolTier,
)

# Colors in BGR hex format for ASS format: &HAABBGGRR&
COLOR_MAP = {
    "yellow": "&H0022F5&",  # Bright vibrant yellow/gold
    "cyan": "&HFFD400&",    # Neon cyan
    "green": "&H10D434&",   # Neon lime green
    "pink": "&HAA22FF&",    # Hot pink
    "white": "&HFFFFFF&",
    "black": "&H000000&"
}


def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


class AssKaraokeBurner(BaseTool):
    name = "ass_karaoke_burner"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "subtitle"
    provider = "ffmpeg"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "FFmpeg with libass and VideoToolbox support is required on macOS."
    agent_skills = ["ffmpeg", "remotion-best-practices"]

    input_schema = {
        "type": "object",
        "required": ["video_path", "words", "output_path"],
        "properties": {
            "video_path": {
                "type": "string",
                "description": "Path to background video file (MP4)."
            },
            "words": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["text", "start", "end"],
                    "properties": {
                        "text": {"type": "string"},
                        "start": {"type": "number"},
                        "end": {"type": "number"}
                    }
                },
                "description": "Word-level timestamp list."
            },
            "output_path": {
                "type": "string",
                "description": "Destination file path for burned video (MP4)."
            },
            "highlight_color": {
                "type": "string",
                "enum": ["yellow", "cyan", "green", "pink"],
                "default": "yellow",
                "description": "Color for active singing/speaking word highlight."
            },
            "words_per_line": {
                "type": "integer",
                "default": 4,
                "description": "Maximum number of words grouped in one subtitle line."
            },
            "font_size": {
                "type": "integer",
                "default": 32,
                "description": "Subtitle font size (e.g. 32 for 1080p, 48 for vertical 9:16 shorts)."
            },
            "bottom_margin": {
                "type": "integer",
                "default": 90,
                "description": "Distance in pixels from bottom of screen (safe zone padding)."
            }
        }
    }

    def _get_ffmpeg(self) -> str:
        for c in ["ffmpeg", "/Users/paul/pinokio/bin/ffmpeg-env/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg"]:
            try:
                res = subprocess.run([c, "-version"], capture_output=True, timeout=2)
                if res.returncode == 0:
                    return c
            except Exception:
                continue
        return "ffmpeg"

    def _generate_ass_script(
        self,
        words: List[Dict[str, Any]],
        words_per_line: int,
        highlight_color: str,
        font_size: int,
        bottom_margin: int
    ) -> str:
        hl_bgr = COLOR_MAP.get(highlight_color.lower(), COLOR_MAP["yellow"])

        header = f"""[Script Info]
Title: OpenMontage Karaoke Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,{font_size},&H00FFFFFF&,&H00FFFFFF&,&H00000000&,&H80000000&,-1,0,0,0,100,100,0,0,1,3.5,2.0,2,20,20,{bottom_margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        dialogue_lines = []

        # Group words into chunks
        chunks = [words[i:i + words_per_line] for i in range(0, len(words), words_per_line)]

        for chunk in chunks:
            chunk_start = float(chunk[0]["start"])
            chunk_end = float(chunk[-1]["end"])

            # For each word in chunk, emit a dialogue event highlighting that specific word
            for idx, active_word in enumerate(chunk):
                w_start = format_ass_time(float(active_word["start"]))
                # Word highlight ends when next word begins, or at chunk end
                w_end_time = float(chunk[idx + 1]["start"]) if idx + 1 < len(chunk) else chunk_end
                w_end = format_ass_time(w_end_time)

                # Build line text with active word highlighted in color
                styled_tokens = []
                for j, w in enumerate(chunk):
                    w_text = w["text"].strip()
                    if j == idx:
                        styled_tokens.append(f"{{\\c{hl_bgr}\\b1}}{w_text}{{\\c&HFFFFFF&\\b0}}")
                    else:
                        styled_tokens.append(w_text)

                line_content = " ".join(styled_tokens)
                dialogue_lines.append(f"Dialogue: 0,{w_start},{w_end},Default,,0,0,0,,{line_content}")

        return header + "\n".join(dialogue_lines) + "\n"

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        video_path = params.get("video_path")
        if not video_path or not os.path.exists(video_path):
            return ToolResult(success=False, error=f"비디오 파일을 찾을 수 없습니다: {video_path}")

        words = params.get("words", [])
        if not words:
            return ToolResult(success=False, error="단어 타임스탬프(words)가 비어있습니다.")

        output_path = params.get("output_path")
        if not output_path:
            return ToolResult(success=False, error="출력 경로가 필요합니다.")

        hl_color = params.get("highlight_color", "yellow")
        words_per_line = int(params.get("words_per_line", 4))
        font_size = int(params.get("font_size", 36))
        margin_v = int(params.get("bottom_margin", 90))

        out_file = Path(output_path).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        ass_file = out_file.parent / f"{out_file.stem}_karaoke.ass"
        ass_content = self._generate_ass_script(words, words_per_line, hl_color, font_size, margin_v)
        with open(ass_file, "w", encoding="utf-8") as f:
            f.write(ass_content)

        ffmpeg_bin = self._get_ffmpeg()
        cmd = [
            ffmpeg_bin, "-y",
            "-i", video_path,
            "-vf", f"ass='{ass_file}'",
            "-c:v", "h264_videotoolbox",
            "-b:v", "8M",
            "-c:a", "copy",
            str(out_file)
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            return ToolResult(success=False, error=f"가라오케 자막 번인 실패: {e.stderr}")

        return ToolResult(
            success=True,
            data={
                "output_path": str(out_file),
                "ass_file": str(ass_file),
                "words_burned": len(words),
                "highlight_color": hl_color,
                "elapsed_seconds": round(time.time() - start_time, 2)
            },
            artifacts=[str(out_file), str(ass_file)]
        )
