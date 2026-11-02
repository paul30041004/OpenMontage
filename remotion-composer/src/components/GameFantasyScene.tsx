import React from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  Img,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { resolveAsset } from "../lib/resolveAsset";

// ---------------------------------------------------------------------------
// GameFantasyScene — one still image + camera move + RPG UI overlays + audio.
// Used by the "조선 던전 헌터" game-fantasy style. All Korean text is rendered
// here in code (never generated inside the image).
// ---------------------------------------------------------------------------

export type GameUiEvent =
  | { kind: "quest"; atSeconds: number; durationSeconds: number; title: string; subtitle?: string }
  | { kind: "skill"; atSeconds: number; durationSeconds: number; name: string; rank?: string; description?: string }
  | { kind: "levelup"; atSeconds: number; durationSeconds: number; from: number; to: number }
  | { kind: "bossHp"; atSeconds: number; durationSeconds: number; name: string; hpFrom: number; hpTo: number }
  | { kind: "flash"; atSeconds: number; durationSeconds: number };

export interface GameSubtitle {
  text: string;
  speaker?: string;
  inSeconds: number;
  outSeconds: number;
  color?: string;
}

export interface GameAudioTrack {
  src: string;
  startSeconds: number;
  volume?: number;
}

export interface GameFantasySceneProps {
  /** Omit (or leave empty) for the audio-story look: dark backdrop + speaker waveform. */
  image?: string;
  durationSeconds: number;
  camera?: {
    from: { scale: number; x: number; y: number };
    to: { scale: number; x: number; y: number };
  };
  events: GameUiEvent[];
  subtitles: GameSubtitle[];
  audio: GameAudioTrack[];
  accent?: string;
}

const FONT = "'Noto Sans KR','Apple SD Gothic Neo','NanumGothic',sans-serif";
const DEFAULT_ACCENT = "#2EE6D6";

export const calculateGameFantasyMetadata: CalculateMetadataFunction<
  GameFantasySceneProps
> = ({ props }) => ({
  durationInFrames: Math.max(1, Math.round(props.durationSeconds * 30)),
});

const Particles: React.FC<{ accent: string }> = ({ accent }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const count = 38;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: count }).map((_, i) => {
        const seed = (i * 9301 + 49297) % 233280;
        const rx = (seed / 233280) * width;
        const speed = 0.4 + ((i * 37) % 10) / 10;
        const size = 2 + ((i * 13) % 5);
        const y = height - ((frame * speed * 2 + i * 57) % (height + 40)) + 20;
        const sway = Math.sin((frame + i * 11) / 18) * 14;
        const op = 0.25 + 0.5 * Math.abs(Math.sin((frame + i * 7) / 24));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: rx + sway,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: accent,
              opacity: op,
              boxShadow: `0 0 ${size * 3}px ${accent}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const panel = (accent: string): React.CSSProperties => ({
  background: "linear-gradient(180deg, rgba(6,18,30,0.86), rgba(4,10,20,0.9))",
  border: `2px solid ${accent}`,
  boxShadow: `0 0 24px ${accent}66, inset 0 0 18px ${accent}22`,
  borderRadius: 6,
  fontFamily: FONT,
  color: "#E8FBFF",
});

const useEventWindow = (e: { atSeconds: number; durationSeconds: number }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = e.atSeconds * fps;
  const end = (e.atSeconds + e.durationSeconds) * fps;
  const enter = spring({ frame: frame - start, fps, config: { damping: 14, stiffness: 120 } });
  const exit = interpolate(frame, [end - 10, end], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return { visible: frame >= start && frame <= end, enter, exit };
};

const SkillWindow: React.FC<{ e: Extract<GameUiEvent, { kind: "skill" }>; accent: string }> = ({ e, accent }) => {
  const { visible, enter, exit } = useEventWindow(e);
  const frame = useCurrentFrame();
  if (!visible) return null;
  const glow = 0.6 + 0.4 * Math.sin(frame / 6);
  return (
    <div
      style={{
        position: "absolute",
        top: 90,
        right: 80,
        width: 520,
        padding: "22px 28px",
        opacity: exit,
        transform: `translateX(${interpolate(enter, [0, 1], [80, 0])}px) scale(${interpolate(enter, [0, 1], [0.92, 1])})`,
        ...panel(accent),
      }}
    >
      <div style={{ fontSize: 20, letterSpacing: 6, color: accent, opacity: glow }}>
        ◆ SKILL ACQUIRED
      </div>
      <div style={{ fontSize: 46, fontWeight: 800, marginTop: 8 }}>
        {e.name}
        {e.rank ? (
          <span style={{ fontSize: 22, marginLeft: 14, color: "#FFD36B" }}>[{e.rank}]</span>
        ) : null}
      </div>
      {e.description ? (
        <div style={{ fontSize: 24, marginTop: 10, opacity: 0.85, lineHeight: 1.4 }}>
          {e.description}
        </div>
      ) : null}
    </div>
  );
};

const LevelUp: React.FC<{ e: Extract<GameUiEvent, { kind: "levelup" }>; accent: string }> = ({ e, accent }) => {
  const { visible, enter, exit } = useEventWindow(e);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!visible) return null;
  const swap = frame - e.atSeconds * fps > fps * 0.5;
  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: 300,
        transform: `translateX(-50%) scale(${interpolate(enter, [0, 1], [0.6, 1])})`,
        opacity: exit,
        textAlign: "center",
        fontFamily: FONT,
      }}
    >
      <div
        style={{
          fontSize: 92,
          fontWeight: 900,
          letterSpacing: 10,
          color: "#FFE38A",
          textShadow: `0 0 28px #FFB300, 0 0 60px ${accent}`,
        }}
      >
        LEVEL UP!
      </div>
      <div style={{ fontSize: 40, marginTop: 6, color: "#E8FBFF", textShadow: `0 0 14px ${accent}` }}>
        Lv.{swap ? e.to : e.from} {swap ? "" : `→ Lv.${e.to}`}
      </div>
    </div>
  );
};

const QuestAlert: React.FC<{ e: Extract<GameUiEvent, { kind: "quest" }>; accent: string }> = ({ e, accent }) => {
  const { visible, enter, exit } = useEventWindow(e);
  if (!visible) return null;
  return (
    <div
      style={{
        position: "absolute",
        top: 70,
        left: "50%",
        transform: `translateX(-50%) translateY(${interpolate(enter, [0, 1], [-60, 0])}px)`,
        opacity: exit,
        padding: "16px 44px",
        textAlign: "center",
        ...panel(accent),
      }}
    >
      <div style={{ fontSize: 18, letterSpacing: 6, color: accent }}>QUEST</div>
      <div style={{ fontSize: 40, fontWeight: 800 }}>{e.title}</div>
      {e.subtitle ? <div style={{ fontSize: 22, opacity: 0.8 }}>{e.subtitle}</div> : null}
    </div>
  );
};

const BossHp: React.FC<{ e: Extract<GameUiEvent, { kind: "bossHp" }>; accent: string }> = ({ e, accent }) => {
  const { visible, enter, exit } = useEventWindow(e);
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!visible) return null;
  const t = interpolate(frame, [e.atSeconds * fps, (e.atSeconds + e.durationSeconds) * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const hp = interpolate(t, [0, 1], [e.hpFrom, e.hpTo]);
  return (
    <div
      style={{
        position: "absolute",
        top: 50,
        left: "50%",
        width: 900,
        transform: `translateX(-50%) scaleX(${enter})`,
        opacity: exit,
        fontFamily: FONT,
        color: "#FFE9E9",
      }}
    >
      <div style={{ fontSize: 30, fontWeight: 800, marginBottom: 6, textShadow: "0 0 12px #FF3B3B" }}>
        {e.name}
      </div>
      <div style={{ height: 22, border: "2px solid #FF5A5A", background: "rgba(40,0,0,0.7)", boxShadow: "0 0 18px #FF3B3B88" }}>
        <div style={{ width: `${hp}%`, height: "100%", background: "linear-gradient(90deg,#FF3B3B,#FF9A5A)" }} />
      </div>
    </div>
  );
};

const Flash: React.FC<{ e: Extract<GameUiEvent, { kind: "flash" }>; accent: string }> = ({ e, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = e.atSeconds * fps;
  const d = e.durationSeconds * fps;
  const op = interpolate(frame, [s, s + 2, s + d], [0, 0.7, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return <AbsoluteFill style={{ background: accent, opacity: op, mixBlendMode: "screen" }} />;
};

// Audio-story backdrop: no picture, a breathing rune glow, a large faint
// speaker name and a waveform tinted by whoever is speaking.
const AudioBackdrop: React.FC<{ subtitles: GameSubtitle[]; accent: string }> = ({
  subtitles,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const active = subtitles.find((s) => t >= s.inSeconds && t <= s.outSeconds - 0.15);
  const color = active?.color ?? accent;
  const level = active ? 1 : 0.12;
  const bars = 56;
  const glow = 0.5 + 0.5 * Math.sin(frame / 38);
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 42%, ${color}${active ? "30" : "18"} 0%, #05101a 48%, #02060b 100%)`,
      }}
    >
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
        <div
          style={{
            width: 620 + glow * 40,
            height: 620 + glow * 40,
            borderRadius: "50%",
            border: `2px solid ${color}55`,
            boxShadow: `0 0 80px ${color}33, inset 0 0 80px ${color}22`,
          }}
        />
      </AbsoluteFill>
      {active?.speaker ? (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <div
            style={{
              fontFamily: FONT,
              fontSize: 260,
              fontWeight: 900,
              color,
              opacity: 0.09,
              letterSpacing: 24,
            }}
          >
            {active.speaker}
          </div>
        </AbsoluteFill>
      ) : null}
      <div
        style={{
          position: "absolute",
          left: (width - bars * 22) / 2,
          top: height * 0.44,
          height: 220,
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        {Array.from({ length: bars }).map((_, i) => {
          const env = Math.sin((i / bars) * Math.PI);
          const wob =
            0.55 +
            0.45 * Math.abs(Math.sin(frame / 3 + i * 1.7) * Math.cos(frame / 5 + i * 0.9));
          const h = 6 + 190 * env * wob * level;
          return (
            <div
              key={i}
              style={{
                width: 12,
                height: h,
                borderRadius: 6,
                background: color,
                opacity: 0.35 + 0.6 * env * level,
                boxShadow: `0 0 14px ${color}`,
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Subtitle: React.FC<{ s: GameSubtitle }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = s.inSeconds * fps;
  const b = s.outSeconds * fps;
  if (frame < a - 2 || frame > b + 6) return null;
  const op =
    interpolate(frame, [a, a + 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) *
    interpolate(frame, [b, b + 6], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        bottom: 70,
        left: 0,
        right: 0,
        textAlign: "center",
        opacity: op,
        fontFamily: FONT,
      }}
    >
      <span
        style={{
          display: "inline-block",
          padding: "10px 30px",
          background: "rgba(0,0,0,0.55)",
          borderRadius: 6,
          fontSize: 40,
          fontWeight: 700,
          color: s.color ?? "#FFFFFF",
          textShadow: "0 2px 8px #000",
          maxWidth: 1660,
          lineHeight: 1.35,
          wordBreak: "keep-all",
          whiteSpace: "normal",
        }}
      >
        {s.speaker ? <span style={{ opacity: 0.75, marginRight: 14, fontSize: 32 }}>{s.speaker}</span> : null}
        {s.text}
      </span>
    </div>
  );
};

export const GameFantasyScene: React.FC<GameFantasySceneProps> = ({
  image,
  durationSeconds,
  camera,
  events,
  subtitles,
  audio,
  accent = DEFAULT_ACCENT,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const total = durationSeconds * fps;
  const cam = camera ?? {
    from: { scale: 1.0, x: 0, y: 0 },
    to: { scale: 1.12, x: -30, y: -10 },
  };
  const p = interpolate(frame, [0, total], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(p, [0, 1], [cam.from.scale, cam.to.scale]);
  const tx = interpolate(p, [0, 1], [cam.from.x, cam.to.x]);
  const ty = interpolate(p, [0, 1], [cam.from.y, cam.to.y]);

  // camera shake while a flash event is active
  const shake = events
    .filter((e) => e.kind === "flash")
    .reduce((acc, e) => {
      const s = e.atSeconds * fps;
      const d = (e.durationSeconds + 0.4) * fps;
      if (frame < s || frame > s + d) return acc;
      const k = 1 - (frame - s) / d;
      return acc + Math.sin(frame * 2.3) * 9 * k;
    }, 0);

  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [total - 12, total], [1, 0], { extrapolateLeft: "clamp" });

  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden", opacity: fadeIn * fadeOut }}>
      {audio.map((a, i) => (
        <Sequence key={i} from={Math.round(a.startSeconds * fps)}>
          <Audio src={resolveAsset(a.src)} volume={a.volume ?? 1} />
        </Sequence>
      ))}

      {image ? (
        <AbsoluteFill style={{ transform: `translate(${tx + shake}px, ${ty}px) scale(${scale})` }}>
          <Img src={resolveAsset(image)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </AbsoluteFill>
      ) : (
        <AudioBackdrop subtitles={subtitles} accent={accent} />
      )}

      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)",
        }}
      />
      <Particles accent={accent} />

      {events.map((e, i) => {
        switch (e.kind) {
          case "flash":
            return <Flash key={i} e={e} accent={accent} />;
          case "skill":
            return <SkillWindow key={i} e={e} accent={accent} />;
          case "levelup":
            return <LevelUp key={i} e={e} accent={accent} />;
          case "quest":
            return <QuestAlert key={i} e={e} accent={accent} />;
          case "bossHp":
            return <BossHp key={i} e={e} accent={accent} />;
        }
      })}

      {subtitles.map((s, i) => (
        <Subtitle key={i} s={s} />
      ))}
    </AbsoluteFill>
  );
};
