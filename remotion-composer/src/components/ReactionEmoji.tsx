import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface ReactionEmojiProps {
  emoji?: string;
  count?: string;
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center";
  accentColor?: string;
  size?: number;
  popStagger?: number;
}

export const ReactionEmoji: React.FC<ReactionEmojiProps> = ({
  emoji = "❤️",
  count = "1.2K",
  position = "bottom-right",
  accentColor = "#EC4899",
  size = 120,
  popStagger = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pop = spring({
    frame: frame - popStagger,
    fps,
    config: { damping: 8, stiffness: 200, mass: 0.5 },
  });

  const floatY = Math.sin((frame + popStagger) / (fps * 0.8)) * 10;

  const posMap: Record<string, React.CSSProperties> = {
    "top-left": { top: "60px", left: "60px" },
    "top-right": { top: "60px", right: "60px" },
    "bottom-left": { bottom: "120px", left: "60px" },
    "bottom-right": { bottom: "120px", right: "60px" },
    center: { top: "50%", left: "50%", transform: "translate(-50%, -50%)" },
  };

  return (
    <div
      style={{
        position: "absolute",
        ...posMap[position],
        display: "flex",
        alignItems: "center",
        gap: "12px",
        background: "rgba(0, 0, 0, 0.6)",
        borderRadius: "40px",
        padding: "12px 24px",
        border: "1px solid rgba(255, 255, 255, 0.2)",
        transform: posMap[position].transform,
        opacity: pop,
      }}
    >
      <div
        style={{
          fontSize: size,
          lineHeight: 1,
          transform: `scale(${interpolate(pop, [0, 1], [0, 1.4])}) translateY(${floatY}px)`,
          filter: `drop-shadow(0 0 16px ${accentColor}88)`,
        }}
      >
        {emoji}
      </div>
      <span
        style={{
          color: "#fff",
          fontSize: size * 0.5,
          fontWeight: 800,
          textShadow: "0 2px 8px rgba(0,0,0,0.5)",
        }}
      >
        {count}
      </span>
    </div>
  );
};
