import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface KineticTypographyProps {
  lines: string[];
  title?: string;
  fontSize?: number;
  color?: string;
  highlightColor?: string;
  backgroundColor?: string;
  highlightWords?: string[];
  staggerFrames?: number;
  fontFamily?: string;
  fontWeight?: number;
  lineHeight?: number;
  align?: "left" | "center" | "right";
}

export const KineticTypography: React.FC<KineticTypographyProps> = ({
  lines,
  title,
  fontSize = 72,
  color = "#F8FAFC",
  highlightColor = "#FACC15",
  backgroundColor = "#0F172A",
  highlightWords = [],
  staggerFrames = 6,
  fontFamily = "Space Grotesk, Inter, system-ui, sans-serif",
  fontWeight = 800,
  lineHeight = 1.25,
  align = "center",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: align === "center" ? "center" : align === "right" ? "flex-end" : "flex-start",
        background: backgroundColor,
        padding: "80px",
      }}
    >
      <div style={{ maxWidth: "88%", textAlign: align }}>
        {title && (
          <div
            style={{
              opacity: titleOpacity,
              fontSize: fontSize * 0.4,
              color: highlightColor,
              fontWeight: 600,
              letterSpacing: "5px",
              textTransform: "uppercase",
              marginBottom: "32px",
              fontFamily,
            }}
          >
            {title}
          </div>
        )}

        {lines.map((line, lineIdx) => {
          const words = line.split(" ");
          return (
            <div
              key={lineIdx}
              style={{
                fontSize,
                color,
                fontFamily,
                fontWeight,
                lineHeight,
                marginBottom: "8px",
              }}
            >
              {words.map((word, wordIdx) => {
                const globalIdx = lineIdx * 20 + wordIdx;
                const wordFrame = globalIdx * staggerFrames;
                const wordSpring = spring({
                  frame: frame - wordFrame,
                  fps,
                  config: { damping: 14, stiffness: 120, mass: 0.8 },
                });
                const isHighlight = highlightWords.some((h) =>
                  word.toLowerCase().includes(h.toLowerCase())
                );

                return (
                  <span
                    key={wordIdx}
                    style={{
                      display: "inline-block",
                      opacity: wordSpring,
                      transform: `translateY(${interpolate(wordSpring, [0, 1], [40, 0])}px) scale(${interpolate(wordSpring, [0, 1], [0.8, 1])})`,
                      color: isHighlight ? highlightColor : color,
                      textShadow: isHighlight ? `0 0 24px ${highlightColor}66` : "none",
                      marginRight: "0.3em",
                    }}
                  >
                    {word}
                  </span>
                );
              })}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
