import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface ScoreboardProps {
  homeTeam: string;
  awayTeam: string;
  homeScore: number;
  awayScore: number;
  periodLabel?: string;
  timeText?: string;
  homeColor?: string;
  awayColor?: string;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
}

export const Scoreboard: React.FC<ScoreboardProps> = ({
  homeTeam,
  awayTeam,
  homeScore,
  awayScore,
  periodLabel = "1Q",
  timeText = "10:00",
  homeColor = "#2563EB",
  awayColor = "#DC2626",
  accentColor = "#FACC15",
  backgroundColor = "#0A0A0F",
  fontFamily = "Inter, system-ui, sans-serif",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 14, stiffness: 120, mass: 0.8 } });
  const scorePop = spring({
    frame: frame - 10,
    fps,
    config: { damping: 10, stiffness: 200, mass: 0.6 },
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-start",
        alignItems: "center",
        paddingTop: "60px",
        fontFamily,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0px",
          background: backgroundColor,
          borderRadius: "16px",
          border: "2px solid rgba(255, 255, 255, 0.15)",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.7)",
          opacity: entrance,
          transform: `translateY(${interpolate(entrance, [0, 1], [-60, 0])}px)`,
          overflow: "hidden",
        }}
      >
        {/* Home Team */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            padding: "20px 32px",
            background: `linear-gradient(135deg, ${homeColor}22, transparent)`,
            borderRight: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              background: homeColor,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 900,
              fontSize: "22px",
            }}
          >
            {homeTeam.charAt(0)}
          </div>
          <span style={{ color: "#fff", fontSize: "30px", fontWeight: 800 }}>{homeTeam}</span>
        </div>

        {/* Score */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "20px",
            padding: "20px 40px",
            background: "rgba(0, 0, 0, 0.5)",
          }}
        >
          <span
            style={{
              color: "#fff",
              fontSize: "64px",
              fontWeight: 900,
              transform: `scale(${interpolate(scorePop, [0, 1], [0.5, 1])})`,
            }}
          >
            {homeScore}
          </span>
          <span style={{ color: "rgba(255, 255, 255, 0.4)", fontSize: "40px", fontWeight: 700 }}>:</span>
          <span
            style={{
              color: "#fff",
              fontSize: "64px",
              fontWeight: 900,
              transform: `scale(${interpolate(scorePop, [0, 1], [0.5, 1])})`,
            }}
          >
            {awayScore}
          </span>
        </div>

        {/* Away Team */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            padding: "20px 32px",
            background: `linear-gradient(135deg, ${awayColor}22, transparent)`,
            borderLeft: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          <span style={{ color: "#fff", fontSize: "30px", fontWeight: 800 }}>{awayTeam}</span>
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              background: awayColor,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#fff",
              fontWeight: 900,
              fontSize: "22px",
            }}
          >
            {awayTeam.charAt(0)}
          </div>
        </div>

        {/* Period + Time */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "16px 24px",
            background: accentColor,
            color: "#000",
          }}
        >
          <span style={{ fontSize: "20px", fontWeight: 800 }}>{periodLabel}</span>
          <span style={{ fontSize: "28px", fontWeight: 900 }}>{timeText}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
