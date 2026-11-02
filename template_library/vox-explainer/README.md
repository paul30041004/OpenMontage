# vox-explainer — 텍스트만 바꿔서 영상 만드는 템플릿 (LLM 불필요)

코드로만 그리는 다큐형 정보 영상 템플릿. **글자만 바꾸면** 새 영상이 나옵니다.
LLM 없이 `content.json` 텍스트 수정 → 명령 한 줄로 MP4 완성.

## 빠른 시작

```bash
cd template_library/vox-explainer
# 1) content.json 안의 글자만 수정
# 2) 빌드
./build.sh                 # -> out/final.mp4
```

다른 콘텐츠 파일을 쓰려면:

```bash
./build.sh content.en.json          # 영어 예시
TTS=none   ./build.sh               # 나레이션 없이 (화면 + 배경음만)
TTS=edge   ./build.sh               # 무료·빠른 TTS (VoxCPM 대신)
SCORE=false ./build.sh              # 배경음 없이
```

## 무엇을 바꾸면 되나

**`content.json` 하나만** 편집합니다. 폴더 안의 다른 파일(`engine.js`, `render.mjs`,
`build_audio.py`)은 건드리지 않아도 됩니다.

- `meta.corner` — 우측 상단 작은 워터마크 텍스트
- `meta.palette` — 색 5개(빨강/크림/종이/남색/노랑). 바꾸면 전체 색이 바뀜
- `meta.sans` / `meta.mono` — 폰트 스택 (한글은 시스템 폰트로 자동 폴백)
- `audio.*` — 나레이션/배경음 설정 (아래 참고)
- `shots[]` — **본문. 컷 하나 = 객체 하나.** `type`에 따라 필드가 다름

### 컷 타입 레퍼런스

| type | 용도 | 필드 |
|---|---|---|
| `kinetic` | 큰 타이포 문장 | `lines:[{text,color,size,y,at}]`, `card:true`로 종이카드 배경 |
| `counter` | 숫자 카운트업 | `value,dec,suffix,size,title,caption:[...],captionsAt:[...],source` |
| `grid` | 아이콘 그리드(키 등) | `cols,rows,icon:"key",caption:[...],source` |
| `code` | 코드 카드 + 마커 | `code:[{text,color}],marker:{x,y,r},caption` |
| `beforeafter` | 날짜 전/후 | `title,left,right,caption,sub,source` |
| `cards` | 좌/우 카드 대비 | `title,left:{lines},right:{lines},caption` |
| `headline` | 브랜드 + 헤드라인 + 날짜칩 | `brand,sub,chip,bottom,source` |
| `badge` | 카운터 + 배지 | `title,value,sub,badge:{value,label},source` |

- `color` 값: 팔레트 키(`"red"`,`"navy"`,`"cream"`,`"yellow"`,"paper") 또는 `"#RRGGBB"`.
- `at` / `captionsAt`: 그 컷이 시작된 뒤 몇 초에 나타날지. `source`: 좌하단 출처칩.
- `dur`: 나레이션이 없을 때 컷 길이(초). 나레이션이 있으면 음성 길이로 자동 재계산됨.

### 오디오 설정 (`content.json`의 `audio`)

```json
"audio": {
  "tts": "voxcpm",           // "none" | "edge" | "voxcpm"
  "voice": "ko-KR-InJoonNeural",  // edge 전용
  "rate": "+10%",            // edge 속도
  "voiceDesign": "(calm, authoritative male Korean documentary narrator)",
  "emotion": "차분하고 단호한 톤으로",     // voxcpm 전용
  "atempo": 1.12,            // 음성 후처리 배속 (voxcpm)
  "pad": 0.35,               // 컷당 여유 초
  "lead": 0.15,              // 컷 시작 후 음성 시작 지연
  "score": true              // 배경음 생성
}
```

각 컷에 `"narration": "대사"`를 넣으면 그 컷의 나레이션이 생성되고, 없으면 무음 컷입니다.
VoxCPM은 첫 컷으로 **앵커**를 만들고 나머지를 **클론**해서 목소리를 통일합니다.

## 요구 사항

- `node` (18+), `ffmpeg`, Google Chrome (헤드리스), `python3` + `numpy`
- `edge` TTS: `pip install edge-tts` (무료, 키 불필요)
- `voxcpm` TTS: OpenMontage 로컬 VoxCPM2 모델 (Apple Silicon 권장)

## 구조

```
content.json           ← 이 파일만 수정
engine.js              렌더 엔진 (컷 타입별 그리기)
render.mjs             content.json -> 프레임 -> MP4 (헤드리스 Chrome + ffmpeg)
build_audio.py         나레이션(edge/voxcpm) + 배경음 + 타이밍
build.sh               한 줄 빌드 엔트리
content.english.json   영어 예시
out/                   결과물 (final.mp4, frames/, timing.json, audio.wav)
```
