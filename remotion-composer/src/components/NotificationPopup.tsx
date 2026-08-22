import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface NotificationPopupProps {
  title?: string;
  message?: string;
  appName?: string;
  appIcon?: string;
  timeText?: string;
  accentColor?: string;
  position?: "top-left" | "top-right" | "top-center";
  fontFamily?: string;
}

export const NotificationPopup: React.FC<NotificationPopupProps> = ({
  title = "새 메시지",
  message = "알림이 도착했습니다.",
  appName = "OpenMontage",
  appIcon = "📱",
  timeText = "지금",
  accentColor = "#38BDF8",
  position = "top-right",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideIn = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 150, mass: 0.7 },
  });

  const posMap: Record<string, React.CSSProperties> = {
    "top-left": { top: "60px", left: "60px" },
    "top-right": { top: "60px", right: "60px" },
    "top-center": { top: "60px", left: "50%", transform: "translateX(-50%)" },
  };

  return (
    <div
      style={{
        position: "absolute",
        ...posMap[position],
        width: "420px",
        background: "rgba(20, 20, 30, 0.92)",
        backdropFilter: "blur(20px)",
        borderRadius: "20px",
        padding: "20px 24px",
        border: "1px solid rgba(255, 255, 255, 0.15)",
        boxShadow: "0 20px 50px rgba(0, 0, 0, 0.6)",
        display: "flex",
        alignItems: "flex-start",
        gap: "16px",
        fontFamily,
        opacity: slideIn,
        transform:
          posMap[position].transform ||
          `translateY(${interpolate(slideIn, [0, 1], [-40, 0])}px)`,
      }}
    >
      <div
        style={{
          width: "48px",
          height: "48px",
          borderRadius: "12px",
          background: accentColor,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "26px",
          flexShrink: 0,
        }}
      >
        {appIcon}
      </div>

      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ color: "#fff", fontSize: "18px", fontWeight: 700 }}>{appName}</span>
          <span style={{ color: "rgba(255,255,255,0.5)", fontSize: "14px" }}>{timeText}</span>
        </div>
        <div style={{ color: "#fff", fontSize: "22px", fontWeight: 800, marginTop: "4px" }}>
          {title}
        </div>
        <div style={{ color: "rgba(255,255,255,0.75)", fontSize: "18px", marginTop: "2px" }}>
          {message}
        </div>
      </div>
    </div>
  );
};
