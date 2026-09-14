# @vibe/shared

Cross-language contract between `apps/web` (TypeScript) and `apps/api`
(Python), so the two don't drift apart silently.

- `schemas/` — canonical JSON Schema definitions for shapes that cross the
  HTTP boundary (`VibeProfile`, `Track`).
- `src/types/` — hand-maintained TypeScript types mirroring those schemas,
  imported by `apps/web` as `@vibe/shared`.

The Python side (`apps/api/app/schemas/`) mirrors the same schema using
pydantic models. There's no codegen wiring these together yet — for now,
keep both sides in sync by hand and treat `schemas/*.schema.json` as the
source of truth when they disagree.
