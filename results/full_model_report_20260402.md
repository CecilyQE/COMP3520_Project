# Full Model Experiment Report

## Summary

This report summarizes four full benchmark runs completed with the universal API on the `study2_british_within` panel.

All four models successfully completed:
- round 1
- round 2
- normalization
- analysis
- plotting

No model showed:
- provider error failures
- empty responses
- reasoning / thinking-process pollution
- truncation-marked outputs

The four evaluated models were:
- `qwen3-coder-plus`
- `glm-5`
- `qwen3.5-plus`
- `gpt-5.4-mini`

## Results Table

| Model | Price Tier | Concurrency | Total Time (s) | Raw Records | Round 2 Candidates | Unresolved | Cross-lingual JSD (R1) | Cross-lingual Top1 (R1) | Human Align EN JSD (R1) | Human Align ZH JSD (R1) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `qwen3-coder-plus` | 1x | 6 | 239.94 | 940 | 2 | 108 | 0.1134 | 0.8667 | 0.4218 | 0.4661 |
| `glm-5` | unknown | 6 | 208.27 | 960 | 3 | 107 | 0.1287 | 0.8000 | 0.4111 | 0.4562 |
| `qwen3.5-plus` | 1x | 4 | 1840.34 | 940 | 2 | 158 | 0.1025 | 0.8667 | 0.3990 | 0.4119 |
| `gpt-5.4-mini` | 2x | 6 | 1024.47 | 940 | 2 | 152 | 0.0973 | 0.8667 | 0.3943 | 0.4055 |

## Per-Model Notes

### `qwen3-coder-plus`

- Best low-cost balance across speed and quality.
- Finished in about 4 minutes.
- Strong round 1 cross-lingual consistency.
- Lower unresolved count than `qwen3.5-plus` and `gpt-5.4-mini`.
- Round 2 did not improve consistency; round 2 cross-lingual JSD rose to `0.6653`.

Interpretation:
`qwen3-coder-plus` is the strongest practical low-cost candidate in this batch.

### `glm-5`

- Fastest run overall.
- Lowest unresolved count in this batch.
- Slightly weaker round 1 cross-lingual consistency than `qwen3-coder-plus`.
- Round 2 degraded less severely than the Qwen models; round 2 top1 match stayed at `0.6667`.

Interpretation:
`glm-5` is the best speed-first option and still produces clean benchmarkable outputs.

### `qwen3.5-plus`

- Round 1 metrics were respectable.
- Human alignment was slightly better than `qwen3-coder-plus` and `glm-5`.
- Runtime was much worse than expected, about 30 minutes.
- Unresolved count was relatively high.
- Round 2 again made cross-lingual consistency worse.

Interpretation:
`qwen3.5-plus` is usable, but its speed / stability tradeoff was poor compared with the other low-cost options.

### `gpt-5.4-mini`

- Best overall round 1 quality metrics in this batch.
- Lowest round 1 cross-lingual JSD.
- Best human-alignment JSD on both English and Chinese prompts.
- Runtime was much longer than the best low-cost models, about 17 minutes.
- Unresolved count remained fairly high.

Interpretation:
`gpt-5.4-mini` is the strongest quality-oriented baseline here, but it is clearly more expensive in time and likely in usage cost.

## Cross-Model Conclusions

### Best low-cost practical model

`qwen3-coder-plus`

Reason:
- very fast
- clean outputs
- strong round 1 cross-lingual stability
- lower unresolved than the other Qwen low-cost full run

### Best speed-first model

`glm-5`

Reason:
- fastest total runtime
- lowest unresolved count
- still clean enough to trust as a benchmark run

### Best quality baseline

`gpt-5.4-mini`

Reason:
- best round 1 JSD
- best human-alignment values
- fully clean execution

### Main pattern across all four models

Round 1 was consistently more informative than round 2.

In this batch:
- round 2 did not act like a robust repair stage
- for most models, cross-lingual consistency worsened in round 2
- this matches the earlier Gemini finding that the current round-2 strategy is not reliably improving outcomes

## Recommendation

If you want one main model for a cost-conscious report:
- use `qwen3-coder-plus`

If you want one fast alternative:
- use `glm-5`

If you want to include a stronger baseline for comparison:
- add `gpt-5.4-mini`

If you want the cleanest story for the write-up, the simplest comparison is:
- `qwen3-coder-plus` as the main low-cost model
- `gpt-5.4-mini` as the higher-cost baseline

## Source Runs

- `qwen3-coder-plus`: `C:\Users\吴彦祖\Desktop\comp3520\artifacts\full_experiments\20260402T015954Z\qwen3-coder-plus\runs\20260401T175954Z`
- `glm-5`: `C:\Users\吴彦祖\Desktop\comp3520\artifacts\full_experiments\20260402T015954Z\glm-5\runs\20260401T180354Z`
- `qwen3.5-plus`: `C:\Users\吴彦祖\Desktop\comp3520\artifacts\full_experiments\20260402T015954Z\qwen3.5-plus\runs\20260401T180722Z`
- `gpt-5.4-mini`: `C:\Users\吴彦祖\Desktop\comp3520\artifacts\full_experiments\20260402T015954Z\gpt-5.4-mini\runs\20260401T183803Z`

