"""Korean text normalization module for OpenMontage TTS pipelines.

Handles conversion of numbers, dates, times, units, currencies, abbreviations,
hymns, and Bible verse citations (e.g. '창 4:1-3' -> '창세기 사장 일절에서 삼절')
into natural Korean phonetic script for flawless TTS synthesis without stuttering.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Korean Sino numbers (한자어 수사)
_SINO_DIGITS = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
_SINO_UNITS = ["", "십", "백", "천"]
_SINO_BIG_UNITS = ["", "만", "억", "조", "경"]

# Native Korean numbers (고유어 수사)
_NATIVE_1_TO_9 = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
_NATIVE_1_TO_9_STANDALONE = ["", "하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉"]
_NATIVE_TENS = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]
_NATIVE_TENS_CLASSIFIER = ["", "열", "스무", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]

# Nouns that trigger Native Korean counting numbers
_NATIVE_CLASSIFIERS = {
    "개", "명", "분", "마리", "권", "병", "잔", "장", "살", "번",
    "가지", "줄", "채", "척", "군데", "대", "발", "통", "벌", "켤레",
    "송이", "포기", "알", "점", "조각", "군", "곳"
}

# 66 Bible book abbreviations to full Korean pronunciation
BIBLE_BOOKS: Dict[str, str] = {
    # 구약 (Old Testament 39)
    "창": "창세기", "출": "출애굽기", "레": "레위기", "민": "민수기", "신": "신명기",
    "수": "여호수아", "삿": "사사기", "룻": "룻기", "삼상": "사무엘상", "삼하": "사무엘하",
    "왕상": "열왕기상", "왕하": "열왕기하", "대상": "역대상", "대하": "역대하", "스": "에스라",
    "느": "느헤미야", "에": "에스더", "욥": "욥기", "시": "시편", "잠": "잠언",
    "전": "전도서", "아": "아가", "사": "이사야", "렘": "예레미야", "애": "예레미야애가",
    "겔": "에스겔", "단": "다니엘", "호": "호세아", "욜": "요엘", "암": "아모스",
    "옵": "오바댜", "욘": "요나", "미": "미가", "나": "나훔", "합": "하박국",
    "습": "스바냐", "학": "학개", "슥": "스가랴", "말": "말라기",
    # 신약 (New Testament 27)
    "마": "마태복음", "막": "마가복음", "눅": "누가복음", "요": "요한복음", "행": "사도행전",
    "롬": "로마서", "고전": "고린도전서", "고후": "고린도후서", "갈": "갈라디아서", "엡": "에베소서",
    "빌": "빌립보서", "골": "골로새서", "살전": "데살로니가전서", "살후": "데살로니가후서",
    "딤전": "디모데전서", "딤후": "디모데후서", "딛": "디도서", "몬": "빌레몬서", "히": "히브리서",
    "약": "야고보서", "벧전": "베드로전서", "벧후": "베드로후서", "요일": "요한일서", "요이": "요한이서",
    "요삼": "요한삼서", "유": "유다서", "계": "요한계시록"
}

# Unit symbols mapping
_UNIT_MAP: Dict[str, str] = {
    "%": " 퍼센트", "km": " 킬로미터", "m": " 미터", "cm": " 센티미터", "mm": " 밀리미터",
    "kg": " 킬로그램", "g": " 그램", "mg": " 밀리그램", "L": " 리터", "ml": " 밀리리터",
    "℃": " 도", "°C": " 도", "°": " 도", "배": " 배", "초": " 초", "분": " 분",
    "시간": " 시간", "원": " 원", "달러": " 달러", "엔": " 엔", "유로": " 유로"
}


def num_to_sino(num: int) -> str:
    """Convert an integer to Sino-Korean (e.g. 2026 -> 이천이십육)."""
    if num == 0:
        return "영"
    if num < 0:
        return "마이너스 " + num_to_sino(-num)

    result = []
    big_unit_idx = 0

    while num > 0:
        chunk = num % 10000
        if chunk > 0:
            chunk_str = []
            for i in range(4):
                digit = (chunk // (10 ** i)) % 10
                if digit > 0:
                    unit_char = _SINO_UNITS[i]
                    digit_char = _SINO_DIGITS[digit]
                    # In Korean, 10 is '십', not '일십'; 100 is '백', not '일백'
                    if digit == 1 and i > 0:
                        chunk_str.append(unit_char)
                    else:
                        chunk_str.append(digit_char + unit_char)
            chunk_text = "".join(reversed(chunk_str))
            big_unit = _SINO_BIG_UNITS[big_unit_idx]
            result.append(chunk_text + big_unit)
        num //= 10000
        big_unit_idx += 1

    return "".join(reversed(result))


def num_to_native(num: int, is_classifier: bool = True) -> str:
    """Convert small integers (1-99) to Native Korean (e.g. 3 -> 세 or 셋)."""
    if num <= 0 or num >= 100:
        return num_to_sino(num)

    tens = num // 10
    ones = num % 10

    tens_str = ""
    if tens > 0:
        if is_classifier and ones == 0 and tens == 2:
            tens_str = "스무"
        else:
            tens_str = _NATIVE_TENS[tens]

    if ones > 0:
        ones_str = _NATIVE_1_TO_9[ones] if is_classifier else _NATIVE_1_TO_9_STANDALONE[ones]
        return tens_str + ones_str
    return tens_str


def normalize_bible_verses(text: str) -> str:
    """Normalize Bible citations like '창 4:1-3' -> '창세기 사장 일절에서 삼절'."""
    # Pattern for book abbreviation or full name + chapter:verse (e.g. 창 4:1, 창세기 4:1-3)
    books_pattern = "|".join(re.escape(k) for k in sorted(BIBLE_BOOKS.keys(), key=lambda x: -len(x)))
    pattern = rf"(?:\b|(?<=[\s(]))({books_pattern})\s*(\d+)장?\s*:\s*(\d+)(?:-(\d+))?"

    def repl(m: re.Match) -> str:
        book_raw = m.group(1)
        ch_num = int(m.group(2))
        v_start = int(m.group(3))
        v_end = int(m.group(4)) if m.group(4) else None

        book_full = BIBLE_BOOKS.get(book_raw, book_raw)
        ch_str = num_to_sino(ch_num) + "장"
        v_start_str = num_to_sino(v_start) + "절"

        if v_end:
            v_end_str = num_to_sino(v_end) + "절"
            return f"{book_full} {ch_str} {v_start_str}에서 {v_end_str}"
        return f"{book_full} {ch_str} {v_start_str}"

    text = re.sub(pattern, repl, text)

    # Hymns: 통 115장 / 새 115장 / 찬송가 115장
    def hymn_repl(m: re.Match) -> str:
        prefix = m.group(1)
        num = int(m.group(2))
        full_prefix = "통일 찬송가 " if "통" in prefix else ("새찬송가 " if "새" in prefix else "찬송가 ")
        return f"{full_prefix}{num_to_sino(num)}장"

    text = re.sub(r"(통일\s*찬송가|통|새찬송가|새|찬송가)\s*(\d+)장", hymn_repl, text)
    return text


def normalize_dates_and_times(text: str) -> str:
    """Normalize dates (2026년 9월 9일) and times (3시 30분)."""
    # Years
    text = re.sub(r"(\d{1,4})년", lambda m: f"{num_to_sino(int(m.group(1)))}년", text)

    # Months with Korean phonetic rules (6월 -> 유월, 10월 -> 시월)
    def month_repl(m: re.Match) -> str:
        m_num = int(m.group(1))
        if m_num == 6:
            return "유월"
        if m_num == 10:
            return "시월"
        return f"{num_to_sino(m_num)}월"

    text = re.sub(r"(\d{1,2})월", month_repl, text)

    # Days
    text = re.sub(r"(\d{1,2})일", lambda m: f"{num_to_sino(int(m.group(1)))}일", text)

    # Time: Hour (native) + Minute (sino) + Second (sino)
    def time_repl(m: re.Match) -> str:
        h = int(m.group(1))
        mins = int(m.group(2))
        sec = int(m.group(3)) if m.group(3) else None
        h_str = num_to_native(h, is_classifier=True) + "시"
        min_str = f" {num_to_sino(mins)}분"
        sec_str = f" {num_to_sino(sec)}초" if sec is not None else ""
        return f"{h_str}{min_str}{sec_str}"

    text = re.sub(r"(\d{1,2})시\s*(\d{1,2})분(?:\s*(\d{1,2})초)?", time_repl, text)
    return text


def normalize_units_and_currencies(text: str) -> str:
    """Normalize currencies and technical units."""
    # Currencies with commas (e.g. 50,000원 -> 오만 원)
    def curr_repl(m: re.Match) -> str:
        raw_num = m.group(1).replace(",", "")
        curr = m.group(2)
        return f"{num_to_sino(int(raw_num))} {curr}"

    text = re.sub(r"(\d[\d,]*)\s*(원|달러|엔|유로|위안)", curr_repl, text)

    # Percentage
    text = re.sub(r"(\d+(?:\.\d+)?)\s*%", lambda m: f"{num_to_sino(int(float(m.group(1))))} 퍼센트", text)

    # Common units (km, m, cm, kg...)
    for unit_sym, unit_ko in _UNIT_MAP.items():
        if unit_sym in ("원", "달러", "엔", "유로", "%"):
            continue
        if unit_sym.isalnum():
            pat = rf"(\d+)\s*{re.escape(unit_sym)}\b"
        else:
            pat = rf"(\d+)\s*{re.escape(unit_sym)}"
        text = re.sub(pat, lambda m, u=unit_ko: f"{num_to_sino(int(m.group(1)))}{u}", text)

    return text


def normalize_classifiers(text: str) -> str:
    """Normalize numbers followed by native counting classifiers (e.g. 3개 -> 세 개)."""
    classifier_pat = "|".join(re.escape(c) for c in _NATIVE_CLASSIFIERS)
    pat = rf"(\d+)\s*({classifier_pat})(?=[은는이가을를과의와에로서로도만뿐까지부터\s.,!?]|$)"

    def repl(m: re.Match) -> str:
        num = int(m.group(1))
        cls = m.group(2)
        if 1 <= num <= 99:
            return f"{num_to_native(num, is_classifier=True)} {cls}"
        return f"{num_to_sino(num)} {cls}"

    return re.sub(pat, repl, text)


def normalize_remaining_numbers(text: str) -> str:
    """Convert any standalone remaining digits to Sino-Korean."""
    return re.sub(r"\b\d+\b", lambda m: num_to_sino(int(m.group(0))), text)


def normalize_korean_text(text: str) -> str:
    """
    Full normalization pipeline:
    Bible citations -> Dates & Times -> Currencies & Units -> Native Classifiers -> Remaining Numbers.
    """
    if not text:
        return text

    t = normalize_bible_verses(text)
    t = normalize_dates_and_times(t)
    t = normalize_units_and_currencies(t)
    t = normalize_classifiers(t)
    t = normalize_remaining_numbers(t)

    # Clean multiple spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


if __name__ == "__main__":
    test_cases = [
        "창 4:1-3 말씀에 아벨은 양 치는 자였고",
        "통 115장 기쁘다 구주 오셨네를 찬양합시다",
        "2026년 6월 15일 3시 30분에 만납시다",
        "사과 3개와 책 5권을 35,000원에 구입했습니다",
        "현재 온도는 25℃이며 습도는 60%입니다",
        "마 5:3 심령이 가난한 자는 복이 있나니",
    ]
    for tc in test_cases:
        print(f"RAW : {tc}")
        print(f"NORM: {normalize_korean_text(tc)}\n")
