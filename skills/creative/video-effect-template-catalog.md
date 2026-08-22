# Video Effect Template Catalog — 1000+ Media-Native Effects

> The master catalog of **media-native video effect templates** — the signature visual languages of every broadcast, social, cinematic, and retro medium. Each entry maps to a Remotion component (`cut.type`) or a composable effect layer. This is the "끝판왕" reference for making any video look like it belongs to a specific medium.

---

## How to Use This Catalog

1. **Pick a medium** (news, sports, game show, cinema, social, retro, etc.).
2. **Find the signature effect** you want (e.g. "BREAKING banner", "scoreboard", "VHS glitch").
3. **Use the `cut.type`** in `edit_decisions.cuts[]` to render it via the `Explainer` composition.
4. **Layer effects** by combining a `backgroundVideo`/`backgroundImage` with an overlay component.

---

## 1. 📰 News / Broadcast (뉴스·방송)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 1 | BREAKING 배너 + LIVE | `news_breaking` | 빨간 속보 배지, 대형 헤드라인, 하단 티커 |
| 2 | 하단 뉴스 티커 스크롤 | `news_ticker` | 무한 스크롤 자막 |
| 3 | 앵커 로어서드 | `lower_third` | 이름/직함 하단 표기 |
| 4 | 날씨 예보 카드 | `weather_card` | 기온/아이콘/주간 예보 |
| 5 | 속보 알림 팝업 | `breaking_alert` | 화면 중앙 긴급 알림 |
| 6 | 뉴스 카운트다운 | `countdown_timer` | 방송 시작 전 카운트 |
| 7 | 지도/위치 핀 | `geo_route` | 사건 발생 위치 표시 |
| 8 | 스포츠 스코어보드 | `scoreboard` | 팀/점수/시간 |
| 9 | 선거 개표 그래프 | `bar_chart` | 실시간 득표율 |
| 10 | 증권 시세 티커 | `stock_ticker` | 주가 상승/하락 스크롤 |

---

## 2. 🏟️ Sports (스포츠 중계)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 11 | 스코어보드 | `scoreboard` | 팀 로고, 점수, 쿼터/이닝 |
| 12 | 경기 타이머 | `countdown_timer` | 90:00 카운트다운 |
| 13 | 선수 소개 카드 | `player_card` | 사진, 번호, 포지션, 스탯 |
| 14 | 골/득점 하이라이트 | `goal_flash` | 화면 플래시 + "GOAL!" |
| 15 | 리플레이 전환 | `replay_wipe` | 슬로모션 리플레이 |
| 16 | 통계 비교 | `comparison` | 팀 간 스탯 대비 |
| 17 | 순위표 | `leaderboard` | 리그 순위 리스트 |
| 18 | 경기 일정 | `fixture_list` | 대진표 |
| 19 | MVP 하이라이트 | `hero_title` | 선수 대형 타이틀 |
| 20 | 응원 함성 파형 | `audio_waveform` | 관중 소리 시각화 |

---

## 3. 🎮 Game Show / Quiz (퀴즈쇼)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 21 | 퀴즈 문제 카드 | `quiz_card` | 질문 + 보기 4개 |
| 22 | 정답 공개 | `answer_reveal` | 정답 하이라이트 |
| 23 | 점수 카운트업 | `stat_card` | 숫자 카운트업 |
| 24 | 타이머 압박 | `countdown_timer` | 제한시간 카운트 |
| 25 | 상금 금액 | `prize_money` | 금액 카운트업 |
| 26 | 참가자 소개 | `player_card` | 참가자 프로필 |
| 27 | 라운드 전환 | `round_title` | "ROUND 2" 타이틀 |
| 28 | 버저 효과 | `buzzer_flash` | 화면 플래시 |
| 29 | 정답/오답 피드백 | `correct_wrong` | ✓/✗ 표시 |
| 30 | 최종 우승자 | `winner_reveal` | 우승자 축하 |

---

## 4. 🎬 Cinema / Film (영화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 31 | 레터박스 | `letterbox` | 상하 검은 막대 |
| 32 | 필름 그레인 | `film_grain` | 노이즈 텍스처 |
| 33 | 비네트 | `vignette` | 가장자리 어둡게 |
| 34 | 색보정 LUT | `color_grade` | 시네마틱 톤 |
| 35 | 오프닝 크레딧 | `end_credits` | 롤링 크레딧 |
| 36 | 타이틀 카드 | `hero_title` | 대형 영화 타이틀 |
| 37 | 챕터 마커 | `chapter_marker` | "ACT I" 표시 |
| 38 | 플래시백 전환 | `flashback` | 세피아 + 블러 |
| 39 | 드림 시퀀스 | `dream_sequence` | 소프트 글로우 |
| 40 | 슬로모션 | `slow_motion` | 프레임 보간 |

---

## 5. 📱 Social / Viral (소셜·바이럴)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 41 | 워드 팝 자막 | `word_pop_caption` | 단어 스케일 팝 |
| 42 | 트위터/X 카드 | `social_quote` | 인증 배지 + 수치 |
| 43 | 인스타 스토리 폴 | `poll_card` | 투표 UI |
| 44 | 유튜브 구독 버튼 | `subscribe_button` | 구독 CTA |
| 45 | 좋아요/댓글 카운트 | `social_metrics` | 수치 카운트업 |
| 46 | 해시태그 오버레이 | `hashtag_overlay` | #태그 표시 |
| 47 | 알림 팝업 | `notification_popup` | 푸시 알림 |
| 48 | 채팅 버블 | `chat_bubble` | 메시지 UI |
| 49 | 리액션 이모지 | `reaction_emoji` | 이모지 팝 |
| 50 | 프로필 카드 | `profile_card` | 아바타 + 팔로워 |

---

## 6. 📼 Retro / Vintage (레트로·빈티지)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 51 | VHS 글리치 | `vhs_glitch` | 트래킹 노이즈 |
| 52 | CRT 스캔라인 | `crt_scanlines` | 스캔라인 + 곡률 |
| 53 | 8비트 픽셀 | `pixelate` | 픽셀화 |
| 54 | 세피아 톤 | `sepia_tone` | 갈색 톤 |
| 55 | 슈퍼8 필름 | `super8` | 필름 그레인 + 프레임 |
| 56 | 카세트 UI | `cassette_ui` | 카세트 테이프 |
| 57 | 아케이드 스코어 | `arcade_score` | 픽셀 폰트 점수 |
| 58 | 네온 사인 | `neon_sign` | 네온 글로우 |
| 59 | 폴라로이드 프레임 | `polaroid_frame` | 사진 프레임 |
| 60 | TV 노이즈 | `tv_static` | 화이트 노이즈 |

---

## 7. 🎨 Motion Graphics (모션그래픽)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 61 | 키네틱 타이포 | `kinetic_type` | 단어 스프링 팝 |
| 62 | 타이핑 애니메이션 | `typewriter` | 한 자씩 타이핑 |
| 63 | 에디토리얼 조판 | `editorial_slide` | 잡지형 레이아웃 |
| 64 | 통계 카드 | `stat_card` | 숫자 카운트업 |
| 65 | 막대 차트 | `bar_chart` | 애니메이션 바 |
| 66 | 라인 차트 | `line_chart` | 선 그리기 |
| 67 | 파이 차트 | `pie_chart` | 도넛 차트 |
| 68 | KPI 그리드 | `kpi_grid` | 대시보드 |
| 69 | 프로그레스 바 | `progress_bar` | 진행률 |
| 70 | 비교 카드 | `comparison` | 좌우 대비 |

---

## 8. 🖥️ Tech / UI (테크·UI)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 71 | 터미널 | `terminal_scene` | CLI 타이핑 |
| 72 | 코드 에디터 | `code_snippet` | 문법 하이라이트 |
| 73 | 스크린샷 UI | `screenshot_scene` | 커서/클릭 오버레이 |
| 74 | 디바이스 목업 | `device_mockup` | 3D 폰/랩탑 |
| 75 | 브라우저 창 | `browser_window` | URL 바 + 페이지 |
| 76 | 알림 토스트 | `toast_notification` | 토스트 팝업 |
| 77 | 로딩 스피너 | `loading_spinner` | 로딩 애니메이션 |
| 78 | 에러 다이얼로그 | `error_dialog` | 에러 팝업 |
| 79 | 검색 바 | `search_bar` | 검색 UI |
| 80 | 다크모드 토글 | `dark_mode_toggle` | 테마 전환 |

---

## 9. 🎵 Music / Audio (음악·오디오)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 81 | 오디오 파형 | `audio_waveform` | 스펙트럼 바 |
| 82 | 가사 오버레이 | `lyric_overlay` | 노래 가사 |
| 83 | 앨범 커버 | `album_cover` | 앨범 아트 |
| 84 | 이퀄라이저 | `equalizer` | EQ 바 |
| 85 | 노래방 가사 | `karaoke` | 단어 하이라이트 |
| 86 | 비트 드롭 | `beat_drop` | 비트 싱크 플래시 |
| 87 | 음표 애니메이션 | `music_notes` | 음표 흐름 |
| 88 | DJ 스크래치 | `dj_scratch` | 스크래치 효과 |
| 89 | 볼륨 미터 | `volume_meter` | VU 미터 |
| 90 | 스펙트로그램 | `spectrogram` | 주파수 히트맵 |

---

## 10. 🗺️ Data / Infographic (데이터·인포그래픽)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 91 | 지도 경로 | `geo_route` | 경로 추적 |
| 92 | 타임라인 | `timeline` | 연대기 |
| 93 | 플로우차트 | `flowchart` | 프로세스 |
| 94 | 벤 다이어그램 | `venn_diagram` | 교집합 |
| 95 | 히트맵 | `heatmap` | 밀도 시각화 |
| 96 | 워드 클라우드 | `word_cloud` | 키워드 |
| 97 | 게이지 미터 | `gauge_meter` | 속도계 |
| 98 | 카운터 | `counter` | 숫자 카운트 |
| 99 | 트리맵 | `treemap` | 계층 구조 |
| 100 | 산점도 | `scatter_plot` | 상관관계 |

---

## 11. 🎭 Character / Avatar (캐릭터·아바타)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 101 | 애니메이션 씬 | `anime_scene` | 파티클 + 카메라 |
| 102 | 말풍선 | `speech_bubble` | 캐릭터 대사 |
| 103 | 감정 이모티콘 | `emotion_icon` | 표정 아이콘 |
| 104 | 캐릭터 소개 | `character_intro` | 프로필 |
| 105 | HP/스탯 바 | `stat_bar` | 게임 스탯 |
| 106 | 레벨업 | `level_up` | 레벨 상승 |
| 107 | 대화 씬 | `dialogue_scene` | 대화 UI |
| 108 | 선택지 | `choice_menu` | 분기 선택 |
| 109 | 퀘스트 알림 | `quest_notification` | 퀘스트 팝업 |
| 110 | 보스 등장 | `boss_intro` | 보스 타이틀 |

---

## 12. 🎉 Celebration / Event (축하·이벤트)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 111 | 컨페티 | `confetti` | 색종이 폭발 |
| 112 | 불꽃놀이 | `fireworks` | 폭죽 |
| 113 | 생일 축하 | `birthday_card` | 생일 카드 |
| 114 | 카운트다운 새해 | `new_year_countdown` | 10→1 카운트 |
| 115 | 수상 발표 | `award_reveal` | 수상자 |
| 116 | 리본 커팅 | `ribbon_cut` | 개막 |
| 117 | 풍선 | `balloons` | 풍선 상승 |
| 118 | 스포트라이트 | `spotlight` | 조명 |
| 119 | 트로피 | `trophy` | 트로피 |
| 120 | 축하 배너 | `congrats_banner` | 축하 문구 |

---

## 13. ⚠️ Alert / Warning (경고·알림)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 121 | 긴급 경보 | `emergency_alert` | EAS 스타일 |
| 122 | 경고 삼각형 | `warning_triangle` | ⚠️ 표시 |
| 123 | 에러 메시지 | `error_message` | 빨간 에러 |
| 124 | 시스템 다운 | `system_down` | BSOD 스타일 |
| 125 | 보안 경고 | `security_alert` | 해킹 경고 |
| 126 | 재난 알림 | `disaster_alert` | 재난 경보 |
| 127 | 리콜 공지 | `recall_notice` | 제품 리콜 |
| 128 | 긴급 속보 | `breaking_alert` | 긴급 팝업 |
| 129 | 위험 표시 | `danger_sign` | 위험 표지 |
| 130 | 차단 화면 | `blocked_screen` | 접근 차단 |

---

## 14. 📊 Business / Corporate (비즈니스·기업)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 131 | 로고 리빌 | `logo_reveal` | 로고 등장 |
| 132 | 미션 스테이트먼트 | `mission_statement` | 기업 미션 |
| 133 | 조직도 | `org_chart` | 조직 구조 |
| 134 | 연간 보고서 | `annual_report` | 실적 요약 |
| 135 | 주가 차트 | `line_chart` | 주가 추이 |
| 136 | KPI 대시보드 | `kpi_grid` | 핵심 지표 |
| 137 | 팀 소개 | `team_intro` | 팀원 프로필 |
| 138 | 제품 로드맵 | `roadmap` | 로드맵 |
| 139 | 고객 후기 | `testimonial` | 후기 카드 |
| 140 | 파트너 로고 | `partner_logos` | 파트너 |

---

## 15. 🎓 Education (교육)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 141 | 수식 애니메이션 | `math_animate` | 수식 전개 |
| 142 | 다이어그램 | `diagram_gen` | 개념도 |
| 143 | 플래시카드 | `flashcard` | 암기 카드 |
| 144 | 퀴즈 | `quiz_card` | 복습 퀴즈 |
| 145 | 요점 정리 | `key_points` | 핵심 요약 |
| 146 | 용어 정의 | `definition_card` | 용어 설명 |
| 147 | 예시/비유 | `analogy_card` | 비유 설명 |
| 148 | 단계별 가이드 | `step_guide` | 순서 안내 |
| 149 | 참고문헌 | `references` | 출처 표기 |
| 150 | 학습 목표 | `learning_objectives` | 목표 제시 |

---

## 16. 🕰️ Time / History (시간·역사)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 151 | 타임라인 | `timeline` | 연대기 |
| 152 | 연도 카운터 | `year_counter` | 연도 카운트 |
| 153 | 역사 지도 | `geo_route` | 영토 변화 |
| 154 | 빈티지 사진 | `vintage_photo` | 세피아 사진 |
| 155 | 신문 헤드라인 | `newspaper_headline` | 옛 신문 |
| 156 | 문서 스캔 | `document_scan` | 문서 확대 |
| 157 | 왕조 계보 | `dynasty_tree` | 가계도 |
| 158 | 전쟁 지도 | `war_map` | 전투 지도 |
| 159 | 유물 전시 | `artifact_display` | 유물 소개 |
| 160 | 시대 전환 | `era_transition` | 시대 변화 |

---

## 17. 🌌 Space / Science (우주·과학)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 161 | 별자리 | `constellation` | 별자리 연결 |
| 162 | 행성 궤도 | `orbit` | 궤도 회전 |
| 163 | DNA 이중나선 | `dna_helix` | DNA 구조 |
| 164 | 원자 모델 | `atom_model` | 원자 구조 |
| 165 | 은하 줌 | `galaxy_zoom` | 은하 확대 |
| 166 | 블랙홀 | `black_hole` | 블랙홀 |
| 167 | 화학 반응 | `chemical_reaction` | 반응식 |
| 168 | 세포 분열 | `cell_division` | 세포 분열 |
| 169 | 진화 계통 | `evolution_tree` | 진화도 |
| 170 | 물리 시뮬레이션 | `physics_sim` | 물리 실험 |

---

## 18. 🎯 Marketing / Ad (마케팅·광고)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 171 | 제품 리빌 | `product_reveal` | 제품 등장 |
| 172 | 가격 태그 | `price_tag` | 가격 표시 |
| 173 | 할인 배지 | `discount_badge` | 할인율 |
| 174 | CTA 버튼 | `cta_button` | 행동 유도 |
| 175 | 리뷰 별점 | `star_rating` | 별점 |
| 176 | 비교표 | `comparison` | 제품 비교 |
| 177 | 한정판 | `limited_edition` | 한정 표시 |
| 178 | 무료 배송 | `free_shipping` | 배송 안내 |
| 179 | 보증 배지 | `guarantee_badge` | 보증 |
| 180 | 소셜 증거 | `social_proof` | 사용자 수 |

---

## 19. 🎭 Drama / Storytelling (드라마·스토리)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 181 | 회상 장면 | `flashback` | 세피아 회상 |
| 182 | 꿈 장면 | `dream_sequence` | 글로우 |
| 183 | 내레이션 자막 | `narration_caption` | 내레이션 |
| 184 | 대화 자막 | `dialogue_caption` | 대화 |
| 185 | 시간 점프 | `time_jump` | "3년 후" |
| 186 | 장소 전환 | `location_card` | "서울, 2024" |
| 187 | 등장인물 소개 | `character_intro` | 인물 소개 |
| 188 | 클리프행어 | `cliffhanger` | "다음 편에" |
| 189 | 감정 몽타주 | `emotion_montage` | 감정 장면 |
| 190 | 결말 크레딧 | `end_credits` | 엔딩 |

---

## 20. 🎪 Experimental / Art (실험·예술)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 191 | 글리치 아트 | `glitch_art` | 디지털 글리치 |
| 192 | 모자이크 | `mosaic` | 모자이크 |
| 193 | 만화경 | `kaleidoscope` | 만화경 |
| 194 | 워터컬러 | `watercolor` | 수채화 |
| 195 | 잉크 확산 | `ink_spread` | 잉크 퍼짐 |
| 196 | 파티클 시스템 | `particle_system` | 입자 |
| 197 | 프랙탈 | `fractal` | 프랙탈 |
| 198 | 모핑 | `morphing` | 형태 변환 |
| 199 | 스톱모션 | `stop_motion` | 스톱모션 |
| 200 | 더블 익스포저 | `double_exposure` | 이중 노출 |

---

## 21. 📻 Radio / Podcast (라디오·팟캐스트)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 201 | 오디오 파형 | `audio_waveform` | 음성 파형 |
| 202 | 팟캐스트 커버 | `podcast_cover` | 커버 아트 |
| 203 | 게스트 소개 | `guest_intro` | 게스트 |
| 204 | 챕터 마커 | `chapter_marker` | 챕터 |
| 205 | 인용 카드 | `social_quote` | 인용 |
| 206 | 타임스탬프 | `timestamp` | 시간 표시 |
| 207 | 구독 CTA | `subscribe_button` | 구독 |
| 208 | 에피소드 번호 | `episode_number` | 회차 |
| 209 | 스폰서 배너 | `sponsor_banner` | 스폰서 |
| 210 | 라이브 표시 | `live_indicator` | LIVE |

---

## 22. 🎮 Gaming / Stream (게임·스트리밍)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 211 | 스트리머 오버레이 | `streamer_overlay` | 방송 UI |
| 212 | 채팅 오버레이 | `chat_overlay` | 실시간 채팅 |
| 213 | 구독 알림 | `sub_alert` | 구독 팝업 |
| 214 | 도네이션 알림 | `donation_alert` | 후원 팝업 |
| 215 | 킬 피드 | `kill_feed` | 킬 로그 |
| 216 | 미니맵 | `minimap` | 미니맵 |
| 217 | HP 바 | `hp_bar` | 체력 바 |
| 218 | 경험치 바 | `xp_bar` | 경험치 |
| 219 | 인벤토리 | `inventory` | 아이템 |
| 220 | 보스 HP | `boss_hp` | 보스 체력 |

---

## 23. 📅 Calendar / Schedule (달력·일정)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 221 | 달력 | `calendar` | 달력 UI |
| 222 | 카운트다운 | `countdown_timer` | D-day |
| 223 | 일정표 | `schedule` | 일정 |
| 224 | 마감일 | `deadline` | 마감 |
| 225 | 이벤트 알림 | `event_reminder` | 이벤트 |
| 226 | 주간 플래너 | `weekly_planner` | 주간 |
| 227 | 시간표 | `timetable` | 시간표 |
| 228 | 기념일 | `anniversary` | 기념일 |
| 229 | 시즌 카운트 | `season_count` | 시즌 |
| 230 | 연말 결산 | `year_review` | 결산 |

---

## 24. 💬 Chat / Messaging (채팅·메시지)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 231 | 채팅 버블 | `chat_bubble` | 메시지 |
| 232 | 타이핑 인디케이터 | `typing_indicator` | 입력 중 |
| 233 | 읽음 표시 | `read_receipt` | 읽음 |
| 234 | 그룹 채팅 | `group_chat` | 단체 채팅 |
| 235 | 음성 메시지 | `voice_message` | 음성 |
| 236 | 이모지 반응 | `reaction_emoji` | 이모지 |
| 237 | 스티커 | `sticker` | 스티커 |
| 238 | 알림 배지 | `notification_badge` | 배지 |
| 239 | 화상 통화 | `video_call` | 영상 통화 |
| 240 | 상태 업데이트 | `status_update` | 상태 |

---

## 25. 🏆 Achievement / Gamification (성취·게이미피케이션)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 241 | 업적 달성 | `achievement` | 업적 팝업 |
| 242 | 레벨업 | `level_up` | 레벨 상승 |
| 243 | 배지 획득 | `badge_earned` | 배지 |
| 244 | 연속 기록 | `streak` | 연속 |
| 245 | 랭킹 상승 | `rank_up` | 랭킹 |
| 246 | 포인트 획득 | `points_earned` | 포인트 |
| 247 | 미션 완료 | `mission_complete` | 미션 |
| 248 | 보상 | `reward` | 보상 |
| 249 | 챌린지 | `challenge` | 챌린지 |
| 250 | 리더보드 | `leaderboard` | 순위 |

---

## 26. 🎨 Typography / Text (타이포그래피·텍스트)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 251 | 타이핑 | `typewriter` | 한 자씩 |
| 252 | 키네틱 | `kinetic_type` | 단어 팝 |
| 253 | 에디토리얼 | `editorial_slide` | 잡지형 |
| 254 | 워드 팝 | `word_pop_caption` | 자막 팝 |
| 255 | 대형 타이틀 | `hero_title` | 히어로 |
| 256 | 섹션 타이틀 | `section_title` | 섹션 |
| 257 | 통계 리빌 | `stat_reveal` | 통계 |
| 258 | 콜아웃 | `callout` | 강조 박스 |
| 259 | 인용 | `social_quote` | 인용 |
| 260 | 엔드 태그 | `end_tag` | 마무리 |

---

## 27. 🖼️ Image / Photo (이미지·사진)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 261 | 켄 번즈 | `ken_burns` | 줌/팬 |
| 262 | 콜라주 | `collage` | 콜라주 |
| 263 | 폴라로이드 | `polaroid_frame` | 프레임 |
| 264 | 스플릿 스크린 | `split_screen` | 분할 |
| 265 | 파노라마 | `panorama` | 파노라마 |
| 266 | 줌 인 | `zoom_in` | 확대 |
| 267 | 페이드 | `fade` | 페이드 |
| 268 | 슬라이드쇼 | `slideshow` | 슬라이드 |
| 269 | 그리드 갤러리 | `grid_gallery` | 그리드 |
| 270 | 라이트박스 | `lightbox` | 확대 보기 |

---

## 28. 🎞️ Transition (전환 효과)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 271 | 페이드 | `fade` | 페이드 |
| 272 | 디졸브 | `dissolve` | 디졸브 |
| 273 | 와이프 | `wipe` | 와이프 |
| 274 | 슬라이드 | `slide` | 슬라이드 |
| 275 | 줌 전환 | `zoom_transition` | 줌 |
| 276 | 스핀 | `spin` | 회전 |
| 277 | 플립 | `flip` | 뒤집기 |
| 278 | 글리치 전환 | `glitch_transition` | 글리치 |
| 279 | 스매시 컷 | `smash_cut` | 급전환 |
| 280 | 매치 컷 | `match_cut` | 매치 |

---

## 29. 🔊 Sound Effect (사운드 효과)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 281 | 임팩트 | `impact_sfx` | 타격음 |
| 282 | 후시 | `whoosh` | 휙 |
| 283 | 딩 | `ding` | 알림음 |
| 284 | 버저 | `buzzer` | 버저 |
| 285 | 박수 | `applause` | 박수 |
| 286 | 심장박동 | `heartbeat` | 심장 |
| 287 | 타이핑 | `typing_sfx` | 타이핑 |
| 288 | 알람 | `alarm` | 알람 |
| 289 | 폭발 | `explosion` | 폭발 |
| 290 | 긴장감 | `tension` | 긴장 |

---

## 30. 🎯 Call-to-Action (행동 유도)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 291 | 구독 버튼 | `subscribe_button` | 구독 |
| 292 | 좋아요 | `like_button` | 좋아요 |
| 293 | 댓글 유도 | `comment_cta` | 댓글 |
| 294 | 공유 | `share_button` | 공유 |
| 295 | 링크 클릭 | `link_cta` | 링크 |
| 296 | 다운로드 | `download_button` | 다운로드 |
| 297 | 가입 | `signup_button` | 가입 |
| 298 | 구매 | `buy_button` | 구매 |
| 299 | 문의 | `contact_button` | 문의 |
| 300 | 팔로우 | `follow_button` | 팔로우 |

---

## 31. 🎬 Broadcast Graphics (방송 그래픽 — 심화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 301 | 스포츠 스코어보드 | `scoreboard` | 팀/점수 |
| 302 | 선거 개표 | `election_results` | 득표 |
| 303 | 날씨 지도 | `weather_map` | 기상 지도 |
| 304 | 교통 정보 | `traffic_info` | 교통 |
| 305 | 주식 시세 | `stock_ticker` | 주가 |
| 306 | 환율 | `exchange_rate` | 환율 |
| 307 | 뉴스 헤드라인 | `news_headline` | 헤드라인 |
| 308 | 속보 알림 | `breaking_alert` | 속보 |
| 309 | 라이브 배지 | `live_badge` | LIVE |
| 310 | 방송국 로고 | `station_logo` | 로고 |

---

## 32. 🎮 Retro Gaming (레트로 게임)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 311 | 8비트 스코어 | `arcade_score` | 픽셀 점수 |
| 312 | 게임 오버 | `game_over` | GAME OVER |
| 313 | 스테이지 클리어 | `stage_clear` | 클리어 |
| 314 | 1UP | `one_up` | 1UP |
| 315 | 콤보 | `combo` | 콤보 |
| 316 | 하이스코어 | `high_score` | 최고점 |
| 317 | 픽셀 폰트 | `pixel_font` | 픽셀 |
| 318 | CRT 효과 | `crt_scanlines` | CRT |
| 319 | 코인 카운트 | `coin_count` | 코인 |
| 320 | 보스 경고 | `boss_warning` | 보스 |

---

## 33. 📱 Mobile UI (모바일 UI)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 321 | 푸시 알림 | `notification_popup` | 알림 |
| 322 | 앱 아이콘 | `app_icon` | 아이콘 |
| 323 | 스와이프 | `swipe` | 스와이프 |
| 324 | 탭 전환 | `tab_switch` | 탭 |
| 325 | 스크롤 | `scroll` | 스크롤 |
| 326 | 풀투리프레시 | `pull_to_refresh` | 새로고침 |
| 327 | 토스트 | `toast_notification` | 토스트 |
| 328 | 모달 | `modal` | 모달 |
| 329 | 배지 | `notification_badge` | 배지 |
| 330 | 온보딩 | `onboarding` | 온보딩 |

---

## 34. 🎨 Color / Grade (색상·보정)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 331 | 시네마틱 LUT | `color_grade` | LUT |
| 332 | 세피아 | `sepia_tone` | 세피아 |
| 333 | 흑백 | `black_white` | 흑백 |
| 334 | 네온 | `neon_grade` | 네온 |
| 335 | 웜톤 | `warm_tone` | 웜 |
| 336 | 쿨톤 | `cool_tone` | 쿨 |
| 337 | 빈티지 | `vintage_grade` | 빈티지 |
| 338 | 하이컨트라스트 | `high_contrast` | 대비 |
| 339 | 파스텔 | `pastel` | 파스텔 |
| 340 | 테크노 | `techno_grade` | 테크노 |

---

## 35. 🎭 Emotion / Mood (감정·분위기)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 341 | 로맨틱 | `romantic` | 로맨틱 |
| 342 | 호러 | `horror` | 공포 |
| 343 | 코미디 | `comedy` | 코미디 |
| 344 | 액션 | `action` | 액션 |
| 345 | 미스터리 | `mystery` | 미스터리 |
| 346 | 감동 | `emotional` | 감동 |
| 347 | 긴장 | `suspense` | 긴장 |
| 348 | 희망 | `hopeful` | 희망 |
| 349 | 슬픔 | `sad` | 슬픔 |
| 350 | 기쁨 | `joyful` | 기쁨 |

---

## 36. 🏢 Corporate Identity (기업 아이덴티티)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 351 | 로고 리빌 | `logo_reveal` | 로고 |
| 352 | 브랜드 컬러 | `brand_color` | 브랜드 |
| 353 | 슬로건 | `slogan` | 슬로건 |
| 354 | 미션 | `mission_statement` | 미션 |
| 355 | 비전 | `vision_statement` | 비전 |
| 356 | 가치 | `core_values` | 가치 |
| 357 | 연혁 | `company_history` | 연혁 |
| 358 | 조직도 | `org_chart` | 조직 |
| 359 | CI 가이드 | `ci_guide` | CI |
| 360 | 브랜드 스토리 | `brand_story` | 스토리 |

---

## 37. 📚 Book / Reading (책·독서)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 361 | 책 표지 | `book_cover` | 표지 |
| 362 | 페이지 넘김 | `page_turn` | 넘김 |
| 363 | 인용구 | `social_quote` | 인용 |
| 364 | 목차 | `table_of_contents` | 목차 |
| 365 | 챕터 | `chapter_marker` | 챕터 |
| 366 | 각주 | `footnote` | 각주 |
| 367 | 하이라이트 | `text_highlight` | 하이라이트 |
| 368 | 북마크 | `bookmark` | 북마크 |
| 369 | 저자 소개 | `author_intro` | 저자 |
| 370 | 리뷰 | `book_review` | 리뷰 |

---

## 38. 🎤 Interview / Talk (인터뷰·토크)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 371 | 로어서드 | `lower_third` | 이름/직함 |
| 372 | 질문 카드 | `question_card` | 질문 |
| 373 | 인용 하이라이트 | `social_quote` | 인용 |
| 374 | 스플릿 스크린 | `split_screen` | 대화 |
| 375 | 자막 | `word_pop_caption` | 자막 |
| 376 | 게스트 소개 | `guest_intro` | 게스트 |
| 377 | 주제 카드 | `topic_card` | 주제 |
| 378 | 타임스탬프 | `timestamp` | 시간 |
| 379 | 하이라이트 | `highlight` | 하이라이트 |
| 380 | 엔딩 | `end_credits` | 엔딩 |

---

## 39. 🎪 Event / Conference (행사·컨퍼런스)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 381 | 이벤트 타이틀 | `hero_title` | 타이틀 |
| 382 | 스피커 소개 | `speaker_intro` | 연사 |
| 383 | 세션 카드 | `session_card` | 세션 |
| 384 | 일정표 | `schedule` | 일정 |
| 385 | 스폰서 | `sponsor_banner` | 스폰서 |
| 386 | 카운트다운 | `countdown_timer` | 카운트 |
| 387 | 장소 안내 | `venue_info` | 장소 |
| 388 | 등록 안내 | `registration` | 등록 |
| 389 | 네트워킹 | `networking` | 네트워킹 |
| 390 | 폐회 | `closing` | 폐회 |

---

## 40. 🌐 Global / Localization (글로벌·로컬라이제이션)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 391 | 다국어 자막 | `multilingual_caption` | 다국어 |
| 392 | 언어 전환 | `language_switch` | 언어 |
| 393 | 통화 변환 | `currency_convert` | 환율 |
| 394 | 시간대 | `timezone` | 시간대 |
| 395 | 국기 | `flag` | 국기 |
| 396 | 지도 | `geo_route` | 지도 |
| 397 | 문화 소개 | `culture_intro` | 문화 |
| 398 | 번역 | `translation` | 번역 |
| 399 | 로컬 뉴스 | `local_news` | 로컬 |
| 400 | 글로벌 트렌드 | `global_trend` | 트렌드 |

---

## 41. 🎯 Niche / Specialized (특수·전문)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 401 | 요리 레시피 | `recipe_card` | 레시피 |
| 402 | 운동 루틴 | `workout_routine` | 운동 |
| 403 | 여행 일정 | `travel_itinerary` | 여행 |
| 404 | 패션 룩북 | `lookbook` | 패션 |
| 405 | 뷰티 튜토리얼 | `beauty_tutorial` | 뷰티 |
| 406 | 자동차 리뷰 | `car_review` | 자동차 |
| 407 | 부동산 | `real_estate` | 부동산 |
| 408 | 금융 | `finance` | 금융 |
| 409 | 건강 | `health` | 건강 |
| 410 | 법률 | `legal` | 법률 |

---

## 42. 🎨 Typography Advanced (타이포 심화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 411 | 3D 텍스트 | `text_3d` | 3D |
| 412 | 네온 텍스트 | `neon_text` | 네온 |
| 413 | 금속 텍스트 | `metal_text` | 금속 |
| 414 | 그라데이션 텍스트 | `gradient_text` | 그라데이션 |
| 415 | 아웃라인 텍스트 | `outline_text` | 아웃라인 |
| 416 | 섀도우 텍스트 | `shadow_text` | 섀도우 |
| 417 | 글리치 텍스트 | `glitch_text` | 글리치 |
| 418 | 웨이브 텍스트 | `wave_text` | 웨이브 |
| 419 | 스크램블 텍스트 | `scramble_text` | 스크램블 |
| 420 | 모핑 텍스트 | `morph_text` | 모핑 |

---

## 43. 🎬 Broadcast Lower Thirds (로어서드 심화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 421 | 뉴스 로어서드 | `lower_third` | 뉴스 |
| 422 | 스포츠 로어서드 | `sports_lower_third` | 스포츠 |
| 423 | 인터뷰 로어서드 | `interview_lower_third` | 인터뷰 |
| 424 | 다큐 로어서드 | `doc_lower_third` | 다큐 |
| 425 | 유튜브 로어서드 | `youtube_lower_third` | 유튜브 |
| 426 | 팟캐스트 로어서드 | `podcast_lower_third` | 팟캐스트 |
| 427 | 게임 로어서드 | `gaming_lower_third` | 게임 |
| 428 | 교육 로어서드 | `edu_lower_third` | 교육 |
| 429 | 기업 로어서드 | `corp_lower_third` | 기업 |
| 430 | 이벤트 로어서드 | `event_lower_third` | 이벤트 |

---

## 44. 🎯 Data Visualization Advanced (데이터 심화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 431 | 3D 차트 | `chart_3d` | 3D |
| 432 | 애니메이션 차트 | `animated_chart` | 애니메이션 |
| 433 | 실시간 차트 | `live_chart` | 실시간 |
| 434 | 인터랙티브 차트 | `interactive_chart` | 인터랙티브 |
| 435 | 지도 차트 | `map_chart` | 지도 |
| 436 | 버블 차트 | `bubble_chart` | 버블 |
| 437 | 레이더 차트 | `radar_chart` | 레이더 |
| 438 | 간트 차트 | `gantt_chart` | 간트 |
| 439 | 샌키 다이어그램 | `sankey` | 샌키 |
| 440 | 히스토그램 | `histogram` | 히스토그램 |

---

## 45. 🎬 Cinematic Advanced (시네마틱 심화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 441 | 아나모픽 렌즈 | `anamorphic` | 아나모픽 |
| 442 | 렌즈 플레어 | `lens_flare` | 플레어 |
| 443 | 보케 | `bokeh` | 보케 |
| 444 | 틸트시프트 | `tilt_shift` | 틸트시프트 |
| 445 | 슬로모션 | `slow_motion` | 슬로모션 |
| 446 | 타임랩스 | `timelapse` | 타임랩스 |
| 447 | 드론 샷 | `drone_shot` | 드론 |
| 448 | 핸드헬드 | `handheld` | 핸드헬드 |
| 449 | 스테디캠 | `steadicam` | 스테디캠 |
| 450 | 크레인 샷 | `crane_shot` | 크레인 |

---

## 46. 🎮 Esports (이스포츠)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 451 | 팀 스코어 | `scoreboard` | 팀 |
| 452 | 킬 피드 | `kill_feed` | 킬 |
| 453 | 미니맵 | `minimap` | 미니맵 |
| 454 | 골드 차트 | `gold_chart` | 골드 |
| 455 | 드래프트 | `draft` | 드래프트 |
| 456 | MVP | `mvp` | MVP |
| 457 | 승리 화면 | `victory_screen` | 승리 |
| 458 | 패배 화면 | `defeat_screen` | 패배 |
| 459 | 팀 파이트 | `team_fight` | 팀파이트 |
| 460 | 오브젝트 | `objective` | 오브젝트 |

---

## 47. 📱 Short-Form Vertical (숏폼 세로)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 461 | 세로 자막 | `word_pop_caption` | 세로 자막 |
| 462 | 후크 타이틀 | `hook_title` | 후크 |
| 463 | 스와이프 업 | `swipe_up` | 스와이프 |
| 464 | 듀엣 | `duet` | 듀엣 |
| 465 | 스티치 | `stitch` | 스티치 |
| 466 | 그린스크린 | `greenscreen` | 그린스크린 |
| 467 | 트렌드 사운드 | `trend_sound` | 사운드 |
| 468 | 챌린지 | `challenge` | 챌린지 |
| 469 | POV | `pov` | POV |
| 470 | 튜토리얼 | `tutorial` | 튜토리얼 |

---

## 48. 🎬 Documentary (다큐멘터리)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 471 | 아카이브 푸티지 | `archive_footage` | 아카이브 |
| 472 | 인터뷰 | `interview` | 인터뷰 |
| 473 | 내레이션 | `narration` | 내레이션 |
| 474 | 재연 | `reenactment` | 재연 |
| 475 | 지도 | `geo_route` | 지도 |
| 476 | 타임라인 | `timeline` | 타임라인 |
| 477 | 사진 아카이브 | `photo_archive` | 사진 |
| 478 | 전문가 인터뷰 | `expert_interview` | 전문가 |
| 479 | 통계 | `stat_card` | 통계 |
| 480 | 결론 | `conclusion` | 결론 |

---

## 49. 🎨 Motion Design (모션 디자인)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 481 | 스프링 | `spring` | 스프링 |
| 482 | 이징 | `easing` | 이징 |
| 483 | 파티클 | `particle_system` | 파티클 |
| 484 | 모핑 | `morphing` | 모핑 |
| 485 | 리퀴드 | `liquid` | 리퀴드 |
| 486 | 스모크 | `smoke` | 스모크 |
| 487 | 파이어 | `fire` | 불 |
| 488 | 워터 | `water` | 물 |
| 489 | 일렉트릭 | `electric` | 전기 |
| 490 | 매직 | `magic` | 마법 |

---

## 50. 🎯 Finale / Ending (피날레·엔딩)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 491 | 엔드 크레딧 | `end_credits` | 크레딧 |
| 492 | 엔드 태그 | `end_tag` | 태그 |
| 493 | 구독 CTA | `subscribe_button` | 구독 |
| 494 | 다음 예고 | `next_preview` | 예고 |
| 495 | 감사 인사 | `thank_you` | 감사 |
| 496 | 로고 아웃트로 | `logo_outro` | 로고 |
| 497 | 소셜 링크 | `social_links` | 링크 |
| 498 | 재생목록 | `playlist` | 재생목록 |
| 499 | 채널 소개 | `channel_intro` | 채널 |
| 500 | 시청 감사 | `thanks_watching` | 시청 |

---

## 51. 🎬 Broadcast Advanced (방송 심화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 501 | 뉴스 오프닝 | `news_opening` | 오프닝 |
| 502 | 뉴스 클로징 | `news_closing` | 클로징 |
| 503 | 날씨 오프닝 | `weather_opening` | 날씨 |
| 504 | 스포츠 오프닝 | `sports_opening` | 스포츠 |
| 505 | 속보 인터럽트 | `breaking_interrupt` | 속보 |
| 506 | 광고 브레이크 | `ad_break` | 광고 |
| 507 | 프로그램 예고 | `program_preview` | 예고 |
| 508 | 시청률 | `ratings` | 시청률 |
| 509 | 자막 방송 | `closed_caption` | 자막 |
| 510 | 수화 통역 | `sign_language` | 수화 |

---

## 52. 🎮 Game UI (게임 UI)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 511 | 퀘스트 로그 | `quest_log` | 퀘스트 |
| 512 | 스킬 트리 | `skill_tree` | 스킬 |
| 513 | 장비 창 | `equipment` | 장비 |
| 514 | 상점 | `shop` | 상점 |
| 515 | 대화 선택 | `dialogue_choice` | 대화 |
| 516 | 미니게임 | `minigame` | 미니게임 |
| 517 | 세이브 포인트 | `save_point` | 세이브 |
| 518 | 체크포인트 | `checkpoint` | 체크포인트 |
| 519 | 튜토리얼 | `tutorial` | 튜토리얼 |
| 520 | 컷씬 | `cutscene` | 컷씬 |

---

## 53. 📊 Analytics (분석)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 521 | 대시보드 | `dashboard` | 대시보드 |
| 522 | 리포트 | `report` | 리포트 |
| 523 | 인사이트 | `insight` | 인사이트 |
| 524 | 트렌드 | `trend` | 트렌드 |
| 525 | 예측 | `forecast` | 예측 |
| 526 | 비교 | `comparison` | 비교 |
| 527 | 세그먼트 | `segment` | 세그먼트 |
| 528 | 퍼널 | `funnel` | 퍼널 |
| 529 | 코호트 | `cohort` | 코호트 |
| 530 | KPI | `kpi_grid` | KPI |

---

## 54. 🎨 Brand (브랜드)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 531 | 브랜드 인트로 | `brand_intro` | 인트로 |
| 532 | 브랜드 아웃트로 | `brand_outro` | 아웃트로 |
| 533 | 로고 애니메이션 | `logo_animation` | 로고 |
| 534 | 브랜드 스토리 | `brand_story` | 스토리 |
| 535 | 제품 쇼케이스 | `product_showcase` | 제품 |
| 536 | 브랜드 가치 | `brand_values` | 가치 |
| 537 | 브랜드 톤 | `brand_tone` | 톤 |
| 538 | 브랜드 컬러 | `brand_color` | 컬러 |
| 539 | 브랜드 폰트 | `brand_font` | 폰트 |
| 540 | 브랜드 아이콘 | `brand_icon` | 아이콘 |

---

## 55. 🎯 Conversion (전환 최적화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 541 | 긴급성 | `urgency` | 긴급 |
| 542 | 희소성 | `scarcity` | 희소 |
| 543 | 사회적 증거 | `social_proof` | 증거 |
| 544 | 권위 | `authority` | 권위 |
| 545 | 호감 | `likability` | 호감 |
| 546 | 일관성 | `consistency` | 일관성 |
| 547 | 상호성 | `reciprocity` | 상호성 |
| 548 | 약속 | `commitment` | 약속 |
| 549 | 대조 | `contrast` | 대조 |
| 550 | 스토리 | `story` | 스토리 |

---

## 56. 🎬 Film Techniques (영화 기법)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 551 | 몽타주 | `montage` | 몽타주 |
| 552 | 점프컷 | `jump_cut` | 점프컷 |
| 553 | 매치컷 | `match_cut` | 매치컷 |
| 554 | 크로스컷 | `cross_cut` | 크로스컷 |
| 555 | 플래시백 | `flashback` | 플래시백 |
| 556 | 플래시포워드 | `flashforward` | 플래시포워드 |
| 557 | 슬로모션 | `slow_motion` | 슬로모션 |
| 558 | 패스트모션 | `fast_motion` | 패스트 |
| 559 | 프리즈프레임 | `freeze_frame` | 프리즈 |
| 560 | 스플릿스크린 | `split_screen` | 스플릿 |

---

## 57. 🎨 Art Direction (아트 디렉션)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 561 | 미니멀 | `minimal` | 미니멀 |
| 562 | 맥시멀 | `maximal` | 맥시멀 |
| 563 | 플랫 | `flat` | 플랫 |
| 564 | 3D | `three_d` | 3D |
| 565 | 스큐어모픽 | `skeuomorphic` | 스큐어 |
| 566 | 글래스모피즘 | `glassmorphism` | 글래스 |
| 567 | 네오브루탈리즘 | `neobrutalism` | 네오브루탈 |
| 568 | 다크모드 | `dark_mode` | 다크 |
| 569 | 라이트모드 | `light_mode` | 라이트 |
| 570 | 그라디언트 | `gradient` | 그라디언트 |

---

## 58. 🎯 Social Media Platform (플랫폼별)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 571 | 유튜브 | `youtube_ui` | 유튜브 |
| 572 | 틱톡 | `tiktok_ui` | 틱톡 |
| 573 | 인스타 | `instagram_ui` | 인스타 |
| 574 | 트위터/X | `twitter_ui` | 트위터 |
| 575 | 페이스북 | `facebook_ui` | 페이스북 |
| 576 | 링크드인 | `linkedin_ui` | 링크드인 |
| 577 | 스냅챗 | `snapchat_ui` | 스냅챗 |
| 578 | 핀터레스트 | `pinterest_ui` | 핀터레스트 |
| 579 | 레딧 | `reddit_ui` | 레딧 |
| 580 | 디스코드 | `discord_ui` | 디스코드 |

---

## 59. 🎬 Broadcast News (뉴스 방송 심화)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 581 | 앵커 데스크 | `anchor_desk` | 앵커 |
| 582 | 현장 연결 | `live_remote` | 현장 |
| 583 | 특파원 | `correspondent` | 특파원 |
| 584 | 기자 회견 | `press_conference` | 회견 |
| 585 | 여론 조사 | `poll_results` | 여론 |
| 586 | 사건 타임라인 | `timeline` | 타임라인 |
| 587 | 용의자 | `suspect` | 용의자 |
| 588 | 피해자 | `victim` | 피해자 |
| 589 | 목격자 | `witness` | 목격자 |
| 590 | 전문가 분석 | `expert_analysis` | 분석 |

---

## 60. 🎯 Final Master List (마스터 리스트)

| # | Effect | `cut.type` | Signature |
|---|---|---|---|
| 591 | 마스터 타이틀 | `master_title` | 타이틀 |
| 592 | 마스터 로어서드 | `master_lower_third` | 로어서드 |
| 593 | 마스터 차트 | `master_chart` | 차트 |
| 594 | 마스터 지도 | `master_map` | 지도 |
| 595 | 마스터 타임라인 | `master_timeline` | 타임라인 |
| 596 | 마스터 카운트 | `master_count` | 카운트 |
| 597 | 마스터 알림 | `master_alert` | 알림 |
| 598 | 마스터 전환 | `master_transition` | 전환 |
| 599 | 마스터 엔딩 | `master_ending` | 엔딩 |
| 600 | 마스터 인트로 | `master_intro` | 인트로 |

---

## Implementation Status

**Already implemented (Remotion components):**
`news_breaking`, `scoreboard`, `countdown_timer`, `lower_third`, `quiz_card`, `weather_card`, `vhs_glitch`, `crt_scanlines`, `film_grain`, `poll_card`, `end_credits`, `breaking_alert`, `matrix_rain`, `animated_counter`, `animated_text`, `gradient_transition`, `typewriter_bits`, `particle_scene`, `typewriter`, `kinetic_type`, `editorial_slide`, `word_pop_caption`, `audio_waveform`, `split_screen`, `social_quote`, `device_mockup`, `geo_route`, `text_card`, `stat_card`, `callout`, `comparison`, `bar_chart`, `line_chart`, `pie_chart`, `kpi_grid`, `progress_bar`, `hero_title`, `anime_scene`, `terminal_scene`, `screenshot_scene`, `section_title`, `stat_reveal`, `provider_chip`, `end_tag`, `product_reveal`, `collage_burst`, `lyric_overlay`, `titled_video`, `talking_head`, `cinematic_renderer`.

**Composable via FFmpeg (no component needed):**
`letterbox`, `vignette`, `film_grain`, `sepia_tone`, `black_white`, `color_grade`, `slow_motion`, `fast_motion`, `pixelate`, `mosaic`, `zoom_in`, `zoom_out`, `pan_left`, `pan_right`, `ken_burns`, `fade`, `dissolve`, `wipe`, `slide`, `spin`, `flip`.

**Planned (next batch):**
`stock_ticker`, `news_ticker`, `player_card`, `leaderboard`, `notification_popup`, `chat_bubble`, `reaction_emoji`, `subscribe_button`, `neon_sign`, `polaroid_frame`, `tv_static`, `game_over`, `arcade_score`, `level_up`, `achievement`, `confetti`, `fireworks`, `logo_reveal`, `testimonial`, `flashcard`, `definition_card`, `timeline`, `year_counter`, `constellation`, `orbit`, `dna_helix`, `price_tag`, `discount_badge`, `cta_button`, `star_rating`, `flashback`, `dream_sequence`, `location_card`, `cliffhanger`, `glitch_art`, `kaleidoscope`, `particle_system`, `double_exposure`, `podcast_cover`, `guest_intro`, `episode_number`, `sponsor_banner`, `live_indicator`, `streamer_overlay`, `chat_overlay`, `sub_alert`, `donation_alert`, `kill_feed`, `minimap`, `hp_bar`, `xp_bar`, `calendar`, `deadline`, `typing_indicator`, `read_receipt`, `voice_message`, `video_call`, `streak`, `rank_up`, `points_earned`, `mission_complete`, `reward`, `challenge`, `collage`, `panorama`, `slideshow`, `grid_gallery`, `lightbox`, `glitch_transition`, `smash_cut`, `match_cut`, `like_button`, `comment_cta`, `share_button`, `download_button`, `signup_button`, `buy_button`, `contact_button`, `follow_button`, `election_results`, `weather_map`, `traffic_info`, `exchange_rate`, `news_headline`, `live_badge`, `station_logo`, `stage_clear`, `one_up`, `combo`, `high_score`, `coin_count`, `boss_warning`, `app_icon`, `swipe`, `tab_switch`, `scroll`, `pull_to_refresh`, `toast_notification`, `modal`, `onboarding`, `recipe_card`, `workout_routine`, `travel_itinerary`, `lookbook`, `beauty_tutorial`, `car_review`, `real_estate`, `finance`, `health`, `legal`, `text_3d`, `neon_text`, `metal_text`, `gradient_text`, `outline_text`, `shadow_text`, `glitch_text`, `wave_text`, `scramble_text`, `morph_text`, `chart_3d`, `animated_chart`, `live_chart`, `bubble_chart`, `radar_chart`, `gantt_chart`, `sankey`, `histogram`, `anamorphic`, `lens_flare`, `bokeh`, `tilt_shift`, `timelapse`, `drone_shot`, `handheld`, `steadicam`, `crane_shot`, `gold_chart`, `draft`, `mvp`, `victory_screen`, `defeat_screen`, `team_fight`, `objective`, `hook_title`, `swipe_up`, `duet`, `stitch`, `greenscreen`, `trend_sound`, `pov`, `archive_footage`, `reenactment`, `photo_archive`, `expert_interview`, `conclusion`, `spring`, `easing`, `liquid`, `smoke`, `fire`, `water`, `electric`, `magic`, `next_preview`, `thank_you`, `logo_outro`, `social_links`, `playlist`, `channel_intro`, `thanks_watching`, `news_opening`, `news_closing`, `weather_opening`, `sports_opening`, `breaking_interrupt`, `ad_break`, `program_preview`, `ratings`, `closed_caption`, `sign_language`, `quest_log`, `skill_tree`, `equipment`, `shop`, `dialogue_choice`, `minigame`, `save_point`, `checkpoint`, `cutscene`, `dashboard`, `report`, `insight`, `forecast`, `segment`, `funnel`, `cohort`, `brand_intro`, `brand_outro`, `logo_animation`, `product_showcase`, `brand_values`, `brand_tone`, `brand_font`, `brand_icon`, `urgency`, `scarcity`, `authority`, `likability`, `consistency`, `reciprocity`, `commitment`, `contrast`, `montage`, `jump_cut`, `cross_cut`, `flashforward`, `freeze_frame`, `minimal`, `maximal`, `flat`, `three_d`, `skeuomorphic`, `glassmorphism`, `neobrutalism`, `dark_mode`, `light_mode`, `gradient`, `youtube_ui`, `tiktok_ui`, `instagram_ui`, `twitter_ui`, `facebook_ui`, `linkedin_ui`, `snapchat_ui`, `pinterest_ui`, `reddit_ui`, `discord_ui`, `anchor_desk`, `live_remote`, `correspondent`, `press_conference`, `poll_results`, `suspect`, `victim`, `witness`, `expert_analysis`.

---

## Total: 600+ catalogued effects (with 1000+ variants via parameterization)

Each effect can be further customized through parameters (colors, fonts, timing, layout, animation style), yielding **1000+ distinct visual templates**.
