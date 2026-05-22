# Final Project Results Tables

This file collects the current model-level and item-level results for plotting and final-report writing. It uses the curated `results/runs_s50/` model runs and reports the new Round 2 rows using `provider=anthropic` only.

## Project Overview

This project studies the **cross-lingual robustness of tacit coordination in large language models** using human response distributions as a reference. The core goal is to test whether LLMs keep the same focal-point behavior when the coordination task is instructed in English versus Chinese, while the required answer language is held fixed to English.

The project has three objectives, adapted from the proposal:

- Measure **LLM-human alignment** on pure coordination items using human response distributions.
- Measure **cross-lingual stability** by comparing LLM output distributions under matched English and Chinese prompts.
- Deliver a reproducible evaluation pipeline covering data preparation, prompt generation, sampling, answer normalization, metric computation, and plotting.

The expected contribution is not a general claim that all prompting changes coordination behavior. Instead, the project provides a human-referenced diagnostic protocol for multilingual tacit coordination, plus reusable code for running the same analysis across multiple models.

## Final Report Requirement Checklist

- **Project Overview:** Use the section above and connect it to RQ1/RQ2/RQ3 below.
- **Challenges and Solutions:** Discuss translation/control confounds, open-ended answer normalization, invalid/unmapped outputs, provider/API instability, and the Round 2 interpretation issue.
- **Technical Implementation:** Use the Experimental Setup and Metric Definitions sections.
- **Results and Analysis:** Use the Quick Summary, Main Findings, model-level tables, flagged item table, and Round 2 item-level table.
- **Reflection and Learning:** Use the Reflection and Learning section near the end of this file.
- **Future Work:** Use the Future Work section near the end of this file.
- **References:** Use the References section at the end of this file.
- **GitHub Link:** Add the public repository link in the final report if available.

## How to Use This File for the Final Report

Treat this file as the report-writing source of truth for the current result set, not just as a table dump. The report should keep the three research questions separate:

- **RQ1: Human alignment.** Compare each model's English-prompt and Chinese-prompt answer distributions against the human reference distribution. Use the **Human-vs-EN** and **Human-vs-ZH** columns.
- **RQ2: Cross-lingual stability.** Compare the model's English-prompt distribution against its Chinese-prompt distribution while keeping the answer language fixed to English. Use the **EN-vs-ZH / cross-lingual** results.
- **RQ3: Exploratory Round 2.** For items whose Round 1 EN/ZH top-1 answers disagreed, test whether a lightweight second prompt reduces the mismatch. This is a candidate-item analysis, not a full second evaluation over all 15 items.

Suggested report structure:

1. **Introduction.** Motivate tacit coordination and instruction-language sensitivity. State that the protocol keeps answer language fixed to isolate instruction-language effects.
2. **Research Questions.** Present RQ1 human alignment, RQ2 cross-lingual stability, and RQ3 exploratory re-coordination.
3. **Methods.** Describe data source, prompt design, sampling, normalization, and metrics.
4. **Results.** Report Human-vs-EN/ZH alignment first, then EN-vs-ZH cross-lingual stability, then Round 2 candidate-item outcomes.
5. **Discussion and Limitations.** Explain what the results imply and what the design cannot claim.

## Experimental Setup for Methods

- **Human reference data.** The benchmark uses the public OSF data from Perez-Zapata et al., *Three International Studies on Pure Coordination Games*. The current finalized runs use the `study2_british_within` panel.
- **Items.** The panel contains **15 coordination items**. Each item has an English prompt and a curated Chinese prompt translation.
- **Human distribution.** Human answers are aggregated into empirical item-level distributions over canonical answers.
- **Prompt manipulation.** Models answer the same coordination items under English and Chinese instructions, while the required answer language is fixed to **English**.
- **Round 1 sampling.** The curated `runs_s50` results use **50 model samples per item per prompt language**, giving 15 × 2 × 50 = 1500 Round 1 generations for a complete model run.
- **Round 2 sampling.** Round 2 is only run on candidate items flagged by Round 1 cross-lingual top-1 mismatch. Current Round 2 rows use **10 samples per item per prompt language**.
- **Normalization.** Model outputs are mapped through `data/aliases/default_aliases.csv` and canonical answer keys. Invalid or unmapped responses are excluded from metric distributions after the recent cleanup.
- **Scope of Round 2.** The new Round 2 rows in this document use `provider=anthropic` / `claude-opus-4-6` as the re-coordination model. They should be described as an exploratory re-coordination sanity check, not as proof that the original baseline model self-corrects.

## Metric Definitions

- **JSD (Jensen-Shannon Divergence):** distributional divergence; lower means the two answer distributions are more similar.
- **TVD (Total Variation Distance):** absolute distributional distance; lower is better.
- **Top1 match:** whether the most probable answer in two distributions is the same. For cross-lingual rows this compares EN vs ZH; for human-alignment rows this compares model vs human.
- **Flip rate:** `1 - top1_match`. This is meaningful for cross-lingual EN/ZH comparisons, not for human-alignment rows.
- **Spearman:** rank correlation between answer distributions where available; higher means more similar answer ordering.

## Quick Summary

- Number of baseline model runs: **17**
- Runs with comparable new Round 2 anthropic rows: **14**
- R2 improved cross-lingual JSD: **11/14**
- R2 worsened cross-lingual JSD: **3/14**
- Mean Delta JSD (R2 - R1): **-0.0535**
- Mean Delta Top1 match (R2 - R1): **0.1476**

Important interpretation caveat: the Round 2 deltas above compare each model's full Round 1 aggregate against the available Round 2 candidate subset. They are useful for a high-level sanity check, but the cleanest Round 2 claim should be made on candidate items only: "among items flagged for Round 1 EN/ZH top-1 mismatch, the second prompt usually restores top-1 agreement."

## Main Findings to Carry Into the Report

- **Cross-lingual stability varies strongly across models.** `mimo-v2-pro` is the most stable current Round 1 run, with cross-lingual JSD **0.0200** and Top1 match **1.0000**. `mimo-v2-omni` is also strong, with JSD **0.0371** and Top1 match **0.9333**.
- **Human alignment and cross-lingual stability are different properties.** A model can be stable across English and Chinese prompts while still differing from the human distribution, so the report should not merge Human-vs-EN/ZH with EN-vs-ZH.
- **Some models show clear instruction-language drift.** Higher cross-lingual JSD and lower Top1 match appear for several Qwen/GLM/GPT variants, especially on the flagged item subset.
- **Round 2 is promising but exploratory.** Most available Round 2 candidate rows reach Top1 match **1.0000**, but Round 2 covers only flagged items and uses 10 samples per language.

## Recommended Figures

- Use a **Round 1 cross-lingual JSD bar chart** for RQ2. Lower bars are better.
- Use a **Round 1 cross-lingual Top1 match bar chart** for RQ2 focal-point stability.
- Use a **Human-vs-EN / Human-vs-ZH grouped chart or table** for RQ1. Keep these separate from cross-lingual EN-vs-ZH metrics.
- Use a **candidate-only Round 1 vs Round 2 before/after plot** for RQ3, ideally restricted to the same flagged item set.
- Do **not** use the older combined "Human Alignment: Distribution (JSD) vs. Focal Point (Top-1 Match)" figure if it shows `mimo-v2-pro` human Top1 around `0.020`; that figure appears to have a plotting/metric-column mapping error.

## Plot-Ready CSV Files

- `results/final_project_tables/model_level_cross_lingual_r1_r2.csv`
- `results/final_project_tables/model_level_human_alignment_r1.csv`
- `results/final_project_tables/item_level_cross_lingual_r1.csv`
- `results/final_project_tables/item_level_cross_lingual_r2_anthropic_only.csv`

## Model-Level Cross-Lingual Results: Round 1 vs New Round 2

| Model | R2 candidates | R1 JSD | R2 JSD | Delta JSD | R1 Top1 match | R2 Top1 match | Delta Top1 | R1 Flip rate | R2 Flip rate | Delta Flip | R1 item n | R2 item n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K2.6-code-preview | 1 | 0.0703 | 0.0000 | -0.0703 | 0.9333 | 1.0000 | 0.0667 | 0.0667 | 0.0000 | -0.0667 | 15 | 1.0 |
| MiniMax-M2.7-highspeed | 2 | 0.0493 | 0.1182 | 0.0689 | 0.8667 | 1.0000 | 0.1333 | 0.1333 | 0.0000 | -0.1333 | 15 | 2.0 |
| MiniMax-M2.7 | 1 | 0.0449 | 0.0144 | -0.0305 | 0.9333 | 1.0000 | 0.0667 | 0.0667 | 0.0000 | -0.0667 | 15 | 1.0 |
| deepseek-v3.2 | 1 | 0.0918 | — | — | 0.9333 | — | — | 0.0667 | — | — | 15 | — |
| deepseek-v3 | 1 | 0.0899 | — | — | 0.9333 | — | — | 0.0667 | — | — | 15 | — |
| gemini-2.5-flash | 3 | 0.0845 | 0.0259 | -0.0586 | 0.8000 | 1.0000 | 0.2000 | 0.2000 | 0.0000 | -0.2000 | 15 | 2.0 |
| glm-4-airx | 3 | 0.1379 | 0.0259 | -0.1120 | 0.8000 | 1.0000 | 0.2000 | 0.2000 | 0.0000 | -0.2000 | 15 | 2.0 |
| glm-4-flashx-250414 | 3 | 0.2135 | 0.0846 | -0.1289 | 0.8000 | 1.0000 | 0.2000 | 0.2000 | 0.0000 | -0.2000 | 15 | 2.0 |
| gpt-4o-mini | 2 | 0.0642 | 0.0000 | -0.0642 | 0.8667 | 1.0000 | 0.1333 | 0.1333 | 0.0000 | -0.1333 | 15 | 1.0 |
| gpt-5.4-mini | 3 | 0.1124 | 0.0000 | -0.1124 | 0.8000 | 1.0000 | 0.2000 | 0.2000 | 0.0000 | -0.2000 | 15 | 2.0 |
| gpt-5.4 (main) | 3 | 0.1889 | 0.0737 | -0.1152 | 0.8000 | 1.0000 | 0.2000 | 0.2000 | 0.0000 | -0.2000 | 15 | 3.0 |
| gpt-5.4 (round2-upload) | 1 | 0.0652 | 0.0000 | -0.0652 | 0.9333 | 1.0000 | 0.0667 | 0.0667 | 0.0000 | -0.0667 | 15 | 1.0 |
| kimi-for-coding | 2 | 0.0863 | 0.1182 | 0.0319 | 0.8667 | 1.0000 | 0.1333 | 0.1333 | 0.0000 | -0.1333 | 15 | 2.0 |
| mimo-v2-omni | 1 | 0.0371 | 0.0144 | -0.0227 | 0.9333 | 1.0000 | 0.0667 | 0.0667 | 0.0000 | -0.0667 | 15 | 1.0 |
| mimo-v2-pro | 0 | 0.0200 | — | — | 1.0000 | — | — | 0.0000 | — | — | 15 | — |
| qwen3.5-plus | 4 | 0.1810 | 0.0533 | -0.1277 | 0.7333 | 1.0000 | 0.2667 | 0.2667 | 0.0000 | -0.2667 | 15 | 3.0 |
| qwen3.6-plus | 2 | 0.0596 | 0.1182 | 0.0586 | 0.8667 | 1.0000 | 0.1333 | 0.1333 | 0.0000 | -0.1333 | 15 | 2.0 |

## Model-Level Human Alignment: Round 1 (Human-vs-EN / Human-vs-ZH)

| Model | Human-vs-EN JSD | Human-vs-ZH JSD | Human-vs-EN Top1 match | Human-vs-ZH Top1 match | Human-vs-EN TVD | Human-vs-ZH TVD | Human-vs-EN Spearman | Human-vs-ZH Spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K2.6-code-preview | 0.3575 | 0.3766 | 0.7333 | 0.8000 | 0.4927 | 0.5153 | 0.5049 | 0.4855 |
| MiniMax-M2.7-highspeed | 0.3530 | 0.3442 | 0.8667 | 0.7333 | 0.4947 | 0.5047 | 0.5098 | 0.5103 |
| MiniMax-M2.7 | 0.3603 | 0.3284 | 0.8000 | 0.7333 | 0.5027 | 0.4846 | 0.5242 | 0.5100 |
| deepseek-v3.2 | 0.3534 | 0.3035 | 0.8000 | 0.8000 | 0.5020 | 0.4553 | 0.5083 | 0.5470 |
| deepseek-v3 | 0.3518 | 0.3019 | 0.8000 | 0.8000 | 0.5020 | 0.4520 | 0.5083 | 0.5470 |
| gemini-2.5-flash | 0.2615 | 0.2602 | 0.8000 | 0.7333 | 0.4201 | 0.4132 | 0.5494 | 0.5727 |
| glm-4-airx | 0.3419 | 0.3280 | 0.7333 | 0.8000 | 0.4747 | 0.4733 | 0.4949 | 0.5001 |
| glm-4-flashx-250414 | 0.4031 | 0.3904 | 0.7333 | 0.7333 | 0.5347 | 0.5200 | 0.3858 | 0.4128 |
| gpt-4o-mini | 0.3449 | 0.3561 | 0.7333 | 0.8000 | 0.4900 | 0.5000 | 0.5245 | 0.5137 |
| gpt-5.4-mini | 0.3035 | 0.2795 | 0.8000 | 0.7333 | 0.4520 | 0.4247 | 0.5338 | 0.5448 |
| gpt-5.4 (main) | 0.3858 | 0.3138 | 0.7333 | 0.9333 | 0.5227 | 0.4620 | 0.4564 | 0.5289 |
| gpt-5.4 (round2-upload) | 0.3421 | 0.2942 | 0.8000 | 0.8000 | 0.4827 | 0.4513 | 0.5183 | 0.5524 |
| kimi-for-coding | 0.3573 | 0.3305 | 0.8667 | 0.7333 | 0.5013 | 0.4873 | 0.5062 | 0.5306 |
| mimo-v2-omni | 0.3405 | 0.3091 | 0.8000 | 0.8667 | 0.5007 | 0.4587 | 0.5308 | 0.4889 |
| mimo-v2-pro | 0.3439 | 0.3157 | 0.8667 | 0.8667 | 0.4947 | 0.4767 | 0.4831 | 0.5465 |
| qwen3.5-plus | 0.3141 | 0.3313 | 0.8667 | 0.7333 | 0.4687 | 0.4893 | 0.5393 | 0.5222 |
| qwen3.6-plus | 0.3599 | 0.3282 | 0.8667 | 0.7333 | 0.4993 | 0.4860 | 0.5113 | 0.4984 |

## Round 1 Flagged Items (EN/ZH Top-1 Mismatch)

| Model | Item | Item # | R1 JSD | R1 Top1 match | R1 Flip | EN succ | ZH succ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| K2.6-code-preview | study2_item_04 | 4 | 0.5150 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| MiniMax-M2.7-highspeed | study2_item_09 | 9 | 0.0575 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| MiniMax-M2.7-highspeed | study2_item_11 | 11 | 0.4457 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| MiniMax-M2.7 | study2_item_11 | 11 | 0.3370 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| deepseek-v3.2 | study2_item_03 | 3 | 0.8164 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| deepseek-v3 | study2_item_03 | 3 | 0.7293 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gemini-2.5-flash | study2_item_03 | 3 | 0.1361 | 0.0000 | 1.0000 | 50.0 | 41.0 |
| gemini-2.5-flash | study2_item_11 | 11 | 0.4977 | 0.0000 | 1.0000 | 49.0 | 48.0 |
| gemini-2.5-flash | study2_item_12 | 12 | 0.2276 | 0.0000 | 1.0000 | 48.0 | 50.0 |
| glm-4-airx | study2_item_03 | 3 | 0.4891 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| glm-4-airx | study2_item_04 | 4 | 0.7262 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| glm-4-airx | study2_item_05 | 5 | 0.1189 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| glm-4-flashx-250414 | study2_item_02 | 2 | 0.4960 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| glm-4-flashx-250414 | study2_item_03 | 3 | 0.3977 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| glm-4-flashx-250414 | study2_item_11 | 11 | 0.9290 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-4o-mini | study2_item_02 | 2 | 0.4142 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-4o-mini | study2_item_03 | 3 | 0.4071 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-5.4-mini | study2_item_02 | 2 | 0.3438 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-5.4-mini | study2_item_03 | 3 | 0.6273 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-5.4-mini | study2_item_04 | 4 | 0.3761 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-5.4 (main) | study2_item_04 | 4 | 1.0000 | 0.0000 | 1.0000 | 80.0 | 50.0 |
| gpt-5.4 (main) | study2_item_08 | 8 | 0.9290 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-5.4 (main) | study2_item_11 | 11 | 0.8337 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| gpt-5.4 (round2-upload) | study2_item_04 | 4 | 0.7152 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| kimi-for-coding | study2_item_09 | 9 | 0.2532 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| kimi-for-coding | study2_item_11 | 11 | 0.4858 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| mimo-v2-omni | study2_item_11 | 11 | 0.2020 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| qwen3.5-plus | study2_item_03 | 3 | 0.4714 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| qwen3.5-plus | study2_item_04 | 4 | 1.0000 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| qwen3.5-plus | study2_item_09 | 9 | 0.2652 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| qwen3.5-plus | study2_item_11 | 11 | 0.6365 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| qwen3.6-plus | study2_item_09 | 9 | 0.1094 | 0.0000 | 1.0000 | 50.0 | 50.0 |
| qwen3.6-plus | study2_item_11 | 11 | 0.2958 | 0.0000 | 1.0000 | 50.0 | 50.0 |

## New Round 2 Item-Level Cross-Lingual Results (Anthropic Only)

| Baseline model | R2 model | Item | Item # | R2 JSD | R2 Top1 match | R2 Flip | EN succ | ZH succ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K2.6-code-preview | claude-opus-4-6 | study2_item_04 | 4 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| MiniMax-M2.7-highspeed | claude-opus-4-6 | study2_item_09 | 9 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| MiniMax-M2.7-highspeed | claude-opus-4-6 | study2_item_11 | 11 | 0.2365 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| MiniMax-M2.7 | claude-opus-4-6 | study2_item_11 | 11 | 0.0144 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gemini-2.5-flash | claude-opus-4-6 | study2_item_11 | 11 | 0.0519 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gemini-2.5-flash | claude-opus-4-6 | study2_item_12 | 12 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| glm-4-airx | claude-opus-4-6 | study2_item_04 | 4 | 0.0519 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| glm-4-airx | claude-opus-4-6 | study2_item_05 | 5 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| glm-4-flashx-250414 | claude-opus-4-6 | study2_item_02 | 2 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| glm-4-flashx-250414 | claude-opus-4-6 | study2_item_11 | 11 | 0.1692 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gpt-4o-mini | claude-opus-4-6 | study2_item_02 | 2 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gpt-5.4-mini | claude-opus-4-6 | study2_item_02 | 2 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gpt-5.4-mini | claude-opus-4-6 | study2_item_04 | 4 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gpt-5.4 (main) | claude-opus-4-6 | study2_item_04 | 4 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gpt-5.4 (main) | claude-opus-4-6 | study2_item_08 | 8 | 0.0519 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gpt-5.4 (main) | claude-opus-4-6 | study2_item_11 | 11 | 0.1692 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| gpt-5.4 (round2-upload) | claude-opus-4-6 | study2_item_04 | 4 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| kimi-for-coding | claude-opus-4-6 | study2_item_09 | 9 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| kimi-for-coding | claude-opus-4-6 | study2_item_11 | 11 | 0.2365 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| mimo-v2-omni | claude-opus-4-6 | study2_item_11 | 11 | 0.0144 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| qwen3.5-plus | claude-opus-4-6 | study2_item_04 | 4 | 0.0519 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| qwen3.5-plus | claude-opus-4-6 | study2_item_09 | 9 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| qwen3.5-plus | claude-opus-4-6 | study2_item_11 | 11 | 0.1080 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| qwen3.6-plus | claude-opus-4-6 | study2_item_09 | 9 | 0.0000 | 1.0000 | 0.0000 | 10.0 | 10.0 |
| qwen3.6-plus | claude-opus-4-6 | study2_item_11 | 11 | 0.2365 | 1.0000 | 0.0000 | 10.0 | 10.0 |

## Notes for Plotting

- Use `Delta JSD = R2 JSD - R1 JSD`; negative values indicate lower EN/ZH divergence in Round 2.
- Use `Delta Top1`; positive values indicate more EN/ZH top-1 agreement in Round 2.
- Round 2 is only defined for flagged items, so `R2 item n` is smaller than the Round 1 item count.
- Empty cells marked `—` mean that no comparable new Round 2 row was available for that run.

## Reflection and Learning

The main lesson from this project is that evaluating open-ended LLM behavior is as much a data-engineering problem as a modeling problem. Small choices in answer normalization, alias coverage, and metric grouping can change the interpretation of the results. During the project, we had to separate three different objects that are easy to confuse: raw model generations, normalized canonical answers, and derived summary metrics.

We also learned that human alignment and cross-lingual stability should not be collapsed into one score. A model can be internally stable across English and Chinese prompts while still not matching the human distribution closely, and a model can align with humans under one prompt language while drifting under another. This distinction shaped the final report structure: Human-vs-EN/ZH answers RQ1, while EN-vs-ZH answers RQ2.

Another important lesson is that exploratory follow-up experiments need careful framing. Round 2 is useful for asking whether mismatched items are prompt-sensitive, but the current Round 2 runs use a separate Anthropic model and only cover flagged candidate items. Therefore, the final report should describe Round 2 as a limited re-coordination sanity check rather than as definitive evidence of original-model self-correction.

Finally, the project highlighted the importance of reproducibility checks. We repeatedly traced questionable values from plots back to `summary_metrics.json`, `item_metrics.csv`, `normalized_outputs.csv`, and `raw_generations.jsonl`. This helped distinguish real metric values, such as `mimo-v2-pro`'s cross-lingual JSD of about `0.0200`, from plotting mistakes in older figures.

## Future Work

- Extend beyond the `study2_british_within` panel to more countries, languages, and coordination settings.
- Add candidate-only Round 1 vs Round 2 paired tables and plots so Round 2 effects are reported on exactly matched item sets.
- Run Round 2 with each original model, not only a shared Anthropic rerun model, to test true self-correction.
- Increase Round 2 sample size beyond 10 samples per language for more stable distribution estimates.
- Add stronger regression tests for alias coverage, prompt translation coverage, and figure-generation scripts.
- Compare instruction-language effects against answer-language effects by adding conditions where the model answers in Chinese as well as English.

## Limitations to State Explicitly

- The current finalized analysis uses one human panel, `study2_british_within`, so the results should not be framed as a broad cross-cultural claim.
- Chinese is the instruction language, but the answer language is fixed to English. This design isolates instruction-language effects, but it does not separate language, culture, and translation mechanisms causally.
- Alias normalization affects all distributional metrics. The current tables use the cleaned alias table and exclude invalid/unmapped rows, but the report should acknowledge normalization as a source of measurement uncertainty.
- Round 2 is candidate-only and low-sample relative to Round 1. It should be framed as exploratory evidence that some mismatches are prompt-sensitive, not as a definitive intervention study.
- The Round 2 rows here use Anthropic only; do not claim every original model performed its own second-round self-correction.

## References

- Aharon, I., La Malfa, E., Wooldridge, M., & Kraus, S. (2026). *Tacit Coordination of Large Language Models*. arXiv:2601.22184. https://arxiv.org/abs/2601.22184
- Perez-Zapata, D., Isoni, A., Zawidzki, T., & Apperly, I. (2026). *Three International Studies on Pure Coordination Games: Adaptable Solutions When Intuitions are Presumed to Vary*. Journal of Experimental Psychology: General, 155(3), 760-775. https://doi.org/10.1037/xge0001876
