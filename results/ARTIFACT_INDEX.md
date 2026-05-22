# Result artifact index (Appendix alignment)

## `results/final_project_tables/`

Paper-ready aggregated CSVs used in `docs/final_report.pdf`:

- `model_level_human_alignment_r1.csv`
- `item_level_cross_lingual_r1.csv`
- `model_level_cross_lingual_r1_r2.csv` (legacy anthropic-only Round 2 summary)
- `strict_permodel_same_item_r1_r2.csv`
- `strict_permodel_cross_lingual_r1_r2.csv`
- `strict_permodel_same_items_model_summary.csv`
- `per_model_round2_strict_audit.csv`

## `results/runs_s50/` (Round 1, 50 samples / cell)

Each `model_timestamp/` folder contains the appendix pipeline outputs:

- `raw_generations.jsonl`
- `normalized_outputs.csv`
- `item_metrics.csv`
- `summary_metrics.json`
- `round2_candidates.csv`
- plus QA files: `run_manifest.json`, `unresolved_queue.csv`, `cell_completeness.csv`, `coord_cell_completeness.csv`, `alias_coverage_report.csv`, `bootstrap_intervals.csv`

## `results/runs_s50_per_model_round2_strict/` (Round 2 exploratory)

Each `model_timestamp__permodelr2/` folder has the same core files after the strict same-model rerun (10 samples / cell on flagged items only).
