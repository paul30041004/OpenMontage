import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface AudioWaveformProps {
  title?: string;
  subtitle?: string;
  barCount?: number;
  waveColor?: string;
  accentColor?: string;
  styleMode?: "bars" | "circle" | "mirror";
}

export const AudioWaveformVisualizer: React.FC<AudioWaveformProps> = ({
  title = "AUDIO PLAYBACK",
  subtitle,
  barCount = 36,
  waveColor = "#6366f1",
  accentColor = "#ec4899",
  styleMode = "mirror",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8 },
  });

  const bars = Array.from({ length: barCount }, (_, i) => {
    // Generate organic simulated frequency peaks using multi-sine harmonics
    const speed = 0.08 + (i % 5) * 0.02;
    const offset = i * 0.35;
    const rawVal =
      Math.sin(frame * speed + offset) * 0.4 +
      Math.cos(frame * (speed * 1.5) + offset * 0.7) * 0.35 +
      Math.sin(frame * 0.15 + i * 0.8) * 0.25;

    // Normalize between 15% and 100% height
    const heightPercent = Math.max(12, Math.min(100, Math.abs(rawVal) * 100));
    return {
      id: i,
      height: heightPercent,
      color: i % 2 === 0 ? waveColor : accentColor,
    };
  });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Title Header */}
      <div
        style={{
          marginBottom: "40px",
          textAlign: "center",
          opacity: entrance,
          transform: `translateY(${interpolate(entrance, [0, 1], [30, 0])}px)`,
        }}
      >
        <span
          style={{
            display: "inline-block",
            padding: "8px 18px",
            background: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(12px)",
            borderRadius: "30px",
            color: "#ffffff",
            fontSize: "18px",
            fontWeight: 700,
            letterSpacing: "3px",
            border: "1px solid rgba(255, 255, 255, 0.2)",
          }}
        >
          {title}
        </span>
        {subtitle && (
          <p
            style={{
              color: "rgba(255, 255, 255, 0.75)",
              fontSize: "24px",
              marginTop: "12px",
              fontWeight: 500,
            }}
          >
            {subtitle}
          </p>
        )}
      </div>

      {/* Waveform Visualization Container */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
          height: "240px",
          width: "80%",
          padding: "30px",
          background: "rgba(15, 23, 42, 0.75)",
          backdropFilter: "blur(20px)",
          borderRadius: "24px",
          border: "1px solid rgba(255, 255, 255, 0.15)",
          boxShadow: `0 20px 50px rgba(0, 0, 0, 0.5), 0 0 40px ${waveColor}33`,
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.9, 1])})`,
        }}
      >
        {bars.map((b) => (
          <div
            key={b.id}
            style={{
              flex: 1,
              height: `${b.height}%`,
              background: `linear-gradient(180deg, ${accentColor} 0%, ${waveColor} 100%)`,
              borderRadius: "10px",
              boxShadow: `0 0 12px ${b.color}88`,
              transition: "height 0.05s ease",
            }}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};
