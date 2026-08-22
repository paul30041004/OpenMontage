import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SpaceGrotesk";
import { TextCard } from "./components/TextCard";
import { StatCard } from "./components/StatCard";
import { CalloutBox } from "./components/CalloutBox";
import { ComparisonCard } from "./components/ComparisonCard";
import { BarChart } from "./components/charts/BarChart";
import { LineChart } from "./components/charts/LineChart";
import { PieChart } from "./components/charts/PieChart";
import { KPIGrid } from "./components/charts/KPIGrid";
import { ProgressBar } from "./components/ProgressBar";
import { CaptionOverlay, WordCaption } from "./components/CaptionOverlay";
import { SectionTitle } from "./components/SectionTitle";
import { StatReveal } from "./components/StatReveal";
import { HeroTitle } from "./components/HeroTitle";
import { AnimeScene } from "./components/AnimeScene";
import type { CameraMotion } from "./components/AnimeScene";
import { TerminalScene } from "./components/TerminalScene";
import type { TerminalStep } from "./components/TerminalScene";
import { ScreenshotScene } from "./components/ScreenshotScene";
import type { ScreenshotStep } from "./components/ScreenshotScene";
import { ProviderChip } from "./components/ProviderChip";
import { AudioWaveformVisualizer } from "./components/AudioWaveformVisualizer";
import { SplitScreen } from "./components/SplitScreen";
import { SocialQuoteCard } from "./components/SocialQuoteCard";
import { DeviceMockup } from "./components/DeviceMockup";
import { GeoRouteMap } from "./components/GeoRouteMap";
import { TypewriterText } from "./components/TypewriterText";
import { KineticTypography } from "./components/KineticTypography";
import { EditorialSlide } from "./components/EditorialSlide";
import { WordPopCaption } from "./components/WordPopCaption";
import { NewsBreaking } from "./components/NewsBreaking";
import { Scoreboard } from "./components/Scoreboard";
import { CountdownTimer } from "./components/CountdownTimer";
import { LowerThird } from "./components/LowerThird";
import { QuizCard } from "./components/QuizCard";
import { WeatherCard } from "./components/WeatherCard";
import { VHSGlitch } from "./components/VHSGlitch";
import { CRTScanlines } from "./components/CRTScanlines";
import { FilmGrain } from "./components/FilmGrain";
import { PollCard } from "./components/PollCard";
import { EndCredits } from "./components/EndCredits";
import { BreakingAlert } from "./components/BreakingAlert";
import { CCTVCamera } from "./components/CCTVCamera";
import { CutBlack } from "./components/CutBlack";
import { ReactionEmoji } from "./components/ReactionEmoji";
import { Text3D } from "./components/Text3D";
import { ChatBubble } from "./components/ChatBubble";
import { SubscribeButton } from "./components/SubscribeButton";
import { NeonText } from "./components/NeonText";
import { NotificationPopup } from "./components/NotificationPopup";
import { LikeButton } from "./components/LikeButton";
import { HashtagOverlay } from "./components/HashtagOverlay";
import { Flashback } from "./components/Flashback";
import { LocationCard } from "./components/LocationCard";
import { Cliffhanger } from "./components/Cliffhanger";
import {
  MatrixRainScene,
  AnimatedCounterScene,
  AnimatedTextScene,
  GradientTransitionScene,
  TypeWriterScene,
  ParticleScene,
} from "./components/RemotionBitsScenes";
import { resolveAsset } from "./lib/resolveAsset";
import type { ParticleType } from "./components/ParticleOverlay";
import { resolveTheme, type ThemeConfig, DEFAULT_THEME } from "./Root";

// Load Space Grotesk font for cinematic typography
const { fontFamily } = loadFont("normal", {
  weights: ["400", "700"],
  subsets: ["latin"],
});

// ---------------------------------------------------------------------------
// Animated Background — Gradient Mesh + Floating Orbs
// ---------------------------------------------------------------------------

// Parse hex color to RGB components
function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const clean = hex.replace("#", "");
  const bigint = parseInt(clean.length === 3
    ? clean.split("").map(c => c + c).join("")
    : clean, 16);
  return { r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 };
}

// Detect if a color is "light" (for choosing grid/overlay treatment)
function isLightColor(hex: string): boolean {
  const { r, g, b } = hexToRgb(hex);
  return (r * 299 + g * 587 + b * 114) / 1000 > 128;
}

// Scrim painted behind a hero title. It has to wash *away* from the theme's
// text color: a dark scrim under a light theme's dark text drops the pair to
// ~3.4:1, which is the same legibility bug in reverse.
function heroScrim(theme: ThemeConfig): string {
  const { r, g, b } = hexToRgb(
    isLightColor(theme.backgroundColor) ? "#FFFFFF" : "#0F172A"
  );
  return (
    `radial-gradient(ellipse at center, rgba(${r},${g},${b},0.35) 0%, ` +
    `rgba(${r},${g},${b},0.55) 100%)`
  );
}

// Darken/lighten a color by mixing toward black or white
function shiftColor(hex: string, amount: number): string {
  const { r, g, b } = hexToRgb(hex);
  const clamp = (v: number) => Math.max(0, Math.min(255, Math.round(v)));
  if (amount < 0) {
    // Darken
    const f = 1 + amount;
    return `rgb(${clamp(r * f)}, ${clamp(g * f)}, ${clamp(b * f)})`;
  }
  // Lighten
  return `rgb(${clamp(r + (255 - r) * amount)}, ${clamp(g + (255 - g) * amount)}, ${clamp(b + (255 - b) * amount)})`;
}

const AnimatedBackground: React.FC<{ theme: ThemeConfig }> = ({ theme }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const bg = theme.backgroundColor;
  const primary = theme.primaryColor;
  const accent = theme.accentColor;
  const surface = theme.surfaceColor;
  const light = isLightColor(bg);

  // Slow-moving gradient angles
  const angle1 = 135 + Math.sin(frame / (fps * 8)) * 30;

  // Build gradient from theme colors instead of hardcoded dark blue
  const { r: bgR, g: bgG, b: bgB } = hexToRgb(bg);
  const { r: priR, g: priG, b: priB } = hexToRgb(primary);
  const { r: accR, g: accG, b: accB } = hexToRgb(accent);

  const gradient = `
    radial-gradient(ellipse at ${30 + Math.sin(frame / (fps * 10)) * 20}% ${40 + Math.cos(frame / (fps * 8)) * 20}%,
      rgba(${priR}, ${priG}, ${priB}, 0.15) 0%, transparent 60%),
    radial-gradient(ellipse at ${70 + Math.cos(frame / (fps * 7)) * 20}% ${60 + Math.sin(frame / (fps * 9)) * 25}%,
      rgba(${accR}, ${accG}, ${accB}, 0.1) 0%, transparent 55%),
    linear-gradient(${angle1}deg, ${bg} 0%, ${shiftColor(bg, light ? -0.05 : 0.05)} 40%, ${surface} 70%, ${bg} 100%)
  `;

  // Floating orbs — derived from theme chart colors with low opacity
  const orbColors = theme.chartColors.slice(0, 5);
  const orbOpacity = light ? 0.06 : 0.08;
  const orbs = [
    { x: 20, y: 30, size: 300, color: orbColors[0] || primary, speedX: 7, speedY: 11 },
    { x: 70, y: 60, size: 250, color: orbColors[1] || accent, speedX: 9, speedY: 8 },
    { x: 40, y: 80, size: 200, color: orbColors[2] || primary, speedX: 13, speedY: 6 },
    { x: 80, y: 20, size: 350, color: orbColors[3] || accent, speedX: 11, speedY: 14 },
    { x: 10, y: 70, size: 180, color: orbColors[4] || primary, speedX: 8, speedY: 10 },
  ];

  // Grid and overlay colors adapt to light vs dark backgrounds
  const gridColor = light ? "rgba(0,0,0,0.03)" : "rgba(255,255,255,0.02)";
  const fadeColor = light
    ? `rgba(${bgR},${bgG},${bgB},0.2)`
    : `rgba(${bgR},${bgG},${bgB},0.4)`;

  return (
    <AbsoluteFill style={{ background: gradient }}>
      {/* Floating glow orbs */}
      {orbs.map((orb, i) => {
        const ox = orb.x + Math.sin(frame / (fps * orb.speedX)) * 15;
        const oy = orb.y + Math.cos(frame / (fps * orb.speedY)) * 12;
        const { r, g, b } = hexToRgb(orb.color);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${ox}%`,
              top: `${oy}%`,
              width: orb.size,
              height: orb.size,
              borderRadius: "50%",
              background: `rgba(${r}, ${g}, ${b}, ${orbOpacity})`,
              filter: `blur(${orb.size * 0.4}px)`,
              transform: "translate(-50%, -50%)",
              willChange: "transform",
            }}
          />
        );
      })}

      {/* Subtle grid overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            linear-gradient(${gridColor} 1px, transparent 1px),
            linear-gradient(90deg, ${gridColor} 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
          opacity: 0.5 + Math.sin(frame / (fps * 20)) * 0.2,
        }}
      />

      {/* Top gradient fade for depth */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "30%",
          background: `linear-gradient(to bottom, ${fadeColor}, transparent)`,
        }}
      />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Types — aligned with edit_decisions artifact schema
// ---------------------------------------------------------------------------

interface Cut {
  id: string;
  source: string;
  in_seconds: number;
  out_seconds: number;
  layer?: string;
  type?: string;
  // Component-specific props
  text?: string;
  stat?: string;
  subtitle?: string;
  callout_type?: "info" | "warning" | "tip" | "quote";
  title?: string;
  // Video source trim — seek to this point in the source before playback.
  // Defaults to 0 (play from beginning). Use this instead of in_seconds for source trimming.
  source_in_seconds?: number;
  // Comparison props
  leftLabel?: string;
  rightLabel?: string;
  leftValue?: string;
  rightValue?: string;
  // Chart props
  chartData?: any[];
  chartSeries?: any[];
  chartColors?: string[];
  chartAnimation?: string;
  donut?: boolean;
  centerLabel?: string;
  centerValue?: string;
  showGrid?: boolean;
  showValues?: boolean;
  showLegend?: boolean;
  showMarkers?: boolean;
  xLabel?: string;
  yLabel?: string;
  columns?: 2 | 3 | 4;
  // Progress bar props
  progress?: number;
  progressLabel?: string;
  progressColor?: string;
  progressAnimation?: string;
  progressSegments?: any[];
  // Hero title props (when used as scene, not overlay)
  heroSubtitle?: string;
  // Styling overrides
  backgroundColor?: string;
  cardBackgroundColor?: string; // Inner card surface (comparison); defaults to theme.surfaceColor
  backgroundImage?: string; // AI-generated or stock image rendered behind the component
  backgroundVideo?: string; // Video clip rendered behind the component (takes priority over backgroundImage)
  backgroundVideoStart?: number; // Seek position in seconds for background video (default 0)
  backgroundOverlay?: number; // Opacity of dark overlay on backgroundImage/backgroundVideo (0-1, default 0.55)
  color?: string;
  accentColor?: string;
  fontSize?: number;
  // Animation & transitions
  animation?: string;
  transition_in?: string;
  transition_out?: string;
  transition_duration?: number;
  transform?: {
    animation?: string;
    scale?: number;
    position?: string | { x: number; y: number };
  };
  // Anime scene props (type: "anime_scene")
  images?: string[];
  particles?: ParticleType;
  particleColor?: string;
  particleCount?: number;
  particleIntensity?: number;
  vignette?: boolean;
  lightingFrom?: string;
  lightingTo?: string;
  // Terminal scene props (type: "terminal_scene")
  steps?: TerminalStep[];
  terminalTitle?: string;
  prompt?: string;
  // Screenshot scene props (type: "screenshot_scene")
  screenshotSteps?: ScreenshotStep[];
  screenshotSize?: { width: number; height: number };
  cursorStartAt?: [number, number];
  // Audio waveform props (type: "audio_waveform")
  waveColor?: string;
  barCount?: number;
  styleMode?: "bars" | "circle" | "mirror";
  // Split screen props (type: "split_screen")
  left?: any;
  right?: any;
  orientation?: "horizontal" | "vertical";
  dividerColor?: string;
  // Social quote props (type: "social_quote")
  authorName?: string;
  authorHandle?: string;
  avatarUrl?: string;
  quoteText?: string;
  highlightWords?: string[];
  verified?: boolean;
  dateText?: string;
  likesCount?: string;
  retweetsCount?: string;
  // Device mockup props (type: "device_mockup")
  deviceType?: "smartphone" | "laptop";
  screenMediaUrl?: string;
  screenMediaType?: "video" | "image";
  // Geo route map props (type: "geo_route")
  waypoints?: any[];
  pathColor?: string;
  // Typewriter props (type: "typewriter")
  charsPerSecond?: number;
  startDelaySeconds?: number;
  showCursor?: boolean;
  cursorColor?: string;
  align?: "left" | "center" | "right";
  // Kinetic typography props (type: "kinetic_type")
  lines?: string[];
  staggerFrames?: number;
  // Editorial slide props (type: "editorial_slide")
  headline?: string;
  body?: string;
  kicker?: string;
  footnote?: string;
  headlineFont?: string;
  bodyFont?: string;
  layout?: "centered" | "left-aligned" | "magazine";
  headlineSize?: number;
  bodySize?: number;
  showRule?: boolean;
  // Word pop caption props (type: "word_pop_caption")
  maxWordsPerLine?: number;
  bottomPadding?: number;
  words?: { word: string; startMs: number; endMs: number }[];
  // News breaking props (type: "news_breaking")
  subheadline?: string;
  category?: string;
  timeText?: string;
  headlineColor?: string;
  showBreakingBanner?: boolean;
  showLowerThird?: boolean;
  showTicker?: boolean;
  tickerItems?: string[];
  // Scoreboard props (type: "scoreboard")
  homeTeam?: string;
  awayTeam?: string;
  homeScore?: number;
  awayScore?: number;
  periodLabel?: string;
  homeColor?: string;
  awayColor?: string;
  // Countdown timer props (type: "countdown_timer")
  fromSeconds?: number;
  showProgressRing?: boolean;
  // Lower third props (type: "lower_third")
  name?: string;
  position?: "bottom-left" | "bottom-right" | "bottom-center";
  // Quiz card props (type: "quiz_card")
  question?: string;
  options?: string[];
  correctIndex?: number;
  revealAnswer?: boolean;
  // Weather card props (type: "weather_card")
  city?: string;
  temperature?: number;
  condition?: string;
  icon?: string;
  highTemp?: number;
  lowTemp?: number;
  // VHS glitch props (type: "vhs_glitch")
  intensity?: number;
  // CRT scanlines props (type: "crt_scanlines")
  scanlineOpacity?: number;
  curvature?: number;
  showFlicker?: boolean;
  // Film grain props (type: "film_grain")
  monochrome?: boolean;
  // Poll card props (type: "poll_card")
  pollOptions?: { label: string; percentage: number }[];
  // End credits props (type: "end_credits")
  credits?: { role: string; name: string }[];
  scrollSpeed?: number;
  // Breaking alert props (type: "breaking_alert")
  // (reuses headline/subheadline/accentColor)
  // remotion-bits props
  matrixColor?: string;
  matrixSpeed?: number;
  matrixDensity?: number;
  matrixStreamLength?: number;
  counterFrom?: number;
  counterTo?: number;
  counterPrefix?: string;
  counterPostfix?: string;
  counterToFixed?: number;
  split?: "none" | "word" | "character" | "line";
  splitStagger?: number;
  glitch?: boolean;
  gradients?: string[];
  typeSpeed?: number;
  errorRate?: number;
  bitsParticleType?: "fireflies" | "snow" | "fountain" | "grid" | "confetti";
  bitsParticleCount?: number;
  // CCTV camera props (type: "cctv_camera")
  cameraId?: string;
  location?: string;
  showRecIndicator?: boolean;
  showCornerBrackets?: boolean;
  showScanlines?: boolean;
  showTimestamp?: boolean;
  showCameraId?: boolean;
  cctvVideoSrc?: string;
  greenTint?: number;
  // Cut black props (type: "cut_black")
  holdSeconds?: number;
  fadeOutSeconds?: number;
  // Reaction emoji props (type: "reaction_emoji")
  emoji?: string;
  emojiCount?: string;
  emojiPosition?: "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center";
  emojiSize?: number;
  // Text 3D props (type: "text_3d")
  shadowColor?: string;
  depth?: number;
  rotateX?: number;
  rotateY?: number;
  float?: boolean;
  // Chat bubble props (type: "chat_bubble")
  messages?: { text: string; sender?: string; avatar?: string; isMe?: boolean }[];
  chatStaggerFrames?: number;
  // Subscribe button props (type: "subscribe_button")
  channelName?: string;
  subscriberCount?: string;
  // Neon text props (type: "neon_text")
  flicker?: boolean;
  glowIntensity?: number;
  // Notification popup props (type: "notification_popup")
  message?: string;
  appName?: string;
  appIcon?: string;
  // Like button props (type: "like_button")
  // (reuses emoji/emojiCount/emojiPosition/emojiSize/position from reaction_emoji)
  burst?: boolean;
  // Hashtag overlay props (type: "hashtag_overlay")
  hashtags?: string[];
  hashtagStaggerFrames?: number;
  // Flashback props (type: "flashback")
  sepiaAmount?: number;
  blurAmount?: number;
  // Location card props (type: "location_card")
  locationDate?: string;
  // Cliffhanger props (type: "cliffhanger")
  // (reuses title/subtitle/accentColor)
}

interface Overlay {
  type: "section_title" | "stat_reveal" | "hero_title" | "provider_chip";
  in_seconds: number;
  out_seconds: number;
  text?: string;
  subtitle?: string;
  accentColor?: string;
  position?: string;
  // provider_chip
  providers?: string[];
  cycleSeconds?: number;
  label?: string;
}

interface AudioLayer {
  src: string;
  volume?: number;
}

interface AudioConfig {
  narration?: AudioLayer;
  music?: AudioLayer & {
    fadeInSeconds?: number;
    fadeOutSeconds?: number;
    /** Start playback from this offset in seconds (skip quiet intros).
     *  Use the audio_energy tool to find the optimal offset. */
    offsetSeconds?: number;
    /** Loop the music if it's shorter than the video duration. */
    loop?: boolean;
  };
}

export interface ExplainerProps {
  [key: string]: unknown;
  cuts: Cut[];
  overlays?: Overlay[];
  captions?: WordCaption[];
  audio?: AudioConfig;
}

// ---------------------------------------------------------------------------
// Image Extensions
// ---------------------------------------------------------------------------

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"];
const VIDEO_EXTENSIONS = [".mp4", ".mov", ".webm", ".avi", ".mkv"];

function isImage(source: string): boolean {
  const lower = source.toLowerCase();
  return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

function isVideo(source: string): boolean {
  const lower = source.toLowerCase();
  return VIDEO_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

// ---------------------------------------------------------------------------
// Cinematic vignette overlay
// ---------------------------------------------------------------------------

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.6) 100%)",
      pointerEvents: "none",
    }}
  />
);

// ---------------------------------------------------------------------------
// Enhanced Image Scene — spring physics, parallax, variety
// ---------------------------------------------------------------------------

const ImageScene: React.FC<{ src: string; animation?: string }> = ({
  src,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Smooth spring fade-in
  const fadeIn = spring({ frame, fps, config: { damping: 18, stiffness: 80 } });

  // Fade-out for crossfade effect
  const fadeOutStart = durationInFrames - 8;
  const fadeOut = interpolate(frame, [fadeOutStart, durationInFrames], [1, 0.3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  let scale = 1;
  let translateX = 0;
  let translateY = 0;
  const anim = animation || "zoom-in";

  // Progress with easing — smoother than linear
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  if (anim === "zoom-in") {
    scale = 1 + progress * 0.18;
  } else if (anim === "zoom-out") {
    scale = 1.18 - progress * 0.18;
  } else if (anim === "pan-left") {
    translateX = interpolate(progress, [0, 1], [40, -40]);
    scale = 1.15;
  } else if (anim === "pan-right") {
    translateX = interpolate(progress, [0, 1], [-40, 40]);
    scale = 1.15;
  } else if (anim === "ken-burns" || anim === "ken-burns-slow-zoom") {
    // Cinematic Ken Burns: gentle zoom + diagonal drift
    scale = 1 + progress * 0.22;
    translateX = interpolate(progress, [0, 1], [0, -25]);
    translateY = interpolate(progress, [0, 1], [0, -15]);
  } else if (anim === "parallax") {
    // Subtle parallax — foreground moves faster
    translateY = interpolate(progress, [0, 1], [15, -15]);
    scale = 1.1;
  }
  // "static" or "none" → just display

  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#0F172A" }}>
      <Img
        src={resolveAsset(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: fadeIn * fadeOut,
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          willChange: "transform, opacity",
        }}
      />
      <Vignette />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Enhanced Video Scene
// ---------------------------------------------------------------------------

const VideoScene: React.FC<{
  src: string;
  startFrom?: number;
  transitionIn?: string;
  transitionOut?: string;
  transitionDuration?: number;
  sceneDurationSeconds: number;
  backgroundColor?: string;
}> = ({
  src,
  startFrom = 0,
  transitionIn,
  transitionOut,
  transitionDuration,
  sceneDurationSeconds,
  backgroundColor = "#0F172A",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const durationInFrames = Math.max(1, Math.round(sceneDurationSeconds * fps));

  const hardIn = ["cut", "none"].includes((transitionIn || "").toLowerCase());
  const hardOut = ["cut", "none"].includes((transitionOut || "").toLowerCase());
  const transitionFrames = Math.max(
    1,
    Math.round((transitionDuration ?? 8 / fps) * fps),
  );
  const fadeIn = hardIn
    ? 1
    : interpolate(frame, [0, transitionFrames], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const fadeOutStart = Math.max(0, durationInFrames - transitionFrames);
  const fadeOut = hardOut
    ? 1
    : interpolate(frame, [fadeOutStart, durationInFrames], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  return (
    <AbsoluteFill style={{ background: backgroundColor }}>
      <OffthreadVideo
        src={resolveAsset(src)}
        startFrom={Math.round(startFrom * fps)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: fadeIn * fadeOut,
        }}
        muted
      />
      <Vignette />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Scene renderer — maps cut type / source to the right component
// ---------------------------------------------------------------------------

// Background image layer — renders an AI-generated/stock image behind data components
const BackgroundImageLayer: React.FC<{
  src: string;
  overlayOpacity?: number;
  children: React.ReactNode;
}> = ({ src, overlayOpacity = 0.55, children }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Subtle ken-burns on the background
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const bgScale = 1 + progress * 0.08;

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* Background image with subtle zoom */}
      <Img
        src={resolveAsset(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${bgScale})`,
          willChange: "transform",
        }}
      />
      {/* Dark overlay for readability */}
      <AbsoluteFill
        style={{
          background: `rgba(15, 23, 42, ${overlayOpacity})`,
        }}
      />
      {/* Component content on top */}
      {children}
    </AbsoluteFill>
  );
};

// Background video layer — plays a looping video behind component content with dark overlay
const BackgroundVideoLayer: React.FC<{
  src: string;
  startFrom?: number;
  overlayOpacity?: number;
  children: React.ReactNode;
}> = ({ src, startFrom = 0, overlayOpacity = 0.55, children }) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {/* Background video */}
      <OffthreadVideo
        src={resolveAsset(src)}
        startFrom={Math.round(startFrom * fps)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
        muted
      />
      {/* Dark overlay for readability */}
      <AbsoluteFill
        style={{
          background: `rgba(15, 23, 42, ${overlayOpacity})`,
        }}
      />
      {/* Component content on top */}
      {children}
    </AbsoluteFill>
  );
};

const SceneRenderer: React.FC<{ cut: Cut; theme: ThemeConfig }> = ({ cut, theme }) => {
  // Wrap component with background video or image if specified
  const maybeWrapWithBg = (element: React.ReactElement) => {
    if (cut.backgroundVideo) {
      return (
        <BackgroundVideoLayer
          src={cut.backgroundVideo}
          startFrom={cut.backgroundVideoStart ?? 0}
          overlayOpacity={cut.backgroundOverlay ?? 0.55}
        >
          {element}
        </BackgroundVideoLayer>
      );
    }
    if (cut.backgroundImage) {
      return (
        <BackgroundImageLayer
          src={cut.backgroundImage}
          overlayOpacity={cut.backgroundOverlay ?? 0.55}
        >
          {element}
        </BackgroundImageLayer>
      );
    }
    return element;
  };

  // Resolve the scene element based on cut type, then wrap with backgroundImage if set
  // Use transparent bg so the animated gradient background shows through
  // When no explicit backgroundColor on the cut, inherit from theme
  const rawBg = (cut.backgroundImage || cut.backgroundVideo) ? "transparent" : (cut.backgroundColor || theme.surfaceColor);
  const bgColor = (rawBg === theme.backgroundColor || rawBg === "#0F172A" || rawBg === "#0f172a") ? "transparent" : rawBg;
  const textColor = cut.color || theme.textColor;
  const accent = cut.accentColor || theme.accentColor;

  // Explicit component types — use theme-derived defaults for colors
  if (cut.type === "text_card" && cut.text) {
    return maybeWrapWithBg(
      <TextCard text={cut.text} fontSize={cut.fontSize} color={textColor} backgroundColor={bgColor} />
    );
  }
  if (cut.type === "stat_card" && cut.stat) {
    return maybeWrapWithBg(
      <StatCard stat={cut.stat} subtitle={cut.subtitle} accentColor={accent} backgroundColor={bgColor} />
    );
  }
  if (cut.type === "callout" && cut.text) {
    return maybeWrapWithBg(
      <CalloutBox
        text={cut.text} type={cut.callout_type} title={cut.title}
        borderColor={accent} backgroundColor={cut.backgroundColor || theme.surfaceColor}
        textColor={textColor} containerBackgroundColor={bgColor}
      />
    );
  }
  if (cut.type === "comparison" && cut.leftLabel && cut.rightLabel && cut.leftValue && cut.rightValue) {
    return maybeWrapWithBg(
      <ComparisonCard
        leftLabel={cut.leftLabel} rightLabel={cut.rightLabel}
        leftValue={cut.leftValue} rightValue={cut.rightValue}
        title={cut.title} backgroundColor={bgColor} textColor={textColor}
        cardBackgroundColor={cut.cardBackgroundColor || theme.surfaceColor}
      />
    );
  }
  if (cut.type === "hero_title" && cut.text) {
    return maybeWrapWithBg(
      <HeroTitle
        title={cut.text}
        subtitle={cut.heroSubtitle || cut.subtitle}
        accentColor={accent}
        textColor={textColor}
        subtitleColor={theme.mutedTextColor}
        scrimBackground={heroScrim(theme)}
      />
    );
  }
  if (cut.type === "terminal_scene" && cut.steps) {
    return maybeWrapWithBg(
      <TerminalScene
        title={cut.terminalTitle || "Terminal"}
        steps={cut.steps as TerminalStep[]}
        prompt={cut.prompt}
        accentColor={accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "screenshot_scene" && cut.backgroundImage && cut.screenshotSteps) {
    return (
      <ScreenshotScene
        backgroundImage={cut.backgroundImage}
        backgroundSize={cut.screenshotSize}
        steps={cut.screenshotSteps as ScreenshotStep[]}
        accentColor={accent}
        cursorStartAt={cut.cursorStartAt}
      />
    );
  }
  if (cut.type === "audio_waveform") {
    return maybeWrapWithBg(
      <AudioWaveformVisualizer
        title={cut.title || cut.text}
        subtitle={cut.subtitle}
        barCount={cut.barCount}
        waveColor={cut.waveColor || accent}
        accentColor={cut.accentColor || theme.primaryColor}
        styleMode={cut.styleMode}
      />
    );
  }
  if (cut.type === "split_screen" && cut.left && cut.right) {
    return (
      <SplitScreen
        left={cut.left}
        right={cut.right}
        title={cut.title}
        orientation={cut.orientation}
        dividerColor={cut.dividerColor || accent}
      />
    );
  }
  if (cut.type === "social_quote" && cut.quoteText) {
    return maybeWrapWithBg(
      <SocialQuoteCard
        authorName={cut.authorName || "Featured Speaker"}
        authorHandle={cut.authorHandle}
        avatarUrl={cut.avatarUrl}
        quoteText={cut.quoteText}
        highlightWords={cut.highlightWords}
        verified={cut.verified !== false}
        dateText={cut.dateText}
        likesCount={cut.likesCount}
        retweetsCount={cut.retweetsCount}
        accentColor={cut.accentColor || accent}
      />
    );
  }
  if (cut.type === "device_mockup") {
    return maybeWrapWithBg(
      <DeviceMockup
        deviceType={cut.deviceType}
        screenMediaUrl={cut.screenMediaUrl || cut.source}
        screenMediaType={cut.screenMediaType}
        title={cut.title}
        subtitle={cut.subtitle}
        accentColor={cut.accentColor || accent}
      />
    );
  }
  if (cut.type === "geo_route" && cut.waypoints) {
    return maybeWrapWithBg(
      <GeoRouteMap
        title={cut.title}
        waypoints={cut.waypoints}
        accentColor={cut.accentColor || accent}
        pathColor={cut.pathColor}
      />
    );
  }
  if (cut.type === "typewriter" && cut.text) {
    return maybeWrapWithBg(
      <TypewriterText
        text={cut.text}
        title={cut.title}
        subtitle={cut.subtitle}
        fontSize={cut.fontSize}
        color={cut.color || textColor}
        cursorColor={cut.cursorColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        charsPerSecond={cut.charsPerSecond}
        startDelaySeconds={cut.startDelaySeconds}
        showCursor={cut.showCursor !== false}
        align={cut.align}
      />
    );
  }
  if (cut.type === "kinetic_type" && cut.lines) {
    return maybeWrapWithBg(
      <KineticTypography
        lines={cut.lines}
        title={cut.title}
        fontSize={cut.fontSize}
        color={cut.color || textColor}
        highlightColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        highlightWords={cut.highlightWords}
        staggerFrames={cut.staggerFrames}
        align={cut.align}
      />
    );
  }
  if (cut.type === "editorial_slide" && cut.headline) {
    return (
      <EditorialSlide
        headline={cut.headline}
        body={cut.body}
        kicker={cut.kicker}
        footnote={cut.footnote}
        backgroundColor={cut.backgroundColor || bgColor || theme.backgroundColor}
        textColor={cut.color || textColor}
        accentColor={cut.accentColor || accent}
        headlineFont={cut.headlineFont}
        bodyFont={cut.bodyFont}
        layout={cut.layout}
        headlineSize={cut.headlineSize}
        bodySize={cut.bodySize}
        showRule={cut.showRule !== false}
      />
    );
  }
  if (cut.type === "word_pop_caption" && cut.words) {
    return (
      <WordPopCaption
        words={cut.words}
        fontSize={cut.fontSize}
        color={cut.color || textColor}
        highlightColor={cut.accentColor || accent}
        backgroundColor={cut.backgroundColor || theme.captionBackgroundColor}
        maxWordsPerLine={cut.maxWordsPerLine}
        bottomPadding={cut.bottomPadding}
      />
    );
  }
  if (cut.type === "news_breaking" && cut.headline) {
    return (
      <NewsBreaking
        headline={cut.headline}
        subheadline={cut.subheadline}
        category={cut.category}
        timeText={cut.timeText}
        backgroundColor={cut.backgroundColor || bgColor || theme.backgroundColor}
        accentColor={cut.accentColor || accent}
        headlineColor={cut.headlineColor || textColor}
        showBreakingBanner={cut.showBreakingBanner !== false}
        showLowerThird={cut.showLowerThird !== false}
        showTicker={cut.showTicker !== false}
        tickerItems={cut.tickerItems}
      />
    );
  }
  if (cut.type === "scoreboard" && cut.homeTeam && cut.awayTeam) {
    return maybeWrapWithBg(
      <Scoreboard
        homeTeam={cut.homeTeam}
        awayTeam={cut.awayTeam}
        homeScore={cut.homeScore ?? 0}
        awayScore={cut.awayScore ?? 0}
        periodLabel={cut.periodLabel}
        timeText={cut.timeText}
        homeColor={cut.homeColor}
        awayColor={cut.awayColor}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "countdown_timer" && cut.fromSeconds) {
    return maybeWrapWithBg(
      <CountdownTimer
        fromSeconds={cut.fromSeconds}
        label={cut.title}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        showProgressRing={cut.showProgressRing !== false}
      />
    );
  }
  if (cut.type === "lower_third" && cut.name) {
    return maybeWrapWithBg(
      <LowerThird
        name={cut.name}
        title={cut.title}
        accentColor={cut.accentColor || accent}
        position={cut.position}
      />
    );
  }
  if (cut.type === "quiz_card" && cut.question && cut.options) {
    return maybeWrapWithBg(
      <QuizCard
        question={cut.question}
        options={cut.options}
        correctIndex={cut.correctIndex}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        revealAnswer={cut.revealAnswer}
      />
    );
  }
  if (cut.type === "weather_card" && cut.city) {
    return maybeWrapWithBg(
      <WeatherCard
        city={cut.city}
        temperature={cut.temperature ?? 0}
        condition={cut.condition || ""}
        icon={cut.icon}
        highTemp={cut.highTemp}
        lowTemp={cut.lowTemp}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "vhs_glitch") {
    return maybeWrapWithBg(
      <VHSGlitch
        intensity={cut.intensity}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "crt_scanlines") {
    return maybeWrapWithBg(
      <CRTScanlines
        scanlineOpacity={cut.scanlineOpacity}
        curvature={cut.curvature}
        backgroundColor={bgColor || theme.backgroundColor}
        showFlicker={cut.showFlicker !== false}
      />
    );
  }
  if (cut.type === "film_grain") {
    return maybeWrapWithBg(
      <FilmGrain intensity={cut.intensity} monochrome={cut.monochrome !== false} />
    );
  }
  if (cut.type === "poll_card" && cut.question && cut.pollOptions) {
    return maybeWrapWithBg(
      <PollCard
        question={cut.question}
        options={cut.pollOptions}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "end_credits" && cut.title && cut.credits) {
    return (
      <EndCredits
        title={cut.title}
        credits={cut.credits}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        scrollSpeed={cut.scrollSpeed}
      />
    );
  }
  if (cut.type === "breaking_alert" && cut.headline) {
    return maybeWrapWithBg(
      <BreakingAlert
        headline={cut.headline}
        subheadline={cut.subheadline}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "matrix_rain") {
    return maybeWrapWithBg(
      <MatrixRainScene
        fontSize={cut.fontSize}
        color={cut.matrixColor || accent}
        speed={cut.matrixSpeed}
        density={cut.matrixDensity}
        streamLength={cut.matrixStreamLength}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "animated_counter" && cut.counterTo !== undefined) {
    return maybeWrapWithBg(
      <AnimatedCounterScene
        from={cut.counterFrom ?? 0}
        to={cut.counterTo}
        prefix={cut.counterPrefix}
        postfix={cut.counterPostfix}
        toFixed={cut.counterToFixed}
        fontSize={cut.fontSize}
        color={cut.color || textColor}
        backgroundColor={bgColor || theme.backgroundColor}
        durationSeconds={cut.out_seconds - cut.in_seconds}
      />
    );
  }
  if (cut.type === "animated_text" && cut.text) {
    return maybeWrapWithBg(
      <AnimatedTextScene
        text={cut.text}
        split={cut.split}
        splitStagger={cut.splitStagger}
        glitch={cut.glitch}
        fontSize={cut.fontSize}
        color={cut.color || textColor}
        backgroundColor={bgColor || theme.backgroundColor}
        durationSeconds={cut.out_seconds - cut.in_seconds}
      />
    );
  }
  if (cut.type === "gradient_transition" && cut.gradients) {
    return (
      <GradientTransitionScene
        gradients={cut.gradients}
        durationSeconds={cut.out_seconds - cut.in_seconds}
      />
    );
  }
  if (cut.type === "typewriter_bits" && cut.text) {
    return maybeWrapWithBg(
      <TypeWriterScene
        text={cut.text}
        typeSpeed={cut.typeSpeed}
        errorRate={cut.errorRate}
        fontSize={cut.fontSize}
        color={cut.color || textColor}
        cursorColor={cut.cursorColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "particle_scene") {
    return maybeWrapWithBg(
      <ParticleScene
        particleType={cut.bitsParticleType}
        count={cut.bitsParticleCount}
        color={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
      />
    );
  }
  if (cut.type === "cctv_camera") {
    return (
      <CCTVCamera
        cameraId={cut.cameraId}
        location={cut.location}
        matrixColor={cut.matrixColor || accent}
        matrixSpeed={cut.matrixSpeed}
        matrixDensity={cut.matrixDensity}
        matrixStreamLength={cut.matrixStreamLength}
        showRecIndicator={cut.showRecIndicator !== false}
        showCornerBrackets={cut.showCornerBrackets !== false}
        showScanlines={cut.showScanlines !== false}
        showTimestamp={cut.showTimestamp !== false}
        showCameraId={cut.showCameraId !== false}
        backgroundColor={bgColor || theme.backgroundColor}
        videoSrc={cut.source ? resolveAsset(cut.source) : undefined}
        greenTint={cut.greenTint}
      />
    );
  }
  if (cut.type === "cut_black") {
    return (
      <CutBlack
        title={cut.text || cut.title}
        subtitle={cut.subtitle}
        backgroundColor={cut.backgroundColor || bgColor || theme.backgroundColor}
        accentColor={cut.color || textColor}
        holdSeconds={cut.holdSeconds}
        fadeOutSeconds={cut.fadeOutSeconds}
      />
    );
  }
  if (cut.type === "reaction_emoji") {
    return (
      <ReactionEmoji
        emoji={cut.emoji}
        count={cut.emojiCount}
        position={cut.emojiPosition}
        accentColor={cut.accentColor || accent}
        size={cut.emojiSize}
      />
    );
  }
  if (cut.type === "text_3d" && cut.text) {
    return maybeWrapWithBg(
      <Text3D
        text={cut.text}
        fontSize={cut.fontSize}
        color={cut.color || textColor}
        shadowColor={cut.shadowColor}
        backgroundColor={bgColor || theme.backgroundColor}
        depth={cut.depth}
        rotateX={cut.rotateX}
        rotateY={cut.rotateY}
        float={cut.float !== false}
      />
    );
  }
  if (cut.type === "chat_bubble" && cut.messages) {
    return maybeWrapWithBg(
      <ChatBubble
        messages={cut.messages}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        staggerFrames={cut.chatStaggerFrames}
      />
    );
  }
  if (cut.type === "subscribe_button") {
    return (
      <SubscribeButton
        channelName={cut.channelName}
        subscriberCount={cut.subscriberCount}
        accentColor={cut.accentColor || accent}
        position={cut.position as any}
      />
    );
  }
  if (cut.type === "neon_text" && cut.text) {
    return maybeWrapWithBg(
      <NeonText
        text={cut.text}
        fontSize={cut.fontSize}
        color={cut.accentColor || cut.color || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        flicker={cut.flicker !== false}
        glowIntensity={cut.glowIntensity}
      />
    );
  }
  if (cut.type === "notification_popup") {
    return (
      <NotificationPopup
        title={cut.title}
        message={cut.message}
        appName={cut.appName}
        appIcon={cut.appIcon}
        timeText={cut.timeText}
        accentColor={cut.accentColor || accent}
        position={cut.position as any}
      />
    );
  }
  if (cut.type === "like_button") {
    return (
      <LikeButton
        emoji={cut.emoji}
        count={cut.emojiCount}
        accentColor={cut.accentColor || accent}
        position={cut.position as any}
        burst={cut.burst !== false}
      />
    );
  }
  if (cut.type === "hashtag_overlay" && cut.hashtags) {
    return (
      <HashtagOverlay
        hashtags={cut.hashtags}
        accentColor={cut.accentColor || accent}
        position={cut.position as any}
        staggerFrames={cut.hashtagStaggerFrames}
      />
    );
  }
  if (cut.type === "flashback") {
    return maybeWrapWithBg(
      <Flashback
        label={cut.title || cut.text}
        backgroundColor={bgColor || theme.backgroundColor}
        accentColor={cut.accentColor || accent}
        sepiaAmount={cut.sepiaAmount}
        blurAmount={cut.blurAmount}
      />
    );
  }
  if (cut.type === "location_card" && cut.location) {
    return maybeWrapWithBg(
      <LocationCard
        location={cut.location}
        dateText={cut.locationDate}
        accentColor={cut.accentColor || accent}
        align={cut.align as any}
      />
    );
  }
  if (cut.type === "cliffhanger") {
    return (
      <Cliffhanger
        title={cut.title || cut.text}
        subtitle={cut.subtitle}
        accentColor={cut.accentColor || accent}
        backgroundColor={bgColor || theme.backgroundColor}
        fadeOutSeconds={cut.fadeOutSeconds}
      />
    );
  }

  // --- Chart types — use theme.chartColors as default palette ---
  if (cut.type === "bar_chart" && cut.chartData) {
    return maybeWrapWithBg(
      <BarChart
        data={cut.chartData} title={cut.title} colors={cut.chartColors || theme.chartColors}
        animationStyle={(cut.chartAnimation as any) || "grow-up"}
        showGrid={cut.showGrid} showValues={cut.showValues} backgroundColor={bgColor}
        textColor={textColor}
      />
    );
  }
  if (cut.type === "line_chart" && cut.chartSeries) {
    return maybeWrapWithBg(
      <LineChart
        series={cut.chartSeries} title={cut.title} colors={cut.chartColors || theme.chartColors}
        animationStyle={(cut.chartAnimation as any) || "draw"}
        showGrid={cut.showGrid} showMarkers={cut.showMarkers} showLegend={cut.showLegend}
        xLabel={cut.xLabel} yLabel={cut.yLabel} backgroundColor={bgColor}
        textColor={textColor}
      />
    );
  }
  if (cut.type === "pie_chart" && cut.chartData) {
    return maybeWrapWithBg(
      <PieChart
        data={cut.chartData} title={cut.title} colors={cut.chartColors || theme.chartColors}
        animationStyle={(cut.chartAnimation as any) || "expand"}
        donut={cut.donut} centerLabel={cut.centerLabel} centerValue={cut.centerValue}
        showLegend={cut.showLegend} backgroundColor={bgColor}
        textColor={textColor}
      />
    );
  }
  if (cut.type === "kpi_grid" && cut.chartData) {
    return maybeWrapWithBg(
      <KPIGrid
        metrics={cut.chartData} title={cut.title} columns={cut.columns}
        colors={cut.chartColors || theme.chartColors} animationStyle={(cut.chartAnimation as any) || "count-up"}
        backgroundColor={bgColor}
        textColor={textColor}
      />
    );
  }
  if (cut.type === "progress_bar" && cut.progress !== undefined) {
    return maybeWrapWithBg(
      <AbsoluteFill
        style={{
          background: bgColor || theme.surfaceColor,
          display: "flex", alignItems: "center", justifyContent: "center",
          padding: "80px 120px",
        }}
      >
        {cut.title && (
          <div style={{
            position: "absolute", top: 120, fontSize: 48, fontWeight: 700,
            color: textColor, textAlign: "center", width: "100%",
          }}>
            {cut.title}
          </div>
        )}
        <ProgressBar
          progress={cut.progress} label={cut.progressLabel}
          color={cut.progressColor || accent}
          animationStyle={(cut.progressAnimation as any) || "fill"}
          segments={cut.progressSegments} backgroundColor={cut.backgroundColor || theme.surfaceColor}
        />
      </AbsoluteFill>
    );
  }

  // --- Anime scene (multi-image crossfade + particles) ---
  if (cut.type === "anime_scene" && cut.images && cut.images.length > 0) {
    return (
      <AnimeScene
        images={cut.images}
        animation={(cut.animation as CameraMotion) || "ken-burns"}
        particles={cut.particles}
        particleColor={cut.particleColor}
        particleCount={cut.particleCount}
        particleIntensity={cut.particleIntensity}
        backgroundColor={cut.backgroundColor}
        vignette={cut.vignette ?? true}
        lightingFrom={cut.lightingFrom}
        lightingTo={cut.lightingTo}
        sceneDurationSeconds={cut.out_seconds - cut.in_seconds}
      />
    );
  }

  // --- Media types (image / video fallback) ---
  const animation = cut.animation || cut.transform?.animation;

  if (cut.source && isImage(cut.source)) {
    return maybeWrapWithBg(<ImageScene src={cut.source} animation={animation} />);
  }

  if (cut.source && isVideo(cut.source)) {
    return maybeWrapWithBg(
      <VideoScene
        src={cut.source}
        startFrom={cut.source_in_seconds ?? 0}
        transitionIn={cut.transition_in}
        transitionOut={cut.transition_out}
        transitionDuration={cut.transition_duration}
        sceneDurationSeconds={cut.out_seconds - cut.in_seconds}
        backgroundColor={cut.backgroundColor}
      />,
    );
  }

  // Final fallback — try as image if source exists, otherwise show text_card
  if (cut.source) {
    return maybeWrapWithBg(<ImageScene src={cut.source} animation={animation} />);
  }

  // No source, no type — render as text card with cut id as fallback
  return <TextCard text={cut.text || cut.id} color={textColor} backgroundColor={bgColor} />;
};

// ---------------------------------------------------------------------------
// Overlay renderer
// ---------------------------------------------------------------------------

const OverlayRenderer: React.FC<{ overlay: Overlay; theme: ThemeConfig }> = ({
  overlay,
  theme,
}) => {
  if (overlay.type === "section_title") {
    return (
      <SectionTitle
        title={overlay.text ?? ""}
        subtitle={overlay.subtitle}
        accentColor={overlay.accentColor || theme.accentColor}
        textColor={theme.textColor}
        position={(overlay.position as any) || "top-left"}
      />
    );
  }
  if (overlay.type === "stat_reveal") {
    return (
      <StatReveal
        stat={overlay.text ?? ""}
        label={overlay.subtitle}
        accentColor={overlay.accentColor || theme.accentColor}
        textColor={theme.textColor}
        position={(overlay.position as any) || "bottom-right"}
      />
    );
  }
  if (overlay.type === "hero_title") {
    return (
      <HeroTitle
        title={overlay.text ?? ""}
        subtitle={overlay.subtitle}
        accentColor={overlay.accentColor || theme.accentColor}
        textColor={theme.textColor}
        subtitleColor={theme.mutedTextColor}
        scrimBackground={heroScrim(theme)}
      />
    );
  }
  if (overlay.type === "provider_chip" && overlay.providers) {
    return (
      <ProviderChip
        providers={overlay.providers as string[]}
        cycleSeconds={overlay.cycleSeconds}
        position={(overlay.position as any) || "bottom-right"}
        accentColor={overlay.accentColor}
        label={overlay.label}
      />
    );
  }
  return null;
};

// ---------------------------------------------------------------------------
// Main composition
// ---------------------------------------------------------------------------

export const Explainer: React.FC<ExplainerProps> = (props) => {
  const { cuts, overlays, captions, audio } = props;
  const { fps, durationInFrames } = useVideoConfig();

  // Resolve theme from props — playbook name, theme name, or custom themeConfig
  const theme = resolveTheme(props as Record<string, unknown>);

  return (
    <AbsoluteFill style={{ background: theme.backgroundColor, fontFamily: theme.headingFont || fontFamily }}>
      {/* Layer 0: Animated gradient background — driven by theme */}
      <AnimatedBackground theme={theme} />

      {/* Layer 1: Visual scenes */}
      {cuts.map((cut) => {
        const from = Math.round(cut.in_seconds * fps);
        const duration = Math.round((cut.out_seconds - cut.in_seconds) * fps);

        return (
          <Sequence key={cut.id} from={from} durationInFrames={duration}>
            <SceneRenderer cut={cut} theme={theme} />
          </Sequence>
        );
      })}

      {/* Layer 2: Overlays (section titles, stat reveals, hero titles) */}
      {overlays?.map((overlay, i) => {
        const from = Math.round(overlay.in_seconds * fps);
        const duration = Math.round(
          (overlay.out_seconds - overlay.in_seconds) * fps
        );

        return (
          <Sequence key={`overlay-${i}`} from={from} durationInFrames={duration}>
            <OverlayRenderer overlay={overlay} theme={theme} />
          </Sequence>
        );
      })}

      {/* Layer 3: Captions (word-by-word highlight) */}
      {captions && captions.length > 0 && (
        <CaptionOverlay
          words={captions}
          wordsPerPage={6}
          fontSize={42}
          color={theme.textColor}
          highlightColor={theme.captionHighlightColor}
          backgroundColor={theme.captionBackgroundColor}
        />
      )}

      {/* Layer 4: Audio — narration */}
      {audio?.narration?.src && (
        <Audio src={resolveAsset(audio.narration.src)} volume={audio.narration.volume ?? 1} />
      )}

      {/* Layer 4: Audio — music with offset, fade in/out, and optional loop */}
      {audio?.music?.src && (
        <Audio
          src={resolveAsset(audio.music.src)}
          startFrom={Math.round((audio.music.offsetSeconds ?? 0) * fps)}
          loop={audio.music.loop ?? false}
          loopVolumeCurveBehavior="repeat"
          volume={(f) => {
            const baseVol = audio.music!.volume ?? 0.1;
            const fadeInDur = (audio.music!.fadeInSeconds ?? 2) * fps;
            const fadeOutDur = (audio.music!.fadeOutSeconds ?? 3) * fps;
            const totalFrames = durationInFrames;

            // Fade in
            const fadeIn = interpolate(f, [0, fadeInDur], [0, baseVol], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            // Fade out
            const fadeOut = interpolate(
              f,
              [totalFrames - fadeOutDur, totalFrames],
              [baseVol, 0],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );
            return Math.min(fadeIn, fadeOut);
          }}
        />
      )}
    </AbsoluteFill>
  );
};
