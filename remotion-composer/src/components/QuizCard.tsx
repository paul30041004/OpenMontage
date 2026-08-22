import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface QuizCardProps {
  question: string;
  options: string[];
  correctIndex?: number;
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  revealAnswer?: boolean;
}

export const QuizCard: React.FC<QuizCardProps> = ({
  question,
  options,
  correctIndex,
  accentColor = "#8B5CF6",
  backgroundColor = "#0F172A",
  fontFamily = "Inter, system-ui, sans-serif",
  revealAnswer = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const questionIn = spring({ frame, fps, config: { damping: 15, stiffness: 100, mass: 0.8 } });

  const optionLabels = ["A", "B", "C", "D"];

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background: backgroundColor,
        padding: "80px",
        fontFamily,
      }}
    >
      <div style={{ width: "80%", maxWidth: "1200px" }}>
        {/* Question */}
        <div
          style={{
            background: "rgba(255, 255, 255, 0.06)",
            borderRadius: "20px",
            padding: "40px",
            marginBottom: "40px",
            border: "1px solid rgba(255, 255, 255, 0.12)",
            opacity: questionIn,
            transform: `translateY(${interpolate(questionIn, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              color: accentColor,
              fontSize: "22px",
              fontWeight: 800,
              letterSpacing: "3px",
              marginBottom: "12px",
            }}
          >
            QUIZ
          </div>
          <div style={{ color: "#fff", fontSize: "44px", fontWeight: 800, lineHeight: 1.3 }}>
            {question}
          </div>
        </div>

        {/* Options */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {options.map((opt, i) => {
            const optIn = spring({
              frame: frame - (15 + i * 6),
              fps,
              config: { damping: 14, stiffness: 120, mass: 0.8 },
            });
            const isCorrect = revealAnswer && correctIndex === i;

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "20px",
                  background: isCorrect
                    ? `${accentColor}33`
                    : "rgba(255, 255, 255, 0.05)",
                  borderRadius: "14px",
                  padding: "20px 28px",
                  border: isCorrect
                    ? `2px solid ${accentColor}`
                    : "1px solid rgba(255, 255, 255, 0.1)",
                  opacity: optIn,
                  transform: `translateX(${interpolate(optIn, [0, 1], [-40, 0])}px)`,
                }}
              >
                <div
                  style={{
                    width: "44px",
                    height: "44px",
                    borderRadius: "50%",
                    background: isCorrect ? accentColor : "rgba(255, 255, 255, 0.1)",
                    color: isCorrect ? "#000" : "#fff",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "20px",
                    fontWeight: 900,
                  }}
                >
                  {isCorrect ? "✓" : optionLabels[i]}
                </div>
                <span style={{ color: "#fff", fontSize: "30px", fontWeight: 600 }}>{opt}</span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
