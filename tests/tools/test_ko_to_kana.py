"""Tests for tools/audio/ko_to_kana.py (Korean→Japanese pronunciation substitution)."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.audio.ko_to_kana import (  # noqa: E402
    hangul_to_hiragana,
    hangul_to_kana,
    ko_syllable_count,
    romaji_to_hiragana,
)


def test_simple_syllables():
    assert hangul_to_kana("나의") == "naui"
    assert hangul_to_kana("여호와는") == "yohowanun"


def test_final_consonant_gets_epenthetic_vowel():
    assert hangul_to_kana("목자") == "mokucha"
    assert hangul_to_kana("걸음") == "koruumu"


def test_mixed_latin_and_punct_passthrough():
    assert hangul_to_kana("잠언 3장") == "chamuon 3chan"
    assert hangul_to_kana("주님, 오늘") == "chunimu, onuru"


def test_non_hangul_unchanged():
    assert hangul_to_kana("hello 123") == "hello 123"


def test_syllable_count():
    assert ko_syllable_count("잠언 3장") == 3
    assert ko_syllable_count("abc") == 0


def test_hiragana_conversion():
    assert romaji_to_hiragana("naui") == "なうぃ"
    assert romaji_to_hiragana("mokucha") == "もくちゃ"
    assert romaji_to_hiragana("shinro") == "しんろ"


def test_hangul_to_hiragana():
    out = hangul_to_hiragana("여호와는")
    assert "よほわ" in out  # 여호와 → よほわ
    assert out.endswith("ぬん")  # 는 → ぬん
