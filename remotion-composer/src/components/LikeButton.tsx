import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface LikeButtonProps {
  emoji?: string;
  count?: string;
  accentColor?: string;
  position?: "bottom-left" | "bottom-right" | "center";
  fontFamily?: string;
  burst?: boolean;
}

export const LikeButton: React.FC<LikeButtonProps> = ({
  emoji = "👍",
  count = "1.2만",
  accentColor = "#38BDF8",
  position = "bottom-left",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  burst = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({ frame, fps, config: { damping: 9, stiffness: 180, mass: 0.5 } });

  const posMap: Record<string, React.CSSProperties> = {
    "bottom-left": { bottom: "80px", left: "60px" },
    "bottom-right": { bottom: "80px", right: "60px" },
    center: { top: "50%", left: "50%", transform: "translate(-50%, -50%)" },
  };

  // Burst particles on pop
  const burstParticles = burst ? Array.from({ length: 6 }, (_, i) => i) : [];

  return (
    <div
      style={{
        position: "absolute",
        ...posMap[position],
        display: "flex",
        alignItems: "center",
        gap: "14px",
        background: "rgba(0, 0, 0, 0.6)",
        borderRadius: "40px",
        padding: "14px 26px",
        border: "1px solid rgba(255, 255, 255, 0.2)",
        fontFamily,
        transform: posMap[position].transform,
      }}
    >
      {/* Burst particles */}
      {burstParticles.map((i) => {
        const angle = (i / 6) * Math.PI * 2;
        const dist = interpolate(pop, [0, 1], [0, 60]);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: "50%",
              top: "50%",
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: accentColor,
              opacity: interpolate(pop, [0, 1], [1, 0]),
              transform: `translate(${Math.cos(angle) * dist}px, ${Math.sin(angle) * dist}px)`,
            }}
          />
        );
      })}

      <div
        style={{
          fontSize: "44px",
          lineHeight: 1,
          transform: `scale(${interpolate(pop, [0, 1], [0, 1.3])})`,
          filter: `drop-shadow(0 0 12px ${accentColor}88)`,
        }}
      >
        {emoji}
      </div>
      <span style={{ color: "#fff", fontSize: "28px", fontWeight: 800 }}>{count}</span>
    </div>
  );
};
