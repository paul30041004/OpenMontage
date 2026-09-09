import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { resolveAsset } from "../lib/resolveAsset";

export interface GenesisSeriesEpisodeProps {
  projectDir: string;
  title: string;
  chapter: number;
  part: number;
  subtitles?: string[];
  bannerText?: string;
}

export const GenesisSeriesEpisode: React.FC<GenesisSeriesEpisodeProps> = ({
  projectDir = "genesis-4-esports",
  title = "성경 레전드 매치",
  chapter = 1,
  part = 1,
  subtitles = [
    "자, 형님들! 인류 역사상 최고의 성경 매치 본격 시작합니다!",
    "선수들 입장하고 경기장의 긴장감이 최고조에 달합니다!",
    "상황이 긴박하게 흘러갑니다! 결정적인 승부의 순간!",
    "여기서 벌어지는 충격적인 판정과 반전의 연속!",
    "운영자 하나님의 놀라운 섭리가 펼쳐지는 클라이맥스!",
    "유리멘탈은 금물! 다음 레전드 매치도 기대해주세요!"
  ],
  bannerText = "GENESIS TOURNAMENT 2026",
}) => {
  const { fps, width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  const narrationSrc = resolveAsset(`${projectDir}/master_narration.wav`);
  const bgmSrc = resolveAsset(`${projectDir}/bgm_esports.mp3`);

  // Default subtitle fallback helper
  const getSub = (idx: number) => {
    if (subtitles && subtitles[idx]) return subtitles[idx];
    return subtitles[subtitles.length - 1] || "";
  };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#070B14",
        overflow: "hidden",
        fontFamily: "'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* Audio Layer */}
      <Audio src={narrationSrc} volume={1.0} />
      <Audio src={bgmSrc} volume={0.16} />

      {/* Global eSports Broadcast Header */}
      <TopEsportsHeader chapter={chapter} part={part} />

      {/* 9 Panels @ 200 frames each (Total 1800 frames = 60s @ 30fps) */}

      {/* Panel 1: 0 - 200 (Opening) */}
      <Sequence from={0} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_01.png`)} zoomIn />
        <VersusMatchupBanner title={`창세기 ${chapter}장 ${part}부`} subtitle={title} />
        <SingleSubtitle text={getSub(0)} />
      </Sequence>

      {/* Panel 2: 200 - 400 (Setup 1) */}
      <Sequence from={200} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_02.png`)} panRight />
        <PlayerTurnCard phase="PHASE 01" action="초반 메타 전개" accent="#F59E0B" />
        <SingleSubtitle text={getSub(1)} />
      </Sequence>

      {/* Panel 3: 400 - 600 (Setup 2) */}
      <Sequence from={400} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_03.png`)} zoomIn />
        <PlayerTurnCard phase="PHASE 02" action="양측 대립 격화" accent="#10B981" />
        <SingleSubtitle text={getSub(2)} />
      </Sequence>

      {/* Panel 4: 600 - 800 (Conflict 1) */}
      <Sequence from={600} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_04.png`)} tiltUp />
        <VerdictBadge headline="⭐ MOMENTUM SHIFT ⭐" detail="운명의 판정이 내려지는 순간" accent="#38BDF8" />
        <SingleSubtitle text={getSub(3)} />
      </Sequence>

      {/* Panel 5: 800 - 1000 (Crisis) */}
      <Sequence from={800} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_05.png`)} zoomIn />
        <AlertBox headline="⚠️ CRISIS ALERT : 긴급 위기 ⚠️" accent="#EF4444" />
        <SingleSubtitle text={getSub(3)} />
      </Sequence>

      {/* Panel 6: 1000 - 1200 (Warning / Turning Point) */}
      <Sequence from={1000} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_06.png`)} panLeft />
        <AlertBox headline="🚨 TURNING POINT : 승부처 🚨" accent="#F59E0B" />
        <SingleSubtitle text={getSub(4)} />
      </Sequence>

      {/* Panel 7: 1200 - 1400 (Climax Event) */}
      <Sequence from={1200} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_07.png`)} handheld />
        <ClimaxBanner headline="⚔️ CLIMAX HIGHLIGHT ⚔️" subtext="역대급 결정적 장면 탄생" />
        <SingleSubtitle text={getSub(4)} />
      </Sequence>

      {/* Panel 8: 1400 - 1600 (Resolution / Dialogue) */}
      <Sequence from={1400} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_08.png`)} />
        <PlayerTurnCard phase="VERDICT" action="심문 및 결말 전개" accent="#818CF8" />
        <SingleSubtitle text={getSub(5)} />
      </Sequence>

      {/* Panel 9: 1600 - 1800 (Outro) */}
      <Sequence from={1600} durationInFrames={200}>
        <SceneBackground src={resolveAsset(`${projectDir}/frame_09.png`)} zoomIn />
        <SeriesEndCard chapter={chapter} part={part} />
        <SingleSubtitle text={getSub(5)} />
      </Sequence>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Design Components
// ---------------------------------------------------------------------------

const TopEsportsHeader: React.FC<{ chapter: number; part: number }> = ({ chapter, part }) => {
  const frame = useCurrentFrame();
  const pulse = Math.sin(frame / 6) * 0.3 + 0.7;

  return (
    <div
      style={{
        position: "absolute",
        top: 24,
        left: 24,
        right: 24,
        zIndex: 50,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          border: "1px solid rgba(239, 68, 68, 0.4)",
          borderRadius: 24,
          padding: "8px 18px",
          backdropFilter: "blur(10px)",
        }}
      >
        <div
          style={{
            width: 12,
            height: 12,
            borderRadius: "50%",
            backgroundColor: "#EF4444",
            opacity: pulse,
            boxShadow: "0 0 10px #EF4444",
          }}
        />
        <span style={{ color: "#F8FAFC", fontSize: 14, fontWeight: 800, letterSpacing: "0.08em" }}>
          LIVE · GENESIS 100 SHORTS
        </span>
      </div>

      <div
        style={{
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          border: "1px solid rgba(56, 189, 248, 0.3)",
          borderRadius: 24,
          padding: "8px 16px",
          color: "#38BDF8",
          fontSize: 13,
          fontWeight: 800,
          backdropFilter: "blur(10px)",
        }}
      >
        창세기 {chapter}장 {part}부
      </div>
    </div>
  );
};

const SceneBackground: React.FC<{
  src: string;
  zoomIn?: boolean;
  panRight?: boolean;
  panLeft?: boolean;
  tiltUp?: boolean;
  handheld?: boolean;
}> = ({ src, zoomIn, panRight, panLeft, tiltUp, handheld }) => {
  const frame = useCurrentFrame();

  let scale = 1.08;
  let translateX = 0;
  let translateY = 0;

  if (zoomIn) {
    scale = interpolate(frame, [0, 200], [1.02, 1.18], { extrapolateRight: "clamp" });
  }
  if (panRight) {
    translateX = interpolate(frame, [0, 200], [-25, 25], { extrapolateRight: "clamp" });
  }
  if (panLeft) {
    translateX = interpolate(frame, [0, 200], [25, -25], { extrapolateRight: "clamp" });
  }
  if (tiltUp) {
    translateY = interpolate(frame, [0, 200], [25, -20], { extrapolateRight: "clamp" });
  }
  if (handheld) {
    translateX = Math.sin(frame * 0.45) * 8;
    translateY = Math.cos(frame * 0.38) * 8;
    scale = 1.12 + Math.sin(frame * 0.2) * 0.04;
  }

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
          filter: "brightness(0.92) contrast(1.08)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 180,
          background: "linear-gradient(to bottom, rgba(7,11,20,0.85), transparent)",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 280,
          background: "linear-gradient(to top, rgba(7,11,20,0.95) 20%, transparent)",
        }}
      />
    </AbsoluteFill>
  );
};

const VersusMatchupBanner: React.FC<{ title: string; subtitle: string }> = ({ title, subtitle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 110,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `translateY(${(1 - spr) * 25}px)`,
        zIndex: 40,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(15, 23, 42, 0.94)",
          border: "2px solid #EC4899",
          borderRadius: 20,
          padding: "16px 20px",
          boxShadow: "0 10px 30px rgba(236, 72, 153, 0.35)",
          backdropFilter: "blur(12px)",
          textAlign: "center",
        }}
      >
        <div style={{ color: "#F472B6", fontSize: 14, fontWeight: 900, letterSpacing: "0.1em" }}>
          {title.toUpperCase()}
        </div>
        <div style={{ color: "#F8FAFC", fontSize: 20, fontWeight: 800, marginTop: 6 }}>
          {subtitle}
        </div>
      </div>
    </div>
  );
};

const PlayerTurnCard: React.FC<{ phase: string; action: string; accent: string }> = ({ phase, action, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 16, stiffness: 140 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 110,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `translateY(${(1 - spr) * 20}px)`,
        backgroundColor: "rgba(15, 23, 42, 0.94)",
        border: `2px solid ${accent}`,
        borderRadius: 20,
        padding: "16px 22px",
        backdropFilter: "blur(12px)",
        boxShadow: `0 8px 30px ${accent}33`,
        zIndex: 40,
      }}
    >
      <div style={{ color: accent, fontSize: 14, fontWeight: 900, letterSpacing: "0.08em" }}>{phase}</div>
      <div style={{ color: "#F8FAFC", fontSize: 21, fontWeight: 800, marginTop: 4 }}>{action}</div>
    </div>
  );
};

const VerdictBadge: React.FC<{ headline: string; detail: string; accent: string }> = ({ headline, detail, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame: frame - 6, fps, config: { damping: 12, stiffness: 180 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 110,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `scale(${interpolate(spr, [0, 1], [1.3, 1.0])})`,
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        border: `3px solid ${accent}`,
        borderRadius: 20,
        padding: "18px 22px",
        textAlign: "center",
        boxShadow: `0 0 35px ${accent}66`,
        backdropFilter: "blur(12px)",
        zIndex: 40,
      }}
    >
      <div style={{ color: accent, fontSize: 22, fontWeight: 900 }}>{headline}</div>
      <div style={{ color: "#E0F2FE", fontSize: 16, fontWeight: 700, marginTop: 6 }}>{detail}</div>
    </div>
  );
};

const AlertBox: React.FC<{ headline: string; accent: string }> = ({ headline, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 12, stiffness: 150 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 110,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `translateY(${(1 - spr) * 20}px)`,
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        border: `2px solid ${accent}`,
        borderRadius: 20,
        padding: "16px 22px",
        textAlign: "center",
        boxShadow: `0 0 30px ${accent}44`,
        backdropFilter: "blur(12px)",
        zIndex: 40,
      }}
    >
      <div style={{ color: accent, fontSize: 20, fontWeight: 900 }}>{headline}</div>
    </div>
  );
};

const ClimaxBanner: React.FC<{ headline: string; subtext: string }> = ({ headline, subtext }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 12, stiffness: 200 } });
  const pulse = Math.sin(frame / 4) * 0.12 + 1.0;

  return (
    <div
      style={{
        position: "absolute",
        top: 100,
        left: 20,
        right: 20,
        opacity: spr,
        transform: `scale(${interpolate(spr, [0, 1], [1.5, 1.0]) * pulse})`,
        backgroundColor: "rgba(185, 28, 28, 0.95)",
        border: "3px solid #EF4444",
        borderRadius: 24,
        padding: "20px 24px",
        textAlign: "center",
        boxShadow: "0 0 45px rgba(239, 68, 68, 0.8)",
        backdropFilter: "blur(16px)",
        zIndex: 45,
      }}
    >
      <div style={{ color: "#FEF2F2", fontSize: 26, fontWeight: 900, textShadow: "0 0 20px rgba(255,255,255,0.8)" }}>
        {headline}
      </div>
      <div style={{ color: "#FEE2E2", fontSize: 17, fontWeight: 800, marginTop: 6 }}>
        {subtext}
      </div>
    </div>
  );
};

const SeriesEndCard: React.FC<{ chapter: number; part: number }> = ({ chapter, part }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });

  const nextText = part === 1 ? `창세기 ${chapter}장 2부에서 계속됩니다!` : `창세기 ${chapter + 1}장 1부에서 계속됩니다!`;

  return (
    <div
      style={{
        position: "absolute",
        top: 110,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `translateY(${(1 - spr) * 20}px)`,
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        border: "2px solid #38BDF8",
        borderRadius: 20,
        padding: "20px 24px",
        textAlign: "center",
        boxShadow: "0 0 35px rgba(56, 189, 248, 0.4)",
        backdropFilter: "blur(12px)",
        zIndex: 40,
      }}
    >
      <div style={{ color: "#38BDF8", fontSize: 20, fontWeight: 800 }}>🏆 GENESIS 100 SHORTS 🏆</div>
      <div style={{ color: "#FDE047", fontSize: 17, fontWeight: 700, marginTop: 8 }}>{nextText}</div>
      <div
        style={{
          marginTop: 14,
          backgroundColor: "#EC4899",
          color: "#FFF",
          padding: "10px 18px",
          borderRadius: 14,
          fontSize: 16,
          fontWeight: 900,
          boxShadow: "0 4px 15px rgba(236, 72, 153, 0.5)",
        }}
      >
        구독 & 좋아요 누르고 다음 화 보기 🔔
      </div>
    </div>
  );
};

const SingleSubtitle: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 20, stiffness: 160 } });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 80,
        left: 20,
        right: 20,
        display: "flex",
        justifyContent: "center",
        opacity: spr,
        transform: `translateY(${(1 - spr) * 12}px)`,
        zIndex: 60,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(7, 11, 20, 0.95)",
          border: "2px solid rgba(255, 255, 255, 0.2)",
          borderRadius: 20,
          padding: "14px 22px",
          maxWidth: "96%",
          boxShadow: "0 10px 35px rgba(0, 0, 0, 0.85)",
          backdropFilter: "blur(12px)",
          textAlign: "center",
        }}
      >
        <span
          style={{
            color: "#FFF",
            fontSize: text.length > 34 ? 20 : text.length > 25 ? 23 : 26,
            fontWeight: 900,
            lineHeight: 1.3,
            letterSpacing: "-0.01em",
            wordBreak: "keep-all",
            textShadow: "0 2px 8px rgba(0,0,0,0.8)",
          }}
        >
          {text}
        </span>
      </div>
    </div>
  );
};
