"""Tests for tools/avatar/latentsync_avatar.py — Apple Silicon MLX lip-sync."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.avatar.latentsync_avatar import LatentSyncAvatar  # noqa: E402


def test_status_reflects_weights():
    status = LatentSyncAvatar().get_status()
    assert status.value in ("available", "degraded", "unavailable")


def test_requires_inputs(tmp_path):
    r = LatentSyncAvatar().execute({"face": "nope.png", "audio_path": str(tmp_path / "x.wav")})
    assert r.success is False


def test_registry():
    from tools.tool_registry import registry

    registry.discover()
    t = registry._tools.get("latentsync_avatar")
    assert t is not None and t.capability == "avatar" and t.provider == "latentsync"
