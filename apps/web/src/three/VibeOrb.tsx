"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { MeshDistortMaterial, Sphere } from "@react-three/drei";
import * as THREE from "three";

import type { AuroraGradient } from "@/lib/vibe-palette";

interface VibeOrbProps {
  gradient: AuroraGradient;
  intensity: number; // 0..1 — drives distortion + rotation speed
  reducedMotion: boolean;
}

// The one signature 3D object: a distorted sphere whose color, distortion,
// and rotation speed directly encode the detected vibe's gradient and
// energy — a literal visualization of the vibe profile, not decoration.
//
// Emissive rather than reflective: a physically-lit metal/glossy look needs
// an environment map to reflect, which this scene deliberately doesn't have
// (it's a particle field, not a studio backdrop) — without one, low
// roughness/metalness just reads as a flat dark blob. Self-glow keeps it
// legible and painterly regardless of scene lighting.
export function VibeOrb({ gradient, intensity, reducedMotion }: VibeOrbProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  // MeshDistortMaterial's concrete type isn't publicly exported by drei,
  // so this ref is intentionally untyped rather than fought into shape.
  const materialRef = useRef<any>(null);
  const currentColor = useMemo(() => new THREE.Color(gradient.from), [gradient.from]);
  const target = useMemo(() => new THREE.Color(), []);

  useFrame((_state, delta) => {
    target.set(gradient.from).lerp(new THREE.Color(gradient.to), 0.5);
    currentColor.lerp(target, reducedMotion ? 1 : Math.min(delta * 1.2, 1));
    if (materialRef.current) {
      materialRef.current.color = currentColor;
      materialRef.current.emissive = currentColor;
    }
    if (meshRef.current && !reducedMotion) {
      meshRef.current.rotation.y += delta * (0.15 + intensity * 0.3);
      meshRef.current.rotation.x += delta * 0.05;
    }
  });

  return (
    <Sphere ref={meshRef} args={[0.95, 128, 128]} position={[0, 1.3, 0]}>
      <MeshDistortMaterial
        ref={materialRef}
        color={gradient.from}
        emissive={gradient.from}
        emissiveIntensity={0.45 + intensity * 0.4}
        distort={0.15 + intensity * 0.2}
        speed={reducedMotion ? 0 : 1 + intensity * 2}
        roughness={0.5}
        metalness={0}
      />
    </Sphere>
  );
}
