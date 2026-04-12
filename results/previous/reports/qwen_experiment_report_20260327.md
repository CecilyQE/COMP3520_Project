# Qwen Experiment Report

## Scope

This note summarizes the most representative Qwen-based benchmark runs currently present in `artifacts/runs/`.

Focus runs:

- `20260324T125130Z`
- `20260324T131440Z`
- `20260324T134951Z`
- `20260326T094323Z`

These cover:

- early full-scale `Qwen/Qwen3.5-35B-A3B` runs
- a larger stream-based `Qwen/Qwen3.5-35B-A3B` run
- a small-scale `Qwen/Qwen3.5-35B-A3B` run

## Executive Summary

The Qwen experiments are real API runs, but the current outputs are not yet reliable as final benchmark evidence.

Main finding:

- cross-lingual consistency can look strong in some runs
- human-alignment is consistently poor
- many runs are heavily contaminated by reasoning-style output (`Thinking Process`) or unresolved responses

Practical interpretation:

- these runs are useful as system/debug evidence
- they are not yet strong enough to serve as clean final experimental results

## Representative Runs

### 1. Full config, 35B, early run

Run:
- `20260324T125130Z`

Files:
- `artifacts/runs/20260324T125130Z/run_manifest.json`
- `artifacts/runs/20260324T125130Z/summary_metrics.json`

Key status:
- config: `configs/atomgit_qwen.yaml`
- model: `Qwen/Qwen3.5-35B-A3B`
- raw records: `90`
- unresolved: `90`
- item metrics: `31`

Key metrics:
- cross-lingual mean JSD: `0.2063`
- cross-lingual top-1 match: `0.75`
- human-alignment mean JSD (en): `1.0`
- human-alignment mean JSD (zh): `1.0`

Interpretation:
- moderate cross-lingual agreement
- essentially no usable human-alignment
- outputs were not cleanly normalized

### 2. Full config, 35B, best-looking 35B run among current full runs

Run:
- `20260324T131440Z`

Files:
- `artifacts/runs/20260324T131440Z/run_manifest.json`
- `artifacts/runs/20260324T131440Z/summary_metrics.json`

Key status:
- config: `configs/atomgit_qwen.yaml`
- model: `Qwen/Qwen3.5-35B-A3B`
- raw records: `90`
- unresolved: `90`
- complete cells: `30`
- item metrics: `45`

Key metrics:
- cross-lingual mean JSD: `0.2018`
- cross-lingual top-1 match: `0.6667`
- human-alignment mean JSD (en): `1.0`
- human-alignment mean JSD (zh): `1.0`

Interpretation:
- this is one of the more complete 35B runs structurally
- but the unresolved count is still very high
- benchmark quality is still limited by output-format problems

### 3. Large stream-based 35B run

Run:
- `20260324T134951Z`

Files:
- `artifacts/runs/20260324T134951Z/run_manifest.json`
- `artifacts/runs/20260324T134951Z/summary_metrics.json`

Key status:
- config: `configs/atomgit_qwen.yaml`
- model: `Qwen/Qwen3.5-35B-A3B`
- backend: stream-based AtomGit path
- raw records: `900`
- unresolved: `900`
- item metrics: `43`

Key metrics:
- cross-lingual mean JSD: `0.0489`
- cross-lingual top-1 match: `1.0`
- human-alignment mean JSD (en): `1.0`
- human-alignment mean JSD (zh): `1.0`

Interpretation:
- apparent cross-lingual performance is misleadingly strong
- because the run is fully unresolved, this should not be treated as a valid final benchmark result
- this run mainly shows that the pipeline can call the model at scale, not that the answers are benchmark-clean

### 4. Small-scale 35B run

Run:
- `20260326T094323Z`

Files:
- `artifacts/runs/20260326T094323Z/run_manifest.json`
- `artifacts/runs/20260326T094323Z/summary_metrics.json`
- `artifacts/runs/20260326T094323Z/raw_generations.jsonl`

Key status:
- config: `configs/atomgit_qwen_small.yaml`
- model: `Qwen/Qwen3.5-35B-A3B`
- raw records: `90`
- unresolved: `90`
- complete cells: `0`
- item metrics: `0`
- analysis warning present

Observed output pattern:
- many responses begin with `Thinking Process:`
- many are truncated with `finish_reason = length`
- some requests fail with service-style error messages

Interpretation:
- this run clearly confirms the current failure mode
- the model is still spending output budget on reasoning text rather than a final short answer

## Overall Assessment

What is real:

- the Qwen runs are genuine API-backed experiments
- both normal and stream-based provider paths were exercised successfully

What is not yet reliable:

- normalized answer quality
- human-alignment estimates
- any conclusion that depends on clean final answers

Current bottleneck:

- the Qwen endpoint frequently emits reasoning-prefixed or truncated output
- this leads to high unresolved counts and weak downstream benchmark validity

## Recommendation

Use the Qwen runs as:

- integration evidence
- debugging evidence
- preliminary cross-lingual observations only

Do not use them yet as:

- final benchmark tables
- headline human-alignment results
- strong comparative claims against cleaner model runs

## Next Step

To make the Qwen experiments report-ready, prioritize:

1. stronger answer-only prompting
2. tighter output limits tuned to final-answer extraction
3. rerunning a small clean validation batch before another full run
