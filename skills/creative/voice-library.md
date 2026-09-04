# 상황별 음성 라이브러리 (Voice Library) — 일관된 롱폼/미드폼 내레이션

> 상황별 anchor 음성 샘플을 미리 생성해두고, 모든 내레이션 세그먼트를
> 그 샘플에서 클론하여 **영상 전체에 걸쳐 일관된 음성**을 만드는 시스템.

---

## 1. 개념

로컬 TTS(VoxCPM2 등)는 호출마다 미세하게 음색이 달라진다(stochastic).
세그먼트를 독립 생성하면 여러 화자가 말하는 것처럼 들린다.

**해결:** 상황별 anchor 샘플을 **한 번만** 생성해 `voice_library/`에 저장하고,
이후 모든 세그먼트를 그 anchor에서 **클론**한다 (tts-sample-unification).

```
voice_library/
├── documentary.wav    (다큐멘터리 내레이션 anchor)
├── news.wav           (뉴스 앵커 anchor)
├── emotional.wav      (감성 위로 anchor)
├── hype.wav           (하이프/에너지 anchor)
├── educational.wav    (교육/설명 anchor)
├── ... 75개 한국 숏폼 보이스 ...
├── voice_library.json     (기본 5개 보이스 메타데이터)
└── voice_library_50.json  (75개 한국 숏폼 보이스 메타데이터)
```

---

## 2. 130개 보이스 (기본 5 + 숏폼 75 + 휴먼 50)

### 기본 5개
documentary, news, emotional, hype, educational

### 숏폼 75개 (15개 카테고리 × 5개)

| 카테고리 | 보이스 (예시) |
|---|---|
| 뉴스/정보 | news_anchor, news_anchor_f, info_quick, info_mystery, info_ranking |
| 코미디/개그 | comedy_over, comedy_deadpan, comedy_tsundere, comedy_ahjussi, comedy_sarcastic |
| 먹방/푸드 | mukbang_excited, mukbang_asmr, food_critic, food_challenge, food_homemade |
| 뷰티/패션 | beauty_trendy, beauty_soft, fashion_ootd, fashion_haul, beauty_review |
| 여행 | travel_vlog, travel_guide, travel_healing, travel_food, travel_tip |
| 게임 | game_hype, game_commentary, game_troll, game_rage, game_chill |
| ASMR/힐링 | asmr_whisper, healing_comfort, meditation, asmr_tapping, healing_nature |
| 리뷰/언박싱 | unboxing_excited, review_honest, review_recommend, review_compare, review_short |
| 스토리/썰 | story_dramatic, story_funny, story_scary, story_heartwarming, story_confession |
| 교육/지식 | edu_teacher, edu_fun, edu_english, edu_history, edu_science |
| 연애/공감 | love_sweet, love_advice, empathy_friend, empathy_consolation, love_tsundere_m |
| 운동/헬스 | fitness_motivation, fitness_guide, fitness_diet, fitness_challenge, fitness_yoga |
| 금융/재테크 | finance_expert, finance_tip, finance_warning, finance_news, finance_beginner |
| 육아/가족 | parenting_tip, parenting_fun, family_warm, kids_story, parenting_advice |
| 반려동물 | pet_cute, pet_tip, pet_funny, pet_healing, pet_training |

### 휴먼 50개 (10개 카테고리 × 5개)

| 카테고리 | 보이스 (예시) |
|---|---|
| 일상 브이로그 | vlog_morning, vlog_daily, vlog_night, vlog_weekend, vlog_cafe |
| 직장인 공감 | office_monday, office_commute, office_lunch, office_overtime, office_boss |
| 학생/수험생 | student_exam, student_study, student_school, student_cram, student_graduate |
| 친구 수다 | friend_gossip, friend_comfort, friend_joke, friend_advice, friend_reunion |
| 연애/썸 | dating_flirt, dating_confession, dating_couple, dating_breakup, dating_jealous |
| 가족/부모 | family_mom, family_dad, family_grandma, family_kids, family_sibling |
| 자취/혼밥 | alone_cooking, alone_dinner, alone_cleaning, alone_lonely, alone_freedom |
| 감성 위로 | comfort_hug, comfort_tears, comfort_encourage, comfort_heal, comfort_night |
| 자학 개그 | selfdeprecating_money, selfdeprecating_diet, selfdeprecating_single, selfdeprecating_age, selfdeprecating_lazy |
| MZ 세대 | mz_trend, mz_slang, mz_reaction, mz_opinion, mz_lifestyle |

전체 목록: `tools/audio/voice_presets_50.py`, `tools/audio/voice_presets_human_50.py`

---

## 3. 사용법

### 3.1 anchor 샘플 생성 (1회)

```bash
# 기본 5개 보이스
PYTHONPATH=. ./.venv/bin/python tools/audio/build_voice_library.py

# 75개 한국 숏폼 보이스
PYTHONPATH=. ./.venv/bin/python tools/audio/build_voice_library.py --50

# 50개 휴먼 보이스
PYTHONPATH=. ./.venv/bin/python tools/audio/build_voice_library.py --human

# 목록 확인
PYTHONPATH=. ./.venv/bin/python tools/audio/build_voice_library.py --list
```

### 3.2 일관된 내레이션 생성 (VoiceLibraryTTS)

```python
from tools.audio.voice_library_tts import VoiceLibraryTTS

tts = VoiceLibraryTTS()

# 코미디 보이스로 클론
tts.execute({
    "text": "이거 진짜 대박이에요!",
    "voice": "comedy_over",   # 75개 중 선택
    "output_path": "assets/audio/seg_01.wav",
})
```

### 3.3 황금가지 파이프라인에서 사용

`golden_bough_video/config.json`:
```json
{
  "tts": {
    "provider": "voice_library",
    "voice": "comedy_over"
  }
}
```

---

## 4. 도구

| 도구 | 모듈 | 역할 |
|---|---|---|
| `build_voice_library` | `tools/audio/build_voice_library.py` | 상황별 anchor 샘플 생성 |
| `voice_library_tts` | `tools/audio/voice_library_tts.py` | anchor 클론 기반 일관 내레이션 |
| `voice_presets_50` | `tools/audio/voice_presets_50.py` | 75개 숏폼 보이스 프리셋 |
| `voice_presets_human_50` | `tools/audio/voice_presets_human_50.py` | 50개 휴먼 보이스 프리셋 |

`voice_library_tts`는 `capability: tts`로 레지스트리에 자동 등록된다.

---

## 5. 규칙 (tts-sample-unification)

1. anchor 샘플은 **한 번만** 생성 (voice_design + emotion)
2. 모든 세그먼트는 anchor를 `reference_audio`로 **클론**
3. `voice_design`/`device`는 anchor와 동일하게 유지, `emotion`/`text`만 장면별로 변경
4. anchor를 중간에 재생성하지 않음 (변경 시 전체 재클론)
5. `voice_design`은 **영어**, 한국어는 `emotion`/`text`에만

---

## 6. 확장

새 보이스 추가: `voice_presets_50.py`의 `VOICE_PRESETS_50`에 항목 추가 후 `--50` 재실행.

