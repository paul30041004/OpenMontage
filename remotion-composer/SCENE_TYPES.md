# Remotion Composer — Scene & Overlay Cheat Sheet

Authoritative list of `cut.type` and `overlay.type` values the `Explainer` composition accepts. Each row maps to a dispatch case in `src/Explainer.tsx`.

When you add a new component, append it here and in `src/components/index.ts`.

---

## Cut types (`cut.type`)

| `type` | Component | Required fields | Common fields | Purpose |
|---|---|---|---|---|
| *(none — video)* | `OffthreadVideo` | `source` (path to mp4) | `source_in_seconds`, `animation` (zoom-in, ken-burns), `in_seconds`, `out_seconds` | Play an MP4 clip directly |
| *(none — image)* | `Img` | `source` (path to png/jpg) | `animation`, `in_seconds`, `out_seconds` | Play a still with Ken Burns |
| `text_card` | `TextCard` | `text` | `fontSize`, `backgroundVideo`, `backgroundOverlay`, `color` | Large-typography beat |
| `hero_title` | `HeroTitle` | `text` | `heroSubtitle`, `backgroundVideo`, `backgroundOverlay` | Title/end card |
| `stat_card` | `StatCard` | `stat` | `subtitle`, `accentColor`, `backgroundVideo` | A single big number |
| `callout` | `CalloutBox` | `text` | `callout_type` (info/warning/tip/quote), `title`, `backgroundVideo` | Boxed message with bullets |
| `comparison` | `ComparisonCard` | `leftLabel`, `leftValue`, `rightLabel`, `rightValue` | `title`, `backgroundColor` | Side-by-side compare |
| `bar_chart` | `BarChart` | `chartData` | `chartAnimation`, `showValues`, `showGrid`, `backgroundVideo` | Animated bars |
| `line_chart` | `LineChart` | `chartSeries` | `chartAnimation`, `xLabel`, `yLabel`, `showMarkers` | Animated line |
| `pie_chart` | `PieChart` | `chartData` | `donut`, `centerLabel`, `centerValue`, `showLegend` | Pie / donut |
| `kpi_grid` | `KPIGrid` | `chartData` | `title`, `columns`, `chartAnimation` | 2–4 column KPI grid |
| `progress_bar` | `ProgressBar` | `progress` | `progressLabel`, `progressColor`, `progressSegments` | Animated progress |
| `anime_scene` | `AnimeScene` | `images` (list) | `particles`, `lightingFrom`, `lightingTo`, `vignette` | Still-image anime scene with particles + camera motion |
| **`terminal_scene`** | **`TerminalScene`** | **`steps`** (list of cmd/out/pause/pill) | **`terminalTitle`, `prompt`, `accentColor`** | **Synthetic terminal animation — NO real capture needed. See [`.agents/skills/synthetic-screen-recording/SKILL.md`](../.agents/skills/synthetic-screen-recording/SKILL.md)** |
| **`screenshot_scene`** | **`ScreenshotScene`** | **`backgroundImage`** (path in `public/`), **`screenshotSteps`** (list of overlays) | **`screenshotSize` (natural px w/h), `cursorStartAt`, `accentColor`** | **Approach-1 synthetic UI — drop any screenshot, animate scripted overlays on top.** |
| **`audio_waveform`** | **`AudioWaveformVisualizer`** | **`title`** | **`subtitle`, `waveColor`, `accentColor`, `barCount`, `styleMode`** | **Procedural audio-reactive sound spectrum visualizer for podcasts & music** |
| **`split_screen`** | **`SplitScreen`** | **`left`, `right`** | **`title`, `orientation`, `dividerColor`** | **Dynamic 2-way side-by-side comparison with animated dividing border** |
| **`social_quote`** | **`SocialQuoteCard`** | **`quoteText`** | **`authorName`, `authorHandle`, `avatarUrl`, `highlightWords`, `verified`** | **Viral social quote card (Twitter/X style with verified badge & metrics)** |
| **`device_mockup`** | **`DeviceMockup`** | *(none)* | **`deviceType` (smartphone/laptop), `screenMediaUrl`, `title`, `accentColor`** | **3D floating smartphone / laptop device mockup with glass reflection** |
| **`geo_route`** | **`GeoRouteMap`** | **`waypoints`** (list of name, x, y) | **`title`, `accentColor`, `pathColor`** | **Animated geographic expedition path tracer with pulsing GPS pins** |
| **`typewriter`** | **`TypewriterText`** | **`text`** | **`title`, `subtitle`, `charsPerSecond`, `cursorColor`, `showCursor`, `align`** | **Character-by-character typing animation with blinking cursor — e-knowledge-channel style** |
| **`kinetic_type`** | **`KineticTypography`** | **`lines`** (list of strings) | **`title`, `highlightWords`, `staggerFrames`, `align`** | **Word-by-word staggered kinetic typography with spring pop-in** |
| **`editorial_slide`** | **`EditorialSlide`** | **`headline`** | **`body`, `kicker`, `footnote`, `layout` (centered/left-aligned/magazine), `headlineFont`, `bodyFont`** | **Magazine-style editorial layout slide with serif headline + rule line** |
| **`word_pop_caption`** | **`WordPopCaption`** | **`words`** (list of word/startMs/endMs) | **`maxWordsPerLine`, `highlightColor`, `bottomPadding`** | **TikTok-style word pop-up captions with scale spring on active word** |
| **`news_breaking`** | **`NewsBreaking`** | **`headline`** | **`subheadline`, `category`, `timeText`, `tickerItems`, `showBreakingBanner`, `showLowerThird`, `showTicker`** | **뉴스속보 스타일 — BREAKING 배너, 대형 헤드라인, 하단 티커 스크롤** |
| **`scoreboard`** | **`Scoreboard`** | **`homeTeam`, `awayTeam`** | **`homeScore`, `awayScore`, `periodLabel`, `timeText`, `homeColor`, `awayColor`** | **스포츠 중계 스코어보드 — 팀/점수/쿼터/타이머** |
| **`countdown_timer`** | **`CountdownTimer`** | **`fromSeconds`** | **`label`, `showProgressRing`, `accentColor`** | **카운트다운 타이머 — 프로그레스 링 + 숫자 펄스** |
| **`lower_third`** | **`LowerThird`** | **`name`** | **`title`, `position` (bottom-left/right/center), `accentColor`** | **방송 로어서드 — 이름/직함 하단 표기** |
| **`quiz_card`** | **`QuizCard`** | **`question`, `options`** | **`correctIndex`, `revealAnswer`, `accentColor`** | **퀴즈쇼 문제 카드 — 질문 + 보기 4개 + 정답 공개** |
| **`weather_card`** | **`WeatherCard`** | **`city`** | **`temperature`, `condition`, `icon`, `highTemp`, `lowTemp`** | **날씨 예보 카드 — 기온/아이콘/주간 예보** |
| **`vhs_glitch`** | **`VHSGlitch`** | *(none)* | **`intensity`, `accentColor`** | **VHS 글리치 — 트래킹 노이즈, RGB 분리, 타임스탬프** |
| **`crt_scanlines`** | **`CRTScanlines`** | *(none)* | **`scanlineOpacity`, `curvature`, `showFlicker`** | **CRT 스캔라인 — 스캔라인 + RGB 인광 마스크 + 곡률** |
| **`film_grain`** | **`FilmGrain`** | *(none)* | **`intensity`, `monochrome`** | **필름 그레인 — 노이즈 텍스처 오버레이** |
| **`poll_card`** | **`PollCard`** | **`question`, `pollOptions`** | **`accentColor`** | **인스타 스토리 폴 — 투표 UI + 퍼센트 바** |
| **`end_credits`** | **`EndCredits`** | **`title`, `credits`** | **`scrollSpeed`, `accentColor`** | **엔드 크레딧 — 롤링 크레딧 스크롤** |
| **`breaking_alert`** | **`BreakingAlert`** | **`headline`** | **`subheadline`, `accentColor`** | **긴급 속보 알림 — 화면 중앙 경고 팝업** |
| **`matrix_rain`** | **`MatrixRainScene`** (remotion-bits) | *(none)* | **`matrixColor`, `matrixSpeed`, `matrixDensity`, `matrixStreamLength`** | **매트릭스 디지털 레인 — 떨어지는 코드 문자** |
| **`animated_counter`** | **`AnimatedCounterScene`** (remotion-bits) | **`counterTo`** | **`counterFrom`, `counterPrefix`, `counterPostfix`, `counterToFixed`** | **숫자 카운트업 (remotion-bits AnimatedCounter)** |
| **`animated_text`** | **`AnimatedTextScene`** (remotion-bits) | **`text`** | **`split` (word/character/line), `splitStagger`, `glitch`** | **단어/문자 스태거 + 글리치 텍스트 애니메이션** |
| **`gradient_transition`** | **`GradientTransitionScene`** (remotion-bits) | **`gradients`** | *(none)* | **Oklch 지각 균일 그라디언트 전환** |
| **`typewriter_bits`** | **`TypeWriterScene`** (remotion-bits) | **`text`** | **`typeSpeed`, `errorRate`, `cursorColor`** | **타이핑 + 오타 시뮬레이션 + 커서 (remotion-bits TypeWriter)** |
| **`particle_scene`** | **`ParticleScene`** (remotion-bits) | *(none)* | **`bitsParticleType` (fireflies/snow/fountain/grid/confetti), `bitsParticleCount`** | **파티클 시스템 — 반딧불/눈/분수/그리드/컨페티** |
| **`cctv_camera`** | **`CCTVCamera`** | *(none)* | **`cameraId`, `location`, `matrixColor`, `matrixSpeed`, `showRecIndicator`, `showCornerBrackets`, `showScanlines`, `showTimestamp`** | **매트릭스 CCTV 감시 카메라 — 매트릭스 레인 + REC + 타임스탬프 + 코너 브래킷** |
| **`cut_black`** | **`CutBlack`** | *(none)* | **`text`, `subtitle`, `holdSeconds`, `fadeOutSeconds`** | **컷블랙 — 절정에서 과감히 끊고 검은 화면으로 페이드아웃 (상상력 극대화)** |
| **`reaction_emoji`** | **`ReactionEmoji`** | *(none)* | **`emoji`, `emojiCount`, `emojiPosition`, `emojiSize`** | **반응 이모지 팝 — ❤️/👍 + 카운트 + 스프링 팝 + 플로팅** |
| **`text_3d`** | **`Text3D`** | **`text`** | **`shadowColor`, `depth`, `rotateX`, `rotateY`, `float`** | **3D 입체 텍스트 — 레이어드 그림자 + 회전 + 플로팅** |
| **`chat_bubble`** | **`ChatBubble`** | **`messages`** | **`accentColor`, `chatStaggerFrames`** | **채팅 버블 — 메신저 대화 UI (송/수신 + 아바타)** |
| **`subscribe_button`** | **`SubscribeButton`** | *(none)* | **`channelName`, `subscriberCount`, `position`, `accentColor`** | **유튜브 구독 버튼 — 채널 아바타 + 구독 CTA + 펄스** |
| **`neon_text`** | **`NeonText`** | **`text`** | **`accentColor`, `flicker`, `glowIntensity`** | **네온 사인 텍스트 — 다중 글로우 + 플리커** |
| **`notification_popup`** | **`NotificationPopup`** | *(none)* | **`title`, `message`, `appName`, `appIcon`, `position`** | **푸시 알림 팝업 — 글래스모피즘 + 슬라이드 인** |
| **`like_button`** | **`LikeButton`** | *(none)* | **`emoji`, `emojiCount`, `position`, `burst`** | **좋아요 버튼 — 👍 + 카운트 + 파티클 버스트** |
| **`hashtag_overlay`** | **`HashtagOverlay`** | **`hashtags`** | **`position`, `hashtagStaggerFrames`, `accentColor`** | **해시태그 오버레이 — 태그 스태거 팝인** |
| **`flashback`** | **`Flashback`** | *(none)* | **`title`, `sepiaAmount`, `blurAmount`, `accentColor`** | **회상 장면 — 세피아 + 블러 + 웨이브 테두리** |
| **`location_card`** | **`LocationCard`** | **`location`** | **`locationDate`, `align`, `accentColor`** | **장소 표시 카드 — 위치 + 날짜 (드라마/다큐)** |
| **`cliffhanger`** | **`Cliffhanger`** | *(none)* | **`title`, `subtitle`, `accentColor`, `fadeOutSeconds`** | **클리프행어 — "다음 편에 계속" + 페이드아웃** |

---

## Overlay types (`overlay.type`)

| `type` | Component | Required fields | Common fields | Purpose |
|---|---|---|---|---|
| `section_title` | `SectionTitle` | `text` | `accentColor`, `position` (top-left, etc.) | Tiny section label |
| `stat_reveal` | `StatReveal` | `text` | `subtitle`, `accentColor`, `position` | Corner stat badge |
| `hero_title` | `HeroTitle` (as overlay) | `text` | `subtitle` | Full-frame title overlay |
| **`provider_chip`** | **`ProviderChip`** | **`providers`** (list of strings) | **`cycleSeconds`, `position`, `accentColor`, `label`** | **Rotating badge that cycles through provider names — used in AI-generated-motion scenes to show which model produced the clip** |

---

## Adding a new scene type

1. Create the React component in `src/components/MyScene.tsx`. Use `interpolate(frame, [inFrame, outFrame], [from, to])` and `spring(...)` for motion. Read `useCurrentFrame()` and `useVideoConfig()`.
2. Export it in `src/components/index.ts`.
3. Add the `type` to the `Cut` interface in `src/Explainer.tsx` (and any new prop fields).
4. Add a dispatch case in `SceneRenderer`:
   ```tsx
   if (cut.type === "my_scene" && cut.mySceneData) {
     return maybeWrapWithBg(<MyScene ... />);
   }
   ```
5. Document it in this file. That's what makes it discoverable to the next agent.

## Existing synthetic-UI components

Currently only `TerminalScene` exists. The pattern generalizes — likely candidates to add next, if a pipeline needs them:

- `ChatTranscript` — Claude/Cursor/GPT chat-bubble timeline with typing animation
- `EditorScene` — VS Code-style code editor with syntax highlight + cursor motion
- `PrReview` — GitHub PR diff view with inline-comment reveals
- `SlackThread` — Slack thread with avatars + reaction pops
- `TicketBoard` — Jira / Linear card moving across columns

Pattern: follow `TerminalScene.tsx` — a `steps` list of timeline primitives, cursor-advancing durations, spring-based reveals, optional non-blocking pills/badges.
