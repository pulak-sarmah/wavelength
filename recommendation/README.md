# recommendation_engine

Translates a `VibePrediction` (from `vibe_ml`) into real song
recommendations, without ever containing ML model logic or HTTP serving
logic itself. See [../docs/recommendation-system.md](../docs/recommendation-system.md).

```
VibePrediction ──▶ RecommendationEngine ──▶ MusicQuery ──▶ MusicProvider ──▶ TrackResult[]
```

## Layout

```
recommendation/
└── src/recommendation_engine/
    ├── types.py            MusicQuery, TrackResult
    ├── genres.py            mood -> genres/energy/valence lookup tables
    ├── engine.py            RecommendationEngine
    └── providers/
        ├── base.py              MusicProvider abstract interface
        ├── mock_provider.py     MockMusicProvider (dev/testing)
        └── jamendo_provider.py  JamendoProvider (real, open-content tracks)
```

## Status

`RecommendationEngine.build_query`/`.recommend` are implemented — a
rule-based mapping from mood/energy/valence to a `MusicQuery`
(`tests/test_engine.py`). Two providers exist: `MockMusicProvider` and
`JamendoProvider` (`tests/test_jamendo_provider.py`, HTTP mocked — no
network access in tests). See
[../docs/recommendation-system.md](../docs/recommendation-system.md) for
why Jamendo and its one known limitation (no energy/valence search
support).
