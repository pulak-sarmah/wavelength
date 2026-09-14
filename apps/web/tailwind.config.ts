import type { Config } from "tailwindcss";

// Cosmic nebula design system — see docs/architecture.md / the stage-5 plan
// for the full rationale. `void`/`nebula`/`starlight`/`dust`/`comet`/`horizon`
// are the fixed UI palette; the mood-reactive aurora gradients used by the
// 3D layer live separately in src/lib/vibe-palette.ts (data-driven, not
// static branding).
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#0A0A16",
        nebula: "#6E5BFF",
        starlight: "#F5F3FF",
        dust: "#9C97B8",
        comet: "#5EEAD4",
        horizon: "#1C1830",
      },
      fontFamily: {
        serif: ["var(--font-instrument-serif)", "Georgia", "serif"],
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
