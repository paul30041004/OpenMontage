import { Config } from "@remotion/cli/config";

// macOS headless Chromium needs ANGLE for WebGL contexts (three.js / @remotion/three).
// Without this, any composition using WebGL fails with "Error creating WebGL context".
Config.setChromiumOpenGlRenderer("angle");
