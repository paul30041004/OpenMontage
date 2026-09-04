"""Tests for tools/avatar/rhubarb_lipsync.py — phoneme-accurate 2D lip-sync."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.avatar.rhubarb_lipsync import RhubarbLipsync  # noqa: E402


def test_status_reflects_binary():
    status = RhubarbLipsync().get_status()
    assert status.value in ("available", "unavailable")


def test_requires_audio():
    r = RhubarbLipsync().execute({"audio_path": "nope.wav"})
    assert r.success is False


def test_mouth_shapes_render():
    from tools.avatar.rhubarb_lipsync import render_face

    for shape in "XABCDEFG":
        img = render_face(shape)
        assert img.size == (1280, 720)
        assert img.mode == "RGBA"


def test_registry():
    from tools.tool_registry import registry

    registry.discover()
    t = registry._tools.get("rhubarb_lipsync")
    assert t is not None and t.capability == "avatar" and t.provider == "rhubarb"
