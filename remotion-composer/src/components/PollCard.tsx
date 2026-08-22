import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface PollCardProps {
  question: string;
  options: { label: string; percentage: number }[];
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
}

export const PollCard: React.FC<PollCardProps> = ({
  question,
  options,
  accentColor = "#EC4899",
  backgroundColor = "#0F172A",
  fontFamily = "Inter, system-ui, sans-serif",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 15, stiffness: 100, mass: 0.8 } });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: backgroundColor,
        padding: "80px",
        fontFamily,
      }}
    >
      <div
        style={{
          width: "70%",
          maxWidth: "900px",
          background: "rgba(255, 255, 255, 0.06)",
          borderRadius: "24px",
          padding: "40px",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.9, 1])})`,
        }}
      >
        <div
          style={{
            color: accentColor,
            fontSize: "20px",
            fontWeight: 800,
            letterSpacing: "3px",
            marginBottom: "16px",
          }}
        >
          📊 POLL
        </div>
        <div style={{ color: "#fff", fontSize: "36px", fontWeight: 800, marginBottom: "32px" }}>
          {question}
        </div>

        {options.map((opt, i) => {
          const barIn = spring({
            frame: frame - (20 + i * 8),
            fps,
            config: { damping: 14, stiffness: 100, mass: 0.8 },
          });
          return (
            <div key={i} style={{ marginBottom: "20px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "8px",
                }}
              >
                <span style={{ color: "#fff", fontSize: "24px", fontWeight: 600 }}>{opt.label}</span>
                <span style={{ color: accentColor, fontSize: "24px", fontWeight: 800 }}>
                  {opt.percentage}%
                </span>
              </div>
              <div
                style={{
                  height: "28px",
                  background: "rgba(255, 255, 255, 0.08)",
                  borderRadius: "14px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${opt.percentage}%`,
                    background: `linear-gradient(90deg, ${accentColor}, ${accentColor}88)`,
                    borderRadius: "14px",
                    transform: `scaleX(${interpolate(barIn, [0, 1], [0, 1])})`,
                    transformOrigin: "left",
                    boxShadow: `0 0 16px ${accentColor}66`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
