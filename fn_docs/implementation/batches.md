# batches.md —— 批次表（待办导航）
> fn-implement 独占更新。▶ = 下一批要完成的任务；未经批间门批准不得增删批次内容。

| 批次 | 函数/任务清单 | 验收点 | 注 |
|---|---|---|---|
| B1 | llm_complete, render_obs, append_jsonl_log, load_episode_set | 四共享 wired + pytest 基线恢复 26 skipped/0 error | 含新增改动：scaffold 占位测试补 import pytest（对账发现，随批修复） |
| ▶ B2 | build_baseline_prompt, make_baseline_policy, connect_env, submit_action, run_episode | run_episode wired + 裸基线单局实跑有可观察输出 | 开工前实核官方 SDK 文档（docs.arcprize.org）落 references/ 并登记 INDEX（铁律 3）；SDK 接口以实核为准 |
| B3 | estimate_difficulty, select_experience_source, make_curriculum_policy, update_experience_store, regularize_experience, make_regularized_policy | 两包装策略 wired（可包装 baseline 出可跑策略对象） |  |
| B4 | build_config_matrix, run_config_batch, aggregate_results, eval_ab | eval_ab wired + 小局集端到端（假 LLM）对照表产出 |  |
| B5 | render_submission_entry, verify_package_layout, build_kaggle_package, submit_package, collect_run_artifacts, render_gain_table, write_report | 打包/提交/报告三口 wired（提交口以 dry-run 或 CLI 回执为准） | render_submission_entry 契约以赛站实核模板为准（B2 已核则引用） |

## 变更记录（计划层事件：签名微调、需求变更往返、放弃等）
| 日期 | 事件 | 说明 |
|---|---|---|
| 2026-10-10 | 新增改动登记 | B1 附 scaffold 占位测试补 import pytest（进入对账发现：26 个收集期 NameError 遮蔽测试基线） |
| 2026-10-10 | Ruling 互指 | B1 共享件 wired 判据降级（详见 tracker Ruling 行）：B2/B3 接线时复验生产调用点 |
