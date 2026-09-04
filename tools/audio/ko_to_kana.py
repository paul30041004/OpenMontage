"""Ko→Kana pronunciation substitution for Bert-VITS2 Korean synthesis.

Bert-VITS2 (fishaudio) natively synthesizes ZH / EN / JP. Korean has no native
path in the stock v2.3 model. This module converts Hangul into a Japanese
phonetic approximation (kana) so the JP pipeline can pronounce it, which is the
documented community approach for Korean TTS with Japanese-trained VITS models.

This is a best-effort pronunciation approximation, not a transliteration: final
consonants (받침) get an epenthetic vowel, and sounds Japanese lacks (ㅅ, ㅈ, ㅊ,
ㅡ…) map to their nearest kana. Quality is "understandable Japanese-accented
Korean". For native-quality Korean, fine-tune a JP model on Korean data (see
`skills/bert-vits2-tts.md` → training section).
"""

from __future__ import annotations

from dataclasses import dataclass

# Hangul jamo ranges
_S_BASE = 0xAC00  # 가
_S_COUNT = 11172
_L_COUNT = 19  # 초성
_V_COUNT = 21  # 중성
_T_COUNT = 28  # 종성 (0 = 없음)

# 초성 (onset) → kana
_INITIAL_KANA = [
    "",      # ㄱ → (base vowel) handled below
    "",      # ㄲ
    "",      # ㄴ
    "",      # ㄷ
    "",      # ㄸ
    "",      # ㄹ
    "",      # ㅁ
    "",      # ㅂ
    "",      # ㅃ
    "",      # ㅅ
    "",      # ㅆ
    "",      # ㅇ
    "",      # ㅈ
    "",      # ㅉ
    "",      # ㅊ
    "",      # ㅋ
    "",      # ㅌ
    "",      # ㅍ
    "",      # ㅎ
]

# 초성 개별 매핑: onset consonant → kana consonant (combines with vowel)
_ONSET_MAP = {
    "ㄱ": "k", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "t", "ㄸ": "tt", "ㄹ": "r",
    "ㅁ": "m", "ㅂ": "p", "ㅃ": "pp", "ㅅ": "s", "ㅆ": "ss", "ㅇ": "",
    "ㅈ": "ch", "ㅉ": "tch", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h",
}

# 중성 (vowel) → kana vowel
_VOWEL_MAP = {
    "ㅏ": "a", "ㅐ": "e", "ㅑ": "ya", "ㅒ": "ye", "ㅓ": "o", "ㅔ": "e",
    "ㅕ": "yo", "ㅖ": "ye", "ㅗ": "o", "ㅘ": "wa", "ㅙ": "we", "ㅚ": "o",
    "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo", "ㅞ": "we", "ㅟ": "ui", "ㅠ": "yu",
    "ㅡ": "u", "ㅢ": "ui", "ㅣ": "i",
}

# 종성 (final consonant) → epenthetic kana syllable (with added vowel)
_FINAL_MAP = {
    "": "", "ㄱ": "ku", "ㄲ": "kku", "ㄳ": "ksu", "ㄴ": "n", "ㄵ": "nchi",
    "ㄶ": "n", "ㄷ": "to", "ㄹ": "ru", "ㄺ": "ruku", "ㄻ": "rumu",
    "ㄼ": "rupu", "ㄽ": "rusu", "ㄾ": "ruto", "ㄿ": "rupu", "ㅀ": "ru",
    "ㅁ": "mu", "ㅂ": "pu", "ㅄ": "pusu", "ㅅ": "su", "ㅆ": "ssu",
    "ㅇ": "n", "ㅈ": "chi", "ㅊ": "chi", "ㅋ": "ku", "ㅌ": "to", "ㅍ": "pu", "ㅎ": "ha",
}

# initial consonant list (index order per Unicode)
_INITIALS = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
             "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
_VOWELS = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ",
           "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
_TRAILING = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ",
             "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ",
             "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]


@dataclass
class KoSyllable:
    initial: str
    vowel: str
    trailing: str


def _decompose(ch: str) -> KoSyllable | None:
    """Decompose one Hangul syllable into initial/vowel/trailing jamo."""
    code = ord(ch)
    if not (_S_BASE <= code < _S_BASE + _S_COUNT):
        return None
    idx = code - _S_BASE
    t = idx % _T_COUNT
    v = (idx // _T_COUNT) % _V_COUNT
    l = idx // (_V_COUNT * _T_COUNT)
    return KoSyllable(_INITIALS[l], _VOWELS[v], _TRAILING[t])


def _kana_for(initial: str, vowel: str) -> str:
    """Combine onset + vowel into a kana reading (romaji-style, JP-pronounceable)."""
    onset = _ONSET_MAP.get(initial, "")
    v = _VOWEL_MAP.get(vowel, "u")
    return onset + v


def hangul_to_kana(text: str) -> str:
    """Convert a Korean string to a Japanese phonetic approximation (romaji).

    Works per syllable: onset+vowel form one kana syllable; the final
    consonant (if any) becomes an extra epenthetic kana. Non-Hangul characters
    (punctuation, whitespace, latin) pass through unchanged.
    """
    out: list[str] = []
    for ch in text:
        syl = _decompose(ch)
        if syl is None:
            out.append(ch)
            continue
        kana = _kana_for(syl.initial, syl.vowel)
        if syl.trailing:
            kana += _FINAL_MAP.get(syl.trailing, "")
        out.append(kana)
    return "".join(out)


# ---- romaji -> hiragana (for the JP Bert-VITS2 phonemizer) ----------------

_ROMANJI_SPECIAL = {
    "shi": "し", "chi": "ち", "tsu": "つ", "fu": "ふ", "ji": "じ",
    "si": "し", "ti": "ち", "tu": "つ", "hu": "ふ", "zi": "じ",
    "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ", "sha": "しゃ", "shu": "しゅ",
    "sho": "しょ", "ja": "じゃ", "ju": "じゅ", "jo": "じょ",
}

_ROMANJI_SMALL = {"ya": "ゃ", "yu": "ゅ", "yo": "ょ"}

# simple consonant + vowel (monographs)
_KANA_MONO = {
    "a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",
    "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
    "sa": "さ", "su": "す", "se": "せ", "so": "そ",
    "ta": "た", "te": "て", "to": "と",
    "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
    "ha": "は", "hi": "ひ", "he": "へ", "ho": "ほ",
    "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
    "ya": "や", "yu": "ゆ", "yo": "よ",
    "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
    "wa": "わ", "wo": "を", "n": "ん",
    "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
    "za": "ざ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
    "da": "だ", "de": "で", "do": "ど",
    "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",
    "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",
    "ui": "うぃ",
}

# consonant (romaji) + ya/yu/yo compound -> small kana
_YOOON = {
    ("k", "ya"): "きゃ", ("k", "yu"): "きゅ", ("k", "yo"): "きょ",
    ("g", "ya"): "ぎゃ", ("g", "yu"): "ぎゅ", ("g", "yo"): "ぎょ",
    ("s", "ya"): "しゃ", ("s", "yu"): "しゅ", ("s", "yo"): "しょ",
    ("z", "ya"): "じゃ", ("z", "yu"): "じゅ", ("z", "yo"): "じょ",
    ("t", "ya"): "ちゃ", ("t", "yu"): "ちゅ", ("t", "yo"): "ちょ",
    ("d", "ya"): "ぢゃ", ("d", "yu"): "ぢゅ", ("d", "yo"): "ぢょ",
    ("n", "ya"): "にゃ", ("n", "yu"): "にゅ", ("n", "yo"): "にょ",
    ("h", "ya"): "ひゃ", ("h", "yu"): "ひゅ", ("h", "yo"): "ひょ",
    ("b", "ya"): "びゃ", ("b", "yu"): "びゅ", ("b", "yo"): "びょ",
    ("p", "ya"): "ぴゃ", ("p", "yu"): "ぴゅ", ("p", "yo"): "ぴょ",
    ("m", "ya"): "みゃ", ("m", "yu"): "みゅ", ("m", "yo"): "みょ",
    ("r", "ya"): "りゃ", ("r", "yu"): "りゅ", ("r", "yo"): "りょ",
}

_GEMINATE = {"kk": "っ", "tt": "っ", "ss": "っ", "pp": "っ", "tch": "っ"}


def romaji_to_hiragana(romaji: str) -> str:
    """Convert the ko_to_kana romaji output into hiragana for pyopenjtalk."""
    out: list[str] = []
    i = 0
    n = len(romaji)
    while i < n:
        # geminate onset (kk, tt, ss, pp, tch)
        matched = False
        for g, small in _GEMINATE.items():
            if romaji.startswith(g, i):
                out.append(small)
                i += len(g)
                matched = True
                break
        if matched:
            continue
        # yo-on: consonant + ya/yu/yo
        if i + 1 < n:
            for (c, y), h in _YOOON.items():
                if romaji.startswith(c + y, i):
                    out.append(h)
                    i += len(c) + len(y)
                    matched = True
                    break
            if matched:
                continue
        # longest special (shi, chi, tsu, fu, cha, cho, ...)
        for k in sorted(_ROMANJI_SPECIAL, key=len, reverse=True):
            if romaji.startswith(k, i):
                out.append(_ROMANJI_SPECIAL[k])
                i += len(k)
                matched = True
                break
        if matched:
            continue
        # mono kana
        for k in sorted(_KANA_MONO, key=len, reverse=True):
            if romaji.startswith(k, i):
                out.append(_KANA_MONO[k])
                i += len(k)
                matched = True
                break
        if matched:
            continue
        out.append(romaji[i])
        i += 1
    return "".join(out)


def hangul_to_hiragana(text: str) -> str:
    """Korean text -> hiragana (via ko_to_kana romaji) for the JP pipeline."""
    return romaji_to_hiragana(hangul_to_kana(text))


def ko_syllable_count(text: str) -> int:
    """Count Hangul syllables (for pacing estimates)."""
    return sum(1 for ch in text if _decompose(ch) is not None)
