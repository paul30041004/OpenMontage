import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

export interface CRTScanlinesProps {
  scanlineOpacity?: number;
  curvature?: number;
  backgroundColor?: string;
  showFlicker?: boolean;
}

export const CRTScanlines: React.FC<CRTScanlinesProps> = ({
  scanlineOpacity = 0.15,
  curvature = 0.06,
  backgroundColor = "#0A0A0F",
  showFlicker = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const flicker = showFlicker ? 1 - Math.sin(frame / (fps * 0.5)) * 0.03 : 1;

  return (
    <AbsoluteFill style={{ background: backgroundColor, overflow: "hidden" }}>
      {/* Scanlines */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "repeating-linear-gradient(0deg, rgba(0,0,0,0.5) 0px, rgba(0,0,0,0.5) 1px, transparent 1px, transparent 3px)",
          opacity: scanlineOpacity * flicker,
          pointerEvents: "none",
        }}
      />

      {/* RGB phosphor mask */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "repeating-linear-gradient(90deg, rgba(255,0,0,0.03) 0px, rgba(0,255,0,0.03) 1px, rgba(0,0,255,0.03) 2px, transparent 3px)",
          pointerEvents: "none",
        }}
      />

      {/* Curvature vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,${curvature * 8}) 100%)`,
          pointerEvents: "none",
        }}
      />

      {/* Screen flicker */}
      {showFlicker && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "rgba(255, 255, 255, 0.02)",
            opacity: Math.sin(frame / 3) * 0.5 + 0.5,
            pointerEvents: "none",
          }}
        />
      )}
    </AbsoluteFill>
  );
};
