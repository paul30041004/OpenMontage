import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface SplitItem {
  type: "video" | "image" | "color";
  src?: string;
  label?: string;
  color?: string;
}

export interface SplitScreenProps {
  left: SplitItem;
  right: SplitItem;
  title?: string;
  orientation?: "horizontal" | "vertical";
  dividerColor?: string;
}

export const SplitScreen: React.FC<SplitScreenProps> = ({
  left,
  right,
  title,
  orientation = "horizontal",
  dividerColor = "#38bdf8",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame,
    fps,
    config: { damping: 16, mass: 0.7 },
  });

  const isHoriz = orientation === "horizontal";

  const renderContent = (item: SplitItem) => {
    if (item.type === "video" && item.src) {
      return (
        <OffthreadVideo
          src={item.src}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      );
    }
    if (item.type === "image" && item.src) {
      return (
        <Img
          src={item.src}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      );
    }
    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          backgroundColor: item.color || "#1e293b",
        }}
      />
    );
  };

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: isHoriz ? "row" : "column",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "#000000",
      }}
    >
      {/* Top Title Overlay */}
      {title && (
        <div
          style={{
            position: "absolute",
            top: "40px",
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 10,
            padding: "10px 24px",
            background: "rgba(0, 0, 0, 0.75)",
            backdropFilter: "blur(12px)",
            borderRadius: "30px",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            color: "#ffffff",
            fontSize: "22px",
            fontWeight: 800,
            letterSpacing: "2px",
          }}
        >
          {title}
        </div>
      )}

      {/* Left / Top Side */}
      <div
        style={{
          flex: 1,
          position: "relative",
          height: isHoriz ? "100%" : "50%",
          width: isHoriz ? "50%" : "100%",
          overflow: "hidden",
          transform: isHoriz
            ? `translateX(${interpolate(progress, [0, 1], [-50, 0])}px)`
            : `translateY(${interpolate(progress, [0, 1], [-50, 0])}px)`,
          opacity: progress,
        }}
      >
        {renderContent(left)}
        {left.label && (
          <div
            style={{
              position: "absolute",
              bottom: "30px",
              left: "30px",
              padding: "8px 20px",
              background: "rgba(0, 0, 0, 0.8)",
              borderRadius: "12px",
              color: "#ffffff",
              fontSize: "20px",
              fontWeight: 700,
              border: "1px solid rgba(255, 255, 255, 0.2)",
            }}
          >
            {left.label}
          </div>
        )}
      </div>

      {/* Animated Divider */}
      <div
        style={{
          width: isHoriz ? "4px" : "100%",
          height: isHoriz ? "100%" : "4px",
          backgroundColor: dividerColor,
          zIndex: 5,
          boxShadow: `0 0 20px ${dividerColor}`,
        }}
      />

      {/* Right / Bottom Side */}
      <div
        style={{
          flex: 1,
          position: "relative",
          height: isHoriz ? "100%" : "50%",
          width: isHoriz ? "50%" : "100%",
          overflow: "hidden",
          transform: isHoriz
            ? `translateX(${interpolate(progress, [0, 1], [50, 0])}px)`
            : `translateY(${interpolate(progress, [0, 1], [50, 0])}px)`,
          opacity: progress,
        }}
      >
        {renderContent(right)}
        {right.label && (
          <div
            style={{
              position: "absolute",
              bottom: "30px",
              right: "30px",
              padding: "8px 20px",
              background: "rgba(0, 0, 0, 0.8)",
              borderRadius: "12px",
              color: "#ffffff",
              fontSize: "20px",
              fontWeight: 700,
              border: "1px solid rgba(255, 255, 255, 0.2)",
            }}
          >
            {right.label}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
