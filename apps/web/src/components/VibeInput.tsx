"use client";

import { useState } from "react";

interface VibeInputProps {
  onSubmit: (text: string) => void;
  loading: boolean;
  error: string | null;
}

export function VibeInput({ onSubmit, loading, error }: VibeInputProps) {
  const [text, setText] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (text.trim() && !loading) {
      onSubmit(text.trim());
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <p className="mb-10 text-sm tracking-wide text-dust">Wavelength</p>

      <h1 className="max-w-2xl font-serif text-5xl leading-tight text-starlight sm:text-6xl md:text-7xl">
        How are you feeling?
      </h1>

      <form onSubmit={handleSubmit} className="mt-10 w-full max-w-xl">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          placeholder="I've had a terrible day and just want to lie down and forget everything."
          className="w-full resize-none rounded-2xl border border-white/10 bg-horizon/60 p-5 text-base text-starlight placeholder:text-dust/70 backdrop-blur-md outline-none transition focus:border-nebula/60"
          disabled={loading}
        />

        <button
          type="submit"
          disabled={!text.trim() || loading}
          className="mt-6 rounded-full bg-nebula px-8 py-3 text-sm font-medium text-starlight transition hover:bg-nebula/80 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Understanding your vibe…" : "Understand my vibe"}
        </button>

        {error && <p className="mt-4 text-sm text-dust">{error}</p>}
      </form>
    </div>
  );
}
