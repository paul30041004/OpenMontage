import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface HashtagOverlayProps {
  hashtags?: string[];
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  position?: "bottom-left" | "bottom-right" | "top-left" | "center";
  staggerFrames?: number;
}

export const HashtagOverlay: React.FC<HashtagOverlayProps> = ({
  hashtags = ["#오픈몽타주", "#숏폼", "#바이럴"],
  accentColor = "#38BDF8",
  backgroundColor = "rgba(0, 0, 0, 0.5)",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  position = "bottom-left",
  staggerFrames = 8,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const posMap: Record<string, React.CSSProperties> = {
    "bottom-left": { bottom: "140px", left: "60px", alignItems: "flex-start" },
    "bottom-right": { bottom: "140px", right: "60px", alignItems: "flex-end" },
    "top-left": { top: "60px", left: "60px", alignItems: "flex-start" },
    center: { top: "50%", left: "50%", alignItems: "center", transform: "translate(-50%, -50%)" },
  };

  return (
    <div
      style={{
        position: "absolute",
        ...posMap[position],
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        fontFamily,
      }}
    >
      {hashtags.map((tag, i) => {
        const tagIn = spring({
          frame: frame - (i * staggerFrames),
          fps,
          config: { damping: 13, stiffness: 130, mass: 0.7 },
        });
        return (
          <span
            key={i}
            style={{
              color: accentColor,
              fontSize: "32px",
              fontWeight: 800,
              background: backgroundColor,
              padding: "8px 20px",
              borderRadius: "30px",
              border: `1px solid ${accentColor}44`,
              opacity: tagIn,
              transform: `translateX(${interpolate(tagIn, [0, 1], [position === "bottom-right" ? 30 : -30, 0])}px)`,
              boxShadow: `0 0 12px ${accentColor}33`,
            }}
          >
            {tag}
          </span>
        );
      })}
    </div>
  );
};
