"""Tests for tools/avatar/sadtalker_avatar.py — Mac-viable talking head."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.avatar.sadtalker_avatar import SadTalkerAvatar  # noqa: E402


def test_status_reflects_weights():
    status = SadTalkerAvatar().get_status()
    assert status.value in ("available", "degraded", "unavailable")


def test_requires_image_and_audio(tmp_path):
    r = SadTalkerAvatar().execute({"source_image": "nope.png",
                                   "driven_audio": str(tmp_path / "x.wav")})
    assert r.success is False


def test_registry():
    from tools.tool_registry import registry

    registry.discover()
    t = registry._tools.get("sadtalker_avatar")
    assert t is not None and t.capability == "avatar" and t.provider == "sadtalker"
