import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface LocationCardProps {
  location?: string;
  dateText?: string;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  align?: "left" | "right" | "center";
}

export const LocationCard: React.FC<LocationCardProps> = ({
  location = "서울, 대한민국",
  dateText = "2026년 8월",
  accentColor = "#38BDF8",
  backgroundColor = "rgba(0, 0, 0, 0.6)",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  align = "left",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 14, stiffness: 110, mass: 0.8 } });

  const alignMap: Record<string, React.CSSProperties> = {
    left: { left: "60px", alignItems: "flex-start" },
    right: { right: "60px", alignItems: "flex-end" },
    center: { left: "50%", transform: "translateX(-50%)", alignItems: "center" },
  };

  return (
    <div
      style={{
        position: "absolute",
        top: "60px",
        ...alignMap[align],
        display: "flex",
        flexDirection: "column",
        gap: "4px",
        fontFamily,
        opacity: entrance,
      }}
    >
      <div
        style={{
          width: "40px",
          height: "3px",
          background: accentColor,
          marginBottom: "8px",
          boxShadow: `0 0 10px ${accentColor}`,
        }}
      />
      <span style={{ color: "#fff", fontSize: "44px", fontWeight: 900, letterSpacing: "2px" }}>
        {location}
      </span>
      <span style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "24px", fontWeight: 500 }}>
        {dateText}
      </span>
    </div>
  );
};
