import React from "react";
import { AbsoluteFill } from "remotion";
import {
  MatrixRain,
  AnimatedCounter,
  AnimatedText,
  GradientTransition,
  TypeWriter,
  Particles,
  Spawner,
  Behavior,
} from "remotion-bits";

// ---------------------------------------------------------------------------
// Wrappers that expose remotion-bits components as OpenMontage scene types.
// Each maps to a cut.type in the Explainer composition.
// ---------------------------------------------------------------------------

export interface MatrixRainSceneProps {
  fontSize?: number;
  color?: string;
  speed?: number;
  density?: number;
  streamLength?: number;
  charset?: string;
  backgroundColor?: string;
}

export const MatrixRainScene: React.FC<MatrixRainSceneProps> = ({
  fontSize = 20,
  color = "#00FF66",
  speed = 1,
  density = 1,
  streamLength = 20,
  charset,
  backgroundColor = "#0A0A0F",
}) => {
  return (
    <AbsoluteFill style={{ background: backgroundColor }}>
      <MatrixRain
        fontSize={fontSize}
        color={color}
        speed={speed}
        density={density}
        streamLength={streamLength}
        charset={charset}
      />
    </AbsoluteFill>
  );
};

export interface AnimatedCounterSceneProps {
  from: number;
  to: number;
  prefix?: string;
  postfix?: string;
  toFixed?: number;
  fontSize?: number;
  color?: string;
  backgroundColor?: string;
  durationSeconds?: number;
}

export const AnimatedCounterScene: React.FC<AnimatedCounterSceneProps> = ({
  from = 0,
  to = 100,
  prefix,
  postfix,
  toFixed = 0,
  fontSize = 120,
  color = "#FFFFFF",
  backgroundColor = "#0F172A",
  durationSeconds = 3,
}) => {
  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <AnimatedCounter
        transition={{
          values: [from, to],
          duration: Math.round(durationSeconds * 30),
          easing: "easeOut",
        }}
        prefix={prefix}
        postfix={postfix}
        toFixed={toFixed}
        style={{ fontSize, color, fontWeight: 900 }}
      />
    </AbsoluteFill>
  );
};

export interface AnimatedTextSceneProps {
  text: string;
  split?: "none" | "word" | "character" | "line";
  splitStagger?: number;
  glitch?: boolean;
  fontSize?: number;
  color?: string;
  backgroundColor?: string;
  durationSeconds?: number;
}

export const AnimatedTextScene: React.FC<AnimatedTextSceneProps> = ({
  text,
  split = "word",
  splitStagger = 4,
  glitch = false,
  fontSize = 72,
  color = "#FFFFFF",
  backgroundColor = "#0F172A",
  durationSeconds = 3,
}) => {
  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        justifyContent: "center",
        alignItems: "center",
        padding: "80px",
      }}
    >
      <AnimatedText
        transition={{
          split,
          splitStagger,
          glitch: glitch ? [0, 1, 0] : undefined,
          duration: Math.round(durationSeconds * 30),
          easing: "easeOut",
        }}
        style={{ fontSize, color, fontWeight: 800, textAlign: "center" }}
      >
        {text}
      </AnimatedText>
    </AbsoluteFill>
  );
};

export interface GradientTransitionSceneProps {
  gradients: string[];
  durationSeconds?: number;
  children?: React.ReactNode;
}

export const GradientTransitionScene: React.FC<GradientTransitionSceneProps> = ({
  gradients,
  durationSeconds = 5,
  children,
}) => {
  return (
    <AbsoluteFill>
      <GradientTransition
        gradient={gradients}
        duration={Math.round(durationSeconds * 30)}
        easing="easeInOut"
      >
        {children}
      </GradientTransition>
    </AbsoluteFill>
  );
};

export interface TypeWriterSceneProps {
  text: string | string[];
  typeSpeed?: number;
  errorRate?: number;
  fontSize?: number;
  color?: string;
  cursorColor?: string;
  backgroundColor?: string;
  loop?: boolean;
}

export const TypeWriterScene: React.FC<TypeWriterSceneProps> = ({
  text,
  typeSpeed = 3,
  errorRate = 0,
  fontSize = 56,
  color = "#FFFFFF",
  cursorColor = "#22D3EE",
  backgroundColor = "#0F172A",
  loop = false,
}) => {
  return (
    <AbsoluteFill
      style={{
        background: backgroundColor,
        justifyContent: "center",
        alignItems: "center",
        padding: "80px",
      }}
    >
      <TypeWriter
        text={text}
        typeSpeed={typeSpeed}
        errorRate={errorRate}
        loop={loop}
        cursor={<span style={{ color: cursorColor }}>|</span>}
        style={{ fontSize, color, fontWeight: 700 }}
      />
    </AbsoluteFill>
  );
};

export interface ParticleSceneProps {
  particleType?: "fireflies" | "snow" | "fountain" | "grid" | "confetti";
  count?: number;
  color?: string;
  backgroundColor?: string;
}

export const ParticleScene: React.FC<ParticleSceneProps> = ({
  particleType = "fireflies",
  count = 60,
  color = "#FACC15",
  backgroundColor = "#0A0A0F",
}) => {
  const config = {
    fireflies: {
      velocity: { x: 0.3, y: -0.2, varianceX: 0.5, varianceY: 0.5 },
      gravity: { y: 0 },
      wiggle: { magnitude: 1.5, frequency: 0.3 },
      lifespan: 120,
    },
    snow: {
      velocity: { x: 0.2, y: 1.5, varianceX: 0.4, varianceY: 0.3 },
      gravity: { y: 0.05 },
      wiggle: { magnitude: 0.8, frequency: 0.2 },
      lifespan: 180,
    },
    fountain: {
      velocity: { x: 0, y: -3, varianceX: 1.5, varianceY: 0.5 },
      gravity: { y: 0.15 },
      wiggle: { magnitude: 0.3, frequency: 0.1 },
      lifespan: 90,
    },
    grid: {
      velocity: { x: 0, y: 0, varianceX: 0, varianceY: 0 },
      gravity: { y: 0 },
      wiggle: { magnitude: 0, frequency: 0 },
      lifespan: 200,
    },
    confetti: {
      velocity: { x: 0, y: -2, varianceX: 2, varianceY: 1 },
      gravity: { y: 0.2 },
      wiggle: { magnitude: 2, frequency: 0.4 },
      lifespan: 100,
    },
  }[particleType];

  return (
    <AbsoluteFill style={{ background: backgroundColor }}>
      <Particles>
        <Spawner
          burst={count}
          velocity={config.velocity}
          lifespan={config.lifespan}
          area={{ width: 1920, height: 1080 }}
        >
          <Behavior
            gravity={config.gravity}
            wiggle={config.wiggle}
            scale={{ start: 1, end: 0.2 }}
            opacity={[1, 0]}
          />
        </Spawner>
      </Particles>
    </AbsoluteFill>
  );
};
