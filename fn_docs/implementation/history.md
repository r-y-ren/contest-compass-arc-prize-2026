# history.md —— 历史表（已完成批次队列，只追加不删改）
> fn-implement 独占更新。每批次完成后尾部追加留痕。

| 完成日期 | 批次 | 任务/函数清单（含操作与来源说明） | 验收摘要 |
|---|---|---|---|
| 2026-10-10 | B1 | llm_complete(9测), render_obs(17测), append_jsonl_log(6测), load_episode_set(10测)+新增改动:占位测试补 import pytest | 四共享 wired（Ruling 弱判据）；pytest 基线 42 passed/22 skipped；四 commit 1a89c33..HEAD |
| 2026-10-10 | B2 | build_baseline_prompt(7测), make_baseline_policy(14测), connect_env(10测), submit_action(14测), run_episode(7测) + 前置:SDK 实核落 references/锁依赖 arc-agi==0.9.9 + 债务①②清（load_episode_set 局 ID 校验 14 测/render_obs REQUIRED_FIELDS 回填 22 测）+ llm_complete 签名微调(+model, 10 测) + 新增私有件 _frame.py | 五函数 wired；pytest 104 passed/17 skipped；真 SDK 在线匿名局实跑 50 步 GAME_OVER（vc33-5430563c，run_id=b2-realrun-vc33，日志入库）；27B vLLM 实跑缺位挂 blocked 待门裁决；commit abb261c..8b62aca |
| 2026-10-11 | B3 | estimate_difficulty(8测), select_experience_source(10测), make_curriculum_policy(10测), update_experience_store(9测), regularize_experience(9测), make_regularized_policy(9测) + run_episode 钩子协议扩展(+2测至 9) | 两包装策略 wired（验收点达成）；pytest 161 passed/11 skipped；桩残留 11（B4×4+B5×7）；commit 790b0a3..6b035c5 |
