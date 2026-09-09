---
name: flow-shorts
description: |
  Primary free image and video asset generator in OpenMontage using Google Flow via
  Chrome DevTools Protocol (CDP). Zero-credit generation: (1) Free images via Nano
  Banana Pro with anchor reference for unified look (0 credits), (2) Free video clips
  via Veo 3.1 - Lite [Lower Priority] in x4 batches (0 credits, 720p 9:16/16:9), and
  (3) Korean text/dimension/subtitle overlay via Remotion (never generated in model).
  USE PROACTIVELY whenever: (a) the user asks for free images, free videos, or free
  assets ("무료 이미지", "무료 영상", "무료 에셋", "0크레딧 영상", "free assets", "zero-cost clips"),
  (b) no paid API keys are available or the user wants to avoid API costs, (c) generating
  look-consistent asset sets with an anchor image, or (d) reproducing the complete Flow
  engineering shorts pipeline.
---

# flow-shorts — Google Flow 자동화 쇼츠 제작 스킬

Google Flow(https://labs.google/fx/ko/tools/flow)를 **API 없이 브라우저 자동화(CDP)**로
조작해서 공학 쇼츠 한 편을 만드는 전 과정 스킬. 그래픽카드·API 결제 없이,
구독 크레딧(하루 50 ≈ 4초 클립 7개) 안에서 한 편이 완성된다.

**핵심 원칙 (영상 분석에서 나온 그대로):**
> "그림은 생성 모델에 맡기고, 글자는 절대 맡기지 않는다."

## 아키텍처

```
flow.json (설정 하나) ──┬─ run_images.py  → 이미지 N장 (0크레딧, 앵커 참조로 룩 통일)
                        │     └ state.json (재개 가능한 상태 파일)
                        └─ run_clips.py   → 클립 선택분만 (4초=7크레딧, 카드 제목으로 원본 지정)
                              └ clips/*.mp4
Remotion (remotion-composer) → 한글 라벨·수치·자막·화살표·치수선 코드로 합성 (컷당 ~2개)
ffmpeg → 나레이션 + 최종 조립
```

## 준비물

1. **구글 계정** — Flow 접속 (지역에 따라 미개방; 이미지만 뽑으면 계정만 있으면 되고
   영상 클립은 크레딧 필요)
2. **원격 디버깅 크롬** — 자동화 전용. 개인 프로필 크롬을 쓰면 녹화에 개인 화면이
   섞인다(제작자가 실제로 당한 사고). 반드시 별도 포트 + 별도 프로필:

   ```bash
   # macOS — 자동화 전용 크롬 (포트 9222, 프로필 분리)
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=9222 \
     --user-data-dir="$HOME/.flow-automation-chrome-profile"
   ```

   이 크롬에서 Flow에 **한 번만 로그인**하면 된다(세션은 복사 안 됨).
   녹화는 **화면이 아니라 탭**을 찍는다 — 탭 자체를 녹화하면 화면에 뭐가 떠 있든 섞일 수 없다.

3. **Python 3.10+** — 외부 패키지는 `requests` 하나만 사용 (CDP 웹소켓은 표준 라이브러리로
   직접 구현됨). 나레이션/전사는 이 프로젝트의 기존 TTS/STT 스킬 사용.

## flow.json — 설정 파일 하나로 끝

```jsonc
{
  "flow_url": "https://labs.google/fx/ko/tools/flow",
  "aspect_ratio": "9:16",
  "look_prompt": "…모든 이미지에 공통으로 붙는 룩 문장…",
  "images": [
    { "id": "anchor-hero", "anchor": true, "prompt": "…" },   // 앵커는 딱 1장
    { "id": "cut-02", "prompt": "…" },                          // 나머지는 전부 앵커 참조
    …
  ],
  "clips": [
    { "id": "clip-hook", "source_image": "cut-02",
      "prompt": "첫 프레임 그대로 유지하고 아주 느린 카메라 이동" }
  ]
}
```

스키마: `scripts/flow.schema.json` / 예제: `examples/flow.example.json`

**앵커 시스템 (룩 통일의 전부):**
- 앵커 이미지를 **딱 한 장 먼저** 만든다(참조 없음).
- 나머지 이미지를 만들 때마다 그 앵커를 **참조 이미지로 물려서** 생성한다.
- 같은 스튜디오, 같은 조명, 같은 색감으로 찍은 것처럼 나온다.
- 이미지는 0크레딧 → 마음에 안 들면 몇 번이고 다시 뽑는다.

## 실행 — 반드시 두 단계로

```bash
cd .agents/skills/flow-shorts/scripts

# 0. 크롬 디버그 포트 확인
python3 browser_harness.py check            # {"ok": true, "flow_tabs": 1}

# 1. 첫 실행은 limit 1 — 앵커 한 장만 뽑아서 룩을 확인
python3 run_images.py --config flow.json --output ./out --limit 1
#    룩이 안 맞으면 flow.json의 look_prompt를 고치고 다시

# 2. 전체 이미지 (0크레딧). 중간에 끊겨도 state.json에 기록되고 이어서 실행됨
python3 run_images.py --config flow.json --output ./out
#    → out/images/*.png 를 눈으로 전부 확인한 뒤에만 다음 단계

# 3. 클립 (여기서만 크레딧). 컷 수만큼 7크레딧씩 나감
python3 run_clips.py --config flow.json --output ./out
#    → out/clips/*.mp4
```

**이미지 단계와 클립 단계를 나눈 이유:** 이미지는 공짜고 클립은 돈이다.
이미지를 전부 만들어 눈으로 확인하고 마음에 들 때만 클립 단계로 넘어간다.

## 0크레딧 비디오 생성 — Veo 3.1 - Lite [Lower Priority]

**실측 검증 (2026-09):** Flow의 모델 드롭다운에 `Veo 3.1 - Lite [Lower Priority]`가
있으며, 설정 패널에 **"Generating will use 0 credits"** 로 표시된다. 실제 생성도
0크레딧으로 완료됨 (720x1280, 8s, h264+aac mp4 정상 출력).

```bash
python3 run_videos.py --config flow.json --output ./out
#    → out/videos/*.mp4   (0크레딧)
```

**규칙과 특성:**
- 지원 조합: **4s / 6s / 8s**, 9:16/16:9, 배수 **기본 x4** (`--batch x4`, x1~x4 선택 가능).
  0크레딧이므로 4배리언트를 한 번에 생성하여 오프라인에서 최선의 1개를 고른다.
  결과물은 `{id}.mp4`, `{id}-v2.mp4`, `{id}-v3.mp4`, `{id}-v4.mp4`로 모두 다운로드된다.
- **Lower Priority = 유료 요청 뒤로 대기.** 클립당 3~10분 이상 걸리고 특정 퍼센트에서
  몇 분씩 멈춰 있는 게 정상이다. `--timeout 1800` (기본 30분) 안에서 기다린다.
- **크레딧 게이트:** `run_videos.py`는 생성 버튼을 누르기 전에 설정 패널의 크레딧
  문구가 "0 credits"인지 확인한다. 구글이 이 모델을 유료화/제거하면 **크레딧을
  쓰기 전에** 중단하고 스크린샷을 남긴다.
- `videos[].reference_image`에 images[]의 id를 지정하면 해당 이미지를 참조(Ingredients)로
  물어서 룩을 맞춘다.
- 완료 판정: 비디오 요소 수 증가 + 진행률 표시 소멸 (이미지와 달리 비디오는 카드
  제목이 아니라 `<video>` 탐지로 판정).

**크레딧 전략 요약:**

| 작업 | 모델 | 크레딧 |
|---|---|---|
| 이미지 N장 | Image 모드 (Nano Banana Pro 등) | 0 |
| 비디오 4/6/8s | Veo 3.1 - Lite [Lower Priority] | 0 (느림) |
| 비디오 4s 고품질 | Omni 1.1 Flash 등 유료 모델 | 12~24/개 |

→ 급하지 않은 모든 비디오는 Lite [Lower Priority]로 0크레딧 생성하고,
훅 등 꼭 퀄리티가 필요한 컷만 유료 모델(`run_clips.py`)로.

## 최신 실측 노트 (2026-09, flow.google.com)

- 도메인이 `labs.google/fx` → **`flow.google.com`**로 이동했다.
- UI는 Angular Material: 설정 칩(`settings-trigger-button`) → 패널
  (`.settings-content`) → `mat-button-toggle` 토글들 + 모델 드롭다운.
- **JS `.click()`은 Angular 바인딩을 타지 않는 경우가 있다** → 하니스의
  `_mouse_click_center()`는 요소 좌표에 `Input.dispatchMouseEvent`로 실제 마우스
  클릭을 쓴다. 새 요소가 안 눌리면 이 방식으로 통일할 것.
- 프롬프트 입력창은 `.ProseMirror` (contenteditable). `selectAll` → `delete` →
  `execCommand('insertText')` 순서로 입력한다 (placeholder 노드가 textContent에
  섞여 보이는 건 정상).
- 생성 완료 감시: 본문의 `NN%` 진행률 표시가 사라지고 결과 요소(img/video)가
  늘어나면 완료. 이미지 생성은 30~60초, Lite 비디오는 수 분.

## 완료 판정 (가장 깨지지 않는 신호)

생성 완료를 확인하는 방법으로 다음은 전부 실패 사례다:
- ❌ 파일 이름 — Flow 생성물엔 파일 이름이 없음
- ❌ URL 패턴 — 구글이 도메인을 옮기며 깨짐 (실제로 이 영상 제작 중에도 깨졌음)
- ❌ 화면 개수 카운트 — 목록이 가상화되어 실제 개수와 안 맞음

✅ **카드 제목이 하나 늘어나면 완료로 본다.** 이 스킬의 `wait_for_new_card_title()`
구현이 그대로 사용한다. 클립 원본 지정도 목록 순서가 아니라 **카드 제목**으로 한다
(선택한 카드가 맨 앞으로 올라오며 순서가 밀림 — 위치 기반 지정으로 엉뚱한 원본에
7크레딧을 날린 사례 있음).

## 프롬프트 규칙

1. **부정문을 쓰지 마세요.** "글자 넣지 마, 사람 넣지 마"라고 쓰면 오히려 그린다.
   "노텍스트(no text)"를 썼더니 화면에 영어 수치를 큼직하게 그린 사례가 있다.
   없어야 할 것은 **아예 언급하지 않고**, 있어야 할 것만 적는다.
2. **클립 프롬프트는 한 줄이면 충분하다.** "첫 프레임 그대로 유지하고 아주 느린 카메라
   이동 하나" — 그게 다다. 여기서 욕심 내면 화면이 제멋대로 변한다.
3. **클립은 꼭 필요한 자리에만.** 훅 / 첫 컷 / 문제를 몸으로 보여주는 컷 / 실패하는
   장면 / 발상이 뒤집히는 컷 / 마지막 롱샷 — 이 다섯 자리는 움직여야 산다.
   수치를 읽는 컷·치수선이 주인공인 컷은 정지 이미지 + 느린 카메라 움직임으로 충분하다.

## 글자는 Remotion으로 (Flow에게 맡기지 않는다)

한글 라벨·수치·자막·화살표·치수선·그래프는 **전부 Remotion(`remotion-composer/`)으로
코드 합성**한다. 코드로 그리면 틀릴 일이 없고, 고치고 싶으면 글자만 바꿔 다시 렌더하면 된다.
한글을 생성 모델에 맡기면 못할 자 하나 때문에 크레딧을 쓴 영상을 다시 뽑아야 한다.

자막 규칙:
- 항상 **한 줄**. 줄수가 컷마다 바뀌면 자막 덩어리가 위아래로 출렁여 눈이 끊긴다.
- 길면 줄을 바꾸는 게 아니라 **글자 크기를 줄이고**, 그래도 안 되면 **시간으로 쪼갠다**.
- 그래픽은 컷당 두 개쯤 — 쉬나홉 없이 들어가야 산다.

## 대본 규격 (공학 쇼츠 단일 템플릿)

구조: **상식적인 해법이 왜 실패하는지 보여주고, 실제로는 어떻게 푸는지 뒤집는다.**
소재만 갈아끼우는 단일 템플릿이다. (한강=하구를 막는다? → 물속에 낮은 턱. 
난지도=치운다? → 가둔 채로 뽑아낸다.)

**소재 통과 조건 3개 — 하나라도 안 되면 소재를 바꾼다. 타협하면 뒤가 전부 낭비다:**
1. 설명 없이 이름만 돼도 아는 대상일 것 (노안·안경처럼)
2. 상식적인 해법이 실제로 실패여야 함 (이중 초점 → 경계에서 상이 큼, 계단 발밑 어긋남)
3. 진짜 해법이 직관에 반해야 함 (흐림을 없애는 게 아니라 안 보는 쪽으로 몰아냄)

**대본 = 650자 안팎, 8구간 고정 비율:**

| 구간 | 비율 |
|---|---|
| 훅 | 9% |
| 문제 | 15% |
| 1차 해법 | 16% |
| 세 문제(실패) | 15% |
| 반박 선점 | 6% |
| 발상 전환 | 10% |
| 작동 원리 | 14% |
| 클로징 | 15% |

훅이 길어지면 본론이 밀리고, 클로징이 짧아지면 여운이 안 남는다.

**팩트 체크:** 수치는 전부 1차 출처에서. 출처가 없으면 아예 안 쓴다.
근거없는 숫자로 채우면 거짓 밀도가 된다. (렌즈 편이 터널 편보다 수치가 적은 건
소재의 실측값이 적었기 때문 — 억지로 채우지 않았다.)

**대본이 끝나면 곧바로 나레이션부터 만든다.** 장면표를 먼저 짜면 안 된다 —
추정 95초로 잡아놓고 실제 음성이 125초로 나오면 장면표가 통째로 밀린다.

## 함정 7가지 (제작자가 실제로 당한 것)

1. **워터마크** — Flow 이미지/영상엔 우하단 별 모양 AI 표시가 붙는다. 설정에서 끌 수
   있으나 눈에 안 보이는 워터마크는 남는다. 어차피 유튜브 업로드 시 합성 콘텐츠 고지를
   체크해야 하므로 숨길 이유가 없다. 끄지 않는 것을 권장.
2. **자동화 전용 브라우저** — 개인 크롬으로 돌리면 녹화에 개인 화면(챗 대화 목록 등)이
   찍힌다. 화면 녹화는 *화면*을 찍고 자동화는 *탭*을 조작하기 때문. 별도 포트 + 별도
   프로필 크롬을 쓰고, 녹화는 탭을 찍는다.
3. **클론 TTS 검증** — 클론 음성이 레퍼런스 대본을 소리 내어 읽는 사고가 있었다.
   정렬 검사는 통과한다(대본 단어가 전부 들어 있으니까). **독립 전사로 대조**해야만 잡힌다.
   레퍼런스는 5~20초로 짧게, 레퍼런스 대본은 넣지 않는다. 넣으면 그걸 읽는다.
4. **하니스 재시작** — 코드를 고치면 데몬을 반드시 재시작. 데몬이 파이썬 모듈을 기억해서
   옛날 코드가 계속 돈다. 브라우저 주소를 바꿔도 데몬은 이전 브라우저를 물고 안 놓는다.
5. **완료 판정** — 개수/파일명/URL로 세지 마라 (위 "완료 판정" 참조). 카드 제목으로.
6. **크레딧 전 설정 확인** — 새 계정은 기본 출력이 2장이라 한 번 누르면 크레딧이 두 배로
   나간다. `run_clips.py`는 출력 수가 1이 아니면 **크레딧을 쓰기 전에 멈춘다**
   (`--force`로 강제할 수 있지만 권장하지 않음).
7. **언젠가 깨진다** — 화면을 보고 누르는 방식이라 구글이 버튼 하나만 옮겨도 어긋난다.
   실제로 이 스킬 제작 도중 Flow가 주소를 옮겨 여덟 군데가 한꺼번에 깨졌다. 모든 실패
   지점에서 **스크린샷을 자동 저장**하니(`out/screenshots/`) 그 파일을 보고 깨진 셀렉터만
   `scripts/selectors.json`에서 고치면 된다. 셀렉터가 바뀐 여파는 이 문서에 기록해 둔다.

## 크레딧 산수

- 4초 클립 1개 = 7크레딧. 하루 50크레딧 = 클립 7개.
- 영상을 더 넣고 싶으면: 상위 플랜, 이틀에 나눠 만들기, 또는 정지컷 비율 높이기.
- 경험치: 28컷에 클립 7개면 충분히 산다. (이 스킬의 예제 편: 이미지 12장 0크레딧 +
  클립 7개 49크레딧 = 합계 49크레딧)

## 나레이션

이 프로젝트의 기존 TTS 스킬(`.agents/skills/`의 `voxcpm-tts`, `qwen3-tts` 등)을 쓴다.
클론을 쓸 경우: 레퍼런스 5~20초, 레퍼런스 대본 금지, 완성 음성은 **독립 전사로 대본과
대조**해서 검증한다 (함정 3).

## 최종 조립

1. `out/clips/*.mp4` (움직여야 할 컷) + `out/images/*.png` (정지 컷, 느린 카메라 움직임)
2. Remotion(`remotion-composer/`)으로 한글 텍스트/그래픽 합성 — 컷당 그래픽 ~2개,
   자막은 항상 한 줄
3. 나레이션 믹스 → `renders/final.mp4`

## 이 스킬에 없는 것 (솔직 고지)

- 썸네일 제작·업로드 자동화 — 없음
- 단어 하나하나 붙는 카라오케 자막 — 없음 (한 줄 자막만)
- 제작자 목소리 클론 프로필 — 각자 직접 만들어야 함