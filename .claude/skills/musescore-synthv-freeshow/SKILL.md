---
name: musescore-synthv-freeshow
description: 3-Way media bridge and synchronization between MuseScore (.musicxml), Synthesizer V Pro (.svp), and FreeShow (.json). Converts score pitch, duration, and lyrics to Synth V singing notes and FreeShow subtitle slides, with reverse lyric traceback. Use when working with sheet music, vocal synthesis, or church presentation subtitles.
---

# MuseScore ⇄ Synthesizer V Pro ⇄ FreeShow 3-Way Media Bridge

맥북(Apple Silicon M-series/M3 Max) 환경에서 MuseScore(악보), Synthesizer V Pro(보컬 AI 음원), FreeShow(자막 방송 소프트웨어)를 삼각 연동하여, **악보를 작성하면 보컬 가이드 트랙과 방송용 자막이 동시 생성**되고, **자막을 수정하면 악보 가사가 자동으로 역추적 업데이트**되는 3-Way 상호 변환 파이프라인 스킬입니다.

---

## 1. 아키텍처 및 파이프라인 흐름도

```
                 ┌─── [1. MuseScore (.musicxml)] ───┐
                 │                                  │
                 ▼ (음정/음길이/가사 추출)          ▼ (가사/타임스탬프 추출)
[2. Synthesizer V Pro (.svp)] ◄──────────────► [3. FreeShow (.json)]
               (보컬 노트 및 가사 양방향 동기화)
```

| 포맷 | 포맷 구조 | 주요 역할 | 핵심 데이터 필드 |
| :--- | :--- | :--- | :--- |
| **MuseScore** (`.musicxml` / `.mxl`) | XML / 압축 ZIP 구조 | 멜로디 및 원본 악보 원천 (현악4중주/합창단 등 다중 파트 자동 감지) | `<pitch>` (`step`, `octave`, `alter`), `<duration>`, `<lyric><text>` |
| **Synthesizer V Pro** (`.svp`) | JSON 구조 (v153) | AI 보컬 가창 가이드 합성 | `tracks[0].mainGroup.notes` (`onset`, `duration`, `pitch`, `lyrics`) |
| **FreeShow** (`.json`) | JSON 구조 | 예배/방송 스트리밍 자막 | `slides` (`lines`, `text`, `time_start_ms`, `time_end_ms`, `items`) |

---

## 2. 각 포맷별 데이터 사양 및 수식 체계

### 2.1. 음고(Pitch) ↔ MIDI 번호 변환 공식
- **MusicXML → MIDI (0 ~ 127)**:
  - 음계 기본 반음 오프셋: $C=0, D=2, E=4, F=5, G=7, A=9, B=11$
  - 수식: $\text{MIDI Pitch} = (\text{Octave} + 1) \times 12 + \text{BaseOffset}(\text{Step}) + \text{Alter}$
  - 예시: $C4 = (4+1)\times 12 + 0 + 0 = 60$, $A4 = (4+1)\times 12 + 9 + 0 = 69$, $F^\sharp 4 = (4+1)\times 12 + 5 + 1 = 66$
- **MIDI → MusicXML (역변환)**:
  - $\text{Octave} = (\text{MIDI Pitch} // 12) - 1$
  - $\text{Semitone} = \text{MIDI Pitch} \% 12$
  - $\text{Semitone}$에 따라 Step과 Alter($\pm 1$) 매핑

### 2.2. 압축 악보(.mxl) 및 다중 파트(현악4중주 등) 처리
- **`.mxl` 압축 포맷 자동 지원**: 내부의 `META-INF/container.xml` 및 루트 XML을 자동 압축 해제 파싱합니다.
- **다중 파트(앙상블/합창) 자동 감지**: 현악4중주(바이올린1, 바이올린2, 비올라, 첼로) 등의 다중 악기 악보에서 가사가 있는 보컬 파트 또는 제1바이올린/소프라노(P1) 멜로디를 자동 선별하며, `--part` 옵션으로 파트를 지정할 수 있습니다.
- **외부 찬양/설교 가사 매핑 (`--lyrics-file` / `--lyrics`)**: 현악4중주처럼 악보 자체에 가사가 없는 기악 편곡 악보라도, 텍스트 가사 파일을 지정하면 멜로디 음표에 한글 음절 단위로 자동 싱크 매핑됩니다.

### 2.3. 시간 및 틱(Tick / Blick) 단위 보정
- **Synthesizer V Pro의 시간 단위는 Blick**:
  - $1\text{ Beat (4분음표, 4/4박)} = 705,600,000 \text{ Blicks}$
  - MusicXML의 `<divisions>`(4분음표 당 분할 단위)로부터 Blick 환산:
    $$\text{duration\_blicks} = \text{round}\left( \frac{\text{note\_duration}}{\text{divisions}} \times 705,600,000 \right)$$
  - 쉼표(`<rest/>`): 보컬 노트는 생성하지 않되, 타임라인 커서(`onset`)를 전진시켜 싱크 포지션을 엄격하게 일치시킵니다.

### 2.4. FreeShow 스마트 래퍼 (2구절 묶음)
- Synthesizer V 또는 MusicXML에서 음절 단위로 쪼개진 가사 중 무효 토큰(`-`, 공백)을 필터링합니다.
- 다음 조건에서 한 구절(Phrase)의 끝으로 판별합니다:
  1. 음절 뒤 구두점(`,`, `.`, `!`, `?`)
  2. 음표 간 쉼표 갭(휴지기 $\ge 600\text{ms}$ 또는 1박자 이상)
  3. 한 행당 음절 수 임계치 초과(12~14음절)
- 구절들을 **슬라이드 1장당 2행(2구절)** 씩 묶어 가독성 높은 방송용 자막 레이아웃을 생성합니다.

---

## 3. 핵심 자동화 스크립트 (`media_converter.py`)

스크립트 위치: `scripts/media_converter.py` (또는 본 스킬의 `scripts/media_converter.py`)

### 3.1. CLI 명령어 레퍼런스

```bash
# 1. 악보(MusicXML 또는 .mxl 압축본) ➡️ Synthesizer V Pro (.svp) 변환
python scripts/media_converter.py xml2svp input.mxl vocal.svp --bpm 100

# 1-1. 현악4중주 등 기악 악보에 외부 가사 텍스트 파일 매핑
python scripts/media_converter.py xml2svp input.mxl vocal.svp --bpm 100 --lyrics-file lyrics.txt --part P1

# 2. Synthesizer V Pro (.svp) ➡️ 악보(MusicXML) 변환
python scripts/media_converter.py svp2xml vocal.svp score.musicxml

# 3. 악보(MusicXML / .mxl) ➡️ FreeShow 자막(.json) 변환 (슬라이드당 2구절)
python scripts/media_converter.py xml2fs input.mxl subtitles.json --lines-per-slide 2

# 4. Synthesizer V Pro (.svp) ➡️ FreeShow 자막(.json) 변환
python scripts/media_converter.py svp2fs vocal.svp subtitles.json --lines-per-slide 2

# 5. FreeShow 자막 수정 시 ➡️ 악보(MusicXML) 가사 역추적 업데이트
python scripts/media_converter.py fs2xml edited_subtitles.json original_score.musicxml updated_score.musicxml

# 6. FreeShow 자막 수정 시 ➡️ Synthesizer V Pro (.svp) 가사 역추적 업데이트
python scripts/media_converter.py fs2svp edited_subtitles.json original_vocal.svp updated_vocal.svp

# 7. 원클릭 동반 브리지 (One-Source Multi-Output)
python scripts/media_converter.py bridge praise_score.mxl --outdir ./output --lyrics-file lyrics.txt
```

---

## 4. Python API 사용법

파이썬 코드 내에서 직접 라이브러리로 임포트하여 파이프라인에 통합할 수 있습니다.

```python
from scripts.media_converter import MediaConverter

converter = MediaConverter(default_bpm=120.0, default_meter=(4, 4))

# 1. 악보를 SVP 보컬 트랙으로 변환
converter.musicxml_to_svp("my_score.musicxml", "vocal_track.svp", bpm=105.0)

# 2. 악보를 2구절 레이아웃의 FreeShow 자막으로 변환
converter.musicxml_to_freeshow("my_score.musicxml", "slides.json", lines_per_slide=2)

# 3. 자막 수정본을 원본 악보에 역추적 반영
converter.freeshow_to_musicxml("edited_slides.json", "my_score.musicxml", "my_score_v2.musicxml")
```

---

## 5. Cursor / Windsurf 프롬프트 가이드

Cursor나 Windsurf에서 이 브리지를 기반으로 추가 기능을 확장할 때 사용할 수 있는 프롬프트 템플릿입니다:

```text
우리는 맥북 M3 Max 환경에서 동작하는 3-Way 미디어 상호 변환 툴(media_converter.py)을 운영하고 있어.
MuseScore(.musicxml) <-> Synthesizer V Pro(.svp) <-> FreeShow(.json) 간 데이터 흐름을 기반으로:
1. MuseScore의 음정(Step, Octave, Alter)과 음길이(Divisions)를 SynthV의 705600000 Blick 단위로 매핑하고 가사는 '-'를 필터링해.
2. FreeShow 변환 시 음표 간 쉼표(Rest) 타이밍 갭을 감지하여 2구절 단위로 슬라이드를 스마트 패키징해.
3. FreeShow 자막 텍스트 수정 시, 기존 MusicXML 템플릿의 멜로디 음정과 박자는 100% 보존하면서 <text> 노드만 정확히 덮어쓰도록 처리해.
모든 파일 입출력은 utf-8을 강제하고 한국어 인코딩 깨짐을 방지해.
```
