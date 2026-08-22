import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface CountdownTimerProps {
  fromSeconds: number;
  label?: string;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  showProgressRing?: boolean;
}

export const CountdownTimer: React.FC<CountdownTimerProps> = ({
  fromSeconds = 10,
  label = "COUNTDOWN",
  accentColor = "#FACC15",
  backgroundColor = "#0A0A0F",
  fontFamily = "Inter, system-ui, sans-serif",
  showProgressRing = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const elapsed = frame / fps;
  const remaining = Math.max(0, fromSeconds - elapsed);
  const display = Math.ceil(remaining);

  const progress = interpolate(elapsed, [0, fromSeconds], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const pulse = spring({
    frame: frame % Math.round(fps),
    fps,
    config: { damping: 8, stiffness: 200, mass: 0.5 },
  });

  const circumference = 2 * Math.PI * 120;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: backgroundColor,
        fontFamily,
      }}
    >
      {label && (
        <div
          style={{
            color: "rgba(255, 255, 255, 0.6)",
            fontSize: "28px",
            fontWeight: 700,
            letterSpacing: "6px",
            marginBottom: "30px",
          }}
        >
          {label}
        </div>
      )}

      <div style={{ position: "relative", width: "300px", height: "300px" }}>
        {showProgressRing && (
          <svg width="300" height="300" style={{ position: "absolute", inset: 0 }}>
            <circle
              cx="150"
              cy="150"
              r="120"
              fill="none"
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="12"
            />
            <circle
              cx="150"
              cy="150"
              r="120"
              fill="none"
              stroke={accentColor}
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={circumference * (1 - progress)}
              transform="rotate(-90 150 150)"
              style={{ filter: `drop-shadow(0 0 12px ${accentColor})` }}
            />
          </svg>
        )}

        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontSize: "120px",
            fontWeight: 900,
            transform: `scale(${interpolate(pulse, [0, 1], [1, 1.08])})`,
            textShadow: `0 0 30px ${accentColor}88`,
          }}
        >
          {display}
        </div>
      </div>
    </AbsoluteFill>
  );
};
