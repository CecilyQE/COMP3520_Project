# All Models Performance Summary 20260405

## 口径说明

这份汇总按“模型”聚合，保留截至 `2026-04-05` 我们手头上**最有解释力**的一次运行结果。  
如果同一个模型有多次尝试，我优先采用：

1. 已生成完整 `summary.json` 的最新可用结果
2. 其次是能拿到 `raw_generations.jsonl` 的半成品结果
3. 最后才是只有 `run_manifest.json` 的启动失败结果

注意两点：

- `wall_seconds` 受 `concurrency` 影响很大，只能看量级，不能当作绝对公平的速度比较。
- `round2_candidate_count` 不是 `unresolved_count`，前者只是“进入二轮处理的候选数”，后者是最终仍未解决的条目数。

## 一、可比较的完整结果

这些模型都成功产出了完整 summary，可以直接横向比较。

| Model | Concurrency | Raw | Round2 | Unresolved | Wall(s) | Cross JSD R1 | Cross Top1 R1 | Human EN JSD | Human ZH JSD | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `gpt-5.4` | 1 | 940 | 2 | 147 | 6925.88 | 0.0909 | 0.8667 | 0.3833 | 0.4046 | 质量最强，R1 一致性和人类对齐都最好 |
| `gpt-5.3-codex` | 1 | 940 | 2 | 151 | 6338.62 | 0.0975 | 0.8667 | 0.4022 | 0.4033 | 与 `gpt-5.4` 很接近，但整体略弱 |
| `kimi-for-coding` | 10 | 960 | 3 | 94 | 211.41 | 0.1020 | 0.8000 | 0.4016 | 0.4543 | 完整结果里遗留问题最少，速度也很快 |
| `gpt-5.4-mini` | 6 | 940 | 2 | 152 | 1024.47 | 0.0973 | 0.8667 | 0.3943 | 0.4055 | 旧批次里质量最强，R1 很稳 |
| `qwen3.5-plus` | 4 | 940 | 2 | 158 | 1840.34 | 0.1025 | 0.8667 | 0.3990 | 0.4119 | 质量不错，但运行代价偏高 |
| `qwen3-coder-plus` | 6 | 940 | 2 | 108 | 239.94 | 0.1134 | 0.8667 | 0.4218 | 0.4661 | 低成本、稳定、性价比高 |
| `glm-5` | 6 | 960 | 3 | 107 | 208.27 | 0.1287 | 0.8000 | 0.4111 | 0.4562 | 最快的稳定完整结果，收尾也干净 |

### 这组完整结果怎么排

- `Cross JSD R1` 最好的是 `gpt-5.4`，说明中英文提示下的一致性最强。
- `Human EN / ZH JSD` 最好也是 `gpt-5.4`，说明它最贴近人类分布。
- `Unresolved` 最低的是 `kimi-for-coding`，其次是 `glm-5` 和 `qwen3-coder-plus`。
- 如果只看“质量优先”，`gpt-5.4` 第一，`gpt-5.4-mini` 和 `gpt-5.3-codex` 紧随其后。
- 如果只看“速度优先”，`glm-5` 和 `kimi-for-coding` 最好。
- 如果只看“低成本平衡”，`qwen3-coder-plus` 是最稳妥的选择。

### Round 2 的整体表现

这一轮最重要的现象是：`Round 2` 没有稳定修复 `Round 1`，反而在多数模型上把一致性拉差了。

典型例子：

- `gpt-5.4`: `0.0909 -> 0.3355`
- `gpt-5.3-codex`: `0.0975 -> 0.5558`
- `qwen3-coder-plus`: `0.1134 -> 0.6653`
- `qwen3.5-plus`: `0.1025 -> 0.6326`
- `gpt-5.4-mini`: `0.0973 -> 0.2840`

结论很直接：

- `Round 1` 比 `Round 2` 更有信息量。
- 当前二轮修复策略不是一个稳定的“纠错器”，更像是一个会引入扰动的补救环节。
- 后面写报告时，应该把 `Round 1` 当主结果，`Round 2` 只能当辅助观察。

## 二、完成但结果不可用

这些模型形式上跑到了 `completed`，但 summary 里已经能看出它们没有产出可分析结果。

| Model | Concurrency | Raw | Provider Errors | Empty | Truncation | Unresolved | Wall(s) | Status | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `claude-sonnet-4-6` | 1 | 900 | 45 | 45 | 11 | 900 | 24860.03 | completed | 全部指标基本失效，`complete_cell_count=0` |
| `MiniMax-M2.7` | 1 | 900 | 166 | 166 | 9 | 900 | 37821.01 | completed | 错误率太高，结果不可用 |

这两条可以理解为：

- `claude-sonnet-4-6` 不是“没跑完”，而是“跑完了但质量完全不行”。
- `MiniMax-M2.7` 比 `claude-sonnet-4-6` 更糟，空响应和 provider error 都更高。
- 这类结果不适合纳入最终性能排序，只适合写进“失败模型说明”。

## 三、早停 / 半成品结果

这些模型没有形成可比的完整 summary，但它们的运行状态仍然有分析价值。

| Model | Status | Raw | Provider Errors | Empty | Truncation | Stop Reason | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `gpt-5.3-codex-spark` | stopped_early | 84 | 17 | 17 | 0 | `provider_error_ratio_gt_20pct` | 前期还能出正常短答，后来错误率超过阈值 |
| `claude-opus-4-6` | stopped_early | 1 | 1 | 1 | 0 | `provider_error_ratio_gt_20pct` | 基本一开始就不稳定 |
| `gemini-3.1-pro` | stopped_early | 1 | 1 | 1 | 0 | `provider_error_ratio_gt_20pct` | 同样是启动后立即失败 |
| `MiniMax-M2.7-highspeed` | partial | 126 | 0 | 31 | 0 | summary missing | 有原始输出，但没生成 summary，像是后处理或收尾阶段断掉了 |
| `step-3.5-flash` | failed_start | 0 | 0 | 0 | 0 | no raw generations | 目录里只有 `run_manifest.json`，没有任何有效原始输出 |

### 这组早停结果说明了什么

- `gpt-5.3-codex-spark` 是“先能跑、后面坏掉”的典型：有 84 条 raw，但错误率冲到 20% 以上后被及时截停。
- `claude-opus-4-6` 和 `gemini-3.1-pro` 是“起步就不稳”，只各拿到 1 条 raw 就失败。
- `MiniMax-M2.7-highspeed` 最值得注意：它有 126 条 raw，而且前面看起来是干净的短答，但 summary 没有生成，说明问题更像在收尾/分析阶段，而不是生成内容本身。
- `step-3.5-flash` 最差，连 raw 都没有，基本算启动失败。

## 四、按维度总结

### 1. 质量最强

`gpt-5.4`

- `Cross JSD R1 = 0.0909`
- `Human EN JSD = 0.3833`
- `Human ZH JSD = 0.4046`
- `Unresolved = 147`

它是这批结果里最强的质量基线，但代价是 `concurrency=1` 下墙钟时间最长之一。

### 2. 最稳的低成本选择

`qwen3-coder-plus`

- `Cross JSD R1 = 0.1134`
- `Unresolved = 108`
- `Wall = 239.94s`

它的质量不是最强，但速度、稳定性和可解释性都很好，属于很实用的主力模型。

### 3. 速度最优

`glm-5`

- `Wall = 208.27s`
- `Unresolved = 107`

它是完整结果里最快的，而且收尾也干净，适合速度优先的场景。

### 4. 最少遗留问题

`kimi-for-coding`

- `Unresolved = 94`
- `Wall = 211.41s`

这条非常值得保留，尤其是在你想要“结果完整度”高于“绝对质量最高”时。

### 5. 需要谨慎使用

`qwen3.5-plus`

- 质量不差
- 但 `Wall = 1840.34s`
- `Unresolved = 158`

它属于“不是不能用，但性价比不占优”的模型。

### 6. 直接排除

- `claude-sonnet-4-6`
- `MiniMax-M2.7`
- `step-3.5-flash`

这些模型要么结果失效，要么起步失败，不建议放进最终比较。

## 五、最终建议

如果你想在报告里只保留少量主模型，我建议这样写：

1. `gpt-5.4` 作为质量上限。
2. `qwen3-coder-plus` 作为低成本主力。
3. `glm-5` 作为速度优先样本。
4. `kimi-for-coding` 作为“遗留问题最少”的补充对照。
5. `gpt-5.4-mini` 作为旧批次的高质量对照。

如果你想把“失败模型”也写进实验说明，可以明确区分：

- `completed but invalid`
- `stopped early`
- `partial / no summary`
- `failed start`

这样读者会很容易理解：  
不是所有模型都同等“可比”，有些只是启动成功，有些只是跑到了结果文件，但真正能做性能比较的只有前面那几条完整结果。

