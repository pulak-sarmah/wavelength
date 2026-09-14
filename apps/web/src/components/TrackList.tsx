"use client";

import { useEffect, useRef, useState } from "react";

import type { AuroraGradient } from "@/lib/vibe-palette";
import type { RecommendationResponse } from "@vibe/shared";

interface TrackListProps {
  result: RecommendationResponse;
  gradient: AuroraGradient;
}

export function TrackList({ result, gradient }: TrackListProps) {
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
    };
  }, []);

  function togglePlay(index: number, previewUrl: string | null) {
    if (!previewUrl) return;

    if (playingIndex === index) {
      audioRef.current?.pause();
      setPlayingIndex(null);
      return;
    }

    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.addEventListener("ended", () => setPlayingIndex(null));
    }
    audioRef.current.src = previewUrl;
    audioRef.current.play();
    setPlayingIndex(index);
  }

  return (
    <div className="mx-auto min-h-screen max-w-2xl px-6 py-24 sm:px-10">
      <h2 className="font-serif text-4xl text-starlight sm:text-5xl">Music for your vibe</h2>
      <p className="mt-3 text-dust">{result.explanation}</p>

      <ul className="mt-10 divide-y divide-white/10">
        {result.tracks.map((track, index) => {
          const isPlaying = playingIndex === index;
          return (
            <li key={`${track.title}-${track.artist}-${index}`} className="flex items-center gap-4 py-4">
              <div
                className="h-14 w-14 shrink-0 overflow-hidden rounded-lg bg-cover bg-center"
                style={{
                  backgroundImage: track.album_art_url
                    ? `url(${track.album_art_url})`
                    : `linear-gradient(135deg, ${gradient.from}, ${gradient.to})`,
                }}
                aria-hidden="true"
              />

              <div className="min-w-0 flex-1 text-left">
                <p className="truncate text-starlight">{track.title}</p>
                <p className="truncate text-sm text-dust">{track.artist}</p>
              </div>

              {track.preview_url && (
                <button
                  type="button"
                  onClick={() => togglePlay(index, track.preview_url)}
                  className="shrink-0 rounded-full border border-white/15 px-4 py-2 text-xs font-medium text-starlight transition hover:border-nebula/60 hover:bg-white/5"
                >
                  {isPlaying ? "Pause" : "Play"}
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
