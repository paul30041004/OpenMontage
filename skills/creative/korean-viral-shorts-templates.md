# 한국 바이럴 숏폼 영상 템플릿 카탈로그

> 웹 크롤링으로 수집한 **한국에서 바이럴되는 숏폼/쇼츠 영상 템플릿과 편집기법**을 OpenMontage Remotion 컴포넌트로 매핑한 마스터 가이드.
> 출처: 토스페이먼츠 숏폼 마케팅 가이드, MoGL CG연구소 숏폼 편집기법 13가지, 캡컷/미리캔버스 자막 템플릿 트렌드, 샌드폴 자막 폰트 트렌드.

---

## Part 1. 숏폼 콘텐츠 5대 유형 (토스페이먼츠)

| # | 유형 | 설명 | 대표 사례 | OpenMontage 매핑 |
|---|---|---|---|---|
| 1 | **스토리텔링형** | 드라마·시트콤·썰, 짧게 재미+공감 | 수협은행 '극한직업', '세대공감 프로젝트' | `editorial_slide` + `typewriter` + `word_pop_caption` |
| 2 | **크리에이터형** | 크리에이터 협업, 일상·음식·시트콤 | 사내뷰공업 × 써브웨이 | `social_quote` + `lower_third` + `split_screen` |
| 3 | **정보성형** | 뉴스·교육·금융 전문지식 쉽게 | MBC 14F, 지그재그 '같은옷 다른키' | `news_breaking` + `stat_card` + `bar_chart` |
| 4 | **클립형** | 기존 영상 하이라이트 편집 | 넷플릭스 릴스, 토스 '머니그라피' | `video_edit` (FFmpeg) + `word_pop_caption` |
| 5 | **참여형 챌린지** | 유행 챌린지 따라하기 | 동원참치 '#한숨에한캔' (6천만뷰) | `countdown_timer` + `particle_scene` |

---

## Part 2. 숏폼 편집기법 13가지 (MoGL CG연구소)

한국 숏폼 크리에이터들이 실제로 쓰는 **편집기법**과 Remotion 매핑:

| # | 기법 | 핵심 원리 | OpenMontage 매핑 (`cut.type`) |
|---|---|---|---|
| 1 | **립싱크** | 스타의 곡/대사를 평범한 사람이 따라함 (언더독 전략) | `talking_head` + `word_pop_caption` |
| 2 | **컷블랙** | 절정(실수)에서 과감히 끊고 디졸브 (상상력 극대화) | `end_tag` + FFmpeg dissolve |
| 3 | **익스트림 줌** | 대상 순간 확대/축소로 기대감 붕괴 | `ImageScene` animation=`zoom-in`/`zoom-out` |
| 4 | **프리즈 프레임** | 공감 순간 화면 정지 (음성지원) | FFmpeg freeze + `text_card` |
| 5 | **교차 편집** | 3-5초 내 악마의 편집으로 스토리 왜곡 | `split_screen` + `cut` |
| 6 | **스턴트** | 바보짓·용기로 놀라움 유발 | `breaking_alert` + `stat_card` |
| 7 | **일탈** | 특정 단어마다 재생속도 변화 (bee Movie 기법) | FFmpeg `setpts` 속도 변화 |
| 8 | **메타편집** | 여러 콘텐츠 덧붙여 하나의 주제 전달 | `collage_burst` + `grid_gallery` |
| 9 | **특수효과** | 트래킹·모션그래픽·매트페인팅 (희소성) | `particle_scene` + `device_mockup` + `anime_scene` |
| 10 | **텍스트어택** | 자막 위치·형태 유동적, 디자인이 내용보다 중요 | `kinetic_type` + `typewriter_bits` + `word_pop_caption` |
| 11 | **그린 스크린** | 크로마키로 배경 교체 (캐릭터 개성) | `green_screen_composite` + `backgroundVideo` |
| 12 | **스토커 편집** | 짧은 시간에 정보 과다 주입, 빠름↔느림 대비 | `beat_sync_cutter` + `staggered_motion` |
| 13 | **카오스 편집** | 무의식적 혼란, 재생속도 제멋대로 (오토마티즘) | `glitch_transition` + `vhs_glitch` + `crt_scanlines` |

---

## Part 3. 한국 유행 자막 템플릿 (캡컷/미리캔버스/샌드폴 트렌드)

### 자막 스타일 10종 (한국 크리에이터 인기)

| # | 스타일 | 특징 | 폰트 | `cut.type` |
|---|---|---|---|---|
| 1 | **노랑 하이라이트** | 활성 단어 노란색 팝 | Pretendard Bold | `word_pop_caption` |
| 2 | **흰색 + 검정 아웃라인** | 기본 쇼츠 자막 | Pretendard | `word_pop_caption` |
| 3 | **네온 글로우** | 발광 텍스트 | Black Han Sans | `kinetic_type` (glitch) |
| 4 | **타이핑 자막** | 한 글자씩 타이핑 | Pretendard | `typewriter` / `typewriter_bits` |
| 5 | **문장 단위 딱딱** | 문장이 스프링 팝인 | Black Han Sans | `animated_text` |
| 6 | **이모지 자막** | 텍스트 + 이모지 조합 | Pretendard | `reaction_emoji` (계획) |
| 7 | **하이라이트 박스** | 형광펜 밑줄 효과 | Noto Sans KR | `callout` |
| 8 | **그라디언트 텍스트** | 그라데이션 글자 | Pretendard | `gradient_transition` |
| 9 | **카운트업 숫자** | 구독자/조회수 카운트 | Black Han Sans | `animated_counter` |
| 10 | **3D 입체 자막** | 그림자+깊이 텍스트 | Black Han Sans | `text_3d` (계획) |

### 한국 인기 폰트 (자막/타이포)

| 폰트 | 용도 | 라이선스 |
|---|---|---|
| **Pretendard** | 기본 자막/본문 | OFL 무료 |
| **Black Han Sans** | 굵은 임팩트 헤드라인 | OFL 무료 |
| **Gmarket Sans** | 제목/강조 | 무료 |
| **Noto Sans KR** | 범용 본문 | OFL 무료 |
| **Jua** | 캐주얼/감성 | OFL 무료 |
| **Do Hyeon** | 강렬한 헤드라인 | OFL 무료 |
| **Gowun Dodum** | 부드러운 본문 | OFL 무료 |
| **Hahmlet** | 클래식/고급 | OFL 무료 |

---

## Part 4. 한국 바이럴 성공 사례 패턴

| 브랜드/채널 | 콘텐츠 | 조회수 | 핵심 기법 |
|---|---|---|---|
| CU '편의점 고인물' | 편의점 알바 공감 에피소드 | 1억뷰 | 스토리텔링 + 크리에이터 협업 |
| 무신사 '출근룩' | 직원 스타일링 소개 | 300만뷰 | 정보성 + 일상 공감 |
| LF '무슨 지갑' | 직원 지갑 소개 | 100만뷰 | 호기심 유발 질문 |
| 동원참치 챌린지 | 한 호흡 레시피 읽기 | 6000만뷰 | 참여형 챌린지 |
| MBC 14F | 3분 뉴스 해설 | 채널 성장 | 정보성 + 재미 포맷 |

---

## Part 5. 바이럴 성공 7원칙 (종합)

1. **0~3초 훅** — 질문, 반전, 카운터인튜이티브 스탯으로 시작 (`news_breaking`, `breaking_alert`, `stat_card`)
2. **자막은 내용보다 디자인** — 위치·형태·색상이 우선 (`word_pop_caption`, `kinetic_type`)
3. **공감을 건드려라** — "누구나 겪는" 순간 프리즈/컷블랙 (`end_tag`)
4. **정보는 짧고 빠르게** — 3초마다 새 정보, 비트 싱크 컷 (`beat_sync_cutter`)
5. **참여를 유도** — 챌린지, 질문, 투표 (`poll_card`)
6. **일탈이 정상** — 재생속도 변화, 특이 연출 (`vhs_glitch`, FFmpeg setpts)
7. **하나의 주제에 집중** — 메타편집으로 여러 콘텐츠를 하나로 (`collage_burst`)

---

## Part 6. 구현 현황

**이미 Remotion 컴포넌트로 구현됨 (바이럴 대응):**
`news_breaking`(정보성/뉴스), `breaking_alert`(속보/반전), `stat_card`(스탯), `animated_counter`(조회수 카운트업), `word_pop_caption`(노랑 하이라이트 자막), `kinetic_type`(텍스트어택), `typewriter`/`typewriter_bits`(타이핑 자막), `animated_text`(문장 스프링), `editorial_slide`(에디토리얼), `social_quote`(크리에이터/인용), `lower_third`(로어서드), `split_screen`(교차편집/비교), `countdown_timer`(챌린지), `poll_card`(참여 유도), `particle_scene`(컨페티/특수효과), `vhs_glitch`/`crt_scanlines`/`film_grain`(레트로/카오스), `matrix_rain`(특수효과), `device_mockup`(앱/UI), `geo_route`(지도), `quiz_card`(퀴즈), `scoreboard`(스포츠), `weather_card`(날씨), `end_credits`(엔딩), `cctv_camera`(감시/메타), `cut_black`(컷블랙), `reaction_emoji`(반응 이모지), `text_3d`(3D 입체 텍스트), `chat_bubble`(채팅 버블), `subscribe_button`(구독 버튼), `neon_text`(네온 사인), `notification_popup`(푸시 알림), `like_button`(좋아요 버튼), `hashtag_overlay`(해시태그), `flashback`(회상), `location_card`(장소 표시), `cliffhanger`(클리프행어).

**FFmpeg 필터로 구현 (속도/전환 기법):**
`컷블랙`(dissolve), `익스트림 줌`(zoompan), `프리즈 프레임`(freeze), `일탈`(setpts 속도변화), `슬로모션`/`패스트모션`, `그린스크린`(chromakey).

**계획 (다음 배치):**
`collage`, `slideshow`, `grid_gallery`, `confetti`(전용), `fireworks`, `streamer_overlay`, `chat_overlay`, `donation_alert`, `kill_feed`, `minimap`, `hp_bar`, `xp_bar`.
