import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface BreakingAlertProps {
  headline: string;
  subheadline?: string;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
}

export const BreakingAlert: React.FC<BreakingAlertProps> = ({
  headline,
  subheadline,
  accentColor = "#E11D48",
  backgroundColor = "#0A0A0F",
  fontFamily = "Inter, system-ui, sans-serif",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const flash = Math.floor(frame / 6) % 2 === 0;
  const entrance = spring({ frame, fps, config: { damping: 12, stiffness: 180, mass: 0.6 } });

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
          width: "75%",
          maxWidth: "1100px",
          background: `linear-gradient(135deg, ${accentColor}22, rgba(10, 10, 15, 0.95))`,
          borderRadius: "20px",
          border: `3px solid ${accentColor}`,
          boxShadow: `0 0 60px ${accentColor}66, 0 30px 60px rgba(0, 0, 0, 0.7)`,
          padding: "50px",
          textAlign: "center",
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.7, 1])})`,
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "12px",
            background: accentColor,
            color: "#fff",
            padding: "12px 28px",
            borderRadius: "30px",
            fontSize: "28px",
            fontWeight: 900,
            letterSpacing: "2px",
            marginBottom: "30px",
            animation: flash ? "none" : "none",
            opacity: flash ? 1 : 0.7,
          }}
        >
          ⚠️ 긴급 속보
        </div>

        <div
          style={{
            color: "#fff",
            fontSize: "56px",
            fontWeight: 900,
            lineHeight: 1.25,
            marginBottom: "20px",
            wordBreak: "keep-all",
          }}
        >
          {headline}
        </div>

        {subheadline && (
          <div
            style={{
              color: "rgba(255, 255, 255, 0.8)",
              fontSize: "28px",
              fontWeight: 500,
              lineHeight: 1.4,
            }}
          >
            {subheadline}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
