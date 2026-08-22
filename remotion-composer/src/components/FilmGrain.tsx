import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";

export interface FilmGrainProps {
  intensity?: number;
  monochrome?: boolean;
}

export const FilmGrain: React.FC<FilmGrainProps> = ({
  intensity = 0.08,
  monochrome = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Deterministic grain pattern that shifts each frame
  const seed = frame * 7919;
  const grainOpacity = intensity;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          opacity: grainOpacity,
          mixBlendMode: monochrome ? "overlay" : "soft-light",
          transform: `translate(${(seed % 7) - 3}px, ${(seed % 5) - 2}px)`,
        }}
      />
    </AbsoluteFill>
  );
};
