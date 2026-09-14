# apps/web

Next.js + TypeScript + Tailwind frontend, with a Three.js (react-three-fiber)
"cosmic nebula" backdrop. Collects the user's text, calls the FastAPI
backend, and renders the vibe reveal + song recommendations. Contains no
business logic — it never talks to the ML model, recommendation engine, or
a music provider directly, only `apps/api` over HTTP.

## Setup

```bash
cd apps/web
npm install
npm run dev
```

Requires `NEXT_PUBLIC_API_URL` (see `.env.example`) pointing at the
FastAPI server (`apps/api`).

## Design system

See the "Stage 5" plan for the full rationale. Summary: a fixed UI palette
(`void`/`nebula`/`starlight`/`dust`/`comet`/`horizon` in `tailwind.config.ts`)
plus a separate, mood-driven aurora palette (`src/lib/vibe-palette.ts`) used
only by the 3D layer — the particle field and the "vibe orb" both
interpolate toward the detected mood's gradient and scale their motion by
its energy, so the spectacle is a literal visualization of the model's
output, not decoration. Typography: Instrument Serif for the large
emotional moments, Geist Sans for everything else.

## Layout

```
app/
├── layout.tsx        fonts, base theme
└── page.tsx           orchestrator — input -> reveal -> music state machine

src/
├── three/
│   ├── Scene.tsx           persistent full-bleed <Canvas>
│   ├── ParticleField.tsx   ambient particle field, mood-reactive color
│   └── VibeOrb.tsx         the signature 3D object (reveal scene only)
├── components/
│   ├── VibeInput.tsx        scene 1
│   ├── VibeReveal.tsx       scene 2
│   └── TrackList.tsx        scene 3
└── lib/
    ├── api-client.ts        fetch wrapper around apps/api
    ├── vibe-palette.ts       mood -> aurora gradient / energy -> intensity
    ├── vibe-display.ts       mood -> human-readable reveal phrase
    └── useReducedMotion.ts   respects prefers-reduced-motion
```

## Status

Fully wired to the real API — `npm run build` and `npm run lint` both
pass clean. Verified end-to-end in a real browser (Playwright) across
three different moods and with `prefers-reduced-motion` on, no console
errors.

**Known pre-existing issue, not introduced by this stage:** `next@14.2.35`
(and `eslint@8`, a dev-only dependency) both have known CVEs; the fix
requires a major-version jump (Next 14→16, which also forces React 18→19
and `@react-three/fiber` v8→v9) — real, separate migration work, tracked
here rather than done silently. Low practical risk today since this is
local dev, not yet deployed.
