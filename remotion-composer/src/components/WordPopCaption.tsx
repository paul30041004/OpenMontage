import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface WordPopCaptionProps {
  words: { word: string; startMs: number; endMs: number }[];
  fontSize?: number;
  color?: string;
  highlightColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  fontWeight?: number;
  maxWordsPerLine?: number;
  bottomPadding?: number;
}

export const WordPopCaption: React.FC<WordPopCaptionProps> = ({
  words,
  fontSize = 52,
  color = "#F8FAFC",
  highlightColor = "#FACC15",
  backgroundColor = "rgba(15, 23, 42, 0.8)",
  fontFamily = "Space Grotesk, Inter, system-ui, sans-serif",
  fontWeight = 800,
  maxWordsPerLine = 4,
  bottomPadding = 90,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentMs = (frame / fps) * 1000;

  // Build lines by chunking words
  const lines: { word: string; startMs: number; endMs: number }[][] = [];
  for (let i = 0; i < words.length; i += maxWordsPerLine) {
    lines.push(words.slice(i, i + maxWordsPerLine));
  }

  // Find the active line (the one containing the current word)
  const activeLineIdx = lines.findIndex((line) =>
    line.some((w) => w.startMs <= currentMs && w.endMs > currentMs)
  );
  const activeLine = activeLineIdx >= 0 ? lines[activeLineIdx] : null;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: bottomPadding,
      }}
    >
      {activeLine && (
        <div
          style={{
            backgroundColor,
            borderRadius: 16,
            padding: "18px 32px",
            maxWidth: "85%",
            textAlign: "center",
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "center",
            gap: "0.25em",
          }}
        >
          {activeLine.map((w, i) => {
            const isActive = w.startMs <= currentMs && w.endMs > currentMs;
            const isPast = w.endMs <= currentMs;
            const pop = spring({
              frame: frame - Math.round((w.startMs / 1000) * fps),
              fps,
              config: { damping: 12, stiffness: 200, mass: 0.6 },
            });

            return (
              <span
                key={`${w.startMs}-${i}`}
                style={{
                  fontSize,
                  fontWeight,
                  fontFamily,
                  color: isActive ? highlightColor : isPast ? color : `${color}88`,
                  transform: isActive ? `scale(${interpolate(pop, [0, 1], [0.5, 1])})` : "none",
                  textShadow: isActive
                    ? `0 0 24px ${highlightColor}88, 0 3px 6px rgba(0,0,0,0.6)`
                    : "0 3px 6px rgba(0,0,0,0.6)",
                  display: "inline-block",
                }}
              >
                {w.word}
              </span>
            );
          })}
        </div>
      )}
    </AbsoluteFill>
  );
};
