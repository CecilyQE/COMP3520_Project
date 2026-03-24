# CoordBench

CoordBench is a self-sufficient Python research pipeline for studying cross-lingual robustness in tacit coordination tasks with LLMs.

It downloads the Perez-Zapata et al. OSF source files itself, reconstructs benchmark-ready human panels, profiles the dataset, samples real models from OpenAI, Gemini, DeepSeek, and Anthropic-compatible endpoints, normalizes outputs against human response distributions, and produces metrics plus plots for research reporting.

## What It Does

- Downloads the public OSF source data for the coordination studies into versioned snapshots.
- Reconstructs participant-level and aggregated human benchmark panels from the raw Qualtrics exports.
- Profiles all prepared panels and recommends a default benchmark panel.
- Runs matched English and Chinese prompt variants while holding answer language fixed.
- Normalizes LLM answers against human canonical answer inventories with alias and fuzzy matching support.
- Computes cross-lingual and human-alignment metrics, bootstrap intervals, round-2 candidate items, and publication-friendly plots.

## Source Data

The default source is the public OSF project for:

- Perez-Zapata et al., *Three International Studies on Pure Coordination Games: Adaptable Solutions When Intuitions are Presumed to Vary*.
- OSF project: [https://osf.io/fv47d/](https://osf.io/fv47d/)
- Accepted manuscript referenced while building this repo: [https://pure-oai.bham.ac.uk/ws/portalfiles/portal/277920622/AcceptedVersionJEPGeneralAlignmentPaper_09.09.2025_.pdf](https://pure-oai.bham.ac.uk/ws/portalfiles/portal/277920622/AcceptedVersionJEPGeneralAlignmentPaper_09.09.2025_.pdf)

The first official benchmark config defaults to `study2_british_within`.

## Setup

```bash
pip install -e .[dev]
```

Create a `.env` from `.env.example` and fill in:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_MODEL`
- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_MODEL` (`claude-opus-4-6` is the default example)

## Main Commands

```bash
coordbench fetch-source-data
coordbench prepare-human-panels
coordbench profile-dataset
coordbench run-sampling --config configs/study2_british_en_zh.yaml
coordbench normalize --config configs/study2_british_en_zh.yaml --run-id <run_id>
coordbench analyze --config configs/study2_british_en_zh.yaml --run-id <run_id>
coordbench plot --config configs/study2_british_en_zh.yaml --run-id <run_id>
coordbench run-all --config configs/study2_british_en_zh.yaml
```

For a quicker smoke pass, use:

```bash
coordbench run-all --config configs/demo.yaml
```

For an Anthropic-compatible smoke run:

```bash
coordbench run-sampling --config configs/anthropic_smoke.yaml
```

For a full Anthropic-only research run on the default panel:

```bash
coordbench run-all --config configs/study2_british_anthropic_en_zh.yaml
```

## Important Outputs

Prepared dataset artifacts live under `data/prepared/<snapshot_id>/` and include:

- `participant_responses.csv`
- `human_distributions.csv`
- `panel_items.csv`
- `panel_summary.csv`
- `dataset_inventory.json`
- `selection_report.md`
- `benchmark_manifest.json`

Run artifacts live under `artifacts/runs/<run_id>/` and include:

- `run_manifest.json`
- `raw_generations.jsonl`
- `normalized_outputs.csv`
- `unresolved_queue.csv`
- `item_metrics.csv`
- `summary_metrics.json`
- `bootstrap_intervals.csv`
- `round2_candidates.csv`
- `plots/`

## Notes

- The default configs set `allow_unmapped: true` so the pipeline can complete even if a model produces novel answers. For publication-tight runs, expand the alias file and switch this to `false`.
- Round 2 is triggered from round-1 cross-lingual top-1 mismatches and is run automatically by `run-all` when candidates are found.
- Dataset preparation currently reconstructs:
  - `study1_british_within`
  - `study1_global_within`
  - `study2_british_within`
  - `study2_british_between`
  - `study2_south_african_within`
  - `study2_south_african_between`
  - `study3_chilean_within`
  - `study3_chilean_between`
  - `study3_south_african_within`
  - `study3_south_african_between`

## Tests

```bash
pytest
```
