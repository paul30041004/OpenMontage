import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface ChatBubbleProps {
  messages: { text: string; sender?: string; avatar?: string; isMe?: boolean }[];
  accentColor?: string;
  backgroundColor?: string;
  fontFamily?: string;
  staggerFrames?: number;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  messages,
  accentColor = "#6366F1",
  backgroundColor = "#0F172A",
  fontFamily = "Pretendard, Inter, system-ui, sans-serif",
  staggerFrames = 20,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        padding: "80px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
        gap: "20px",
        fontFamily,
      }}
    >
      {messages.map((msg, i) => {
        const msgIn = spring({
          frame: frame - (i * staggerFrames),
          fps,
          config: { damping: 14, stiffness: 140, mass: 0.7 },
        });
        const isMe = msg.isMe;

        return (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "flex-end",
              gap: "14px",
              flexDirection: isMe ? "row-reverse" : "row",
              opacity: msgIn,
              transform: `translateY(${interpolate(msgIn, [0, 1], [30, 0])}px) scale(${interpolate(msgIn, [0, 1], [0.9, 1])})`,
            }}
          >
            {msg.avatar && !isMe && (
              <div
                style={{
                  width: "52px",
                  height: "52px",
                  borderRadius: "50%",
                  background: accentColor,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#fff",
                  fontSize: "24px",
                  fontWeight: 800,
                  flexShrink: 0,
                }}
              >
                {msg.avatar}
              </div>
            )}

            <div style={{ maxWidth: "60%" }}>
              {msg.sender && !isMe && (
                <div style={{ color: "rgba(255,255,255,0.5)", fontSize: "18px", marginBottom: "6px" }}>
                  {msg.sender}
                </div>
              )}
              <div
                style={{
                  background: isMe ? accentColor : "rgba(255, 255, 255, 0.12)",
                  color: "#fff",
                  padding: "18px 24px",
                  borderRadius: isMe ? "24px 24px 6px 24px" : "24px 24px 24px 6px",
                  fontSize: "30px",
                  fontWeight: 600,
                  lineHeight: 1.4,
                  wordBreak: "keep-all",
                  boxShadow: isMe ? `0 6px 20px ${accentColor}44` : "none",
                }}
              >
                {msg.text}
              </div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
