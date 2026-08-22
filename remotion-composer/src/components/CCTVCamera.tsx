import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, OffthreadVideo } from "remotion";
import { MatrixRain } from "remotion-bits";

export interface CCTVCameraProps {
  cameraId?: string;
  location?: string;
  timestamp?: string;
  matrixColor?: string;
  matrixSpeed?: number;
  matrixDensity?: number;
  matrixStreamLength?: number;
  showRecIndicator?: boolean;
  showCornerBrackets?: boolean;
  showScanlines?: boolean;
  showTimestamp?: boolean;
  showCameraId?: boolean;
  backgroundColor?: string;
  fontFamily?: string;
  videoSrc?: string;
  greenTint?: number;
}

export const CCTVCamera: React.FC<CCTVCameraProps> = ({
  cameraId = "CAM-07",
  location = "서울 강남구 테헤란로 152",
  timestamp = "2026-08-22 14:32:07",
  matrixColor = "#00FF66",
  matrixSpeed = 1,
  matrixDensity = 1,
  matrixStreamLength = 18,
  showRecIndicator = true,
  showCornerBrackets = true,
  showScanlines = true,
  showTimestamp = true,
  showCameraId = true,
  backgroundColor = "#050505",
  fontFamily = "monospace",
  videoSrc,
  greenTint = 0.12,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Blinking REC dot
  const recBlink = Math.floor(frame / 15) % 2 === 0;

  // Timestamp ticking (simulate live seconds)
  const liveSeconds = Math.floor(frame / fps);
  const liveTime = `2026-08-22 14:32:${String(7 + (liveSeconds % 60)).padStart(2, "0")}`;

  // Subtle camera shake / interference
  const shakeX = Math.sin(frame * 0.7) * 1.5;
  const shakeY = Math.cos(frame * 0.5) * 1.2;

  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        overflow: "hidden",
        fontFamily,
      }}
    >
      {/* Background: real CCTV video (if provided) or Matrix Rain fallback */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${shakeX}px, ${shakeY}px)`,
        }}
      >
        {videoSrc ? (
          <OffthreadVideo
            src={videoSrc}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          <MatrixRain
            fontSize={18}
            color={matrixColor}
            speed={matrixSpeed}
            density={matrixDensity}
            streamLength={matrixStreamLength}
          />
        )}
      </div>

      {/* CCTV green tint overlay (stronger for real footage to look like CCTV) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: videoSrc
            ? `rgba(0, 255, 102, ${greenTint})`
            : "rgba(0, 255, 102, 0.04)",
          mixBlendMode: videoSrc ? "screen" : "normal",
          pointerEvents: "none",
        }}
      />

      {/* Desaturation + slight green for real footage CCTV look */}
      {videoSrc && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "rgba(0, 0, 0, 0.15)",
            filter: "saturate(0.6)",
            pointerEvents: "none",
          }}
        />
      )}

      {/* Scanlines */}
      {showScanlines && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "repeating-linear-gradient(0deg, rgba(0,0,0,0.4) 0px, rgba(0,0,0,0.4) 1px, transparent 1px, transparent 3px)",
            opacity: 0.35,
            pointerEvents: "none",
          }}
        />
      )}

      {/* Vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.7) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* Corner brackets */}
      {showCornerBrackets && (
        <>
          {[
            { top: 20, left: 20, borderTop: "3px solid #00FF66", borderLeft: "3px solid #00FF66" },
            { top: 20, right: 20, borderTop: "3px solid #00FF66", borderRight: "3px solid #00FF66" },
            { bottom: 20, left: 20, borderBottom: "3px solid #00FF66", borderLeft: "3px solid #00FF66" },
            { bottom: 20, right: 20, borderBottom: "3px solid #00FF66", borderRight: "3px solid #00FF66" },
          ].map((style, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                width: "50px",
                height: "50px",
                ...style,
              }}
            />
          ))}
        </>
      )}

      {/* Top-left: REC indicator + camera ID */}
      <div
        style={{
          position: "absolute",
          top: "30px",
          left: "40px",
          display: "flex",
          alignItems: "center",
          gap: "12px",
        }}
      >
        {showRecIndicator && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              background: "rgba(0, 0, 0, 0.7)",
              padding: "6px 14px",
              borderRadius: "4px",
              border: "1px solid rgba(0, 255, 102, 0.4)",
            }}
          >
            <div
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                background: "#FF0000",
                opacity: recBlink ? 1 : 0.2,
                boxShadow: recBlink ? "0 0 10px #FF0000" : "none",
              }}
            />
            <span style={{ color: "#FF0000", fontSize: "20px", fontWeight: 900, letterSpacing: "2px" }}>
              REC
            </span>
          </div>
        )}
        {showCameraId && (
          <span
            style={{
              color: "#00FF66",
              fontSize: "22px",
              fontWeight: 700,
              textShadow: "0 0 8px #00FF66",
            }}
          >
            {cameraId}
          </span>
        )}
      </div>

      {/* Top-right: timestamp */}
      {showTimestamp && (
        <div
          style={{
            position: "absolute",
            top: "30px",
            right: "40px",
            color: "#00FF66",
            fontSize: "20px",
            fontWeight: 700,
            textShadow: "0 0 8px #00FF66",
            background: "rgba(0, 0, 0, 0.6)",
            padding: "6px 14px",
            borderRadius: "4px",
          }}
        >
          {liveTime}
        </div>
      )}

      {/* Bottom-left: location */}
      <div
        style={{
          position: "absolute",
          bottom: "30px",
          left: "40px",
          color: "#00FF66",
          fontSize: "18px",
          fontWeight: 600,
          textShadow: "0 0 8px #00FF66",
          background: "rgba(0, 0, 0, 0.6)",
          padding: "6px 14px",
          borderRadius: "4px",
        }}
      >
        📍 {location}
      </div>

      {/* Bottom-right: resolution / status */}
      <div
        style={{
          position: "absolute",
          bottom: "30px",
          right: "40px",
          color: "#00FF66",
          fontSize: "16px",
          fontWeight: 600,
          textShadow: "0 0 8px #00FF66",
          background: "rgba(0, 0, 0, 0.6)",
          padding: "6px 14px",
          borderRadius: "4px",
        }}
      >
        1080p • 30fps • LIVE
      </div>

      {/* Center crosshair */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          pointerEvents: "none",
        }}
      >
        <div
          style={{
            width: "40px",
            height: "40px",
            border: "1px solid rgba(0, 255, 102, 0.3)",
            borderRadius: "50%",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: "6px",
            height: "6px",
            background: "#00FF66",
            borderRadius: "50%",
            transform: "translate(-50%, -50%)",
            boxShadow: "0 0 8px #00FF66",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
