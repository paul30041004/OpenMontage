import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface NeonTextProps {
  text: string;
  fontSize?: number;
  color?: string;
  backgroundColor?: string;
  fontFamily?: string;
  flicker?: boolean;
  glowIntensity?: number;
}

export const NeonText: React.FC<NeonTextProps> = ({
  text,
  fontSize = 110,
  color = "#FF2D95",
  backgroundColor = "#0A0A0F",
  fontFamily = "Black Han Sans, Inter, system-ui, sans-serif",
  flicker = true,
  glowIntensity = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 14, stiffness: 90, mass: 0.9 } });

  // Neon flicker (subtle random brightness variation)
  const flickerAmount = flicker
    ? 1 - Math.abs(Math.sin(frame / 5)) * 0.15 - (Math.floor(frame / 13) % 3 === 0 ? 0.3 : 0)
    : 1;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: backgroundColor,
        fontFamily,
      }}
    >
      <div
        style={{
          opacity: entrance * flickerAmount,
          fontSize,
          fontWeight: 900,
          color,
          textAlign: "center",
          letterSpacing: "2px",
          whiteSpace: "pre-wrap",
          textShadow: `
            0 0 7px ${color},
            0 0 10px ${color},
            0 0 21px ${color},
            0 0 42px ${color},
            0 0 82px ${color}
          `,
          filter: `blur(${(1 - glowIntensity) * 2}px)`,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
