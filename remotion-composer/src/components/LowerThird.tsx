import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface LowerThirdProps {
  name: string;
  title?: string;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  position?: "bottom-left" | "bottom-right" | "bottom-center";
}

export const LowerThird: React.FC<LowerThirdProps> = ({
  name,
  title,
  accentColor = "#E11D48",
  backgroundColor = "rgba(10, 10, 15, 0.85)",
  fontFamily = "Inter, system-ui, sans-serif",
  position = "bottom-left",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 15, stiffness: 120, mass: 0.8 } });

  const alignMap = {
    "bottom-left": { left: "60px", right: "auto", alignItems: "flex-start" as const },
    "bottom-right": { left: "auto", right: "60px", alignItems: "flex-end" as const },
    "bottom-center": { left: "50%", right: "auto", alignItems: "center" as const },
  };
  const pos = alignMap[position];

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: pos.alignItems,
        paddingBottom: "80px",
        paddingLeft: pos.left === "50%" ? 0 : undefined,
        fontFamily,
      }}
    >
      <div
        style={{
          position: "absolute",
          bottom: "80px",
          left: pos.left,
          right: pos.right,
          display: "flex",
          alignItems: "center",
          gap: "16px",
          background: backgroundColor,
          borderRadius: "8px",
          padding: "16px 24px",
          border: "1px solid rgba(255, 255, 255, 0.15)",
          boxShadow: "0 10px 30px rgba(0, 0, 0, 0.6)",
          opacity: entrance,
          transform: `${pos.left === "50%" ? "translateX(-50%)" : ""} translateY(${interpolate(entrance, [0, 1], [30, 0])}px)`,
        }}
      >
        <div
          style={{
            width: "5px",
            height: "48px",
            background: accentColor,
            borderRadius: "3px",
            boxShadow: `0 0 12px ${accentColor}`,
          }}
        />
        <div>
          <div style={{ color: "#fff", fontSize: "32px", fontWeight: 800, lineHeight: 1.2 }}>
            {name}
          </div>
          {title && (
            <div style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "20px", fontWeight: 500 }}>
              {title}
            </div>
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
