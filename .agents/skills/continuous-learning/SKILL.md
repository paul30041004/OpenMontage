---
name: continuous-learning
description: Instinct-based learning system that observes coding sessions, records user corrections, tracks framework quirks, and auto-adapts agent behaviors with confidence scoring.
metadata:
  version: 2.1.0
  origin: ECC
---

# Continuous Learning (Instinct-Based Architecture)

An advanced learning skill that captures lessons, user preferences, and error resolutions from coding sessions into atomic, reusable "instincts".

## When to Activate

- Capturing lessons and project-specific conventions from sessions
- Recording user corrections (e.g. "always use Apple Silicon MPS", "never hardcode secrets")
- Tracking workarounds to framework or library quirks
- Applying confidence-weighted behavior adaptations across turns

## The Instinct Model

An instinct is an atomic learned behavior:
- **Trigger**: When this behavior should activate (e.g. "when writing TTS scripts")
- **Action**: The exact concrete rule to follow (e.g. "always use Korean normalizer on numbers and Bible verses")
- **Confidence**: 0.3 (tentative) to 0.9 (near-certain / core rule)
- **Evidence**: The observation, mistake, or user correction that formed the rule

## Core Rules for Agent Learning

1. **User Corrections Take Precedence**: When a user corrects an assumption (e.g. "use python3 not python", "audio.narration.src is nested"), immediately record it as an active high-confidence instinct.
2. **Never Repeat a Resolved Error**: Check previous session lessons before executing similar tasks to prevent regression.
3. **Keep Rules Atomic**: One trigger, one action. Complex multi-step rules are split into small, clear invariants.
