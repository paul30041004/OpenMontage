"""Tests for tools/subtitle/karaoke_subtitle.py — word-coloring + pop ASS."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.subtitle.karaoke_subtitle import KaraokeSubtitle, build_ass, _split_words  # noqa: E402


def test_split_words():
    assert _split_words("내가 산을 향하여") == ["내가", "산을", "향하여"]


def test_build_ass_karaoke_tags():
    segments = [{"start": 0.0, "end": 2.0, "text": "내가 산을"}]
    ass = build_ass(segments, ["내가 산을"])
    assert "{\\k" in ass          # karaoke tags present
    assert "[V4+ Styles]" in ass
    assert "Pop" in ass           # pop style present
    assert "Layer: " in ass or "[Events]" in ass


def test_status():
    assert KaraokeSubtitle().get_status().value in ("available", "unavailable")


def test_registry():
    from tools.tool_registry import registry

    registry.discover()
    t = registry._tools.get("karaoke_subtitle")
    assert t is not None and t.capability == "subtitle"
