# Post-Code-Update GPT-5.4 Temperature Runs (2026-04-12)

This note records the run classification after the code/risk fixes and the artifact mirroring into `results/`.

## Scope

- Model: `gpt-5.4`
- Concurrency: `4`
- Panel: `study2_british_within`
- All runs below were executed **after** the code updates documented in:
  - `docs/risks/RAW_DATA_AND_RISKS.md`
  - Alias merge + replay updates on `2026-04-12`

## Main vs Exploratory

- **Main evaluation (for primary reporting)**:
  - `temp=1.0`
  - `results/runs_s50/temp_test_20260412_gpt5.4/temp1.0_main_eval_20260412T043325Z`
- **Exploratory only (sensitivity check, not primary table)**:
  - `temp=0.2`
  - `results/runs_s50/temp_test_20260412_gpt5.4/temp0.2_exploratory_20260412T052251Z`
  - `temp=1.2`
  - `results/runs_s50/temp_test_20260412_gpt5.4/temp1.2_exploratory_20260412T052251Z`

## Key R1 Metrics

| Run | Cross JSD | Cross Top1 | Top1 mismatch | Human EN JSD | Human ZH JSD | Unresolved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `temp=1.0` (main) | 0.2077 | 0.7857 | 0.2143 | 0.7914 | 0.7874 | 30 |
| `temp=0.2` (exploratory) | 0.2534 | 0.7143 | 0.2857 | 0.7734 | 0.7917 | 30 |
| `temp=1.2` (exploratory) | 0.2266 | 0.7143 | 0.2857 | 0.7785 | 0.7917 | 30 |

## Notes

- `run-all` for `temp=0.2/1.2` stopped at normalize due `allow_unmapped: false`; `analyze` was then run explicitly on completed raw+normalized outputs.
- Remaining unresolved rows are the known `study2_item_04` (`house/church`) bucket.
- Artifacts were mirrored from `artifacts/full_experiments/...` to `results/runs_s50/temp_test_20260412_gpt5.4/...` to keep reporting assets centralized.
