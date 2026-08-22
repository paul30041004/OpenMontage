import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface SubscribeButtonProps {
  channelName?: string;
  subscriberCount?: string;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  position?: "bottom-left" | "bottom-right" | "center";
}

export const SubscribeButton: React.FC<SubscribeButtonProps> = ({
  channelName = "OpenMontage",
  subscriberCount = "10만 구독자",
  accentColor = "#FF0000",
  backgroundColor = "rgba(0, 0, 0, 0.75)",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  position = "bottom-right",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({ frame, fps, config: { damping: 12, stiffness: 160, mass: 0.7 } });

  // Pulsing "구독" badge
  const pulse = spring({
    frame: frame % Math.round(fps * 2),
    fps,
    config: { damping: 8, stiffness: 150, mass: 0.5 },
  });

  const posMap: Record<string, React.CSSProperties> = {
    "bottom-left": { bottom: "80px", left: "60px" },
    "bottom-right": { bottom: "80px", right: "60px" },
    center: { top: "50%", left: "50%", transform: "translate(-50%, -50%)" },
  };

  return (
    <div
      style={{
        position: "absolute",
        ...posMap[position],
        display: "flex",
        alignItems: "center",
        gap: "16px",
        background: backgroundColor,
        borderRadius: "20px",
        padding: "16px 24px",
        border: "1px solid rgba(255, 255, 255, 0.2)",
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.6)",
        opacity: entrance,
        transform: posMap[position].transform,
        fontFamily,
      }}
    >
      {/* Channel avatar */}
      <div
        style={{
          width: "56px",
          height: "56px",
          borderRadius: "50%",
          background: `linear-gradient(135deg, ${accentColor}, #818CF8)`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#fff",
          fontSize: "28px",
          fontWeight: 900,
          flexShrink: 0,
        }}
      >
        {channelName.charAt(0)}
      </div>

      <div>
        <div style={{ color: "#fff", fontSize: "24px", fontWeight: 800 }}>{channelName}</div>
        <div style={{ color: "rgba(255, 255, 255, 0.6)", fontSize: "16px" }}>
          {subscriberCount}
        </div>
      </div>

      {/* Subscribe button */}
      <div
        style={{
          background: accentColor,
          color: "#fff",
          padding: "12px 24px",
          borderRadius: "30px",
          fontSize: "22px",
          fontWeight: 900,
          letterSpacing: "1px",
          transform: `scale(${interpolate(pulse, [0, 1], [1, 1.08])})`,
          boxShadow: `0 0 20px ${accentColor}66`,
        }}
      >
        구독
      </div>
    </div>
  );
};
