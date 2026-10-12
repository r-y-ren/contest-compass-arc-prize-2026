# ARC-AGI-3 自进化智能体复现报告

- runs 目录：`/mnt/data/Code/autoC/workspace/arc-prize-2026/fn_work/runs`
- 对照表：`runs/eval-1791773879-s42/ab_table.csv`

## 1. 增益表

| name | policy | episodes | wins | success_rate | avg_steps | d_success_rate | d_avg_steps | source |
|---|---|---|---|---|---|---|---|---|
| baseline | baseline | 2 | 0 | 0.0 | 75.0 | 0.0 | 0.0 | [eval-1791683161-s42](runs/eval-1791683161-s42) · [csv](runs/eval-1791683161-s42/ab_table.csv) |
| plus_curriculum | curriculum | 2 | 0 | 0.0 | 75.0 | 0.0 | 0.0 | [eval-1791773312-s42](runs/eval-1791773312-s42) · [csv](runs/eval-1791773312-s42/ab_table.csv) |
| plus_regularized | regularized | 2 | 0 | 0.0 | 75.0 | 0.0 | 0.0 | [eval-1791773312-s42](runs/eval-1791773312-s42) · [csv](runs/eval-1791773312-s42/ab_table.csv) |
| full | curriculum+regularized | 2 | 0 | 0.0 | 75.0 | 0.0 | 0.0 | [eval-1791773312-s42](runs/eval-1791773312-s42) · [csv](runs/eval-1791773312-s42/ab_table.csv) |

## 2. 配置说明

| 配置 | 组合 | 说明 |
|---|---|---|
| baseline | baseline | 裸基线：固定提示词 + 冻结 LLM（对照起点） |
| plus_curriculum | curriculum | 课程调度（R3/ActiveSaddler 降级）：先易后难编排经验源，包装 baseline |
| plus_regularized | regularized | 经验正则（R4/RRSI 降级）：筛选正则化历史经验入提示，包装 baseline |
| full | curriculum+regularized | 全开：课程调度 ∘ 经验正则 ∘ 裸基线（编排层在外、记忆层在内） |

## 3. 运行产物溯源附录

| run_id | 修改时间 | 文件数 | 对照表 |
|---|---|---|---|
| eval-1791683161-s42 | 2026-10-11T06:47:02.016514+00:00 | 2 | [ab_table.csv](runs/eval-1791683161-s42/ab_table.csv)（1 行） |
| eval-1791773312-s42 | 2026-10-12T02:57:39.592330+00:00 | 1 | [ab_table.csv](runs/eval-1791773312-s42/ab_table.csv)（4 行） |
| eval-1791773879-s42 | 2026-10-12T03:07:46.715872+00:00 | 1 | [ab_table.csv](runs/eval-1791773879-s42/ab_table.csv)（4 行） |
