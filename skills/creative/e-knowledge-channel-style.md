# E-Knowledge Channel Style Video Production Skill

> Complete blueprint for producing **e지식채널 (EBS 지식채널e) 스타일**의 고품격 지식·교양·인문 영상 — 타이포그래피 중심의 조판 슬라이드, 타이핑 애니메이션, 키네틱 타이포, 에디토리얼 레이아웃을 활용한 감성 지식 콘텐츠.

---

## 1. e지식채널 스타일의 핵심 미학

e지식채널은 **"글자(타이포그래피)가 곧 영상"** 인 대표적인 지식 콘텐츠 포맷입니다. 화려한 실사 영상보다 **정제된 조판(Typesetting)과 타이핑/키네틱 텍스트 애니메이션**으로 지식의 무게감과 감동을 전달합니다.

```
┌──────────────────────────────────────────────────────────────┐
│              e지식채널 스타일 디자인 원칙                     │
├──────────────────────────────────────────────────────────────┤
│  1. 여백(Whitespace)의 미학 — 텍스트가 숨 쉴 공간 확보        │
│  2. 세리프(Serif) 헤드라인 + 산세리프(Sans) 본문 대비         │
│  3. 타이핑 애니메이션 — 글자가 한 자씩 등장하며 몰입 유도     │
│  4. 키네틱 타이포 — 단어 단위 스프링 팝인으로 리듬감 부여     │
│  5. 에디토리얼 조판 — 잡지/신문 레이아웃의 격조 있는 구성     │
│  6. 절제된 컬러 — 1~2개 포인트 컬러 + 중성 배경               │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. 전용 타이포그래피 컴포넌트 라이브러리

OpenMontage Remotion 엔진에 e지식채널 스타일을 위한 **4종의 전용 타이포그래피 컴포넌트**를 새로 구축했습니다.

| 컴포넌트 | `cut.type` | 핵심 연출 | 활용 예시 |
|---|---|---|---|
| **`TypewriterText`** | `typewriter` | 글자가 한 자씩 타이핑되며 깜빡이는 커서 | 인용문, 명언, 핵심 문장 강조 |
| **`KineticTypography`** | `kinetic_type` | 단어 단위 스프링 팝인 + 하이라이트 | 주제어, 키워드, 슬로건 |
| **`EditorialSlide`** | `editorial_slide` | 세리프 헤드라인 + 룰 라인 + 잡지형 조판 | 챕터 오프닝, 개념 정의 |
| **`WordPopCaption`** | `word_pop_caption` | 활성 단어 스케일 팝 + 글로우 | 나레이션 싱크 자막 |

---

## 3. e지식채널 스타일 씬 스키마 예시

### 3.1 타이핑 애니메이션 (명언/핵심 문장)
```json
{
  "id": "cut_01",
  "type": "typewriter",
  "text": "우리는 모두 별의 먼지로 만들어졌다.",
  "title": "CARL SAGAN",
  "subtitle": "코스모스, 1980",
  "charsPerSecond": 12,
  "cursorColor": "#FACC15",
  "align": "center",
  "in_seconds": 0,
  "out_seconds": 12
}
```

### 3.2 키네틱 타이포 (주제어 강조)
```json
{
  "id": "cut_02",
  "type": "kinetic_type",
  "title": "CHAPTER 01",
  "lines": [
    "우주는 왜",
    "이토록 정밀하게",
    "설계되었는가"
  ],
  "highlightWords": ["정밀하게", "설계"],
  "staggerFrames": 6,
  "align": "center",
  "in_seconds": 12,
  "out_seconds": 24
}
```

### 3.3 에디토리얼 조판 슬라이드 (개념 정의)
```json
{
  "id": "cut_03",
  "type": "editorial_slide",
  "kicker": "CONCEPT",
  "headline": "미세조정 우주",
  "body": "우주의 물리 상수가 생명체 존재를 위해 극도로 정밀하게 맞춰져 있다는 현대 우주론의 발견.",
  "footnote": "출처: Cambridge Physics Review",
  "layout": "magazine",
  "headlineFont": "Playfair Display",
  "bodyFont": "Inter",
  "in_seconds": 24,
  "out_seconds": 40
}
```

### 3.4 워드 팝 자막 (나레이션 싱크)
```json
{
  "id": "cut_04",
  "type": "word_pop_caption",
  "words": [
    { "word": "우주는", "startMs": 0, "endMs": 400 },
    { "word": "우연이", "startMs": 400, "endMs": 800 },
    { "word": "아닙니다", "startMs": 800, "endMs": 1400 }
  ],
  "maxWordsPerLine": 4,
  "highlightColor": "#FACC15",
  "in_seconds": 40,
  "out_seconds": 50
}
```

---

## 4. e지식채널 스타일 제작 워크플로우

### Phase 1: 지식 구조화 (스크립트)
* **핵심 메시지 1개** + **지지 근거 3개** 구조로 압축.
* 문장은 짧고 선언적으로 — 한 문장 20자 내외.
* 명언/인용문은 `typewriter` 씬으로 분리해 몰입감 극대화.

### Phase 2: 타이포그래피 조판 설계
* **헤드라인:** Playfair Display / Noto Serif KR (세리프, 격조)
* **본문:** Inter / Pretendard (산세리프, 가독성)
* **포인트 컬러:** 1개만 사용 (예: 골드 `#FACC15`, 크림슨 `#C0392B`)
* **배경:** 중성 톤 (아이보리 `#F5F1E8`, 딥 네이비 `#0F172A`)

### Phase 3: 애니메이션 리듬
* 타이핑 속도: **10~15자/초** (지식 콘텐츠는 여유 있게)
* 키네틱 스태거: **5~8프레임** 간격
* 씬 전환: 페이드/디졸브 (0.5~1.0초) — 급격한 컷 지양

### Phase 4: 나레이션 & 사운드
* **VoxCPM2** 감정연기 나레이션 (차분하고 묵직한 톤)
* **EdgeTTS** `ko-KR-InJoonNeural` (신뢰감 있는 지식 전달)
* BGM: 잔잔한 피아노/현악기 (Pixabay `"ambient piano documentary"`)

---

## 5. e지식채널 스타일 품질 체크리스트

- [ ] 헤드라인은 세리프, 본문은 산세리프로 대비되는가?
- [ ] 타이핑 애니메이션 속도가 읽기 편한가 (10~15자/초)?
- [ ] 포인트 컬러가 1~2개로 절제되어 있는가?
- [ ] 여백이 충분히 확보되어 텍스트가 숨 쉬는가?
- [ ] 키네틱 타이포의 하이라이트 단어가 핵심 메시지와 일치하는가?
- [ ] 나레이션과 워드 팝 자막이 정확히 싱크되는가?
- [ ] 씬 전환이 급격하지 않고 지식 콘텐츠의 무게감을 유지하는가?
