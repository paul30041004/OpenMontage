import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface Waypoint {
  name: string;
  x: number; // 0 to 100%
  y: number; // 0 to 100%
  labelPosition?: "top" | "bottom" | "left" | "right";
}

export interface GeoRouteMapProps {
  title?: string;
  waypoints: Waypoint[];
  accentColor?: string;
  pathColor?: string;
}

export const GeoRouteMap: React.FC<GeoRouteMapProps> = ({
  title = "GLOBAL EXPEDITION ROUTE",
  waypoints,
  accentColor = "#38bdf8",
  pathColor = "#f43f5e",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8 },
  });

  const progress = interpolate(frame, [10, durationInFrames - 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Build SVG path data connecting waypoints
  const pathD = waypoints.reduce((acc, pt, idx) => {
    return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
  }, "");

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "50px",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Title Header */}
      {title && (
        <div
          style={{
            position: "absolute",
            top: "40px",
            zIndex: 10,
            padding: "10px 28px",
            background: "rgba(15, 23, 42, 0.85)",
            backdropFilter: "blur(16px)",
            borderRadius: "30px",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            color: "#ffffff",
            fontSize: "22px",
            fontWeight: 800,
            letterSpacing: "2px",
            opacity: entrance,
            transform: `translateY(${interpolate(entrance, [0, 1], [-20, 0])}px)`,
          }}
        >
          {title}
        </div>
      )}

      {/* Map Graphic Canvas */}
      <div
        style={{
          width: "90%",
          height: "75%",
          background: "radial-gradient(ellipse at center, #1e293b 0%, #0f172a 100%)",
          borderRadius: "28px",
          position: "relative",
          overflow: "hidden",
          border: "1px solid rgba(255, 255, 255, 0.15)",
          boxShadow: "0 30px 60px rgba(0, 0, 0, 0.7)",
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.9, 1])})`,
        }}
      >
        {/* Futuristic Map Grid Lines */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `
              linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px)
            `,
            backgroundSize: "40px 40px",
          }}
        />

        {/* Animated Connecting Route Line */}
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
        >
          {/* Base Track */}
          <path
            d={pathD}
            fill="none"
            stroke="rgba(255, 255, 255, 0.2)"
            strokeWidth="0.8"
            strokeDasharray="2,2"
          />

          {/* Active Animated Path */}
          <path
            d={pathD}
            fill="none"
            stroke={pathColor}
            strokeWidth="1.2"
            pathLength="100"
            strokeDasharray="100"
            strokeDashoffset={interpolate(progress, [0, 1], [100, 0])}
            style={{ filter: `drop-shadow(0 0 4px ${pathColor})` }}
          />
        </svg>

        {/* Waypoint Markers */}
        {waypoints.map((wp, idx) => {
          const wpProgress = idx / Math.max(1, waypoints.length - 1);
          const isReached = progress >= wpProgress;
          const radarScale = isReached ? 1 + (Math.sin(frame * 0.2 + idx) + 1) * 0.8 : 0;

          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                left: `${wp.x}%`,
                top: `${wp.y}%`,
                transform: "translate(-50%, -50%)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                zIndex: 5,
              }}
            >
              {/* Pulsing Radar Ring */}
              {isReached && (
                <div
                  style={{
                    position: "absolute",
                    width: "36px",
                    height: "36px",
                    borderRadius: "50%",
                    border: `2px solid ${accentColor}`,
                    transform: `scale(${radarScale})`,
                    opacity: 2 - radarScale,
                    pointerEvents: "none",
                  }}
                />
              )}

              {/* Pin Dot */}
              <div
                style={{
                  width: "18px",
                  height: "18px",
                  borderRadius: "50%",
                  backgroundColor: isReached ? accentColor : "rgba(255, 255, 255, 0.4)",
                  boxShadow: isReached ? `0 0 16px ${accentColor}` : "none",
                  border: "2px solid #ffffff",
                  transition: "all 0.3s ease",
                }}
              />

              {/* Label */}
              <div
                style={{
                  marginTop: "8px",
                  padding: "4px 12px",
                  background: "rgba(0, 0, 0, 0.85)",
                  borderRadius: "8px",
                  color: isReached ? "#ffffff" : "rgba(255, 255, 255, 0.5)",
                  fontSize: "14px",
                  fontWeight: 700,
                  whiteSpace: "nowrap",
                  border: `1px solid ${isReached ? accentColor : "rgba(255,255,255,0.1)"}`,
                }}
              >
                {wp.name}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
