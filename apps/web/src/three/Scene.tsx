"use client";

import { Canvas } from "@react-three/fiber";

import type { AuroraGradient } from "@/lib/vibe-palette";
import { ParticleField } from "./ParticleField";
import { VibeOrb } from "./VibeOrb";

interface SceneProps {
  gradient: AuroraGradient;
  intensity: number;
  showOrb: boolean;
  reducedMotion: boolean;
}

// Persistent full-bleed 3D backdrop. Lives behind every scene in the flow
// (see app/page.tsx) — the particle field is always present and reacts to
// the active gradient; the vibe orb only appears once a vibe is known.
export function Scene({ gradient, intensity, showOrb, reducedMotion }: SceneProps) {
  return (
    <div className="fixed inset-0 -z-10" aria-hidden="true">
      <Canvas camera={{ position: [0, 0, 6], fov: 50 }} dpr={[1, 2]}>
        <ambientLight intensity={0.5} />
        <pointLight position={[4, 3, 5]} intensity={1.5} color={gradient.to} />
        <pointLight position={[-4, -2, 3]} intensity={0.8} color={gradient.from} />
        <ParticleField gradient={gradient} intensity={intensity} reducedMotion={reducedMotion} />
        {showOrb && <VibeOrb gradient={gradient} intensity={intensity} reducedMotion={reducedMotion} />}
      </Canvas>
    </div>
  );
}
