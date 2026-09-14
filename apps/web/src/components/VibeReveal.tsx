"use client";

import type { VibeProfile } from "@vibe/shared";
import { MOOD_TO_DISPLAY_NAME } from "@/lib/vibe-display";

interface VibeRevealProps {
  vibe: VibeProfile;
  onContinue: () => void;
}

const ENERGY_LABEL: Record<string, string> = {
  very_low: "Very low",
  low: "Low",
  medium: "Medium",
  high: "High",
  very_high: "Very high",
};

const SOCIAL_LABEL: Record<string, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export function VibeReveal({ vibe, onContinue }: VibeRevealProps) {
  return (
    // The 3D vibe orb (Scene.tsx) sits in the upper portion of the
    // viewport — this content is anchored below it, not centered over it,
    // so the two never overlap regardless of viewport height.
    <div className="flex min-h-screen flex-col items-center px-6 pt-[46vh] text-center">
      <h2 className="font-serif text-4xl italic text-starlight sm:text-5xl">
        {MOOD_TO_DISPLAY_NAME[vibe.mood]}
      </h2>

      <dl className="mt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-2 text-sm text-dust">
        <div>
          <dt className="inline text-dust">Energy </dt>
          <dd className="inline text-starlight">{ENERGY_LABEL[vibe.energy]}</dd>
        </div>
        <div>
          <dt className="inline text-dust">Social energy </dt>
          <dd className="inline text-starlight">{SOCIAL_LABEL[vibe.social_energy]}</dd>
        </div>
        <div>
          <dt className="inline text-dust">Time </dt>
          <dd className="inline capitalize text-starlight">{vibe.context}</dd>
        </div>
      </dl>

      <button
        type="button"
        onClick={onContinue}
        className="mt-12 rounded-full border border-white/15 px-8 py-3 text-sm font-medium text-starlight transition hover:border-nebula/60 hover:bg-white/5"
      >
        See your music
      </button>
    </div>
  );
}
