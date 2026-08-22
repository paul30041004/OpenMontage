import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface VHSGlitchProps {
  intensity?: number;
  accentColor?: string;
  backgroundColor?: string;
}

export const VHSGlitch: React.FC<VHSGlitchProps> = ({
  intensity = 1,
  accentColor = "#00FF66",
  backgroundColor = "#0A0A0F",
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // Deterministic pseudo-random glitch based on frame
  const glitchSeed = Math.floor(frame / 3);
  const glitchActive = glitchSeed % 5 === 0;

  // Horizontal displacement bands
  const bandCount = 8;
  const bands = Array.from({ length: bandCount }, (_, i) => {
    const bandY = (i / bandCount) * height;
    const bandHeight = height / bandCount;
    const offset = glitchActive
      ? Math.sin(frame * 0.5 + i * 2.7) * 30 * intensity
      : 0;
    return { y: bandY, height: bandHeight, offset };
  });

  // RGB split
  const rgbSplit = glitchActive ? 6 * intensity : 0;

  return (
    <AbsoluteFill style={{ background: backgroundColor, overflow: "hidden" }}>
      {/* Scanline tracking noise */}
      {glitchActive && (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: `${(frame * 3) % height}px`,
            height: "40px",
            background: "rgba(255, 255, 255, 0.15)",
            mixBlendMode: "screen",
          }}
        />
      )}

      {/* Horizontal displacement bands */}
      {bands.map((band, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: band.y,
            height: band.height,
            background: `rgba(${i % 2 === 0 ? "0,255,102" : "255,0,102"}, 0.03)`,
            transform: `translateX(${band.offset}px)`,
          }}
        />
      ))}

      {/* RGB chromatic aberration bars */}
      {glitchActive && (
        <>
          <div
            style={{
              position: "absolute",
              left: -rgbSplit,
              right: rgbSplit,
              top: "30%",
              height: "2px",
              background: "#FF0000",
              opacity: 0.6,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: rgbSplit,
              right: -rgbSplit,
              top: "50%",
              height: "2px",
              background: "#00FFFF",
              opacity: 0.6,
            }}
          />
        </>
      )}

      {/* VHS timestamp overlay */}
      <div
        style={{
          position: "absolute",
          top: "20px",
          left: "20px",
          color: accentColor,
          fontFamily: "monospace",
          fontSize: "24px",
          fontWeight: 700,
          textShadow: `0 0 8px ${accentColor}`,
        }}
      >
        ▶ PLAY
      </div>
      <div
        style={{
          position: "absolute",
          bottom: "20px",
          right: "20px",
          color: accentColor,
          fontFamily: "monospace",
          fontSize: "20px",
          textShadow: `0 0 8px ${accentColor}`,
        }}
      >
        {`00:${String(Math.floor(frame / fps)).padStart(2, "0")}:${String(frame % fps).padStart(2, "0")}`}
      </div>
    </AbsoluteFill>
  );
};
