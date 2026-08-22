import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface TypewriterTextProps {
  text: string;
  title?: string;
  subtitle?: string;
  fontSize?: number;
  color?: string;
  cursorColor?: string;
  backgroundColor?: string;
  charsPerSecond?: number;
  startDelaySeconds?: number;
  showCursor?: boolean;
  align?: "left" | "center" | "right";
  fontFamily?: string;
  fontWeight?: number;
  lineHeight?: number;
}

export const TypewriterText: React.FC<TypewriterTextProps> = ({
  text,
  title,
  subtitle,
  fontSize = 56,
  color = "#F8FAFC",
  cursorColor = "#22D3EE",
  backgroundColor = "#0F172A",
  charsPerSecond = 18,
  startDelaySeconds = 0.3,
  showCursor = true,
  align = "left",
  fontFamily = "Space Grotesk, Inter, system-ui, sans-serif",
  fontWeight = 700,
  lineHeight = 1.4,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const startFrame = startDelaySeconds * fps;
  const charsPerFrame = charsPerSecond / fps;
  const typedChars = Math.floor(Math.max(0, frame - startFrame) * charsPerFrame);
  const visibleText = text.slice(0, typedChars);
  const isTyping = typedChars < text.length;

  // Blinking cursor (deterministic: on/off every 12 frames)
  const cursorVisible = showCursor && Math.floor(frame / 12) % 2 === 0;

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
      <div style={{ maxWidth: "85%", textAlign: align }}>
        {title && (
          <div
            style={{
              opacity: titleOpacity,
              fontSize: fontSize * 0.5,
              color: cursorColor,
              fontWeight: 600,
              letterSpacing: "4px",
              textTransform: "uppercase",
              marginBottom: "24px",
              fontFamily,
            }}
          >
            {title}
          </div>
        )}

        <div
          style={{
            fontSize,
            color,
            fontFamily,
            fontWeight,
            lineHeight,
            whiteSpace: "pre-wrap",
            wordBreak: "keep-all",
          }}
        >
          {visibleText}
          {isTyping && cursorVisible && (
            <span
              style={{
                display: "inline-block",
                width: "0.08em",
                height: "1em",
                backgroundColor: cursorColor,
                marginLeft: "4px",
                verticalAlign: "text-bottom",
                boxShadow: `0 0 12px ${cursorColor}`,
              }}
            />
          )}
        </div>

        {subtitle && typedChars >= text.length && (
          <div
            style={{
              opacity: interpolate(frame, [startFrame + text.length / charsPerFrame, startFrame + text.length / charsPerFrame + 20], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
              fontSize: fontSize * 0.45,
              color: "rgba(255, 255, 255, 0.7)",
              fontWeight: 400,
              marginTop: "28px",
              fontFamily,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
