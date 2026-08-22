import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface Text3DProps {
  text: string;
  fontSize?: number;
  color?: string;
  shadowColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  depth?: number;
  rotateX?: number;
  rotateY?: number;
  float?: boolean;
}

export const Text3D: React.FC<Text3DProps> = ({
  text,
  fontSize = 120,
  color = "#FFFFFF",
  shadowColor = "#1E3A8A",
  backgroundColor = "#0F172A",
  fontFamily = "Black Han Sans, Inter, system-ui, sans-serif",
  depth = 8,
  rotateX = 0,
  rotateY = 0,
  float = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 14, stiffness: 90, mass: 0.9 } });

  const floatY = float ? Math.sin(frame / (fps * 1.5)) * 12 : 0;
  const floatRotX = rotateX + (float ? Math.sin(frame / (fps * 2)) * 4 : 0);
  const floatRotY = rotateY + (float ? Math.cos(frame / (fps * 2.5)) * 6 : 0);

  // Build layered text shadows for 3D depth
  const shadows = Array.from({ length: depth }, (_, i) => {
    const offset = i + 1;
    return { x: offset * 1.5, y: offset * 1.5, color: shadowColor, opacity: 1 - i * 0.08 };
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: backgroundColor,
        perspective: "1000px",
        fontFamily,
      }}
    >
      <div
        style={{
          position: "relative",
          opacity: entrance,
          transform: `translateY(${floatY}px) rotateX(${floatRotX}deg) rotateY(${floatRotY}deg) scale(${interpolate(entrance, [0, 1], [0.7, 1])})`,
          transformStyle: "preserve-3d",
        }}
      >
        {/* Depth shadows */}
        {shadows.map((s, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              transform: `translate(${s.x}px, ${s.y}px)`,
              color: s.color,
              fontSize,
              fontWeight: 900,
              textAlign: "center",
              whiteSpace: "pre-wrap",
              zIndex: -i - 1,
            }}
          >
            {text}
          </div>
        ))}

        {/* Front face */}
        <div
          style={{
            position: "relative",
            color,
            fontSize,
            fontWeight: 900,
            textAlign: "center",
            whiteSpace: "pre-wrap",
            textShadow: "0 2px 4px rgba(0,0,0,0.4)",
            zIndex: 10,
          }}
        >
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};
