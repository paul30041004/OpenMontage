import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface EditorialSlideProps {
  headline: string;
  body?: string;
  kicker?: string;
  footnote?: string;
  backgroundColor?: string;
  textColor?: string;
  accentColor?: string;
  headlineFont?: string;
  bodyFont?: string;
  layout?: "centered" | "left-aligned" | "magazine";
  headlineSize?: number;
  bodySize?: number;
  showRule?: boolean;
}

export const EditorialSlide: React.FC<EditorialSlideProps> = ({
  headline,
  body,
  kicker,
  footnote,
  backgroundColor = "#F5F1E8",
  textColor = "#1A1A2E",
  accentColor = "#C0392B",
  headlineFont = "Playfair Display, Georgia, serif",
  bodyFont = "Inter, system-ui, sans-serif",
  layout = "magazine",
  headlineSize = 88,
  bodySize = 34,
  showRule = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const kickerIn = spring({ frame, fps, config: { damping: 16, mass: 0.8 } });
  const headlineIn = spring({
    frame: frame - 8,
    fps,
    config: { damping: 15, stiffness: 90, mass: 0.9 },
  });
  const bodyIn = spring({
    frame: frame - 20,
    fps,
    config: { damping: 18, mass: 0.8 },
  });

  const isCentered = layout === "centered";
  const isMagazine = layout === "magazine";

  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        padding: isMagazine ? "100px 120px" : "80px",
        display: "flex",
        flexDirection: "column",
        justifyContent: isCentered ? "center" : "flex-start",
        alignItems: isCentered ? "center" : "flex-start",
      }}
    >
      {kicker && (
        <div
          style={{
            opacity: kickerIn,
            transform: `translateY(${interpolate(kickerIn, [0, 1], [20, 0])}px)`,
            color: accentColor,
            fontFamily: bodyFont,
            fontSize: bodySize * 0.6,
            fontWeight: 700,
            letterSpacing: "6px",
            textTransform: "uppercase",
            marginBottom: "28px",
          }}
        >
          {kicker}
        </div>
      )}

      {showRule && (
        <div
          style={{
            width: isCentered ? "120px" : "80px",
            height: "4px",
            background: accentColor,
            marginBottom: "36px",
            opacity: kickerIn,
            transform: `scaleX(${interpolate(kickerIn, [0, 1], [0, 1])})`,
            transformOrigin: "left",
          }}
        />
      )}

      <h1
        style={{
          opacity: headlineIn,
          transform: `translateY(${interpolate(headlineIn, [0, 1], [50, 0])}px)`,
          color: textColor,
          fontFamily: headlineFont,
          fontSize: headlineSize,
          fontWeight: 700,
          lineHeight: 1.15,
          margin: 0,
          maxWidth: isMagazine ? "70%" : "100%",
          textAlign: isCentered ? "center" : "left",
        }}
      >
        {headline}
      </h1>

      {body && (
        <p
          style={{
            opacity: bodyIn,
            transform: `translateY(${interpolate(bodyIn, [0, 1], [30, 0])}px)`,
            color: textColor,
            fontFamily: bodyFont,
            fontSize: bodySize,
            fontWeight: 400,
            lineHeight: 1.6,
            marginTop: "40px",
            maxWidth: isMagazine ? "55%" : "80%",
            textAlign: isCentered ? "center" : "left",
          }}
        >
          {body}
        </p>
      )}

      {footnote && (
        <div
          style={{
            position: "absolute",
            bottom: "60px",
            left: isCentered ? "50%" : "120px",
            transform: isCentered ? "translateX(-50%)" : "none",
            color: "rgba(0, 0, 0, 0.5)",
            fontFamily: bodyFont,
            fontSize: bodySize * 0.5,
            fontWeight: 500,
            letterSpacing: "1px",
            opacity: bodyIn,
          }}
        >
          {footnote}
        </div>
      )}
    </AbsoluteFill>
  );
};
