# COMP3520_Project Reorganization Update (2026-04-12)

本文档记录本次“项目太乱”整理中，**原来哪里**改成了**现在什么**。

## 1) 顶层文件归位

| 原位置 | 新位置 | 说明 |
|---|---|---|
| `COMP3520_Proposal.pdf` | `docs/proposal/COMP3520_Proposal.pdf` | Proposal 文档集中到 `docs` |
| `update.pdf` | `docs/proposal/update.pdf` | 同上 |
| `RAW_DATA_AND_RISKS.md` | `docs/risks/RAW_DATA_AND_RISKS.md` | 风险文档集中到 `docs/risks` |
| `aggregate_all_models.py` | `tools/aggregate_all_models.py` | 一次性聚合脚本移出根目录 |
| `auto_gen_aliases.py` | `tools/auto_gen_aliases.py` | 别名生成工具移出根目录 |
| `test_prompt_hack.py` | `scripts/debug/prompt_hack.py` | 临时调试脚本归档到 debug |
| `test_stream.py` | `scripts/debug/stream_probe.py` | 临时调试脚本归档到 debug |
| `log_hard_instruction.txt` | `scripts/debug/log_hard_instruction.txt` | 调试日志归档 |
| `log_one_word.txt` | `scripts/debug/log_one_word.txt` | 调试日志归档 |

## 2) results 目录重构（按实验类型分层）

| 原位置 | 新位置 |
|---|---|
| `results/new_models_full_experiments_*.json` | `results/full_experiments/indexes/new_models_full_experiments_*.json` |
| `results/new_models_full_experiments_*.md` | `results/full_experiments/indexes/new_models_full_experiments_*.md` |
| `results/full_experiment_summary_*.md` | `results/full_experiments/summaries/full_experiment_summary_*.md` |
| `results/model_stability_probe_*.json` | `results/stability_probes/model_stability_probe_*.json` |
| `results/model_stability_probe_*.md` | `results/stability_probes/model_stability_probe_*.md` |
| `results/concurrency_sweep_*.md` | `results/concurrency_sweeps/concurrency_sweep_*.md` |
| `results/all_models_performance_summary_*.md` | `results/reports/all_models_performance_summary_*.md` |
| `results/all_valid_models_report_*.md` | `results/reports/all_valid_models_report_*.md` |
| `results/full_model_report_*.md` | `results/reports/full_model_report_*.md` |
| `results/qwen_experiment_report_*.md` | `results/reports/qwen_experiment_report_*.md` |
| `results/20260324T134951Z/` | `results/runs/20260324T134951Z/` |
| `results/runs-gemini-2.5-flash/` | `results/runs/runs-gemini-2.5-flash/` |

新增：
- `results/README.md`：说明新目录语义与命名规则。

## 3) 代码行为更新（输出路径统一）

### 3.1 Full experiments

- `scripts/run_new_models_full_experiments.py`
  - 原来：
    - index 输出到 `results/new_models_full_experiments_<batch>.{json,md}`
    - per-run summary 输出到 `results/full_experiment_summary_<root_tag>.md`
  - 现在：
    - index 输出到 `results/full_experiments/indexes/`
    - per-run summary 输出到 `results/full_experiments/summaries/`

- `scripts/run_universal_full_experiments.py`
  - 原来：summary 输出到 `results/full_experiment_summary_<root_tag>.md`
  - 现在：输出到 `results/full_experiments/summaries/`

### 3.2 Stability / Sweep

- `scripts/run_model_stability_probe.py`
  - 原来：输出到 `results/model_stability_probe_<batch>.{json,md}`
  - 现在：输出到 `results/stability_probes/`

- `scripts/run_universal_concurrency_sweep.py`
  - 原来：输出到 `results/concurrency_sweep_<tag>.md`
  - 现在：输出到 `results/concurrency_sweeps/`
  - 额外：`main()` 中显式 `mkdir` 新结果目录。

## 4) README 更新

- 更新了输出目录说明（新增按实验类型分层描述）。
- 把旧说明
  - `allow_unmapped: true` 默认
  - `round2` 只由跨语 top1 mismatch 触发
  改为当前实现口径：
  - 默认 `allow_unmapped: false`
  - `round2_trigger` 支持 `cross_lingual_top1_mismatch` / `human_top1_mismatch` / `either_top1_mismatch`
- 增加 Project Layout 小节，解释 `src/`、`tests/`、`scripts/`、`tools/`、`docs/` 的职责。

## 5) 工具脚本修复

- `tools/aggregate_all_models.py`
  - 原来：Windows 固定绝对路径 + 无参数 + 异常吞噬较多。
  - 现在：支持 `--artifacts-root` 参数、默认仓库相对路径、结构化读取。

- `tools/auto_gen_aliases.py`
  - 原来：`run_id` 写死、路径写死。
  - 现在：支持 `--run-id`、`--run-root`、`--alias-file` 参数，可复用。
