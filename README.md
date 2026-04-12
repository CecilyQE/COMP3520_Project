# CoordBench (COMP3520 Project)

CoordBench is a reproducible benchmark pipeline for evaluating cross-lingual robustness of tacit coordination in LLMs, with human-reference metrics.

It supports:
- OSF source data fetch + panel preparation
- EN/ZH matched prompting with fixed answer language
- answer normalization against human canonical distributions
- cross-lingual + human-alignment metrics
- round-2 re-coordination candidate generation

## Quick Start

1. Install:

```bash
pip install -e .[dev]
```

2. Configure `.env` from `.env.example`:
- `OPENAI_API_KEY`, `OPENAI_MODEL`
- `GEMINI_API_KEY`, `GEMINI_MODEL`
- `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`
- `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`

3. Run full pipeline with default benchmark config:

```bash
coordbench run-all --config configs/study2_british_en_zh.yaml
```

## Core CLI

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

## Standard Workflow

1. `fetch-source-data`
2. `prepare-human-panels`
3. `profile-dataset`
4. `run-sampling`
5. `normalize`
6. `analyze`
7. `plot`

Or use `run-all` to run 4–7 end-to-end.

## Config Conventions

- Default panel: `study2_british_within`
- Default prompt languages: `en`, `zh`
- Default answer language: `English`
- Normalization default: `allow_unmapped: false`
- Round-2 trigger supports:
  - `cross_lingual_top1_mismatch`
  - `human_top1_mismatch`
  - `either_top1_mismatch`

## Repository Layout

- `src/coordbench/`: package source code
- `tests/`: unit/integration tests
- `configs/`: benchmark and provider configs
- `scripts/`: experiment runners and monitors
- `scripts/debug/`: ad-hoc debugging scripts
- `tools/`: one-off utility scripts
- `docs/proposal/`: proposal files
- `docs/risks/`: risk/method notes
- `docs/updates/`: repository update logs

## Output Layout

### Prepared data

`data/prepared/<snapshot_id>/`:
- `participant_responses.csv`
- `human_distributions.csv`
- `panel_items.csv`
- `panel_summary.csv`
- `dataset_inventory.json`
- `selection_report.md`
- `benchmark_manifest.json`

### Run artifacts

`artifacts/runs/<run_id>/`:
- `run_manifest.json`
- `raw_generations.jsonl`
- `normalized_outputs.csv`
- `unresolved_queue.csv`
- `item_metrics.csv`
- `summary_metrics.json`
- `bootstrap_intervals.csv`
- `round2_candidates.csv`
- `plots/`

### Experiment reports

`results/` is organized by experiment type:
- `results/full_experiments/indexes/`
- `results/full_experiments/summaries/`
- `results/stability_probes/`
- `results/concurrency_sweeps/`
- `results/reports/`
- `results/runs/` (archived legacy run folders)

See `results/README.md` for naming conventions.

## Script Entry Points

- Full multi-model experiments: `scripts/run_new_models_full_experiments.py`
- Single full experiment: `scripts/run_one_full_experiment.py`
- Universal full experiments: `scripts/run_universal_full_experiments.py`
- Stability probe: `scripts/run_model_stability_probe.py`
- Concurrency sweep: `scripts/run_universal_concurrency_sweep.py`
- Monitoring: `scripts/watch_full_experiment_status.py`, `scripts/monitor_token_usage.py`

## Tests

```bash
pytest -q
```

## Source Data

- OSF project: https://osf.io/fv47d/
- Perez-Zapata et al., *Three International Studies on Pure Coordination Games*
