"""Korean G2P (grapheme-to-phoneme) module for OpenMontage.

Wraps kyubyong/g2pK — the standard Korean G2P library — to convert script text
into "actual pronunciation" (연음 / 구개음화 / 된소리 / 격음화 …). This is the
Nexon-style preprocessing core: the TTS pipeline learns from the pronounced
form, not the written form.

Example (matches the canonical g2pK demo):
    "신을 신고 얼른 동사무소에 가서 혼인 신고 해라"
  -> "시늘 신꼬 얼른 동사무소에 가서 호닌 신고 해라"

g2pK uses Mecab for morphological context when available and falls back to
jamo-level rules otherwise. Either path produces valid Korean pronunciation.
"""

from __future__ import annotations

import functools
from typing import Optional

_jamo_available = True
try:
    from jamo import h2j, j2hcj  # noqa: F401
except Exception:  # pragma: no cover
    _jamo_available = False


@functools.lru_cache(maxsize=1)
def _g2p() -> object:
    from g2pk import G2p

    return G2p()


def g2p(text: str, descriptive: bool = False, group_vowels: bool = False) -> str:
    """Convert Korean script to its pronounced form (romanized hangul output).

    Returns the phonetic string (e.g. '시늘 신꼬 …'). `descriptive` keeps some
    spelling-to-pronunciation inconsistencies, `group_vowels` merges diphthongs.
    """
    if not text:
        return text
    try:
        return _g2p()(text, descriptive=descriptive, group_vowels=group_vowels)
    except Exception:
        return text


def decompose(text: str) -> Optional[str]:
    """Decompose Hangul into Jamo (초성/중성/종성) if `jamo` is installed."""
    if not _jamo_available:
        return None
    try:
        return j2hcj(h2j(text))
    except Exception:
        return None


if __name__ == "__main__":
    demo = "신을 신고 얼른 동사무소에 가서 혼인 신고 해라"
    print("IN :", demo)
    print("OUT:", g2p(demo))
