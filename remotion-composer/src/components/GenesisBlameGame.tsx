import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { resolveAsset } from "../lib/resolveAsset";

export interface GenesisBlameGameProps {
  projectDir?: string;
}

export const GenesisBlameGame: React.FC<GenesisBlameGameProps> = ({
  projectDir = "genesis-3-blame-game",
}) => {
  const { fps, width, height } = useVideoConfig();
  const frame = useCurrentFrame();

  const narrationSrc = resolveAsset(`${projectDir}/master_narration.mp3`);
  const bgmSrc = resolveAsset(`${projectDir}/bgm_comedy.mp3`);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden", fontFamily: "sans-serif" }}>
      {/* Background Audio Tracks */}
      <Audio src={narrationSrc} volume={1.0} />
      <Audio src={bgmSrc} volume={0.20} />

      {/* ========================================================
          SCENE 1: 0.0s - 6.67s (Frames 0 - 200) - Audit Hook
         ======================================================== */}
      <Sequence from={0} durationInFrames={200}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/scene_01_audit_hook.png`)}
          zoomIn
        />
        {/* Top Topic Tag */}
        <TopBadge tag="성경/공학 비하인드 · EP.01" highlight="인류 최초 감사" />

        {/* Audit Stamp */}
        <AuditStamp text="긴급 본사 감사" sub="AUDIT IN PROGRESS" />

        {/* Subtitle */}
        <SingleSubtitle text="인류 역사상 가장 치졸하고 완벽한 핑계는 바로 창세기 3장에서 탄생했습니다." />
      </Sequence>

      {/* ========================================================
          SCENE 2: 6.67s - 20.42s (Frames 200 - 612) - Fig Leaf OOTD
         ======================================================== */}
      <Sequence from={200} durationInFrames={412}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/scene_02_fig_leaf_ootd.png`)}
          panLeft
        />
        <TopBadge tag="에덴동산 불시 점검" highlight="적발 1초 전" />

        {/* Callout Card */}
        <CalloutBox
          title="OOTD : 무화과 잎 치마 (급조됨)"
          body="위기 탈출용 위장 전술 (식은땀 분출 99%)"
          accent="#F59E0B"
        />

        {/* Split Subtitles */}
        <Sequence from={0} durationInFrames={200}>
          <SingleSubtitle text="선악과를 냅다 먹고 눈이 밝아진 아담과 하와." />
        </Sequence>
        <Sequence from={200} durationInFrames={212}>
          <SingleSubtitle text="무화과 잎으로 가리고 숨었는데, 대표님의 발소리가 들립니다. '네가 어디 있느냐?'" />
        </Sequence>
      </Sequence>

      {/* ========================================================
          SCENE 3: 20.42s - 33.76s (Frames 612 - 1012) - Interrogation
         ======================================================== */}
      <Sequence from={612} durationInFrames={400}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/scene_03_interrogation.png`)}
        />
        <TopBadge tag="제1차 대면 청문회" highlight="증인 심문" />

        {/* Evasion Gauge */}
        <GaugeBar label="동문서답 회피 지수" percent="99%" color="#EF4444" />

        <Sequence from={0} durationInFrames={200}>
          <SingleSubtitle text="아담은 '제가 벗어서 두려워 숨었습니다'라며 동문서답을 날렸지만," />
        </Sequence>
        <Sequence from={200} durationInFrames={200}>
          <SingleSubtitle text="대표님의 질문은 날카로웠습니다. '누가 너더러 벗었다더냐? 먹지 말란 과일 먹었지?'" />
        </Sequence>
      </Sequence>

      {/* ========================================================
          SCENE 4: 33.76s - 49.94s (Frames 1012 - 1498) - Adam's 50:50 Hero
         ======================================================== */}
      <Sequence from={1012} durationInFrames={486}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/scene_04_adam_pie_chart.png`)}
          dollyIn
        />
        <TopBadge tag="전설의 핑계 콤보" highlight="책임 분할 50:50" />

        {/* 50:50 Split Pie / Bar */}
        <BlameSplitCard />

        <Sequence from={0} durationInFrames={240}>
          <SingleSubtitle text="여기서 아담의 전설적인 핑계가 폭발합니다. '하나님이 주신 그 여자가 줘서 먹었는데요?'" />
        </Sequence>
        <Sequence from={240} durationInFrames={246}>
          <SingleSubtitle text="즉, 50%는 아내 탓, 50%는 그녀를 채용한 인사 담당자, 하나님 탓이라는 겁니다." />
        </Sequence>
      </Sequence>

      {/* ========================================================
          SCENE 5: 49.94s - 61.94s (Frames 1498 - 1858) - Eve's Bomb Pass
         ======================================================== */}
      <Sequence from={1498} durationInFrames={360}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/scene_05_eve_bomb_pass.png`)}
          panRight
        />
        <TopBadge tag="책임 폭탄 토스" highlight="반응속도 0.1초" />

        {/* Pass Graphic */}
        <CalloutBox
          title="책임 폭탄 고속 패스 완료!"
          body="하와 ➔ 뱀에게 100% 토스 ('뱀이 절 속였어요!')"
          accent="#10B981"
        />

        <SingleSubtitle text="불똥이 튄 하와도 0.1초 만에 뱀에게 패스합니다. '뱀이 저를 속여서 먹은 건데요?'" />
      </Sequence>

      {/* ========================================================
          SCENE 6: 61.94s - 72.67s (Frames 1858 - 2180) - Snake Verdict
         ======================================================== */}
      <Sequence from={1858} durationInFrames={322}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/scene_06_snake_judgment.png`)}
          tiltDown
        />
        <TopBadge tag="최종 판결 선고" highlight="변명권 기각" />

        {/* Verdict Stamp */}
        <VerdictStamp title="[ 선 고 ]" subtitle="변명 기회 박탈 & 다리 즉시 영구 압수" />

        <SingleSubtitle text="억울할 뻔했던 뱀. 하지만 하나님은 질문조차 던지지 않고 곧바로 다리를 압수하셨습니다." />
      </Sequence>

      {/* ========================================================
          SCENE 7: 72.67s - 83.52s (Frames 2180 - 2506) - DNA Closing
         ======================================================== */}
      <Sequence from={2180} durationInFrames={326}>
        <SceneBackground
          src={resolveAsset(`${projectDir}/scene_07_dna_closing.png`)}
          zoomOut
        />
        <TopBadge tag="인류 유산" highlight="남 탓 유전자 100%" />

        {/* Closing CTA */}
        <CalloutBox
          title="핑계의 역사는 에덴에서 시작되었다"
          body="여러분이 들어본 최고의 핑계는? 댓글로 남겨주세요!"
          accent="#8B5CF6"
        />

        <SingleSubtitle text="위기 때 남 탓부터 튀어나오는 우리 유전자, 이미 에덴동산에서 완벽히 코딩되었습니다." />
      </Sequence>
    </AbsoluteFill>
  );
};

// ==========================================
// SUB-COMPONENTS
// ==========================================

const SceneBackground: React.FC<{
  src: string;
  zoomIn?: boolean;
  zoomOut?: boolean;
  panLeft?: boolean;
  panRight?: boolean;
  dollyIn?: boolean;
  tiltDown?: boolean;
}> = ({ src, zoomIn, zoomOut, panLeft, panRight, dollyIn, tiltDown }) => {
  const frame = useCurrentFrame();

  let scale = 1.0;
  let translateX = 0;
  let translateY = 0;

  if (zoomIn || dollyIn) {
    scale = interpolate(frame, [0, 400], [1.0, 1.08], { extrapolateRight: "clamp" });
  } else if (zoomOut) {
    scale = interpolate(frame, [0, 400], [1.08, 1.0], { extrapolateRight: "clamp" });
  } else if (panLeft) {
    scale = 1.05;
    translateX = interpolate(frame, [0, 400], [10, -15], { extrapolateRight: "clamp" });
  } else if (panRight) {
    scale = 1.05;
    translateX = interpolate(frame, [0, 400], [-10, 15], { extrapolateRight: "clamp" });
  } else if (tiltDown) {
    scale = 1.05;
    translateY = interpolate(frame, [0, 400], [-10, 15], { extrapolateRight: "clamp" });
  }

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
        transformOrigin: "center center",
      }}
    >
      <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 20%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.85) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

const TopBadge: React.FC<{ tag: string; highlight?: string }> = ({ tag, highlight }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 18, stiffness: 120 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 54,
        left: 40,
        display: "flex",
        alignItems: "center",
        gap: 12,
        opacity: spr,
        transform: `translateY(${(1 - spr) * -20}px)`,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(15, 23, 42, 0.88)",
          border: "1px solid rgba(56, 189, 248, 0.45)",
          borderRadius: 8,
          padding: "8px 16px",
          color: "#38BDF8",
          fontSize: 20,
          fontWeight: 700,
          letterSpacing: "0.03em",
          backdropFilter: "blur(8px)",
        }}
      >
        {tag}
      </div>
      {highlight && (
        <div
          style={{
            backgroundColor: "rgba(239, 68, 68, 0.25)",
            border: "1px solid rgba(239, 68, 68, 0.6)",
            borderRadius: 8,
            padding: "8px 14px",
            color: "#F87171",
            fontSize: 18,
            fontWeight: 700,
          }}
        >
          {highlight}
        </div>
      )}
    </div>
  );
};

const AuditStamp: React.FC<{ text: string; sub: string }> = ({ text, sub }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame: frame - 15, fps, config: { damping: 14, stiffness: 200 } });

  if (frame < 15) return null;

  return (
    <div
      style={{
        position: "absolute",
        top: 380,
        left: 60,
        right: 60,
        display: "flex",
        justifyContent: "center",
        opacity: spr,
        transform: `scale(${interpolate(spr, [0, 1], [2.2, 1.0])}) rotate(-8deg)`,
      }}
    >
      <div
        style={{
          border: "5px solid #EF4444",
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          padding: "16px 32px",
          borderRadius: 14,
          textAlign: "center",
          boxShadow: "0 0 30px rgba(239, 68, 68, 0.5)",
          backdropFilter: "blur(6px)",
        }}
      >
        <div style={{ color: "#EF4444", fontSize: 44, fontWeight: 900, letterSpacing: "0.1em" }}>
          {text}
        </div>
        <div style={{ color: "#FCA5A5", fontSize: 20, fontWeight: 700, letterSpacing: "0.15em", marginTop: 4 }}>
          {sub}
        </div>
      </div>
    </div>
  );
};

const GaugeBar: React.FC<{ label: string; percent: string; color: string }> = ({ label, percent, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame: frame - 10, fps, config: { damping: 16, stiffness: 120 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 360,
        left: 50,
        right: 50,
        backgroundColor: "rgba(15, 23, 42, 0.88)",
        border: "1px solid rgba(255, 255, 255, 0.15)",
        borderRadius: 14,
        padding: "18px 24px",
        backdropFilter: "blur(10px)",
        opacity: spr,
        transform: `translateY(${(1 - spr) * 20}px)`,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
        <span style={{ color: "#E2E8F0", fontSize: 20, fontWeight: 700 }}>{label}</span>
        <span style={{ color, fontSize: 22, fontWeight: 900 }}>{percent}</span>
      </div>
      <div style={{ width: "100%", height: 14, backgroundColor: "rgba(255, 255, 255, 0.1)", borderRadius: 7, overflow: "hidden" }}>
        <div
          style={{
            width: `${interpolate(spr, [0, 1], [0, 99])}%`,
            height: "100%",
            backgroundColor: color,
            borderRadius: 7,
            boxShadow: `0 0 10px ${color}`,
          }}
        />
      </div>
    </div>
  );
};

const BlameSplitCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame: frame - 15, fps, config: { damping: 15, stiffness: 140 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 320,
        left: 40,
        right: 40,
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        border: "2px solid rgba(56, 189, 248, 0.5)",
        borderRadius: 18,
        padding: "24px 22px",
        boxShadow: "0 20px 40px rgba(0,0,0,0.7)",
        backdropFilter: "blur(12px)",
        opacity: spr,
        transform: `scale(${0.9 + 0.1 * spr})`,
      }}
    >
      <div style={{ textAlign: "center", color: "#F8FAFC", fontSize: 24, fontWeight: 800, marginBottom: 16 }}>
        아담의 책임 전가 콤보 분석
      </div>
      <div style={{ display: "flex", gap: 12, height: 90 }}>
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(239, 68, 68, 0.2)",
            border: "1px solid #EF4444",
            borderRadius: 12,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <div style={{ color: "#F87171", fontSize: 16, fontWeight: 700 }}>아내(하와) 탓</div>
          <div style={{ color: "#FFFFFF", fontSize: 32, fontWeight: 900 }}>50%</div>
        </div>
        <div
          style={{
            flex: 1,
            backgroundColor: "rgba(59, 130, 246, 0.2)",
            border: "1px solid #3B82F6",
            borderRadius: 12,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <div style={{ color: "#60A5FA", fontSize: 16, fontWeight: 700 }}>하나님(채용) 탓</div>
          <div style={{ color: "#FFFFFF", fontSize: 32, fontWeight: 900 }}>50%</div>
        </div>
      </div>
      <div style={{ textAlign: "center", color: "#94A3B8", fontSize: 16, marginTop: 14, fontWeight: 600 }}>
        "하나님이 주셔서 나와 함께 있게 하신 여자"
      </div>
    </div>
  );
};

const VerdictStamp: React.FC<{ title: string; subtitle: string }> = ({ title, subtitle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame: frame - 15, fps, config: { damping: 12, stiffness: 180 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 360,
        left: 40,
        right: 40,
        display: "flex",
        justifyContent: "center",
        opacity: spr,
        transform: `scale(${interpolate(spr, [0, 1], [1.8, 1.0])})`,
      }}
    >
      <div
        style={{
          border: "4px solid #F59E0B",
          backgroundColor: "rgba(245, 158, 11, 0.15)",
          padding: "20px 24px",
          borderRadius: 16,
          textAlign: "center",
          boxShadow: "0 0 35px rgba(245, 158, 11, 0.4)",
          backdropFilter: "blur(8px)",
        }}
      >
        <div style={{ color: "#F59E0B", fontSize: 36, fontWeight: 900 }}>{title}</div>
        <div style={{ color: "#FDE68A", fontSize: 20, fontWeight: 700, marginTop: 8 }}>{subtitle}</div>
      </div>
    </div>
  );
};

const CalloutBox: React.FC<{ title: string; body: string; accent: string }> = ({ title, body, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const spr = spring({ frame, fps, config: { damping: 18, stiffness: 120 } });

  return (
    <div
      style={{
        position: "absolute",
        top: 360,
        left: 40,
        right: 40,
        backgroundColor: "rgba(15, 23, 42, 0.9)",
        border: `1px solid ${accent}`,
        borderRadius: 16,
        padding: "20px 24px",
        backdropFilter: "blur(12px)",
        boxShadow: "0 10px 30px rgba(0,0,0,0.6)",
        opacity: spr,
        transform: `translateY(${(1 - spr) * 20}px)`,
      }}
    >
      <div style={{ color: accent, fontSize: 22, fontWeight: 800, marginBottom: 8 }}>{title}</div>
      <div style={{ color: "#F1F5F9", fontSize: 18, fontWeight: 600, lineHeight: 1.4 }}>{body}</div>
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
        bottom: 120,
        left: 30,
        right: 30,
        display: "flex",
        justifyContent: "center",
        opacity: spr,
        transform: `translateY(${(1 - spr) * 12}px)`,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(10, 15, 30, 0.94)",
          border: "1px solid rgba(255, 255, 255, 0.16)",
          borderRadius: 16,
          padding: "14px 26px",
          maxWidth: "94%",
          boxShadow: "0 8px 30px rgba(0, 0, 0, 0.75)",
          backdropFilter: "blur(10px)",
          textAlign: "center",
        }}
      >
        <span
          style={{
            color: "#FFFFFF",
            fontSize: text.length > 36 ? 24 : text.length > 28 ? 27 : 30,
            fontWeight: 800,
            lineHeight: 1.25,
            letterSpacing: "-0.01em",
            whiteSpace: "nowrap",
            textShadow: "0 2px 6px rgba(0,0,0,0.6)",
          }}
        >
          {text}
        </span>
      </div>
    </div>
  );
};
