"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

import type { AuroraGradient } from "@/lib/vibe-palette";

interface ParticleFieldProps {
  gradient: AuroraGradient;
  intensity: number; // 0..1 — drives drift speed
  reducedMotion: boolean;
}

const PARTICLE_COUNT = 1400;
const RADIUS = 7;

// A soft circular glow, generated on the client rather than shipped as an
// asset — pointsMaterial renders hard squares without a sprite map, which
// reads as digital confetti rather than starlight/nebula dust.
function useGlowTexture(): THREE.Texture {
  return useMemo(() => {
    const size = 64;
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d")!;
    const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    gradient.addColorStop(0, "rgba(255,255,255,1)");
    gradient.addColorStop(0.4, "rgba(255,255,255,0.6)");
    gradient.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    return texture;
  }, []);
}

function randomPointInSphere(radius: number): [number, number, number] {
  let x = 0;
  let y = 0;
  let z = 0;
  do {
    x = Math.random() * 2 - 1;
    y = Math.random() * 2 - 1;
    z = Math.random() * 2 - 1;
  } while (x * x + y * y + z * z > 1);
  return [x * radius, y * radius, z * radius];
}

export function ParticleField({ gradient, intensity, reducedMotion }: ParticleFieldProps) {
  const groupRef = useRef<THREE.Group>(null);
  const geometryRef = useRef<THREE.BufferGeometry>(null);
  const glowTexture = useGlowTexture();

  const { positions, seeds } = useMemo(() => {
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const seeds = new Float32Array(PARTICLE_COUNT);
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const [x, y, z] = randomPointInSphere(RADIUS);
      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;
      seeds[i] = Math.random();
    }
    return { positions, seeds };
  }, []);

  const colors = useMemo(() => new Float32Array(PARTICLE_COUNT * 3), []);
  const colorA = useMemo(() => new THREE.Color(), []);
  const colorB = useMemo(() => new THREE.Color(), []);
  const target = useMemo(() => new THREE.Color(), []);

  useFrame((_state, delta) => {
    colorA.set(gradient.from);
    colorB.set(gradient.to);

    const colorAttr = geometryRef.current?.getAttribute("color") as THREE.BufferAttribute | undefined;
    if (colorAttr) {
      const lerpSpeed = reducedMotion ? 1 : Math.min(delta * 1.5, 1);
      const array = colorAttr.array as Float32Array;
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        target.copy(colorA).lerp(colorB, seeds[i]);
        const idx = i * 3;
        array[idx] += (target.r - array[idx]) * lerpSpeed;
        array[idx + 1] += (target.g - array[idx + 1]) * lerpSpeed;
        array[idx + 2] += (target.b - array[idx + 2]) * lerpSpeed;
      }
      colorAttr.needsUpdate = true;
    }

    if (groupRef.current && !reducedMotion) {
      groupRef.current.rotation.y += delta * (0.03 + intensity * 0.08);
      groupRef.current.rotation.x += delta * 0.01;
    }
  });

  return (
    <group ref={groupRef}>
      <points>
        <bufferGeometry ref={geometryRef}>
          <bufferAttribute attach="attributes-position" count={PARTICLE_COUNT} array={positions} itemSize={3} />
          <bufferAttribute attach="attributes-color" count={PARTICLE_COUNT} array={colors} itemSize={3} />
        </bufferGeometry>
        <pointsMaterial
          map={glowTexture}
          size={0.16}
          vertexColors
          transparent
          opacity={0.9}
          sizeAttenuation
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
}
