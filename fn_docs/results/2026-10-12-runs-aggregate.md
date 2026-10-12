# 运行结果数据快照（2026-10-12 拉取）

> 拉取口径：requirements.md 外部依赖节登记的"结果数据源 = fn_work/runs/ 产物"。
> 本快照由 fn-analyze 数据拉取子代理生成；每个数字标注来源文件。

## 1. Run 清单（实际 3 个 run 目录，非任务预期 6 个）

| run_id | mtime | 文件清单 | 性质 | 来源 |
|---|---|---|---|---|
| eval-1791683161-s42 | 2026-10-11 09:46 (csv) / 14:47 (report) | ab_table.csv（1 数据行）、report.md | 假 LLM E2E（B4 收档对照，b4-realrun） | `fn_work/runs/eval-1791683161-s42/` |
| eval-1791773312-s42 | 2026-10-12 10:57 (csv) / 11:08 (report) | ab_table.csv（4 数据行）、report.md | 真 27B R5 双跑·第 1 轮 | `fn_work/runs/eval-1791773312-s42/` |
| eval-1791773879-s42 | 2026-10-12 11:07 (csv) / 11:08 (report) | ab_table.csv（4 数据行）、report.md | 真 27B R5 双跑·第 2 轮 | `fn_work/runs/eval-1791773879-s42/` |

另有非 run 目录件：`fn_work/runs/submit-dryrun-receipt-arc-prize-2026-arc-agi-3.jsonl`（1 行提交 dry-run 回执，status=dry_run, verified=true，ts 2026-10-11T14:42:49+08:00）。

runs/ 下无其他 run 目录——"6 个 run 目录"的说法与实际不符（本快照如实记 3 个）。

## 2. 每 run 配置行（ab_table.csv 原文数字）

### 2.1 eval-1791683161-s42（假 LLM E2E 对照）

| name | policy | episodes | wins | success_rate | avg_steps | duration_s | prompt_tokens | completion_tokens | d_success_rate | d_avg_steps |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | baseline | 2 | 0 | 0.0 | 75.0 | 0.683 | 1400 | 600 | 0.0 | 0.0 |

来源：`fn_work/runs/eval-1791683161-s42/ab_table.csv`。
假 LLM 指认依据：duration 0.683s 跑完 2 局×75 步（真 27B 单步约 1.8s，见 §4），且 token 为小额整数（1400/600），非服务端实测用量。

### 2.2 eval-1791773312-s42（真 27B 双跑·第 1 轮）

| name | policy | episodes | wins | success_rate | avg_steps | duration_s | prompt_tokens | completion_tokens | d_success_rate | d_avg_steps |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | baseline | 2 | 0 | 0.0 | 75.0 | 128.168 | 397312 | 1344 | 0.0 | 0.0 |
| plus_curriculum | curriculum | 2 | 0 | 0.0 | 75.0 | 126.024 | 384311 | 1250 | 0.0 | 0.0 |
| plus_regularized | regularized | 2 | 0 | 0.0 | 75.0 | 136.857 | 327709 | 1350 | 0.0 | 0.0 |
| full | curriculum+regularized | 2 | 0 | 0.0 | 75.0 | 134.607 | 384311 | 1250 | 0.0 | 0.0 |

来源：`fn_work/runs/eval-1791773312-s42/ab_table.csv`。

### 2.3 eval-1791773879-s42（真 27B 双跑·第 2 轮）

| name | policy | episodes | wins | success_rate | avg_steps | duration_s | prompt_tokens | completion_tokens | d_success_rate | d_avg_steps |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | baseline | 2 | 0 | 0.0 | 75.0 | 140.638 | 397312 | 1344 | 0.0 | 0.0 |
| plus_curriculum | curriculum | 2 | 0 | 0.0 | 75.0 | 141.035 | 384311 | 1250 | 0.0 | 0.0 |
| plus_regularized | regularized | 2 | 0 | 0.0 | 75.0 | 145.461 | 327709 | 1350 | 0.0 | 0.0 |
| full | curriculum+regularized | 2 | 0 | 0.0 | 75.0 | 139.234 | 384311 | 1250 | 0.0 | 0.0 |

来源：`fn_work/runs/eval-1791773879-s42/ab_table.csv`。

## 3. 27B 双跑逐列一致性判定（确定性证据）

对比 eval-1791773312-s42 vs eval-1791773879-s42（同 seed s42、同 4 配置）：

| 配置 | 列 | 第 1 轮 | 第 2 轮 | 一致 |
|---|---|---|---|---|
| baseline | wins/success_rate | 0 / 0.0 | 0 / 0.0 | 一致 |
| baseline | avg_steps | 75.0 | 75.0 | 一致 |
| baseline | prompt_tokens / completion_tokens | 397312 / 1344 | 397312 / 1344 | 一致 |
| baseline | duration_s | 128.168 | 140.638 | **不一致（墙钟）** |
| plus_curriculum | wins/success_rate/avg_steps | 0 / 0.0 / 75.0 | 0 / 0.0 / 75.0 | 一致 |
| plus_curriculum | prompt / completion tokens | 384311 / 1250 | 384311 / 1250 | 一致 |
| plus_curriculum | duration_s | 126.024 | 141.035 | 不一致（墙钟） |
| plus_regularized | wins/success_rate/avg_steps | 0 / 0.0 / 75.0 | 0 / 0.0 / 75.0 | 一致 |
| plus_regularized | prompt / completion tokens | 327709 / 1350 | 327709 / 1350 | 一致 |
| plus_regularized | duration_s | 136.857 | 145.461 | 不一致（墙钟） |
| full | wins/success_rate/avg_steps | 0 / 0.0 / 75.0 | 0 / 0.0 / 75.0 | 一致 |
| full | prompt / completion tokens | 384311 / 1250 | 384311 / 1250 | 一致 |
| full | duration_s | 134.607 | 139.234 | 不一致（墙钟） |

结论：**全部质量列（wins/steps/token）逐项一致，仅 duration_s（墙钟耗时）随机器波动**——temperature=0 贪心解码确定性成立（与 batches.md 2026-10-12 D1 销账记载相符）。

跨配置附带观察（两轮同型，来源同上两 csv）：
- plus_curriculum 与 full 的 prompt/completion tokens 完全相同（384311/1250，两轮均然）——课程编排下经验正则层未改变实际 LLM 调用序列（提示内容等效），组件叠加未产生行为差异；
- 四配置 avg_steps 全部 75.0——所有局全部打满步数上限（0 胜的机理即此），策略间无行为分化；
- baseline 比 plus_curriculum/full 多 13001 prompt tokens（397312 vs 384311）——包装层反而压缩了提示（或课程选源更短）。

## 4. 27B 单局冒烟日志分析（/tmp/d1_smoke_logs/20261012.jsonl）

文件在，21 行（20 条 step 事件 + 1 条 episode_end），run_id=d1-smoke-27b，game vc33-5430563c，真 27B（gemma-3-27b-it-int4-awq @ tower 3090Ti，据 fn_docs/implementation/batches.md 2026-10-12 D1 销账行）。逐项数字：

### 4.1 动作分布

| 动作 | 次数 | 占比 |
|---|---|---|
| ACTION6 (x=10, y=10) | 20/20 | 100% |

**坐标完全不多样：恒 (10,10)。**

### 4.2 回退触发痕迹判定

- 策略层回退常量是 **(32,32)**（`fn_work/src/make_baseline_policy/make_baseline_policy.py` L53：`return {"name": "ACTION6", "x": 32, "y": 32}`）——日志全程 (10,10)，**不是策略回退**；
- LLM 层回退（llm_complete SAFE_FALLBACK）返回时 token 记 0（`fn_work/src/shared/llm_complete.py` L106-111）——episode_end 汇总 prompt=52964/completion=180/calls=20，**每次调用 token 非零，无一次 LLM 层回退**；
- 结论：20 步动作全部是**解析成功的真实模型输出**。恒 (10,10) 的成因是温度 0 贪心 + 观测不变（obs_summary 全程 NOT_FINISHED / levels_completed=0 / available_actions=[6] / frame 64x64 完全相同）→ 同提示同解码 → 同输出。属"模型输出可解析但退化重复"，不属"输出未被解析"。

### 4.3 每步延迟分布（latency_ms，20 步）

| min | median | max | mean |
|---|---|---|---|
| 1786 | 1817.0 | 2599 | 1873.5 |

首步 2599ms（冷启动），其余 1786-1860ms 窄带。来源：20261012.jsonl 各 step 事件 payload.latency_ms。

### 4.4 局终与用量

episode_end：outcome=STEP_LIMIT，steps=20，duration_s=37.485，levels_completed=0（win_levels=7），prompt_tokens=52964，completion_tokens=180，calls=20（≈2648 prompt/9 completion tokens 每步）。来源：20261012.jsonl 末行。

## 5. 样本量与限界（如实登记）

- 每配置仅 **2 episodes**（R1 验收口径 N≥20 未在此批达到）；0 胜下 success_rate 无分辨率；
- 冒烟仅 **1 局 20 步**（STEP_LIMIT=20，与正式 eval 的 75 步上限不同口径）；
- 冒烟日志在 /tmp（易失），runs/ 内无对应入库副本；正式双跑 runs/ 内只有 csv+report，无步级 JSONL（fn_work/logs/ 常规跑批不入库策略所致，据 batches.md 2026-10-11 D3 行）；
- 量化格式偏差：真 27B 实为 **INT4-AWQ**（gemma-3-27b-it-int4-awq），非 requirements 技术栈决策的 FP8（batches.md D1 部署路径裁决行已登记偏差）；OBS_BUDGET 4000→2500 字符截断（tracker.md Ruling 行，4096 上下文上限所迫）。
