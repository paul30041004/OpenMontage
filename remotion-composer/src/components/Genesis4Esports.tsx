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

export interface Genesis4EsportsProps {
  projectDir?: string;
}

export const Genesis4Esports: React.FC<Genesis4EsportsProps> = ({
  projectDir = "genesis-4-esports",
}) => {
  const { fps, width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  const narrationSrc = resolveAsset(`${projectDir}/master_narration.wav`);
  const bgmSrc = resolveAsset(`${projectDir}/bgm_esports.mp3`);

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
      <TopEsportsHeader />

      {/* ========================================================
          SCENE 1: 0.0s - 9.60s (Frames 0 - 288) - Opening Matchup
         ======================================================== */}
      <Sequence from={0} durationInFrames={288}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_01.png`)}
          zoomIn
        />
        <VersusMatchupBanner
          title="인류 최초의 공식전 결승"
          player1="카인 (농작물 메타)"
          player2="아벨 (양고기 1등급)"
        />
        <SingleSubtitle text="자, 인류 역사상 최초의 공식전! 카인 대 아벨의 제사 공물 메타 결승전 시작합니다!" />
      </Sequence>

      {/* ========================================================
          SCENE 2: 9.60s - 14.23s (Frames 288 - 427) - Cain's Offering
         ======================================================== */}
      <Sequence from={288} durationInFrames={139}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_02.png`)}
          panRight
        />
        <PlayerTurnCard
          player="P1 카인 (Cain)"
          action="선공 공물 바치기"
          item="정성껏 수확한 곡식 & 땅의 소산 바구니"
          tier="B-Tier 메타 픽"
          accent="#F59E0B"
        />
        <SingleSubtitle text="선공 카인 선수, 정성껏 수확한 농작물을 올립니다!" />
      </Sequence>

      {/* ========================================================
          SCENE 3: 14.23s - 18.88s (Frames 427 - 566) - Abel's Offering
         ======================================================== */}
      <Sequence from={427} durationInFrames={139}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_03.png`)}
          zoomIn
        />
        <PlayerTurnCard
          player="P2 아벨 (Abel)"
          action="맞불 제물 바치기"
          item="어린 양의 첫 새끼 & 엄선된 기름진 부위"
          tier="S-Tier 1등급 공물"
          accent="#10B981"
        />
        <SingleSubtitle text="이어서 아벨 선수, 어린 양의 기름진 첫 새끼로 정면 승부!" />
      </Sequence>

      {/* ========================================================
          SCENE 4: 18.88s - 24.80s (Frames 566 - 744) - Operator's Pick
         ======================================================== */}
      <Sequence from={566} durationInFrames={178}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_04.png`)}
          zoomIn
        />
        <VerdictBadge
          headline="⭐ OPERATOR'S PICK : 아벨 채택 ⭐"
          detail="하늘의 열납 불꽃 강림 · 아벨의 제물만 수락"
          accent="#38BDF8"
        />
        <SingleSubtitle text="그런데 여기서 판정 갈립니다! 운영자 신(God), 아벨의 제물만 채택!" />
      </Sequence>

      {/* ========================================================
          SCENE 5: 24.80s - 30.72s (Frames 744 - 922) - Cain's Breakdown
         ======================================================== */}
      <Sequence from={744} durationInFrames={178}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_05.png`)}
          zoomIn
        />
        <MentalGaugeBar
          player="카인 (Cain)"
          status="안색 흑화 · 멘탈 붕괴 경보"
          percent="5%"
          color="#EF4444"
        />
        <SingleSubtitle text="카인 선수 안색이 굳어지면서 멘탈 터지기 직전이에요!" />
      </Sequence>

      {/* ========================================================
          SCENE 6: 30.72s - 37.83s (Frames 922 - 1135) - Warning Ping
         ======================================================== */}
      <Sequence from={922} durationInFrames={213}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_06.png`)}
          tiltUp
        />
        <WarningPingAlert
          title="🚨 운영자 긴급 경고 핑 (Warning)"
          message='"네가 분하여 함은 어찜이며... 죄의 소원을 다스릴지니라"'
          penalty="경고 무시 시 페널티 부과"
        />
        <SingleSubtitle text="운영자가 죄를 다스리라 경고 핑을 찍었지만!" />
      </Sequence>

      {/* ========================================================
          SCENE 7: 37.83s - 44.96s (Frames 1135 - 1349) - Solo Kill (PK)
         ======================================================== */}
      <Sequence from={1135} durationInFrames={214}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_07.png`)}
          handheld
        />
        <SoloKillBanner
          killer="카인 (Cain)"
          victim="아벨 (Abel)"
          method="밀밭 유인 기습 짱돌 어택"
        />
        <SingleSubtitle text="아, 카인 선수, 아벨을 들판으로 부르더니... 그대로 솔로킬! 인류 최초의 피케이가 터집니다!" />
      </Sequence>

      {/* ========================================================
          SCENE 8: 44.96s - 50.00s (Frames 1349 - 1500) - Interrogation
         ======================================================== */}
      <Sequence from={1349} durationInFrames={151}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_08.png`)}
        />
        <InterrogationDialogueBox
          question='운영자: "네 아우 아벨이 어디 있느냐?"'
          excuse='카인: "내가 알지 못하나이다! 내가 서포터입니까?!"'
        />
        <SingleSubtitle text="네 아우 어디 있냐는 심문에, 제가 지키는 서포터입니까 핑계 대보지만!" />
      </Sequence>

      {/* ========================================================
          SCENE 9 (Pt 1): 50.00s - 55.04s (Frames 1500 - 1651) - Perma Ban
         ======================================================== */}
      <Sequence from={1500} durationInFrames={151}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_09.png`)}
          panLeft
        />
        <PermaBanStamp
          stampText="ACCOUNT PERMA-BANNED"
          reason="인류 최초 PK 위반 · 에덴 동쪽 노드 땅 영구 유배"
        />
        <SingleSubtitle text="결국 노드 땅으로 영구 밴 확정!" />
      </Sequence>

      {/* ========================================================
          SCENE 9 (Pt 2): 55.04s - 63.00s (Frames 1651 - 1890) - Outro
         ======================================================== */}
      <Sequence from={1651} durationInFrames={239}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/frame_09.png`)}
          zoomIn
        />
        <MarkOfCainEndCard
          title="질투가 부른 참혹한 결말"
          markInfo="🛡️ 가인의 표 (보호 패치 적용)"
          ctaText="다음 역사 매치 예고 · 구독 & 좋아요"
        />
        <SingleSubtitle text="질투와 분노가 부른 유리멘탈의 참혹한 결말! 다음 레전드 성경 매치에서 뵙겠습니다!" />
      </Sequence>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Sub-components: Top Header, HUD, Badges, and Overlays
// ---------------------------------------------------------------------------

const TopEsportsHeader: React.FC = () => {
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
          backgroundColor: "rgba(15, 23, 42, 0.88)",
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
        <span
          style={{
            color: "#F8FAFC",
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: "0.08em",
          }}
        >
          LIVE · GENESIS LEAGUE 2026
        </span>
      </div>

      <div
        style={{
          backgroundColor: "rgba(15, 23, 42, 0.88)",
          border: "1px solid rgba(56, 189, 248, 0.3)",
          borderRadius: 24,
          padding: "8px 16px",
          color: "#38BDF8",
          fontSize: 13,
          fontWeight: 800,
          backdropFilter: "blur(10px)",
        }}
      >
        창세기 4장 결승전
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
    scale = interpolate(frame, [0, 250], [1.02, 1.18], { extrapolateRight: "clamp" });
  }
  if (panRight) {
    translateX = interpolate(frame, [0, 200], [-25, 25], { extrapolateRight: "clamp" });
  }
  if (panLeft) {
    translateX = interpolate(frame, [0, 200], [25, -25], { extrapolateRight: "clamp" });
  }
  if (tiltUp) {
    translateY = interpolate(frame, [0, 250], [30, -20], { extrapolateRight: "clamp" });
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
      {/* Top & Bottom Vignette Gradients for Text Readability */}
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

const VersusMatchupBanner: React.FC<{
  title: string;
  player1: string;
  player2: string;
}> = ({ title, player1, player2 }) => {
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
        display: "flex",
        flexDirection: "column",
        gap: 10,
        zIndex: 40,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(15, 23, 42, 0.92)",
          border: "2px solid #EC4899",
          borderRadius: 20,
          padding: "16px 20px",
          boxShadow: "0 10px 30px rgba(236, 72, 153, 0.3)",
          backdropFilter: "blur(12px)",
          textAlign: "center",
        }}
      >
        <div style={{ color: "#F472B6", fontSize: 14, fontWeight: 900, letterSpacing: "0.1em" }}>
          {title.toUpperCase()}
        </div>
        <div style={{ display: "flex", justifyContent: "space-around", alignItems: "center", marginTop: 10 }}>
          <div style={{ color: "#FBBF24", fontSize: 18, fontWeight: 800 }}>{player1}</div>
          <div
            style={{
              backgroundColor: "#EC4899",
              color: "#FFF",
              padding: "4px 10px",
              borderRadius: 8,
              fontSize: 14,
              fontWeight: 900,
            }}
          >
            VS
          </div>
          <div style={{ color: "#34D399", fontSize: 18, fontWeight: 800 }}>{player2}</div>
        </div>
      </div>
    </div>
  );
};

const PlayerTurnCard: React.FC<{
  player: string;
  action: string;
  item: string;
  tier: string;
  accent: string;
}> = ({ player, action, item, tier, accent }) => {
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
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        border: `2px solid ${accent}`,
        borderRadius: 20,
        padding: "18px 24px",
        backdropFilter: "blur(12px)",
        boxShadow: `0 8px 30px ${accent}33`,
        zIndex: 40,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ color: accent, fontSize: 16, fontWeight: 800 }}>{player}</span>
        <span
          style={{
            backgroundColor: `${accent}22`,
            color: accent,
            border: `1px solid ${accent}`,
            padding: "2px 10px",
            borderRadius: 12,
            fontSize: 13,
            fontWeight: 800,
          }}
        >
          {tier}
        </span>
      </div>
      <div style={{ color: "#F8FAFC", fontSize: 20, fontWeight: 800, marginTop: 6 }}>{item}</div>
      <div style={{ color: "#94A3B8", fontSize: 14, fontWeight: 600, marginTop: 4 }}>{action}</div>
    </div>
  );
};

const VerdictBadge: React.FC<{
  headline: string;
  detail: string;
  accent: string;
}> = ({ headline, detail, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame: frame - 10, fps, config: { damping: 12, stiffness: 180 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 110,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `scale(${interpolate(spr, [0, 1], [1.3, 1.0])})`,
        backgroundColor: "rgba(15, 23, 42, 0.94)",
        border: `3px solid ${accent}`,
        borderRadius: 20,
        padding: "20px 24px",
        textAlign: "center",
        boxShadow: `0 0 35px ${accent}66`,
        backdropFilter: "blur(12px)",
        zIndex: 40,
      }}
    >
      <div style={{ color: accent, fontSize: 24, fontWeight: 900 }}>{headline}</div>
      <div style={{ color: "#E0F2FE", fontSize: 16, fontWeight: 700, marginTop: 8 }}>{detail}</div>
    </div>
  );
};

const MentalGaugeBar: React.FC<{
  player: string;
  status: string;
  percent: string;
  color: string;
}> = ({ player, status, percent, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });
  const dropW = interpolate(frame, [0, 100], [100, 5], { extrapolateRight: "clamp" });

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
        border: `2px solid ${color}`,
        borderRadius: 20,
        padding: "18px 24px",
        backdropFilter: "blur(12px)",
        boxShadow: `0 0 30px ${color}44`,
        zIndex: 40,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ color: "#F8FAFC", fontSize: 17, fontWeight: 800 }}>{player} 멘탈 수치</span>
        <span style={{ color: color, fontSize: 16, fontWeight: 900 }}>{status}</span>
      </div>
      {/* Gauge track */}
      <div
        style={{
          width: "100%",
          height: 16,
          backgroundColor: "rgba(255,255,255,0.1)",
          borderRadius: 8,
          overflow: "hidden",
          marginTop: 12,
        }}
      >
        <div
          style={{
            width: `${dropW}%`,
            height: "100%",
            backgroundColor: color,
            borderRadius: 8,
            boxShadow: `0 0 12px ${color}`,
          }}
        />
      </div>
    </div>
  );
};

const WarningPingAlert: React.FC<{
  title: string;
  message: string;
  penalty: string;
}> = ({ title, message, penalty }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 10, stiffness: 140 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 110,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `translateY(${(1 - spr) * 25}px)`,
        backgroundColor: "rgba(30, 20, 10, 0.94)",
        border: "2px solid #F59E0B",
        borderRadius: 20,
        padding: "18px 22px",
        boxShadow: "0 0 30px rgba(245, 158, 11, 0.4)",
        backdropFilter: "blur(12px)",
        zIndex: 40,
      }}
    >
      <div style={{ color: "#F59E0B", fontSize: 18, fontWeight: 900 }}>{title}</div>
      <div style={{ color: "#FEF3C7", fontSize: 16, fontWeight: 700, marginTop: 8, lineHeight: 1.4 }}>
        {message}
      </div>
      <div style={{ color: "#FBBF24", fontSize: 13, fontWeight: 600, marginTop: 8 }}>{penalty}</div>
    </div>
  );
};

const SoloKillBanner: React.FC<{
  killer: string;
  victim: string;
  method: string;
}> = ({ killer, victim, method }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 12, stiffness: 200 } });
  const pulse = Math.sin(frame / 4) * 0.15 + 1.0;

  return (
    <div
      style={{
        position: "absolute",
        top: 100,
        left: 20,
        right: 20,
        opacity: spr,
        transform: `scale(${interpolate(spr, [0, 1], [1.6, 1.0]) * pulse})`,
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
      <div
        style={{
          color: "#FEF2F2",
          fontSize: 32,
          fontWeight: 900,
          letterSpacing: "0.05em",
          textShadow: "0 0 20px rgba(255,255,255,0.8)",
        }}
      >
        ⚔️ FIRST BLOOD / SOLO KILL ⚔️
      </div>
      <div style={{ color: "#FEE2E2", fontSize: 19, fontWeight: 800, marginTop: 8 }}>
        {killer} ➔ {victim}
      </div>
      <div style={{ color: "#FECACA", fontSize: 14, fontWeight: 600, marginTop: 4 }}>
        사유: {method}
      </div>
    </div>
  );
};

const InterrogationDialogueBox: React.FC<{
  question: string;
  excuse: string;
}> = ({ question, excuse }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 15, stiffness: 130 } });

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
        border: "2px solid #818CF8",
        borderRadius: 20,
        padding: "18px 24px",
        backdropFilter: "blur(12px)",
        boxShadow: "0 10px 30px rgba(129, 140, 248, 0.3)",
        zIndex: 40,
      }}
    >
      <div style={{ color: "#818CF8", fontSize: 16, fontWeight: 800 }}>{question}</div>
      <div
        style={{
          color: "#F8FAFC",
          fontSize: 18,
          fontWeight: 800,
          marginTop: 10,
          backgroundColor: "rgba(239, 68, 68, 0.2)",
          padding: "8px 14px",
          borderRadius: 10,
          borderLeft: "4px solid #EF4444",
        }}
      >
        {excuse}
      </div>
    </div>
  );
};

const PermaBanStamp: React.FC<{
  stampText: string;
  reason: string;
}> = ({ stampText, reason }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame: frame - 8, fps, config: { damping: 10, stiffness: 200 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 120,
        left: 24,
        right: 24,
        opacity: spr,
        transform: `scale(${interpolate(spr, [0, 1], [1.8, 1.0])})`,
        backgroundColor: "rgba(0, 0, 0, 0.92)",
        border: "4px solid #EF4444",
        borderRadius: 24,
        padding: "24px 28px",
        textAlign: "center",
        boxShadow: "0 0 50px rgba(239, 68, 68, 0.8)",
        backdropFilter: "blur(14px)",
        zIndex: 45,
      }}
    >
      <div style={{ color: "#EF4444", fontSize: 32, fontWeight: 900, letterSpacing: "0.08em" }}>
        🚫 {stampText}
      </div>
      <div style={{ color: "#FCA5A5", fontSize: 17, fontWeight: 700, marginTop: 10 }}>
        {reason}
      </div>
    </div>
  );
};

const MarkOfCainEndCard: React.FC<{
  title: string;
  markInfo: string;
  ctaText: string;
}> = ({ title, markInfo, ctaText }) => {
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
        transform: `translateY(${(1 - spr) * 20}px)`,
        backgroundColor: "rgba(15, 23, 42, 0.94)",
        border: "2px solid #38BDF8",
        borderRadius: 20,
        padding: "20px 24px",
        textAlign: "center",
        boxShadow: "0 0 35px rgba(56, 189, 248, 0.4)",
        backdropFilter: "blur(12px)",
        zIndex: 40,
      }}
    >
      <div style={{ color: "#38BDF8", fontSize: 20, fontWeight: 800 }}>{title}</div>
      <div style={{ color: "#FDE047", fontSize: 17, fontWeight: 700, marginTop: 8 }}>{markInfo}</div>
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
        {ctaText}
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
