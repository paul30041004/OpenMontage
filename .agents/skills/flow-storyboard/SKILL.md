---
name: flow-storyboard
description: |
  Advanced visual storyboarding, Google Maps street-view location grounding, character locking,
  3x3 grid generation, and grid-to-video cinematic expansion using Google Flow (with Gemini Omni /
  Veo 3.1 Lite). Use when: (1) Grounding AI backgrounds in real-world Google Maps US street addresses,
  (2) Registering and maintaining consistent characters via Flow's Characters menu, (3) Generating
  3x3 storyboard contact sheet grid images with character & setting continuity, (4) Converting storyboard
  grids into 10-second continuous cinematic video clips, (5) Slicing grid images into sequential keyframes
  and interpolating them to stretch video duration, or (6) Using Flow Agent for multi-turn conversational edits.
---

# flow-storyboard — Google Flow 구글맵 연동, 캐릭터 고정, 3x3 그리드 및 비디오 변환 스킬

Google Flow(https://labs.google/fx/ko/tools/flow)의 최신 기능들을 결합하여,
**구글맵 실제 주소 배경 연동 ➔ 일관성 캐릭터 고정 ➔ 3×3 그리드 스토리보드 생성 ➔ 10초 시네마틱 비디오 변환 ➔ 프레임 보간 확장**을
완성하는 고급 제작 워크플로 스킬.

---

## 5대 핵심 기법

### 1. 구글맵 실제 주소 배경 생성 (Google Maps Grounding)
Google Maps에서 미국 내 실제 거리 주소를 복사해 프롬프트에 넣으면, Flow Agent가 실제 스트리트 뷰의 지형, 건물 외관, 도로 폭, 분위기를 그대로 반영한 사실적인 배경 이미지를 생성합니다.
- **지원 지역**: 현재 미국 스트리트 뷰 위치 지원 (마이애미, 뉴욕, LA 등)
- **프롬프트 팁**: 영어 주소를 그대로 포함하고 주변 날씨·시간대·미학(예: GTA 6 바이스시티 스타일, 골든 아워)을 명시합니다.
  ```
  Street level photograph at 1001 Ocean Dr, Miami Beach, FL 33139, late afternoon golden hour, GTA 6 Vice City aesthetic, neon signs glowing, palm trees, ultra photorealistic
  ```

### 2. 캐릭터 일관성 등록 (Character Locking)
생성하거나 업로드한 실사/카툰 인물 이미지를 Flow의 **Characters** 메뉴에 등록하여, 향후 모든 씬에서 동일한 얼굴, 체형, 성격을 유지합니다.
1. 인물 생성 후 좌측 사이드바 `Characters` (캐릭터) 메뉴 진입
2. `Add from project` 클릭 후 기준 이미지 선택
3. 캐릭터 이름(예: `Jason`), 어울리는 음성, 성격 키워드 입력 후 저장
4. 프롬프트 작성 시 `@Jason` 형태로 호출하여 캐릭터 외모 고정

### 3. 대화형 말로 수정 (Conversational Multi-Turn Editing)
생성된 이미지를 선택한 뒤 프롬프트에 수정 사항을 말로 지시:
- *"표정을 더 긴장한 표정으로 바꿔줘"*
- *"의상을 검은색 후드티로 변경해줘"*
- *"조명을 네온 조명으로 바꾸고 배경 주소를 1428 Brickell Ave, Miami로 교체해줘"*

### 4. 3×3 스토리보드 그리드 이미지 (Storyboard Grid)
캐릭터와 배경을 프롬프트에 첨부하고 3x3 (또는 2x2) 그리드 이미지 생성을 요청하면, Flow가 **한 장 안에 9개의 연속된 영화/게임 미션 컷**을 일관성 있게 구성합니다.
- **프롬프트 템플릿**:
  ```
  A 3x3 storyboard contact sheet grid featuring @Jason at 1001 Ocean Dr, Miami Beach. 9 sequential action panels showing Jason spotting an unmarked car, sprinting through an alley, jumping over a fence, and escaping on a speedboat. Consistent character face and clothing across all panels, cinematic film stills, sharp photorealistic details
  ```

### 5. 그리드 이미지 ➔ 10초 시네마틱 영상 변환 (Grid-to-Video)
완성된 3×3 그리드 이미지와 캐릭터를 프롬프트에 첨부(재료)하고, **캐릭터의 연속된 행동 + 카메라 무빙**을 지시하여 10초 분량의 영화 같은 시네마틱 클립으로 확장합니다.
- 모델 선택:
  - **무료(0크레딧)**: `Veo 3.1 - Lite [Lower Priority]` (8초 720p, x4 일괄 생성)
  - **고품질/유료**: `Omni 1.1 Flash` / `Veo 3.1 Fast` (10초, 프레임 안정성 극대화)
- **프롬프트 공식**:
  ```
  Cinematic 10-second video following @Jason based on the attached storyboard grid. The camera starts with a tight tracking shot as the character starts running, smoothly transitioning into a wide dolly-out revealing the Miami boulevard. Smooth cinematic motion, continuous action, 720p 24fps
  ```

---

## 보조 도구 (Scripts)

스킬 디렉토리(`scripts/`)에 그리드 이미지 분할 및 영상 길이 확장을 위한 유틸리티가 포함되어 있습니다:

### A. 3×3 그리드 이미지 9분할 (`slice_grid.py`)
Flow가 생성한 3×3 그리드 한 장을 9개의 개별 컷 이미지(`frame_01.png` ~ `frame_09.png`)로 자동 크롭합니다.
```bash
python3 .agents/skills/flow-storyboard/scripts/slice_grid.py \
  --input storyboard_grid.png \
  --output ./sliced_frames \
  --rows 3 --cols 3
```

### B. 프레임 간 모션 보간 영상 생성 (`interpolate_frames.py`)
분할된 키프레임들 사이에 FFmpeg의 `minterpolate`(광학 흐름 모션 보정 / 블렌드) 필터를 적용하여, 부드러운 전환과 함께 씬의 길이를 원하는 만큼 늘려 비디오로 렌더링합니다.
```bash
python3 .agents/skills/flow-storyboard/scripts/interpolate_frames.py \
  --input-dir ./sliced_frames \
  --output ./extended_animatic.mp4 \
  --duration-per-frame 2.5 \
  --mode blend
```

---

## 프롬프트 작성 핵심 팁 (비디오 제작자 검증)

1. **영어 프롬프트 권장**: 복잡한 카메라 무빙(dolly-in, tracking shot, pan), 조명(golden hour, volumetric rim lighting), 구글맵 주소 연동 시 한글보다 영어 프롬프트가 모델의 디테일 반응도가 월등히 높습니다 (`prompt_templates.json` 참조).
2. **부정문 금지**: "No cars, don't show text" 대신 "Empty alleyway, clean asphalt"처럼 **있어야 할 요소만 긍정문으로 묘사**합니다.
3. **카메라 무빙 한 줄 명시**: 카메라가 고정인지, 인물을 따라가는 트래킹 샷인지, 줌아웃되는지 반드시 1문장으로 방향을 지정합니다.
