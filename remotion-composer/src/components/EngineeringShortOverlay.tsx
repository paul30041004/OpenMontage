import React from "react";
import {
  AbsoluteFill,
  Img,
  Video,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { resolveAsset } from "../lib/resolveAsset";

export interface EngineeringShortOverlayProps {
  mediaSrc: string;
  isVideo?: boolean;
  topicTag?: string;
  dimensionLabel?: string;
  focalCallout?: string;
  badgeText?: string;
  subtitle: string;
  metricHighlight?: string;
}

export const EngineeringShortOverlay: React.FC<EngineeringShortOverlayProps> = ({
  mediaSrc,
  isVideo = false,
  topicTag = "공학 비하인드 · EP.03",
  dimensionLabel = "14.2mm 누진 회랑 (Progressive Corridor)",
  focalCallout = "곡률 반경 R = 42.8mm (왜곡 억제율 98.4%)",
  badgeText = "상단: 원거리 (0.0D) / 하단: 독서 (+2.5D)",
  subtitle = "경계선을 없애는 대신, 보이지 않는 측면으로 수차를 밀어냅니다.",
  metricHighlight = "수차 분산 99.1%",
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const resolvedSrc = resolveAsset(mediaSrc);

  // Subtle slow camera push on still images
  const scale = isVideo
    ? 1.0
    : interpolate(frame, [0, 240], [1.0, 1.07], { extrapolateRight: "clamp" });
  const translateY = isVideo
    ? 0
    : interpolate(frame, [0, 240], [0, -15], { extrapolateRight: "clamp" });

  // Spring animations for UI elements
  const topBadgeSpring = spring({ frame, fps, config: { damping: 18, stiffness: 120 } });
  const techLineSpring = spring({ frame: frame - 15, fps, config: { damping: 20, stiffness: 100 } });
  const calloutSpring = spring({ frame: frame - 30, fps, config: { damping: 20, stiffness: 120 } });
  const subtitleSpring = spring({ frame: frame - 10, fps, config: { damping: 22, stiffness: 150 } });

  // Measurement line width animation
  const lineWidth = interpolate(techLineSpring, [0, 1], [0, 480]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden", fontFamily: "sans-serif" }}>
      {/* 1. Background Media */}
      <AbsoluteFill
        style={{
          transform: `scale(${scale}) translateY(${translateY}px)`,
          transformOrigin: "center center",
        }}
      >
        {isVideo ? (
          <Video
            src={resolvedSrc}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <Img
            src={resolvedSrc}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        )}
      </AbsoluteFill>

      {/* Subtle top & bottom vignette to ensure text contrast */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.85) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* 2. Top Topic Tag */}
      <div
        style={{
          position: "absolute",
          top: 54,
          left: 40,
          display: "flex",
          alignItems: "center",
          gap: 12,
          opacity: topBadgeSpring,
          transform: `translateY(${(1 - topBadgeSpring) * -20}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.85)",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            borderRadius: 8,
            padding: "8px 16px",
            color: "#38BDF8",
            fontSize: 20,
            fontWeight: 700,
            letterSpacing: "0.05em",
            backdropFilter: "blur(8px)",
          }}
        >
          {topicTag}
        </div>
        {metricHighlight && (
          <div
            style={{
              backgroundColor: "rgba(34, 197, 94, 0.2)",
              border: "1px solid rgba(34, 197, 94, 0.6)",
              borderRadius: 8,
              padding: "8px 14px",
              color: "#4ADE80",
              fontSize: 18,
              fontWeight: 600,
              fontFamily: "monospace",
            }}
          >
            {metricHighlight}
          </div>
        )}
      </div>

      {/* 3. Technical Dimension Line (치수선) Overlay */}
      <div
        style={{
          position: "absolute",
          top: 360,
          left: (width - 480) / 2,
          width: 480,
          opacity: techLineSpring,
        }}
      >
        {/* Dimension Line with Arrow Ticks */}
        <div style={{ position: "relative", height: 28, display: "flex", alignItems: "center" }}>
          {/* Left Vertical Tick */}
          <div style={{ width: 2, height: 20, backgroundColor: "#38BDF8" }} />
          {/* Horizontal Line */}
          <div
            style={{
              width: lineWidth,
              height: 2,
              backgroundColor: "#38BDF8",
              boxShadow: "0 0 8px rgba(56, 189, 248, 0.6)",
            }}
          />
          {/* Right Vertical Tick */}
          <div style={{ width: 2, height: 20, backgroundColor: "#38BDF8" }} />
        </div>
        {/* Dimension Label */}
        <div
          style={{
            marginTop: 6,
            textAlign: "center",
            color: "#E2E8F0",
            fontSize: 17,
            fontWeight: 600,
            fontFamily: "monospace",
            textShadow: "0 2px 4px rgba(0,0,0,0.8)",
            letterSpacing: "0.02em",
          }}
        >
          {dimensionLabel}
        </div>
      </div>

      {/* 4. Optical Analysis Callout Card */}
      <div
        style={{
          position: "absolute",
          top: 480,
          left: 40,
          right: 40,
          opacity: calloutSpring,
          transform: `scale(${0.9 + 0.1 * calloutSpring})`,
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.8)",
            border: "1px solid rgba(148, 163, 184, 0.25)",
            borderRadius: 14,
            padding: "16px 20px",
            backdropFilter: "blur(12px)",
            boxShadow: "0 10px 25px rgba(0,0,0,0.5)",
          }}
        >
          <div
            style={{
              color: "#94A3B8",
              fontSize: 16,
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: 4,
            }}
          >
            Focal Surface Calibration
          </div>
          <div style={{ color: "#F8FAFC", fontSize: 21, fontWeight: 700, lineHeight: 1.35 }}>
            {focalCallout}
          </div>
          <div
            style={{
              marginTop: 10,
              display: "inline-block",
              backgroundColor: "rgba(56, 189, 248, 0.15)",
              color: "#38BDF8",
              borderRadius: 6,
              padding: "4px 10px",
              fontSize: 16,
              fontWeight: 600,
            }}
          >
            {badgeText}
          </div>
        </div>
      </div>

      {/* 5. Subtitle: ALWAYS EXACTLY ONE LINE (영상 규칙 준수) */}
      <div
        style={{
          position: "absolute",
          bottom: 120,
          left: 30,
          right: 30,
          display: "flex",
          justifyContent: "center",
          opacity: subtitleSpring,
          transform: `translateY(${(1 - subtitleSpring) * 15}px)`,
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(10, 15, 30, 0.92)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: 16,
            padding: "14px 28px",
            maxWidth: "92%",
            boxShadow: "0 8px 30px rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(10px)",
            textAlign: "center",
          }}
        >
          <span
            style={{
              color: "#FFFFFF",
              fontSize: subtitle.length > 32 ? 26 : 30, // 글자 수 많으면 크기 축소 (줄바꿈 방지)
              fontWeight: 800,
              lineHeight: 1.2,
              letterSpacing: "-0.01em",
              whiteSpace: "nowrap", // 무조건 한 줄 유지
              textShadow: "0 2px 6px rgba(0,0,0,0.6)",
            }}
          >
            {subtitle}
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
