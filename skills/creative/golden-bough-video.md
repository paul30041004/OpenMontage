# 영상 제작 황금가지 (Golden Bough Video) — 무한동력 에이전트 스킬

> 황금가지(golden-bough)의 견고한 분산 에이전트 패턴을 영상 제작에 적용한
> 자율 영상 제작 시스템. 로컬 LLM(Ollama/LM Studio) + OpenMontage 도구를
> 5-스테이지 파이프라인으로 오케스트레이션한다.

---

## 1. 아키텍처 개요

```
외부 세계(요청/트렌드) → pipeline.py (오케스트레이터)
   ├─ ingest.py    흡입: 영상 아이디어 & 참조 수집
   ├─ filter.py    선별: LLM 기반 컨셉 평가 & 우선순위
   ├─ transform.py 변환: 스크립트/스토리보드/ComfyUI 프롬프트 생성
   ├─ emit.py      방출: TTS + ComfyUI + video_compose 렌더링
   └─ feedback.py  재점화: 자체 평가 & 가중치 재계산 → ingest로 순환
```

**핵심 원칙 (황금가지 패턴):**
- 각 스테이지는 **독립 파이썬 모듈**로 존재
- 스테이지 간 통신은 **JSON (stdout)** 으로만
- `pipeline.py`가 **서브프로세스**로 실행해 격리 + 병렬 처리
- 피드백이 다시 ingest로 순환하는 **무한동력 루프**

---

## 2. 5-스테이지 상세

### 2.1 ingest.py (흡입)
- **사용자 요청 리스너:** `requests/*.json` 파일 모니터링 (처리 후 archive로 이동)
- **트렌드 RSS:** Reddit/HackerNews 등에서 바이럴 토픽 씨앗 수집
- **참조 분석:** `reference_urls` → OpenMontage `video_analyzer` 메타데이터 추출
- **출력:** `data/raw/YYYY-MM-DD/ingest_*.jsonl`

### 2.2 filter.py (선별)
- 중복/노이즈 제거
- **로컬 LLM 평가:** 실현가능성/독창성/난이도/일관성 4축 평가
- 점수 부여 & 최우선 컨셉 선정 (top_n)
- **출력:** `data/curated/YYYY-MM-DD/curated_*.jsonl`

### 2.3 transform.py (변환)
- **로컬 LLM 스크립트 생성:** 장면별 내레이션/시각 묘사/카메라/전환
- **ComfyUI 프롬프트 엔지니어링:** 스토리보드 → 생성 모델 프롬프트 묶음
- **출력:** `data/knowledge/YYYY-MM-DD/script_*.json`

### 2.4 emit.py (방출)
- **TTS (기본 VoxCPM2):** 로컬 감정연기 TTS로 장면별 내레이션 생성
  - 첫 장면 = anchor 샘플 (voice_design + emotion)
  - 이후 장면 = anchor clone (음색 통일, tts-sample-unification)
  - VoxCPM2 없으면 edge_tts로 자동 폴백
- **TTS (옵션 OmniVoice):** 600+ 언어 zero-shot voice cloning/design
  - `config.json` → `tts.provider: "omnivoice"`로 전환
  - Apple Silicon(MPS) 또는 CPU에서 로컬 실행
- **ComfyUI:** 서버 있으면 비디오 클립 생성 (없으면 스킵)
- **렌더링:** OpenMontage `video_compose`로 최종 MP4
- **출력:** `data/output/YYYY-MM-DD/final.mp4`

### 2.5 feedback.py (재점화)
- **자체 평가:** LLM으로 생성 영상 품질/훅/페이싱 평가
- **가중치 재계산:** 스타일별 반응 기반 가중치 조정
- **출력:** `data/feedback/feedback.jsonl` + `style_weights.json`

---

## 3. 로컬 AI 스택

| 구성요소 | 기본값 | 환경변수 |
|---|---|---|
| 로컬 LLM | Ollama `qwen3.6:35b-mlx` | `OLLAMA_URL`, `GOLDEN_BOUGH_LLM_MODEL` |
| LM Studio | `http://localhost:1234` | `LMSTUDIO_URL` |
| ComfyUI | `http://localhost:8188` | `COMFYUI_VIDEO_SERVER_URL` |
| **TTS (기본)** | **VoxCPM2** (로컬 감정연기, MPS) | `config.json` → `tts.provider` |
| TTS (옵션) | **OmniVoice** (600+ 언어 zero-shot 클로닝) | `config.json` → `tts.provider: "omnivoice"` |
| TTS (폴백) | edge_tts (ko-KR-InJoonNeural) | — |

**TTS 기본값은 VoxCPM2**다. `config.json`의 `tts` 섹션으로 제어:
```json
{
  "tts": {
    "provider": "voxcpm",          // "voxcpm" | "omnivoice" | "edge_tts"
    "fallback": "edge_tts",
    "voice_design": "warm, gentle, emotional Korean male narrator, deep and cinematic",
    "emotion": "잔잔하고 따뜻하게, 깊은 감동을 전달하듯이",
    "device": "mps",
    "timesteps": 8,
    "num_step": 32
  }
}
```

**폴백:** LLM/ComfyUI가 없어도 결정적 폴백(휴리스틱 평가 + 텍스트 카드 렌더)으로 동작.

---

## 4. 사용법

```bash
# 1. 요청 파일 작성
cat > golden_bough_video/requests/my_video.json << 'EOF'
{
  "title": "우주가 우연이 아니라는 60초 쇼츠",
  "prompt": "광대한 우주와 미세조정 우주론을 다루는 감성 지식 쇼츠",
  "style": "cinematic, deep space, dark blue, golden accent",
  "duration_seconds": 60,
  "platform": "youtube"
}
EOF

# 2. 1회 전체 파이프라인 실행
PYTHONPATH=. ./.venv/bin/python golden_bough_video/pipeline.py

# 3. 병렬 모드 (filter + transform 동시)
PYTHONPATH=. ./.venv/bin/python golden_bough_video/pipeline.py --mode parallel

# 4. 무한 루프 (데몬/스케줄러)
PYTHONPATH=. ./.venv/bin/python golden_bough_video/pipeline.py --loop --interval 3600
```

---

## 5. GitHub Actions 스케줄러

`.github/workflows/golden-bough-video.yml`이 이미 구성되어 있다:
- **cron:** 매일 09:00 UTC (한국 18:00) 자동 실행
- **수동 실행:** `workflow_dispatch`
- **시크릿:** `OLLAMA_URL`, `GOLDEN_BOUGH_LLM_MODEL` (원격 Ollama 사용 시)

---

## 6. 데이터 흐름

```
data/raw/YYYY-MM-DD/ingest_*.jsonl      (흡입)
data/curated/YYYY-MM-DD/curated_*.jsonl (선별)
data/knowledge/YYYY-MM-DD/script_*.json (변환)
data/output/YYYY-MM-DD/final.mp4        (방출)
data/feedback/feedback.jsonl            (재점화)
logs/pipeline_log.jsonl                 (오케스트레이션 로그)
```

---

## 7. 확장 포인트

- **새 소스 추가:** `ingest.py`에 새 RSS/API/크롤러 클래스 추가
- **새 평가 축:** `filter.py`의 `llm_evaluate`에 평가 기준 추가
- **새 생성 모델:** `emit.py`의 `generate_comfyui_clips`에 다른 도구 연결
- **새 방출 채널:** `emit.py`에 텔레그램/디스코드/유튜브 업로드 추가
- **새 피드백 신호:** `feedback.py`의 `record_feedback`에 반응 유형 추가
