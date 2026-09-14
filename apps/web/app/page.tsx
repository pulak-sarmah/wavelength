"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import type { RecommendationResponse } from "@vibe/shared";

import { getVibeRecommendation } from "@/lib/api-client";
import { ENERGY_TO_INTENSITY, IDLE_GRADIENT, MOOD_TO_GRADIENT } from "@/lib/vibe-palette";
import { useReducedMotion } from "@/lib/useReducedMotion";
import { Scene } from "@/three/Scene";
import { VibeInput } from "@/components/VibeInput";
import { VibeReveal } from "@/components/VibeReveal";
import { TrackList } from "@/components/TrackList";

type Phase = "input" | "reveal" | "music";

const FADE = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.6, ease: "easeInOut" as const },
};

export default function Home() {
  const [phase, setPhase] = useState<Phase>("input");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const reducedMotion = useReducedMotion();

  const gradient = result ? MOOD_TO_GRADIENT[result.vibe.mood] : IDLE_GRADIENT;
  const intensity = result ? ENERGY_TO_INTENSITY[result.vibe.energy] : 0.3;

  async function handleSubmit(text: string) {
    setLoading(true);
    setError(null);
    try {
      const data = await getVibeRecommendation(text);
      setResult(data);
      setPhase("reveal");
    } catch {
      setError("Something interrupted your vibe check — try describing it again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Scene gradient={gradient} intensity={intensity} showOrb={phase === "reveal"} reducedMotion={reducedMotion} />

      <AnimatePresence mode="wait">
        {phase === "input" && (
          <motion.div key="input" {...FADE}>
            <VibeInput onSubmit={handleSubmit} loading={loading} error={error} />
          </motion.div>
        )}

        {phase === "reveal" && result && (
          <motion.div key="reveal" {...FADE}>
            <VibeReveal vibe={result.vibe} onContinue={() => setPhase("music")} />
          </motion.div>
        )}

        {phase === "music" && result && (
          <motion.div key="music" {...FADE}>
            <TrackList result={result} gradient={gradient} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
