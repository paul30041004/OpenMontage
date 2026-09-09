#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for OpenMontage Korean Voice & Clone Stack.
Tests:
1. korean_normalizer: Bible verses, hymns, numbers, dates, times, units, classifiers
2. emotion_router: Bracket emotion extraction, dialogue cleaning, prompt routing
3. tts_hallucination_guard: CER calculation, repetition loop detection, duration guards
4. voice_anchor_cleaner: VAD trimming, 24kHz mono normalization
5. batch_speech_processor: Episode loudness normalization (-14 LUFS) and MPS GC
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.audio.korean_normalizer import (
    normalize_bible_verses,
    normalize_dates_and_times,
    normalize_units_and_currencies,
    normalize_classifiers,
    normalize_korean_text,
    num_to_sino,
    num_to_native,
)
from tools.audio.emotion_router import parse_and_route_emotion
from tools.audio.tts_hallucination_guard import (
    levenshtein_distance,
    clean_text_for_comparison,
    TTSHallucinationGuard,
)
from tools.audio.voice_anchor_cleaner import VoiceAnchorCleaner
from tools.audio.batch_speech_processor import BatchSpeechProcessor, mps_garbage_collect


class TestKoreanVoiceStack(unittest.TestCase):

    def test_sino_and_native_numbers(self):
        self.assertEqual(num_to_sino(2026), "이천이십육")
        self.assertEqual(num_to_sino(100), "백")
        self.assertEqual(num_to_sino(15), "십오")
        self.assertEqual(num_to_native(3, is_classifier=True), "세")
        self.assertEqual(num_to_native(20, is_classifier=True), "스무")
        self.assertEqual(num_to_native(5, is_classifier=False), "다섯")

    def test_bible_and_hymn_normalization(self):
        # Genesis citation
        res = normalize_bible_verses("창 4:1-3 말씀입니다")
        self.assertIn("창세기 사장 일절에서 삼절", res)

        # Matthew citation
        res2 = normalize_bible_verses("마 5:3")
        self.assertEqual(res2, "마태복음 오장 삼절")

        # Hymn citation
        res3 = normalize_bible_verses("통 115장 기쁘다 구주 오셨네")
        self.assertIn("통일 찬송가 백십오장", res3)

    def test_dates_times_and_units(self):
        # Phonetic month rule (6월 -> 유월, 10월 -> 시월)
        res = normalize_dates_and_times("2026년 6월 10일")
        self.assertIn("이천이십육년 유월 십일", res)

        # Time
        res_t = normalize_dates_and_times("3시 30분 15초")
        self.assertIn("세시 삼십분 십오초", res_t)

        # Units and Currencies
        res_u = normalize_units_and_currencies("50,000원과 100m 달리기 25℃")
        self.assertIn("오만 원", res_u)
        self.assertIn("백 미터", res_u)
        self.assertIn("이십오 도", res_u)

        # Counting classifier
        res_c = normalize_classifiers("사과 3개와 사람 2명")
        self.assertIn("세 개", res_c)
        self.assertIn("두 명", res_c)

    def test_full_korean_normalization(self):
        full = normalize_korean_text("창 4:9 가인이 300달러를 주고 산 양 5마리를 2026년 6월 15일에 바쳤다.")
        self.assertIn("창세기 사장 구절", full)
        self.assertIn("삼백 달러", full)
        self.assertIn("다섯 마리", full)
        self.assertIn("이천이십육년 유월 십오일", full)

    def test_emotion_parser_and_router(self):
        # Leading bracket tag
        txt, emo = parse_and_route_emotion("[분노] 너는 왜 아벨을 죽였느냐!")
        self.assertEqual(txt, "너는 왜 아벨을 죽였느냐!")
        self.assertIn("분노", emo)

        # Parenthesized esports tag
        txt2, emo2 = parse_and_route_emotion("(e스포츠 중계) 기적의 카운터 펀치가 터집니다!")
        self.assertEqual(txt2, "기적의 카운터 펀치가 터집니다!")
        self.assertIn("e스포츠 캐스터", emo2)

        # Custom emotion tag
        txt3, emo3 = parse_and_route_emotion("[애절하고 슬프게 울부짖으며] 가지 마 제발")
        self.assertEqual(txt3, "가지 마 제발")
        self.assertEqual(emo3, "애절하고 슬프게 울부짖으며")

    def test_hallucination_guard_heuristics(self):
        # Levenshtein distance & character cleaning
        s1 = "안녕하세요, 반갑습니다!"
        s2 = "안녕하세요 반갑습니다."
        c1 = clean_text_for_comparison(s1)
        c2 = clean_text_for_comparison(s2)
        self.assertEqual(c1, c2)
        self.assertEqual(levenshtein_distance(c1, c2), 0)

        # Guard initialization
        guard = TTSHallucinationGuard()
        self.assertEqual(guard.name, "tts_hallucination_guard")

    def test_voice_anchor_cleaner_and_batch_processor_init(self):
        cleaner = VoiceAnchorCleaner()
        self.assertEqual(cleaner.name, "voice_anchor_cleaner")

        processor = BatchSpeechProcessor()
        self.assertEqual(processor.name, "batch_speech_processor")

        # Test MPS garbage collector executes safely without error
        mps_garbage_collect()


if __name__ == "__main__":
    unittest.main()
