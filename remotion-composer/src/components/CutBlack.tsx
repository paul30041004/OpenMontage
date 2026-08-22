import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface CutBlackProps {
  title?: string;
  subtitle?: string;
  backgroundColor?: string;
  accentColor?: string;
  fontFamily?: string;
  holdSeconds?: number;
  fadeOutSeconds?: number;
}

export const CutBlack: React.FC<CutBlackProps> = ({
  title,
  subtitle,
  backgroundColor = "#000000",
  accentColor = "#FFFFFF",
  fontFamily = "Inter, system-ui, sans-serif",
  holdSeconds = 2.5,
  fadeOutSeconds = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Fade IN from black
  const fadeIn = interpolate(frame, [0, Math.round(fps * 0.5)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Hold, then fade OUT to black (the "cut to black" effect)
  const holdFrames = Math.round(holdSeconds * fps);
  const fadeOutStart = durationInFrames - Math.round(fadeOutSeconds * fps);
  const fadeOut = interpolate(frame, [fadeOutStart, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: backgroundColor, fontFamily }}>
      {title && (
        <AbsoluteFill
          style={{
            justifyContent: "center",
            alignItems: "center",
            opacity: fadeIn * fadeOut,
            transform: `scale(${interpolate(fadeIn, [0, 1], [0.95, 1])})`,
          }}
        >
          <div
            style={{
              color: accentColor,
              fontSize: "88px",
              fontWeight: 900,
              textAlign: "center",
              letterSpacing: "1px",
              wordBreak: "keep-all",
            }}
          >
            {title}
          </div>
          {subtitle && (
            <div
              style={{
                color: "rgba(255, 255, 255, 0.6)",
                fontSize: "32px",
                fontWeight: 500,
                marginTop: "20px",
              }}
            >
              {subtitle}
            </div>
          )}
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
