"""Tests for tools/audio/ko_g2p.py (Korean G2P — g2pK wrapper).

The canonical g2pK demo sentence must map to its known pronunciation.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.audio.ko_g2p import g2p  # noqa: E402


def test_canonical_g2pk_example():
    # Known output of kyubyong/g2pK for the classic demo sentence.
    out = g2p("신을 신고 얼른 동사무소에 가서 혼인 신고 해라")
    assert out == "시늘 신꼬 얼른 동사무소에 가서 호닌 신고 해라"


def test_liaison_handled():
    # 마음을 -> 마으믈 (연음)
    assert "마으믈" in g2p("네 마음을 다하여 여호와를 신뢰하라")


def test_empty_returns_empty():
    assert g2p("") == ""


def test_numbers_read_out():
    # g2pK normalizes Arabic numerals to Hangul reading (3장 -> 삼장)
    assert "삼장" in g2p("잠언 3장")
