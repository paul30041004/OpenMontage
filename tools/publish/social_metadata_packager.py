"""Social Metadata & Thumbnail Packager for YouTube Shorts / TikTok / Reels.

Generates SEO-optimized titles, hashtags, chapters, and engagement pinned comments,
and extracts the highest-impact visual thumbnail frame from the rendered MP4.
Prepares an upload-ready release bundle in a single pass.
"""

from __future__ import annotations

import json
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


class SocialMetadataPackager(BaseTool):
    name = "social_metadata_packager"
    version = "0.1.0"
    tier = ToolTier.PUBLISH
    capability = "publish"
    provider = "openmontage"
    stability = ToolStability.PRODUCTION
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC

    dependencies = ["cmd:ffmpeg"]
    install_instructions = "FFmpeg is required for thumbnail frame extraction."
    agent_skills = ["ffmpeg"]

    input_schema = {
        "type": "object",
        "required": ["video_path", "title", "output_dir"],
        "properties": {
            "video_path": {
                "type": "string",
                "description": "Path to final rendered MP4 video."
            },
            "title": {
                "type": "string",
                "description": "Base topic or video title."
            },
            "output_dir": {
                "type": "string",
                "description": "Output directory for the release bundle."
            },
            "script_text": {
                "type": "string",
                "description": "Optional script text for hashtag and summary extraction."
            },
            "thumbnail_second": {
                "type": "number",
                "default": 3.0,
                "description": "Timestamp in seconds to extract thumbnail frame (default: 3.0s)."
            },
            "category": {
                "type": "string",
                "enum": ["shorts", "bible", "worship", "tech", "entertainment"],
                "default": "shorts",
                "description": "Content category for hashtag targeting."
            }
        }
    }

    CATEGORY_TAGS: Dict[str, List[str]] = {
        "shorts": ["#shorts", "#쇼츠", "#viral", "#fyp", "#trending"],
        "bible": ["#성경", "#창세기", "#성경인물", "#기독교", "#말씀", "#shorts"],
        "worship": ["#찬양", "#찬송가", "#worship", "#ccm", "#hymn", "#shorts"],
        "tech": ["#AI", "#인공지능", "#기술", "#개발자", "#tech", "#shorts"],
        "entertainment": ["#레전드", "#꿀잼", "#쇼츠", "#이슈", "#shorts"]
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
        video_path = params.get("video_path")
        if not video_path or not os.path.exists(video_path):
            return ToolResult(success=False, error=f"비디오 파일을 찾을 수 없습니다: {video_path}")

        base_title = params.get("title", "OpenMontage Release").strip()
        out_dir = Path(params["output_dir"]).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        cat = params.get("category", "shorts")
        tags = self.CATEGORY_TAGS.get(cat, self.CATEGORY_TAGS["shorts"])
        thumb_sec = float(params.get("thumbnail_second", 3.0))

        # 1. Generate High-CTR Short-Form Titles
        hook_title = f"{base_title} | 1분 안에 끝내는 핵심 요약 #shorts"
        if cat == "bible":
            hook_title = f"[창세기] {base_title}의 충격적인 진실?! #shorts"
        elif cat == "worship":
            hook_title = f"[찬양] {base_title} 가상 합창단 & 보컬 가이드"

        # 2. Extract Thumbnail Frame
        thumb_path = out_dir / "thumbnail.jpg"
        ffmpeg_bin = self._get_ffmpeg()
        cmd = [
            ffmpeg_bin, "-y",
            "-ss", str(thumb_sec),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            str(thumb_path)
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            pass

        # 3. Build Description & Pinned Comment
        script_summary = params.get("script_text", "").strip()[:200]
        description = (
            f"{hook_title}\n\n"
            f"📌 내용 요약:\n{script_summary or base_title}\n\n"
            f"🔔 좋아요와 구독은 큰 힘이 됩니다!\n\n"
            f"{' '.join(tags)}"
        )

        pinned_comment = (
            f"여러분이 생각하시는 가장 인상 깊은 장면은 무엇인가요? 댓글로 의견을 나눠주세요! 👇"
        )

        metadata = {
            "title": hook_title,
            "description": description,
            "tags": tags,
            "pinned_comment": pinned_comment,
            "category": cat,
            "thumbnail_path": str(thumb_path) if thumb_path.exists() else None,
            "video_path": str(Path(video_path).resolve())
        }

        # Save metadata.json & release_card.txt
        meta_json_path = out_dir / "metadata.json"
        with open(meta_json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        card_path = out_dir / "upload_card.txt"
        with open(card_path, "w", encoding="utf-8") as f:
            f.write(f"=== [YouTube Shorts / Reels 업로드 카드] ===\n\n")
            f.write(f"▶ 제목 (Title):\n{hook_title}\n\n")
            f.write(f"▶ 본문 설명 (Description):\n{description}\n\n")
            f.write(f"▶ 고정 댓글 (Pinned Comment):\n{pinned_comment}\n\n")
            f.write(f"▶ 썸네일 이미지: {thumb_path.name}\n")

        return ToolResult(
            success=True,
            data={
                "bundle_dir": str(out_dir),
                "title": hook_title,
                "metadata_file": str(meta_json_path),
                "upload_card": str(card_path),
                "thumbnail_file": str(thumb_path) if thumb_path.exists() else None
            },
            artifacts=[str(meta_json_path), str(card_path)]
        )
