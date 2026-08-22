import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface FlashbackProps {
  label?: string;
  backgroundColor?: string;
  accentColor?: string;
  fontFamily?: string;
  sepiaAmount?: number;
  blurAmount?: number;
}

export const Flashback: React.FC<FlashbackProps> = ({
  label = "회상",
  backgroundColor = "#0F172A",
  accentColor = "#C8A165",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  sepiaAmount = 0.7,
  blurAmount = 2,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Flashback transition: blur in → sepia → label
  const blurIn = interpolate(frame, [0, Math.round(fps * 0.6)], [8, blurAmount], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const labelIn = spring({ frame: frame - 8, fps, config: { damping: 15, stiffness: 100, mass: 0.8 } });

  // Wavy dream-like edge
  const wave = Math.sin(frame / (fps * 0.5)) * 4;

  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        fontFamily,
        filter: `sepia(${sepiaAmount}) blur(${blurIn}px)`,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Wavy borders (dream sequence feel) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          border: `8px solid rgba(200, 161, 101, 0.3)`,
          borderRadius: "40px",
          margin: "30px",
          transform: `scale(${1 + wave * 0.002})`,
        }}
      />

      <div
        style={{
          color: accentColor,
          fontSize: "72px",
          fontWeight: 900,
          letterSpacing: "8px",
          opacity: labelIn,
          transform: `scale(${interpolate(labelIn, [0, 1], [0.8, 1])})`,
          textShadow: `0 0 30px ${accentColor}88`,
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};
