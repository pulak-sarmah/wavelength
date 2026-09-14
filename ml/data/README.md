# ml/data

- `raw/` — untouched source data. Currently unused: we pull GoEmotions
  directly via Hugging Face `datasets` (cached in `~/.cache/huggingface`,
  not in this repo) rather than vendoring a raw copy.
- `processed/` — `train.csv` / `val.csv` / `test.csv`, produced by
  `python -m vibe_ml.data.goemotions`. Gitignored (except `.gitkeep`);
  fully reproducible from the command above.

## Dataset: GoEmotions

[GoEmotions](https://huggingface.co/datasets/google-research-datasets/go_emotions)
(`simplified` config) — ~43k/5.4k/5.4k train/val/test Reddit comments,
labeled with 28 fine-grained emotions. We keep GoEmotions' own split
(not a re-split) so numbers stay comparable to published baselines.

`vibe_ml.data.goemotions.load_and_map_goemotions`:
1. Drops multi-label rows (ambiguous for a single mood target).
2. Maps the remaining single label onto our 9-mood taxonomy via
   `vibe_ml.labels.GOEMOTIONS_TO_MOOD`.
3. Drops rows whose label has no clean mood mapping (`confusion`,
   `curiosity`, `realization`, `surprise` — genuinely ambiguous valence).

## Known taxonomy gaps (as of the GoEmotions mapping)

Real counts from the mapped train split:

| mood      | rows   |
|-----------|--------|
| neutral   | 12823  |
| happy     | 9857   |
| angry     | 4376   |
| romantic  | 2465   |
| sad       | 1918   |
| anxious   | 718    |
| excited   | 510    |
| calm      | 88     |
| nostalgic | **0**  |

- **`nostalgic` has zero rows.** GoEmotions has no emotion category that
  maps to it. The baseline classifier is trained only on the 8 moods that
  have support — `nostalgic` stays defined in `MOOD_LABELS`/`MOOD_TO_DERIVED`
  as a documented gap, not a class the model can currently predict. Closing
  this needs either a different/additional dataset or a small hand-labeled
  seed set.
- **`calm` is extremely thin** (88 rows, only from GoEmotions' `relief`).
  It's kept as an active class since it's non-zero, but expect weak
  recall — see `ml/models/latest/metrics.json`.

See [../../docs/ml-plan.md](../../docs/ml-plan.md) for the full plan.
