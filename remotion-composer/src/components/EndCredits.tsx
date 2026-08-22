import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface EndCreditsProps {
  title: string;
  credits: { role: string; name: string }[];
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  scrollSpeed?: number;
}

export const EndCredits: React.FC<EndCreditsProps> = ({
  title,
  credits,
  accentColor = "#FACC15",
  backgroundColor = "#0A0A0F",
  fontFamily = "Inter, system-ui, sans-serif",
  scrollSpeed = 1.2,
}) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();

  const scrollY = frame * scrollSpeed;

  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        overflow: "hidden",
        fontFamily,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          transform: `translateY(${-scrollY}px)`,
          textAlign: "center",
          width: "80%",
        }}
      >
        <div
          style={{
            color: "#fff",
            fontSize: "56px",
            fontWeight: 900,
            marginBottom: "60px",
            letterSpacing: "2px",
          }}
        >
          {title}
        </div>

        <div
          style={{
            width: "80px",
            height: "3px",
            background: accentColor,
            margin: "0 auto 60px",
            boxShadow: `0 0 16px ${accentColor}`,
          }}
        />

        {credits.map((c, i) => (
          <div key={i} style={{ marginBottom: "36px" }}>
            <div
              style={{
                color: accentColor,
                fontSize: "22px",
                fontWeight: 700,
                letterSpacing: "3px",
                textTransform: "uppercase",
                marginBottom: "6px",
              }}
            >
              {c.role}
            </div>
            <div style={{ color: "#fff", fontSize: "34px", fontWeight: 600 }}>{c.name}</div>
          </div>
        ))}

        <div style={{ marginTop: "80px", color: "rgba(255, 255, 255, 0.5)", fontSize: "20px" }}>
          OpenMontage Production
        </div>
      </div>
    </AbsoluteFill>
  );
};
