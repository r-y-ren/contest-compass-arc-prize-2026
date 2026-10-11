# Kaggle 赛站提交契约实核（ARC Prize 2026 · ARC-AGI-3）

- 实核日期：2026-10-11（kaggle CLI 已鉴权实查 + 官方文档 WebFetch）
- 赛站：`arc-prize-2026-arc-agi-3`（`kaggle competitions list -s "ARC-AGI"` 查得；截止 2026-11-02 23:59:00 UTC；Feature 赛，$850,000；榜单可查——2026-10-11 榜首 Yi-Chia Chen 62.96）

## 提交契约（来源：https://docs.arcprize.org/arc-prize-2026.md，2026-10-11 抓取）

1. **code competition：提交件是 notebook**——原文 "The competition is a code competition: you submit a notebook"；本地经 starter kit `make submit` 构建并推送（`kaggle kernels push`），产物 submission.parquet 为得分文件。
2. **两阶段评测**：Phase A = Save & Run All（notebook 无错执行验证）；Phase B = Competition Rerun（网页点击 "Submit to Competition" 后 agent 跑隐藏局集出榜）。原文："clicking Submit to Competition is the deliberate moment you spend a daily submission."
3. **agent 契约**：唯一编辑点 `agent/my_agent.py`——`MyAgent(Agent)` 类，方法 `is_done(frames, latest_frame) -> bool` 与 `choose_action(frames, latest_frame) -> GameAction`；依赖/提交格式/对局编排由 kit 承担。Python 3.12（arc-agi 要求）。
4. **限额**：每日提交次数有限（网页提交消耗 daily submission）；加速器默认 t4，rtx6000 为 ARC-AGI-3 专属且耗 GPU 配额更快。
5. **首提前置**：kit 的 `notebooks/kernel-metadata.json` 中 `REPLACE_WITH_YOUR_USERNAME` 需改为自己的 Kaggle 用户名。

## 对本项目的影响

- requirements R6 验收原文假定 `kaggle competitions submit -f <包>`——与实核契约（notebook push+网页提交）不符，已登记 tracker Ruling（2026-10-11），requirements R6 措辞待 fn-close 前修订。
- submit_package 实跑模式按计划形态执行（被拒时 SubmitError 附 CLI 原始输出原样暴露）；真实提交走 kit notebook 组装且属外部动作，默认 dry_run。
