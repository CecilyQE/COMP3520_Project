# Model Stability Probe 20260405T234609Z

- Item snapshot: `20260324T070530Z`
- Item count per model: `5`
- Concurrency ladder: `1, 2, 4`
- Model pool size: `17`

## Model Summary

| Model | Tested Concurrency | Stable Concurrency | Recommended | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| claude-opus-4-6 | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |
| claude-sonnet-4-6 | 1, 2 | 1 | 1 | stable | provider_errors=1; empty_responses=1; retry_records=4 |
| gemini-3.1-flash | 1 | - | none | unstable | provider_errors=10; empty_responses=10; retry_records=10 |
| gemini-3.1-flash-lite | 1 | - | none | unstable | provider_errors=10; empty_responses=10; retry_records=10 |
| gemini-3.1-pro | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |
| glm-5 | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |
| gpt-5.3-codex | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |
| gpt-5.3-codex-spark | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |
| gpt-5.4 | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |
| gpt-5.4-mini | 1, 2, 4 | 1, 2, 4 | 4 | stable | ok |

## Run Details

| Model | C | Status | Raw | Expected | Provider Err | Empty | Thinking | Trunc | Avg Latency | Max Latency | Unresolved | JSD R1 | Top1 R1 | EN JSD | ZH JSD | Note |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| claude-opus-4-6 | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 3.38 | 4.69 | 0 | 0.0 | 1.0 | 0.4433467721229709 | 0.4433467721229709 | ok |
| claude-opus-4-6 | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 4.08 | 6.25 | 1 | 0.2 | 0.8 | 0.4433467721229709 | 0.544662250970942 | retry_records=1 |
| claude-opus-4-6 | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 4.29 | 5.71 | 1 | 0.2 | 0.8 | 0.4433467721229709 | 0.4629158199432064 | ok |
| claude-sonnet-4-6 | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 6.99 | 11.53 | 0 | 0.2 | 0.8 | 0.5427245858724767 | 0.5196264876630499 | retry_records=5 |
| claude-sonnet-4-6 | 2 | unstable | 10 | 10 | 1 | 1 | 0 | 0 | 6.92 | 9.56 | 10 |  |  |  |  | provider_errors=1; empty_responses=1; retry_records=4 |
| gemini-3.1-flash | 1 | unstable | 10 | 10 | 10 | 10 | 0 | 0 |  |  | 10 |  |  |  |  | provider_errors=10; empty_responses=10; retry_records=10 |
| gemini-3.1-flash-lite | 1 | unstable | 10 | 10 | 10 | 10 | 0 | 0 |  |  | 10 |  |  |  |  | provider_errors=10; empty_responses=10; retry_records=10 |
| gemini-3.1-pro | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 6.27 | 12.83 | 4 | 0.0 | 1.0 | 0.6285061863618925 | 0.6285061863618925 | ok |
| gemini-3.1-pro | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 6.25 | 16.66 | 1 | 0.2 | 0.8 | 0.4508717810342392 | 0.5151141589812421 | ok |
| gemini-3.1-pro | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 5.52 | 8.51 | 2 | 0.0 | 1.0 | 0.5151141589812421 | 0.5151141589812421 | ok |
| glm-5 | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 1.9 | 3.37 | 0 | 0.2 | 0.8 | 0.5427245858724767 | 0.46213097809191783 | retry_records=8 |
| glm-5 | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 1.85 | 2.7 | 1 | 0.2 | 0.8 | 0.5569263517760967 | 0.46213097809191783 | retry_records=3 |
| glm-5 | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 1.91 | 3.22 | 1 | 0.2 | 0.8 | 0.46213097809191783 | 0.5569263517760967 | retry_records=5 |
| gpt-5.3-codex | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 5.66 | 7.0 | 3 | 0.2 | 0.8 | 0.6758001790143923 | 0.5879045555212 | ok |
| gpt-5.3-codex | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 6.24 | 9.88 | 3 | 0.2 | 0.8 | 0.6758001790143923 | 0.5952420121599928 | ok |
| gpt-5.3-codex | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 5.54 | 7.91 | 3 | 0.2 | 0.8 | 0.6758001790143923 | 0.5952420121599928 | ok |
| gpt-5.3-codex-spark | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 4.59 | 8.81 | 3 | 0.2 | 0.8 | 0.6448219752692891 | 0.5569263517760967 | retry_records=3 |
| gpt-5.3-codex-spark | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 3.92 | 8.35 | 0 | 0.4 | 0.6 | 0.5236621775741972 | 0.5269639443018427 | retry_records=2 |
| gpt-5.3-codex-spark | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 3.71 | 5.59 | 2 | 0.2 | 0.8 | 0.5642638084148895 | 0.5642638084148895 | retry_records=2 |
| gpt-5.4 | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 5.69 | 8.05 | 3 | 0.2 | 0.8 | 0.6758001790143923 | 0.5879045555212 | ok |
| gpt-5.4 | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 5.38 | 7.5 | 3 | 0.2 | 0.8 | 0.6758001790143923 | 0.5952420121599928 | ok |
| gpt-5.4 | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 5.73 | 7.67 | 3 | 0.2 | 0.8 | 0.6758001790143923 | 0.5879045555212 | ok |
| gpt-5.4-mini | 1 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 4.45 | 6.72 | 3 | 0.6 | 0.4 | 0.603679744013107 | 0.6285061863618925 | ok |
| gpt-5.4-mini | 2 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 5.04 | 6.35 | 1 | 0.2 | 0.8 | 0.5642638084148895 | 0.5309996342129899 | ok |
| gpt-5.4-mini | 4 | stable | 10 | 10 | 0 | 0 | 0 | 0 | 4.63 | 5.85 | 0 | 0.4 | 0.6 | 0.5236621775741972 | 0.4508717810342392 | ok |
