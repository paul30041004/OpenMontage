# Synthetic VFX & Motion Component Catalog

> Guide to using OpenMontage's Remotion React motion graphics components for **GPU-free, code-generated visual effects** that turn plain videos into broadcast-grade presentations.

---

## 1. Component Architecture & Cut Schemas

All components are rendered frame-accurately via the `Explainer` composition. Pass the corresponding `type` and prop fields inside `edit_decisions.cuts[]`.

---

## 2. Component Reference Guide

### 1. `audio_waveform` (`AudioWaveformVisualizer`)
Procedurally animates dynamic harmonic sound spectrum bars synchronized to voice or music.
* **Cut schema:**
  ```json
  {
    "id": "cut_01",
    "type": "audio_waveform",
    "title": "VOICE SPECTRUM",
    "subtitle": "Dr. Carl Sagan (1980 Interview)",
    "barCount": 42,
    "waveColor": "#38bdf8",
    "accentColor": "#ec4899",
    "in_seconds": 0,
    "out_seconds": 15
  }
  ```

### 2. `split_screen` (`SplitScreen`)
2-way split screen (horizontal or vertical) with animated glowing border divider and individual source playback.
* **Cut schema:**
  ```json
  {
    "id": "cut_02",
    "type": "split_screen",
    "title": "MYTH VS REALITY",
    "left": {
      "type": "video",
      "src": "assets/video/pyramid_decay.mp4",
      "label": "Myth: Stone Lasts Forever"
    },
    "right": {
      "type": "video",
      "src": "assets/video/lunar_module.mp4",
      "label": "Reality: Moon Artifacts"
    },
    "orientation": "horizontal",
    "dividerColor": "#38bdf8",
    "in_seconds": 15,
    "out_seconds": 30
  }
  ```

### 3. `social_quote` (`SocialQuoteCard`)
Viral Twitter/X style glassmorphism quote card with custom verified badges, highlights, and stats.
* **Cut schema:**
  ```json
  {
    "id": "cut_03",
    "type": "social_quote",
    "authorName": "Albert Einstein",
    "authorHandle": "@einstein_official",
    "quoteText": "Look deep into nature, and then you will understand everything better.",
    "highlightWords": ["deep", "understand", "better"],
    "verified": true,
    "likesCount": "128.4K",
    "retweetsCount": "42.1K",
    "accentColor": "#f59e0b",
    "in_seconds": 30,
    "out_seconds": 45
  }
  ```

### 4. `device_mockup` (`DeviceMockup`)
3D floating smartphone or laptop mockup with perspective tilting and reflection glaze.
* **Cut schema:**
  ```json
  {
    "id": "cut_04",
    "type": "device_mockup",
    "deviceType": "smartphone",
    "screenMediaUrl": "assets/video/app_demo.mp4",
    "screenMediaType": "video",
    "title": "OpenMontage Mobile App",
    "subtitle": "Available for iOS and Android",
    "accentColor": "#6366f1",
    "in_seconds": 45,
    "out_seconds": 60
  }
  ```

### 5. `geo_route` (`GeoRouteMap`)
Futuristic grid map with animated SVG trajectory drawing and pulsing waypoint markers.
* **Cut schema:**
  ```json
  {
    "id": "cut_05",
    "type": "geo_route",
    "title": "VOYAGER 1 INTERSTELLAR TRAJECTORY",
    "waypoints": [
      { "name": "Earth Launch (1977)", "x": 15, "y": 70 },
      { "name": "Jupiter Flyby (1979)", "x": 38, "y": 45 },
      { "name": "Saturn Encounter (1980)", "x": 65, "y": 30 },
      { "name": "Interstellar Space (2012+)", "x": 90, "y": 15 }
    ],
    "accentColor": "#38bdf8",
    "pathColor": "#ef4444",
    "in_seconds": 60,
    "out_seconds": 85
  }
  ```

### 6. `terminal_scene` (`TerminalScene`)
Simulated command-line interface execution with realistic typing cadence, output streams, and status badges.
* **Cut schema:**
  ```json
  {
    "id": "cut_06",
    "type": "terminal_scene",
    "terminalTitle": "bash — openmontage@cli",
    "prompt": "$",
    "steps": [
      { "cmd": "openmontage create --pipeline explainer", "pause": 1.2 },
      { "out": "✔ Auto-discovered 15 free CPU tools\n✔ Synthesizing VoxCPM emotional voiceover...\n✔ Assembling Remotion 4K Master...", "pause": 1.5 },
      { "pill": "SUCCESS", "pillColor": "#10b981", "pause": 2.0 }
    ],
    "in_seconds": 85,
    "out_seconds": 105
  }
  ```

---

## 3. Best Practices for High Retention
1. **Never stay on a static visual for > 3.0 seconds:** Combine background stock video with an overlay component (e.g., `backgroundVideo` with `SocialQuoteCard`).
2. **Spring Physics Consistency:** Use damping: 14–16 and mass: 0.8 for snappy, Apple-like entrance transitions.
3. **Color Harmony:** Tie `accentColor` across charts, text highlights, and waveform visualizers to the project's selected style playbook.
