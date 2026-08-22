import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface WeatherCardProps {
  city: string;
  temperature: number;
  condition: string;
  icon?: string;
  highTemp?: number;
  lowTemp?: number;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({
  city,
  temperature,
  condition,
  icon = "☀️",
  highTemp,
  lowTemp,
  accentColor = "#38BDF8",
  backgroundColor = "#0F172A",
  fontFamily = "Inter, system-ui, sans-serif",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 14, stiffness: 100, mass: 0.8 } });
  const tempCount = interpolate(frame, [0, 30], [0, temperature], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

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
          background: "linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(15, 23, 42, 0.9))",
          borderRadius: "28px",
          padding: "50px 60px",
          border: "1px solid rgba(255, 255, 255, 0.15)",
          boxShadow: "0 30px 60px rgba(0, 0, 0, 0.6)",
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.85, 1])})`,
          textAlign: "center",
        }}
      >
        <div style={{ color: "rgba(255, 255, 255, 0.6)", fontSize: "28px", fontWeight: 600, marginBottom: "8px" }}>
          {city}
        </div>

        <div style={{ fontSize: "100px", margin: "20px 0" }}>{icon}</div>

        <div
          style={{
            color: "#fff",
            fontSize: "120px",
            fontWeight: 900,
            lineHeight: 1,
            textShadow: `0 0 40px ${accentColor}66`,
          }}
        >
          {Math.round(tempCount)}°
        </div>

        <div style={{ color: accentColor, fontSize: "36px", fontWeight: 700, marginTop: "12px" }}>
          {condition}
        </div>

        {(highTemp !== undefined || lowTemp !== undefined) && (
          <div
            style={{
              display: "flex",
              gap: "24px",
              justifyContent: "center",
              marginTop: "20px",
              color: "rgba(255, 255, 255, 0.7)",
              fontSize: "24px",
              fontWeight: 600,
            }}
          >
            {highTemp !== undefined && <span>최고 {highTemp}°</span>}
            {lowTemp !== undefined && <span>최저 {lowTemp}°</span>}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
