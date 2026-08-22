import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface CliffhangerProps {
  title?: string;
  subtitle?: string;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  fadeOutSeconds?: number;
}

export const Cliffhanger: React.FC<CliffhangerProps> = ({
  title = "다음 편에 계속...",
  subtitle = "곧 공개됩니다",
  accentColor = "#FACC15",
  backgroundColor = "#0A0A0F",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  fadeOutSeconds = 0.8,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 15, stiffness: 100, mass: 0.8 } });

  const fadeOutStart = durationInFrames - Math.round(fadeOutSeconds * fps);
  const fadeOut = interpolate(frame, [fadeOutStart, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        justifyContent: "center",
        alignItems: "center",
        fontFamily,
        opacity: fadeOut,
      }}
    >
      <div
        style={{
          textAlign: "center",
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.8, 1])})`,
        }}
      >
        <div
          style={{
            color: accentColor,
            fontSize: "28px",
            fontWeight: 800,
            letterSpacing: "6px",
            marginBottom: "20px",
          }}
        >
          TO BE CONTINUED
        </div>
        <div style={{ color: "#fff", fontSize: "60px", fontWeight: 900, wordBreak: "keep-all" }}>
          {title}
        </div>
        {subtitle && (
          <div style={{ color: "rgba(255,255,255,0.6)", fontSize: "28px", marginTop: "16px" }}>
            {subtitle}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
