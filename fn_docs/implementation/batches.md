# batches.md —— 批次表（待办导航）
> fn-implement 独占更新。▶ = 下一批要完成的任务；未经批间门批准不得增删批次内容。

| 批次 | 函数/任务清单 | 验收点 | 注 |
|---|---|---|---|
| B1 | llm_complete, render_obs, append_jsonl_log, load_episode_set | 四共享 wired + pytest 基线恢复 26 skipped/0 error | 含新增改动：scaffold 占位测试补 import pytest（对账发现，随批修复） |
| ▶ B5 | render_submission_entry, verify_package_layout, build_kaggle_package, submit_package, collect_run_artifacts, render_gain_table, write_report | 打包/提交/报告三口 wired（提交口以 dry-run 或 CLI 回执为准） | render_submission_entry 契约以赛站实核模板为准（B2 已核则引用）；D1 随 27B 服务落地补、D4 随 R1 集成验收（B5 报告口可先挂占位说明） |

## 变更记录（计划层事件：签名微调、需求变更往返、放弃等）
| 日期 | 事件 | 说明 |
|---|---|---|
| 2026-10-10 | 新增改动登记 | B1 附 scaffold 占位测试补 import pytest（进入对账发现：26 个收集期 NameError 遮蔽测试基线） |
| 2026-10-10 | Ruling 互指 | B1 共享件 wired 判据降级（详见 tracker Ruling 行）：B2/B3 接线时复验生产调用点 |
| 2026-10-10 | B2 债务登记（评审建议） | load_episode_set 补 SDK 局 ID 存在性校验；render_obs 回填 REQUIRED_FIELDS+修正 docstring 截断措辞——B2 收档前须清 |
| 2026-10-10 | Ruling 互指 | llm_complete 签名微调：+可选 model 参数（详见 tracker Ruling 行）；随 make_baseline_policy 批次实施 |
| 2026-10-10 | B2 收档 | SDK 实核前置（references/arc_agi_3_sdk.md+INDEX，abb261c）+债务①②已清+五函数 wired；验收点"裸基线单局实跑"以真 SDK+脚本策略替代达成，27B vLLM 缺口挂 blocked（tracker 注记）待用户裁决 |
| 2026-10-10 | B2 批间评审 | 三轴过门（建议级 4 项）；债务登记：D1 baseline 真 LLM 端到端+确定性双跑（随 27B 落地补，继承 blocked）、D2 步日志 obs 摘要策略（B4 eval_ab 集成前定义）、D3 logs/ 入库保留策略（B4 前定：证据性实跑入库/常规跑批落 runs/ 不入库）、D4 submit_action 错误码佐证（R1 集成验收时 SDK 侧日志佐证或明示接受） |
| 2026-10-11 | Ruling 互指 | run_episode 策略协议扩展（+可选局边界钩子，详见 tracker Ruling 行）；随 make_curriculum_policy 批次实施 |
| 2026-10-11 | B3 收档 | 六函数 wired（两包装策略+两降级件+难度/选源）；含 run_episode 钩子协议扩展 Ruling；pytest 161 passed/11 skipped |
| 2026-10-11 | B3 批间评审 | 三轴 17/17 过门零阻断；建议级并入 B4 复核：钩子 start/end 失败不对称（connect_env 抛错则 end 永不触发，B4 失败重试设计须知晓）；estimate_difficulty 记录口径（尝试次数=len(history)）备察 |
| 2026-10-11 | Ruling 互指 | aggregate_results 签名微调：+可选 out_dir 参数（详见 tracker Ruling 行）；随 B4 实施 |
| 2026-10-11 | D2/D3 债务清账 | D2：步日志补 obs_summary（状态/进度/可用动作/帧形状，无全量帧防爆炸，可回放定位）；D3：fn_work/logs/ 入 ignore（常规跑批日志不入库，B2 期已入库的历史证据保留），证据性产物走 fn_work/runs/ 入库（指标件 CSV 等），需日志级证据时 ARC_LOG_DIR 指向 run 子目录强加 |
| 2026-10-11 | B4 收档 | 四函数 wired + D2/D3 债务清账（4eecdaa）；端到端验收达成（真 CLI+真 SDK+假 LLM 2 局对照表）；pytest 203 passed/7 skipped；桩残留 7（B5） |
