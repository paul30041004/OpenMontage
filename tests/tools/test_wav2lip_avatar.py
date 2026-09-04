"""Tests for tools/avatar/wav2lip_avatar.py — Mac-viable lip-sync tool."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.avatar.wav2lip_avatar import Wav2LipAvatar  # noqa: E402
from tools.base_tool import ToolStatus  # noqa: E402


def test_status_reflects_weights():
    # available if weights+env exist, degraded if env but no weights,
    # unavailable if env missing — never crashes.
    status = Wav2LipAvatar().get_status()
    assert status.value in ("available", "degraded", "unavailable")


def test_requires_face_and_audio(tmp_path):
    r = Wav2LipAvatar().execute({"face": "nope.png", "audio_path": str(tmp_path / "x.wav")})
    assert r.success is False


def test_registry_capability():
    from tools.tool_registry import registry

    registry.discover()
    t = registry._tools.get("wav2lip_avatar")
    assert t is not None
    assert t.capability == "avatar"
    assert t.provider == "wav2lip"
