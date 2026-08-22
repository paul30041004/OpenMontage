import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface NewsBreakingProps {
  headline: string;
  subheadline?: string;
  category?: string;
  timeText?: string;
  backgroundColor?: string;
  accentColor?: string;
  headlineColor?: string;
  fontFamily?: string;
  showBreakingBanner?: boolean;
  showLowerThird?: boolean;
  showTicker?: boolean;
  tickerItems?: string[];
}

export const NewsBreaking: React.FC<NewsBreakingProps> = ({
  headline,
  subheadline,
  category = "속보",
  timeText = "LIVE",
  backgroundColor = "#0A0A0F",
  accentColor = "#E11D48",
  headlineColor = "#FFFFFF",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  showBreakingBanner = true,
  showLowerThird = true,
  showTicker = true,
  tickerItems = [],
}) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();

  const bannerIn = spring({ frame, fps, config: { damping: 14, stiffness: 160, mass: 0.7 } });
  const headlineIn = spring({
    frame: frame - 8,
    fps,
    config: { damping: 16, stiffness: 120, mass: 0.8 },
  });
  const lowerThirdIn = spring({
    frame: frame - 16,
    fps,
    config: { damping: 15, stiffness: 110, mass: 0.8 },
  });

  // Ticker scroll speed (pixels per frame)
  const tickerSpeed = 2.2;
  const tickerText = tickerItems.length > 0 ? tickerItems.join("  •  ") : "";
  const tickerOffset = (frame * tickerSpeed) % (tickerText.length * 20 + width);

  return (
    <AbsoluteFill style={{ background: backgroundColor, fontFamily, overflow: "hidden" }}>
      {/* BREAKING NEWS Banner */}
      {showBreakingBanner && (
        <div
          style={{
            position: "absolute",
            top: "60px",
            left: 0,
            display: "flex",
            alignItems: "center",
            opacity: bannerIn,
            transform: `translateX(${interpolate(bannerIn, [0, 1], [-100, 0])}px)`,
          }}
        >
          <div
            style={{
              background: accentColor,
              color: "#FFFFFF",
              padding: "18px 36px",
              fontSize: "44px",
              fontWeight: 900,
              letterSpacing: "2px",
              boxShadow: `0 0 30px ${accentColor}88`,
            }}
          >
            {category}
          </div>
          <div
            style={{
              background: "rgba(255, 255, 255, 0.08)",
              color: headlineColor,
              padding: "18px 30px",
              fontSize: "30px",
              fontWeight: 700,
              letterSpacing: "1px",
              border: "1px solid rgba(255, 255, 255, 0.15)",
            }}
          >
            {timeText}
          </div>
        </div>
      )}

      {/* Main Headline */}
      <div
        style={{
          position: "absolute",
          top: "38%",
          left: "80px",
          right: "80px",
          opacity: headlineIn,
          transform: `translateY(${interpolate(headlineIn, [0, 1], [40, 0])}px)`,
        }}
      >
        <h1
          style={{
            color: headlineColor,
            fontSize: "96px",
            fontWeight: 900,
            lineHeight: 1.15,
            margin: 0,
            textShadow: "0 4px 20px rgba(0, 0, 0, 0.6)",
            wordBreak: "keep-all",
          }}
        >
          {headline}
        </h1>
        {subheadline && (
          <p
            style={{
              color: "rgba(255, 255, 255, 0.85)",
              fontSize: "40px",
              fontWeight: 500,
              marginTop: "24px",
              lineHeight: 1.4,
              wordBreak: "keep-all",
            }}
          >
            {subheadline}
          </p>
        )}
      </div>

      {/* Lower Third */}
      {showLowerThird && (
        <div
          style={{
            position: "absolute",
            bottom: "120px",
            left: "80px",
            display: "flex",
            alignItems: "center",
            gap: "20px",
            opacity: lowerThirdIn,
            transform: `translateY(${interpolate(lowerThirdIn, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              width: "6px",
              height: "60px",
              background: accentColor,
              boxShadow: `0 0 16px ${accentColor}`,
            }}
          />
          <div>
            <div style={{ color: accentColor, fontSize: "26px", fontWeight: 800, letterSpacing: "3px" }}>
              OPENMONTAGE NEWS
            </div>
            <div style={{ color: "rgba(255, 255, 255, 0.7)", fontSize: "22px", fontWeight: 500 }}>
              실시간 뉴스속보
            </div>
          </div>
        </div>
      )}

      {/* Bottom Ticker */}
      {showTicker && tickerText && (
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: "70px",
            background: "rgba(0, 0, 0, 0.85)",
            borderTop: `3px solid ${accentColor}`,
            display: "flex",
            alignItems: "center",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              background: accentColor,
              color: "#FFFFFF",
              padding: "0 28px",
              height: "100%",
              display: "flex",
              alignItems: "center",
              fontSize: "28px",
              fontWeight: 900,
              letterSpacing: "2px",
              zIndex: 2,
            }}
          >
            속보
          </div>
          <div
            style={{
              whiteSpace: "nowrap",
              color: "#FFFFFF",
              fontSize: "30px",
              fontWeight: 600,
              transform: `translateX(${-tickerOffset}px)`,
              position: "absolute",
              left: "160px",
            }}
          >
            {tickerText}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
