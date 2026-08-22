# Remotion 오픈소스 컴포넌트 라이브러리 통합 가이드

> 한국 크리에이터들이 가장 많이 쓰고 대박나는 Remotion 관련 오픈소스 라이브러리와 컴포넌트들을 OpenMontage에 통합하는 방법과 사용 가이드.

---

## 1. 통합된 오픈소스 라이브러리

### 1.1 `remotion-bits` (⭐ 444 stars)

**GitHub:** https://github.com/av/remotion-bits
**npm:** `remotion-bits`

Remotion 전용 **84개 ready-made 애니메이션 컴포넌트** 모음. 텍스트 효과, 그라디언트 전환, 파티클 시스템, 3D 씬, 카운터, 타이프라이터 등.

**핵심 컴포넌트:**
- `AnimatedText` — 단어/문자 스태거 + 글리치 텍스트
- `AnimatedCounter` — 숫자 카운트업 (키프레임 + hold 지원)
- `TypeWriter` — 타이핑 + 오타 시뮬레이션 + 커서
- `MatrixRain` — 매트릭스 디지털 레인
- `GradientTransition` — Oklch 지각 균일 그라디언트 전환
- `Particles` / `Spawner` / `Behavior` — 파티클 시스템 (반딧불/눈/분수/컨페티)
- `Scene3D` / `Element3D` / `Transform3D` — 3D 씬
- `ScrollingColumns` — 스크롤 컬럼
- `StaggeredMotion` — 스태거 모션

### 1.2 `remotion-animated` (v2.2.0)

**GitHub:** https://github.com/stefanwittwer/remotion-animated
**npm:** `remotion-animated`

선언적(declarative) 방식으로 JSX 안에서 직접 애니메이션을 조합하는 라이브러리. `interpolate` 호출을 줄이고, `Move`/`Scale`/`Rotate`/`Fade`/`Size` 애니메이션을 JSX에 인라인으로 작성.

### 1.3 `@remotion/animation-utils` (공식)

**npm:** `@remotion/animation-utils`

Remotion 공식 애니메이션 유틸리티. `spring`, `interpolate`, `Easing` 등.

---

## 2. OpenMontage 씬 타입 매핑

`remotion-bits` 컴포넌트를 OpenMontage `Explainer` 컴포지션의 `cut.type`으로 노출:

| `cut.type` | 컴포넌트 | 핵심 props |
|---|---|---|
| `matrix_rain` | `MatrixRainScene` | `matrixColor`, `matrixSpeed`, `matrixDensity`, `matrixStreamLength` |
| `animated_counter` | `AnimatedCounterScene` | `counterFrom`, `counterTo`, `counterPrefix`, `counterPostfix`, `counterToFixed` |
| `animated_text` | `AnimatedTextScene` | `text`, `split` (word/character/line), `splitStagger`, `glitch` |
| `gradient_transition` | `GradientTransitionScene` | `gradients` (배열) |
| `typewriter_bits` | `TypeWriterScene` | `text`, `typeSpeed`, `errorRate`, `cursorColor` |
| `particle_scene` | `ParticleScene` | `bitsParticleType` (fireflies/snow/fountain/grid/confetti), `bitsParticleCount` |

---

## 3. 사용 예시

### 3.1 매트릭스 디지털 레인
```json
{
  "id": "cut_01",
  "type": "matrix_rain",
  "matrixColor": "#00FF66",
  "matrixSpeed": 1,
  "matrixDensity": 1,
  "in_seconds": 0,
  "out_seconds": 8
}
```

### 3.2 숫자 카운트업 (구독자 수, 조회수)
```json
{
  "id": "cut_02",
  "type": "animated_counter",
  "counterFrom": 0,
  "counterTo": 1000000,
  "counterPostfix": "+",
  "fontSize": 120,
  "in_seconds": 8,
  "out_seconds": 14
}
```

### 3.3 글리치 텍스트 애니메이션
```json
{
  "id": "cut_03",
  "type": "animated_text",
  "text": "우주는 우연이 아니다",
  "split": "word",
  "splitStagger": 4,
  "glitch": true,
  "fontSize": 72,
  "in_seconds": 14,
  "out_seconds": 20
}
```

### 3.4 그라디언트 전환 배경
```json
{
  "id": "cut_04",
  "type": "gradient_transition",
  "gradients": [
    "linear-gradient(90deg, #ff0000, #0000ff)",
    "linear-gradient(180deg, #00ff00, #ffff00)"
  ],
  "in_seconds": 20,
  "out_seconds": 26
}
```

### 3.5 타이핑 + 오타 시뮬레이션
```json
{
  "id": "cut_05",
  "type": "typewriter_bits",
  "text": "안녕하세요, 오픈몽타주입니다.",
  "typeSpeed": 3,
  "errorRate": 0.05,
  "fontSize": 56,
  "in_seconds": 26,
  "out_seconds": 34
}
```

### 3.6 파티클 시스템 (컨페티/눈/반딧불)
```json
{
  "id": "cut_06",
  "type": "particle_scene",
  "bitsParticleType": "confetti",
  "bitsParticleCount": 80,
  "in_seconds": 34,
  "out_seconds": 40
}
```

---

## 4. 한국 크리에이터 인기 폰트 (자막/타이포)

한국 유튜브/쇼츠에서 가장 많이 쓰이는 무료 폰트:

| 폰트 | 용도 | 라이선스 |
|---|---|---|
| **Pretendard** | 본문/자막 (기본) | OFL (무료) |
| **Black Han Sans** | 굵은 헤드라인/임팩트 | OFL (무료) |
| **Gmarket Sans** | 제목/강조 | 무료 |
| **Noto Sans KR** | 범용 본문 | OFL (무료) |
| **Nanum Gothic** | 본문 | OFL (무료) |
| **Jua** | 캐주얼/감성 | OFL (무료) |
| **Do Hyeon** | 강렬한 헤드라인 | OFL (무료) |
| **Gowun Dodum** | 부드러운 본문 | OFL (무료) |

**자막 스타일 트렌드 (2025-2026):**
- 노란색/흰색 활성 단어 하이라이트 (`#FACC15` / `#FFFFFF`)
- 2-4px 검은색 아웃라인
- 단어 단위 팝업 (Word Pop)
- Pretendard Bold + Black Han Sans 조합

---

## 5. 설치 상태

```bash
# 이미 설치됨
npm install remotion-bits remotion-animated culori
```

**검증 완료:**
- `npx tsc --noEmit` 통과
- `matrix_rain`, `animated_counter`, `particle_scene`, `typewriter_bits`, `animated_text` 모두 정상 렌더링 확인
