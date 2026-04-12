# Results Layout

This folder is organized by experiment type to make each model run easier to trace.

## Folders

- `full_experiments/indexes/`
  - Batch-level index files from `scripts/run_new_models_full_experiments.py`.
  - Naming: `new_models_full_experiments_<batch_tag>.json|md`
- `full_experiments/summaries/`
  - Per-run summary tables from full experiment scripts.
  - Naming: `full_experiment_summary_<root_tag>.md`
- `stability_probes/`
  - Outputs from `scripts/run_model_stability_probe.py`.
  - Naming: `model_stability_probe_<batch_tag>.json|md`
- `concurrency_sweeps/`
  - Reports from `scripts/run_universal_concurrency_sweep.py`.
  - Naming: `concurrency_sweep_<sweep_tag>.md`
- `reports/`
  - Curated, narrative roll-up reports.
- `runs/`
  - Archived historical run folders from legacy layouts.
  - Includes curated post-update mirrored runs:
    - `results/runs/post_code_update_20260412/`
    - Contains `temp=1.0` main evaluation and `temp=0.2/1.2` exploratory runs for `gpt-5.4`.

## Where Raw Run Artifacts Live

Primary raw run artifacts are still under `artifacts/`:

- `artifacts/runs/<run_id>/...`
- `artifacts/full_experiments/<root_tag>/...`
- `artifacts/stability_probes/<batch_tag>/...`
- `artifacts/sweeps/<sweep_tag>/...`

For reporting convenience, selected finalized runs can be mirrored into `results/runs/...` (without provider cache folders). See:

- `results/reports/post_code_update_gpt54_temperature_runs_20260412.md`
