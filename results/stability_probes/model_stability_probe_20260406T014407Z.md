# Model Stability Probe 20260406T014407Z

- Item snapshot: `20260324T070530Z`
- Item count per model: `5`
- Concurrency ladder: `1, 2, 4`
- Model pool size: `2`

## Model Summary

| Model | Tested Concurrency | Stable Concurrency | Recommended | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| mimo-v2-omni | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |
| mimo-v2-pro | 1, 2, 4 | 1, 2 | 2 | stable | truncation_count=1; retry_records=2 |

## Run Details

| Model | C | Status | Raw | Expected | Provider Err | Empty | Thinking | Trunc | Avg Latency | Max Latency | Unresolved | JSD R1 | Top1 R1 | EN JSD | ZH JSD | Note |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| mimo-v2-omni | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 3.24 | 5.41 | 0 | 0.2 | 0.8 | 0.5236621775741972 | 0.44353432439544643 | retry_records=2 |
| mimo-v2-omni | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 3.09 | 4.69 | 1 | 0.4 | 0.6 | 0.5269639443018427 | 0.5569263517760967 | retry_records=1 |
| mimo-v2-omni | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 3.18 | 4.79 | 2 | 0.2 | 0.8 | 0.5569263517760967 | 0.5569263517760967 | retry_records=1 |
| mimo-v2-pro | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 3.93 | 5.07 | 1 | 0.2 | 0.8 | 0.5569263517760967 | 0.5427245858724767 | ok |
| mimo-v2-pro | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 4.22 | 5.97 | 0 | 0.2 | 0.8 | 0.5196264876630499 | 0.5427245858724767 | retry_records=1 |
| mimo-v2-pro | 4 | unstable | 10 | 10 | 0 | 0 | 0 | 1 | 4.32 | 7.18 | 2 | 0.2 | 0.8 | 0.5569263517760967 | 0.5569263517760967 | truncation_count=1; retry_records=2 |
