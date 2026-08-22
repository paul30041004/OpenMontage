import React from "react";
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface SocialQuoteProps {
  authorName: string;
  authorHandle?: string;
  avatarUrl?: string;
  quoteText: string;
  highlightWords?: string[];
  platform?: "twitter" | "quote" | "discord";
  verified?: boolean;
  dateText?: string;
  likesCount?: string;
  retweetsCount?: string;
  accentColor?: string;
}

export const SocialQuoteCard: React.FC<SocialQuoteProps> = ({
  authorName,
  authorHandle = "@creator",
  avatarUrl,
  quoteText,
  highlightWords = [],
  platform = "twitter",
  verified = true,
  dateText = "Just now",
  likesCount = "14.2K",
  retweetsCount = "3.8K",
  accentColor = "#38bdf8",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame,
    fps,
    config: { damping: 15, mass: 0.8 },
  });

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <div
        style={{
          width: "850px",
          maxWidth: "90%",
          padding: "40px",
          background: "rgba(15, 23, 42, 0.85)",
          backdropFilter: "blur(24px)",
          borderRadius: "28px",
          border: `1px solid rgba(255, 255, 255, 0.15)`,
          boxShadow: `0 30px 60px rgba(0, 0, 0, 0.6), 0 0 40px ${accentColor}22`,
          opacity: entrance,
          transform: `scale(${interpolate(entrance, [0, 1], [0.85, 1])}) translateY(${interpolate(entrance, [0, 1], [40, 0])}px)`,
        }}
      >
        {/* User Header */}
        <div style={{ display: "flex", alignItems: "center", gap: "18px", marginBottom: "28px" }}>
          {avatarUrl ? (
            <Img
              src={avatarUrl}
              style={{
                width: "68px",
                height: "68px",
                borderRadius: "50%",
                objectFit: "cover",
                border: `2px solid ${accentColor}`,
              }}
            />
          ) : (
            <div
              style={{
                width: "68px",
                height: "68px",
                borderRadius: "50%",
                background: `linear-gradient(135deg, ${accentColor}, #818cf8)`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#ffffff",
                fontSize: "28px",
                fontWeight: 800,
              }}
            >
              {authorName.charAt(0).toUpperCase()}
            </div>
          )}

          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ color: "#ffffff", fontSize: "24px", fontWeight: 700 }}>
                {authorName}
              </span>
              {verified && (
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: "20px",
                    height: "20px",
                    borderRadius: "50%",
                    background: accentColor,
                    color: "#000000",
                    fontSize: "12px",
                    fontWeight: 900,
                  }}
                >
                  ✓
                </span>
              )}
            </div>
            <span style={{ color: "rgba(255, 255, 255, 0.5)", fontSize: "18px" }}>
              {authorHandle}
            </span>
          </div>

          <div style={{ color: "rgba(255, 255, 255, 0.4)", fontSize: "16px" }}>{dateText}</div>
        </div>

        {/* Quote Content */}
        <p
          style={{
            color: "#ffffff",
            fontSize: "32px",
            lineHeight: 1.45,
            fontWeight: 500,
            margin: "0 0 32px 0",
            wordBreak: "keep-all",
          }}
        >
          {quoteText.split(" ").map((word, idx) => {
            const isHighlight = highlightWords.some((h) =>
              word.toLowerCase().includes(h.toLowerCase())
            );
            return (
              <span
                key={idx}
                style={{
                  color: isHighlight ? accentColor : "#ffffff",
                  fontWeight: isHighlight ? 800 : 500,
                  textShadow: isHighlight ? `0 0 15px ${accentColor}88` : "none",
                }}
              >
                {word}{" "}
              </span>
            );
          })}
        </p>

        {/* Stats Footer */}
        <div
          style={{
            display: "flex",
            gap: "36px",
            paddingTop: "20px",
            borderTop: "1px solid rgba(255, 255, 255, 0.1)",
            color: "rgba(255, 255, 255, 0.6)",
            fontSize: "18px",
            fontWeight: 600,
          }}
        >
          <div>
            <span style={{ color: "#ffffff", fontWeight: 800 }}>{retweetsCount}</span> Retweets
          </div>
          <div>
            <span style={{ color: "#ffffff", fontWeight: 800 }}>{likesCount}</span> Likes
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
