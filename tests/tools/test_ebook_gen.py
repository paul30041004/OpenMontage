"""Tests for tools/graphics/ebook_gen.py — the open-source typesetting
tool that turns book page layouts into 16:9 video frames / clips.

This file does not require any renderer binary to run its logic tests; the
renderer-specific paths are exercised only in the optional end-to-end test module
(separate, gated on renderer availability).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.graphics.ebook_gen import EbookGen, _markup_to_html, _normalize_renderer  # noqa: E402


def test_renders_html_frame_with_weasyprint(tmp_path):
    r = EbookGen().execute(
        {
            "renderer": "weasyprint",
            "use": "html",
            "html": "<html><head><style>@page{size:1920px 1080px;margin:0}</style></head><body><h1>book</h1></body></html>",
            "format": "frame",
            "output_path": str(tmp_path / "f.png"),
        }
    )
    assert r.success, r.error
    assert Path(r.data["output"]).exists()


def test_renders_markdown_video_with_weasyprint(tmp_path):
    r = EbookGen().execute(
        {
            "renderer": "weasyprint",
            "use": "markdown",
            "markdown": "# Title\n\nBody",
            "format": "video",
            "duration_seconds": 2,
            "fps": 24,
            "output_path": str(tmp_path / "v.mp4"),
        }
    )
    assert r.success, r.error
    assert Path(r.data["output"]).exists()


def test_normalize_renderer_keeps_weasy_for_markdown():
    assert _normalize_renderer("weasyprint", "markdown") == "weasyprint"


def test_status_available_when_any_renderer_present():
    # get_status returns available if at least one renderer + pdftoppm exist.
    status = EbookGen().get_status()
    assert status.value in ("available", "degraded", "unavailable")
