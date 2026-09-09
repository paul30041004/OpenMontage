"""Apple Silicon VideoToolbox Hardware Accelerated Encoder for OpenMontage.

Leverages Apple Silicon's dedicated M-series hardware media engines
via FFmpeg's `h264_videotoolbox` and `hevc_videotoolbox` encoders.
Delivers up to 10x faster export speeds with near-zero CPU load,
subtitles burning, scaling, and bitrate management.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

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


class VideoToolboxEncoder(BaseTool):
    name = "videotoolbox_encoder"
    version = "0.1.0"
    tier = ToolTier.CORE
    capability = "video_post"
    provider = "ffmpeg"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "FFmpeg with VideoToolbox support is required on macOS."
    agent_skills = ["ffmpeg"]

    input_schema = {
        "type": "object",
        "required": ["input_path", "output_path"],
        "properties": {
            "input_path": {
                "type": "string",
                "description": "Path to input video file."
            },
            "output_path": {
                "type": "string",
                "description": "Destination file path for hardware-encoded video."
            },
            "codec": {
                "type": "string",
                "enum": ["h264", "hevc", "prores"],
                "default": "h264",
                "description": "Apple Silicon hardware encoder (h264_videotoolbox, hevc_videotoolbox, prores_videotoolbox)."
            },
            "bitrate": {
                "type": "string",
                "default": "8M",
                "description": "Target video bitrate (e.g. '8M', '15M', '25M')."
            },
            "scale": {
                "type": "string",
                "description": "Optional resolution scale (e.g. '1920:1080', '1080:1920' for 9:16 vertical shorts)."
            },
            "fps": {
                "type": "integer",
                "default": 30,
                "description": "Output frame rate (default: 30)."
            },
            "subtitles_path": {
                "type": "string",
                "description": "Optional path to an .srt file to hard-burn into the video."
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

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        input_path = params.get("input_path")
        if not input_path or not os.path.exists(input_path):
            return ToolResult(success=False, error=f"입력 비디오 파일을 찾을 수 없습니다: {input_path}")

        output_path = params.get("output_path")
        if not output_path:
            return ToolResult(success=False, error="출력 경로(output_path)가 필요합니다.")

        codec_choice = params.get("codec", "h264").lower()
        encoder_map = {
            "h264": "h264_videotoolbox",
            "hevc": "hevc_videotoolbox",
            "prores": "prores_videotoolbox"
        }
        vcodec = encoder_map.get(codec_choice, "h264_videotoolbox")
        bitrate = params.get("bitrate", "8M")
        fps = int(params.get("fps", 30))
        scale = params.get("scale")
        subtitles_path = params.get("subtitles_path")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        ffmpeg_bin = self._get_ffmpeg()

        # Build filter chain
        vf_filters = []
        if scale:
            vf_filters.append(f"scale={scale}")
        if subtitles_path and os.path.exists(subtitles_path):
            vf_filters.append(f"subtitles='{subtitles_path}'")
        if fps:
            vf_filters.append(f"fps={fps}")

        cmd = [ffmpeg_bin, "-y", "-i", input_path]

        if vf_filters:
            cmd.extend(["-vf", ",".join(vf_filters)])

        cmd.extend([
            "-c:v", vcodec,
            "-b:v", bitrate,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            return ToolResult(success=False, error=f"VideoToolbox 인코딩 실패: {e.stderr}")

        elapsed = round(time.time() - start_time, 2)
        out_file = Path(output_path)

        return ToolResult(
            success=True,
            data={
                "output_path": str(out_file.resolve()),
                "encoder": vcodec,
                "bitrate": bitrate,
                "file_size": out_file.stat().st_size,
                "elapsed_seconds": elapsed,
                "message": f"Apple Silicon {vcodec} 하드웨어 인코딩 완료 ({elapsed}초 소요)."
            },
            artifacts=[str(out_file)]
        )
