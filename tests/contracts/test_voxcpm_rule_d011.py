"""Contract test enforcing user rule d-011: VoxCPM voice_design must be in English."""

from __future__ import annotations

import pytest

from tools.audio.voxcpm_tts import VoxCPMTTS


def test_voxcpm_rejects_korean_in_voice_design():
    tool = VoxCPMTTS()
    result = tool.execute({
        "text": "안녕하세요",
        "voice_design": "부드러운 중년 남성 목소리",
    })
    assert not result.success
    assert "d-011" in result.error
    assert "ENGLISH" in result.error


def test_voxcpm_accepts_english_in_voice_design():
    tool = VoxCPMTTS()
    # Should not fail on voice_design validation (will proceed to model check or execution)
    result = tool.execute({
        "text": "안녕하세요",
        "voice_design": "(calm, authoritative Korean male narrator)",
        "model_path": "/nonexistent/path/to/test/error/early",
    })
    assert not result.success
    # Fails because model is missing, NOT because of rule d-011
    assert "d-011" not in (result.error or "")
    assert "VoxCPM2 model missing" in (result.error or "")
