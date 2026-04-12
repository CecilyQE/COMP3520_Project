# All Valid Models Report 20260407

## 1. Scope and validity rule

This report only includes **valid model runs** that satisfy all of the following:

- `status = completed`
- core metrics are present, especially `cross_lingual_round1_jsd`
- the run can be used for quality comparison rather than only for failure logging

Excluded from the main comparison:

- `gemini-3.1-flash`
- `gemini-3.1-flash-lite`
- `MiniMax-M2.7`
- `claude-sonnet-4-6`
- `glm-5` rerun at `c4`

These runs either stopped early or completed with `null` core metrics / invalid final analysis.

The main table below uses **the latest valid run for each model**. When a model has multiple valid runs, rerun variance is discussed separately in Section 5.

## 2. Latest valid model table

| Model | Source Run | Wall(s) | Raw | Round2 | Unresolved | Cross-Lingual JSD R1 | Human EN JSD | Human ZH JSD | Provider Err | Empty | Trunc | Quota Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `qwen3-coder-plus` | `20260402T015954Z` | 239.94 | 940 | 2 | 108 | 0.1134 | 0.4218 | 0.4661 | 0 | 0 | 0 | n/a |
| `glm-5` | `20260402T015954Z` | 208.27 | 960 | 3 | 107 | 0.1287 | 0.4111 | 0.4562 | 0 | 0 | 0 | n/a |
| `qwen3.5-plus` | `20260402T015954Z` | 1840.34 | 940 | 2 | 158 | 0.1025 | 0.3990 | 0.4119 | 0 | 0 | 0 | n/a |
| `gpt-5.4-mini` | `20260406T121647Z_gpt-5.4-mini_c4` | 1536.17 | 940 | 2 | 156 | 0.1042 | 0.4047 | 0.4176 | 0 | 0 | 0 | 913554 |
| `kimi-for-coding` | `20260406T121647Z_kimi-for-coding_c1` | 1608.89 | 960 | 3 | 84 | 0.1485 | 0.4132 | 0.4649 | 0 | 0 | 0 | 369190 |
| `gpt-5.4` | `20260406T121647Z_gpt-5.4_c4` | 2644.58 | 940 | 2 | 163 | 0.1325 | 0.3976 | 0.4390 | 0 | 0 | 0 | 2328755 |
| `gpt-5.3-codex` | `20260406T121647Z_gpt-5.3-codex_c4` | 2050.61 | 940 | 2 | 151 | 0.1363 | 0.3699 | 0.4107 | 0 | 0 | 0 | 6183580 |
| `gemini-3.1-pro` | `20260406T121647Z_gemini-3.1-pro_c4` | 1676.58 | 920 | 1 | 126 | 0.0394 | 0.3527 | 0.3722 | 0 | 0 | 45 | 9462336 |
| `mimo-v2-omni` | `20260406T121647Z_mimo-v2-omni_c4` | 5363.44 | 920 | 1 | 122 | 0.0619 | 0.3491 | 0.3850 | 0 | 0 | 2 | 3376881 |
| `claude-opus-4-6` | `20260406T121647Z_claude-opus-4-6_c4` | 1066.64 | 940 | 2 | 83 | 0.1160 | 0.3232 | 0.3359 | 0 | 0 | 0 | 1401980 |

## 3. Headline findings

- If we prioritize **cross-lingual consistency**, `gemini-3.1-pro` is the current strongest latest-valid run with `JSD = 0.0394`, followed by `mimo-v2-omni` at `0.0619`.
- If we prioritize **human alignment**, `claude-opus-4-6` is the clear leader. It has the best English and Chinese human-alignment JSDs, `0.3232` and `0.3359`, and also the lowest `unresolved_count = 83`.
- If we prioritize **speed**, `glm-5` remains the fastest valid full run at `208.27s`, with `qwen3-coder-plus` close behind at `239.94s`.
- If we prioritize **low unresolved count**, the strongest group is `claude-opus-4-6` (`83`), `kimi-for-coding` (`84`), `glm-5` (`107`), and `qwen3-coder-plus` (`108`).
- If we prioritize **quota efficiency among the new monitored runs**, `kimi-for-coding` is by far the cheapest useful full run in this batch at `369190`, while still keeping `unresolved_count = 84`.

## 4. Dimension-by-dimension analysis

### 4.1 Cross-lingual consistency

Sorted by `cross_lingual_round1_jsd` ascending:

1. `gemini-3.1-pro` - `0.0394`
2. `mimo-v2-omni` - `0.0619`
3. `qwen3.5-plus` - `0.1025`
4. `gpt-5.4-mini` - `0.1042`
5. `qwen3-coder-plus` - `0.1134`
6. `claude-opus-4-6` - `0.1160`
7. `glm-5` - `0.1287`
8. `gpt-5.4` - `0.1325`
9. `gpt-5.3-codex` - `0.1363`
10. `kimi-for-coding` - `0.1485`

Interpretation:

- `gemini-3.1-pro` and `mimo-v2-omni` form a distinct top tier for cross-lingual stability.
- `qwen3.5-plus`, `gpt-5.4-mini`, and `qwen3-coder-plus` form a strong middle tier.
- `kimi-for-coding` is not strong on distributional consistency, but compensates elsewhere through low unresolved count and low quota.

### 4.2 Human alignment

English-side human alignment ranking:

1. `claude-opus-4-6` - `0.3232`
2. `mimo-v2-omni` - `0.3491`
3. `gemini-3.1-pro` - `0.3527`
4. `gpt-5.3-codex` - `0.3699`
5. `gpt-5.4` - `0.3976`
6. `qwen3.5-plus` - `0.3990`
7. `gpt-5.4-mini` - `0.4047`
8. `glm-5` - `0.4111`
9. `kimi-for-coding` - `0.4132`
10. `qwen3-coder-plus` - `0.4218`

Chinese-side human alignment ranking:

1. `claude-opus-4-6` - `0.3359`
2. `gemini-3.1-pro` - `0.3722`
3. `mimo-v2-omni` - `0.3850`
4. `gpt-5.3-codex` - `0.4107`
5. `qwen3.5-plus` - `0.4119`
6. `gpt-5.4-mini` - `0.4176`
7. `gpt-5.4` - `0.4390`
8. `glm-5` - `0.4562`
9. `kimi-for-coding` - `0.4649`
10. `qwen3-coder-plus` - `0.4661`

Interpretation:

- `claude-opus-4-6` is the strongest human-aligned model in the current valid pool.
- `gemini-3.1-pro` and `mimo-v2-omni` are also unusually strong, especially on Chinese alignment.
- `qwen3-coder-plus` is fast and stable but relatively weak on human-distribution matching.

### 4.3 Completion quality and unresolved items

Sorted by `unresolved_count` ascending:

1. `claude-opus-4-6` - `83`
2. `kimi-for-coding` - `84`
3. `glm-5` - `107`
4. `qwen3-coder-plus` - `108`
5. `mimo-v2-omni` - `122`
6. `gemini-3.1-pro` - `126`
7. `gpt-5.3-codex` - `151`
8. `gpt-5.4-mini` - `156`
9. `qwen3.5-plus` - `158`
10. `gpt-5.4` - `163`

Interpretation:

- `claude-opus-4-6` and `kimi-for-coding` are currently the best at leaving the fewest unresolved items.
- `glm-5` and `qwen3-coder-plus` remain very practical because they combine low unresolved count with much lower latency.
- `gpt-5.4` and `gpt-5.4-mini` are not dominant on unresolved count in the latest valid runs.

### 4.4 Speed

Sorted by `wall_seconds` ascending:

1. `glm-5` - `208.27`
2. `qwen3-coder-plus` - `239.94`
3. `claude-opus-4-6` - `1066.64`
4. `gpt-5.4-mini` - `1536.17`
5. `kimi-for-coding` - `1608.89`
6. `gemini-3.1-pro` - `1676.58`
7. `qwen3.5-plus` - `1840.34`
8. `gpt-5.3-codex` - `2050.61`
9. `gpt-5.4` - `2644.58`
10. `mimo-v2-omni` - `5363.44`

Interpretation:

- The older `glm-5` and `qwen3-coder-plus` runs are still much faster than the newer high-end models.
- `claude-opus-4-6` is surprisingly competitive on speed relative to its human-alignment strength.
- `mimo-v2-omni` is excellent on quality, but its latency is the highest among the valid models in this report.

### 4.5 Quota efficiency

Quota data is only available for the monitored `20260406T121647Z` batch, so comparisons here are limited to those runs.

Sorted by `quota_delta` ascending:

1. `kimi-for-coding` - `369190`
2. `gpt-5.4-mini` - `913554`
3. `claude-opus-4-6` - `1401980`
4. `gpt-5.4` - `2328755`
5. `mimo-v2-omni` - `3376881`
6. `gpt-5.3-codex` - `6183580`
7. `gemini-3.1-pro` - `9462336`

Interpretation:

- `kimi-for-coding` is the clear quota winner among the new monitored full runs.
- `gpt-5.4-mini` is substantially cheaper than `gpt-5.4`.
- `gemini-3.1-pro` delivers excellent quality, but it is the most expensive valid monitored run by a wide margin.

## 5. Rerun variance and caution points

Several models were run more than once. The later valid reruns are not always better:

- `gpt-5.4`
  - earlier valid run: `JSD 0.0909`, `unresolved 147`
  - later valid run: `JSD 0.1325`, `unresolved 163`
  - quality and unresolved count both worsened

- `gpt-5.3-codex`
  - earlier valid run: `JSD 0.0975`, `unresolved 151`
  - later valid run: `JSD 0.1363`, `unresolved 151`
  - quality worsened while unresolved count stayed flat

- `gpt-5.4-mini`
  - earlier valid run: `JSD 0.0973`, `unresolved 152`
  - later valid run: `JSD 0.1042`, `unresolved 156`
  - slight degradation in both quality and unresolved count

- `kimi-for-coding`
  - earlier valid run: `211.41s`, `JSD 0.1020`, `unresolved 94`
  - later valid run: `1608.89s`, `JSD 0.1485`, `unresolved 84`
  - later run had better unresolved count, but was much slower and less consistent cross-lingually

- `glm-5`
  - earlier valid run was excellent
  - later `c4` rerun produced `null` core metrics and is excluded from the valid table

This means the code path is stable enough to finish, but model behavior is still affected by routing, concurrency, or service-side variability. For formal reporting, it is safer to cite either:

- the **latest valid run per model**, if we want a single current snapshot
- or the **best valid run per model**, if we want a quality frontier

## 6. Recommendations

If the goal is **best overall quality**, the strongest current candidates are:

- `gemini-3.1-pro`
- `mimo-v2-omni`
- `claude-opus-4-6`

If the goal is **fast and practical experimentation**, the strongest candidates are:

- `glm-5`
- `qwen3-coder-plus`
- `kimi-for-coding`

If the goal is **best value among the newly monitored runs**, the strongest candidates are:

- `kimi-for-coding`
- `gpt-5.4-mini`
- `claude-opus-4-6`

If the goal is **formal report writing**, the safest summary sentence is:

> Among all valid model runs, `gemini-3.1-pro` and `mimo-v2-omni` lead on cross-lingual consistency, `claude-opus-4-6` leads on human alignment and unresolved count, while `glm-5`, `qwen3-coder-plus`, and `kimi-for-coding` remain the most practical choices when speed or quota efficiency matters.
