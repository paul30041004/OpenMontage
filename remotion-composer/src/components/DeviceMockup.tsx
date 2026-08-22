import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface DeviceMockupProps {
  deviceType?: "smartphone" | "laptop";
  screenMediaUrl?: string;
  screenMediaType?: "video" | "image";
  title?: string;
  subtitle?: string;
  accentColor?: string;
}

export const DeviceMockup: React.FC<DeviceMockupProps> = ({
  deviceType = "smartphone",
  screenMediaUrl,
  screenMediaType = "image",
  title,
  subtitle,
  accentColor = "#6366f1",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.9 },
  });

  const floatY = Math.sin(frame / (fps * 2)) * 12;
  const rotateX = Math.cos(frame / (fps * 3)) * 4;
  const rotateY = Math.sin(frame / (fps * 2.5)) * 6;

  const isPhone = deviceType === "smartphone";
  const frameWidth = isPhone ? "360px" : "800px";
  const frameHeight = isPhone ? "720px" : "480px";
  const borderRadius = isPhone ? "48px" : "20px";

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        perspective: "1200px",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Title */}
      {title && (
        <div
          style={{
            textAlign: "center",
            marginBottom: "30px",
            opacity: entrance,
            transform: `translateY(${interpolate(entrance, [0, 1], [30, 0])}px)`,
          }}
        >
          <h2 style={{ color: "#ffffff", fontSize: "36px", fontWeight: 800, margin: 0 }}>
            {title}
          </h2>
          {subtitle && (
            <p style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "20px", marginTop: "8px" }}>
              {subtitle}
            </p>
          )}
        </div>
      )}

      {/* 3D Device Frame */}
      <div
        style={{
          width: frameWidth,
          height: frameHeight,
          background: "#0f172a",
          borderRadius: borderRadius,
          padding: isPhone ? "14px" : "18px 18px 28px 18px",
          border: `3px solid rgba(255, 255, 255, 0.25)`,
          boxShadow: `0 40px 80px rgba(0, 0, 0, 0.8), 0 0 50px ${accentColor}33`,
          display: "flex",
          flexDirection: "column",
          position: "relative",
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.8, 1])}) translateY(${floatY}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
          transformStyle: "preserve-3d",
        }}
      >
        {/* Dynamic Island / Notch for Phone */}
        {isPhone && (
          <div
            style={{
              position: "absolute",
              top: "22px",
              left: "50%",
              transform: "translateX(-50%)",
              width: "110px",
              height: "28px",
              background: "#000000",
              borderRadius: "20px",
              zIndex: 10,
            }}
          />
        )}

        {/* Screen Viewport */}
        <div
          style={{
            flex: 1,
            borderRadius: isPhone ? "36px" : "12px",
            overflow: "hidden",
            position: "relative",
            backgroundColor: "#000000",
          }}
        >
          {screenMediaUrl ? (
            screenMediaType === "video" ? (
              <OffthreadVideo
                src={screenMediaUrl}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            ) : (
              <Img
                src={screenMediaUrl}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            )
          ) : (
            <div
              style={{
                width: "100%",
                height: "100%",
                background: `linear-gradient(135deg, ${accentColor} 0%, #1e1b4b 100%)`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#ffffff",
                fontSize: "24px",
                fontWeight: 700,
              }}
            >
              PREVIEW SCREEN
            </div>
          )}

          {/* Glass glare overlay */}
          <div
            style={{
              position: "absolute",
              inset: 0,
              background:
                "linear-gradient(125deg, rgba(255, 255, 255, 0.15) 0%, transparent 45%, rgba(255, 255, 255, 0.05) 100%)",
              pointerEvents: "none",
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
