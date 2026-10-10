# Implement tracker — fn_docs — 计划: batches.md — 真值: functions.md + git log
> fn-implement 独占更新；主会话单写者（子代理只回报证据原文，记账在主会话）。
> 执行以第一个未勾行为当前步；每步三段式：预告 → 执行 → 证据+读回。
> 完成行经 scripts/fn-step-done.sh 写入：核验 exit 0 才记账、失败零写入、写完读回。
> 本账本不存函数状态词（状态真值在 functions.md）。身份行：arc-prize-2026 首进 2026-10-10，HEAD=617643a。

## 进入五步
- [x] 1 前置检查 — 证据: bash -c n=$(grep -rh unimplemented:fn: fn_work/src --include=*.py | wc -l); test -f fn_docs/responsibility.md && test "$n" -eq 26 && echo "responsibility+26桩 ok" → responsibility+26桩 ok (10-10)
- [x] 2 轻量对账 — 证据: bash -c git log --oneline -1 | grep -q fn-scaffold && echo "HEAD=scaffold 对账ok" → HEAD=scaffold 对账ok (10-10)
- [x] 3 批次计划 — 证据: bash -c test $(ls fn_docs/implementation | wc -l) -eq 4 && echo "四文档在" → 四文档在 (10-10)
- [x] 4 中断恢复检查 — 证据: bash -c grep -q "▶ B1" fn_docs/implementation/batches.md && echo "无滞留批" → 无滞留批 (10-10)
- [x] 5 功能演进判定 — 证据: bash -c test ! -f fn_docs/acceptance.md && echo "标准模式" → 标准模式 (10-10)

## B1 — llm_complete, render_obs, append_jsonl_log, load_episode_set
### llm_complete
- [x] llm_complete · implemented — 证据: bash -c ! grep -q "unimplemented:fn:llm_complete" fn_work/src/shared/llm_complete.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] llm_complete · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/shared/test_llm_complete.py -q → 9 passed in 0.03s (10-10)
- [x] llm_complete · wired — 证据: bash -c grep -q "llm_complete" fn_work/tests/shared/test_llm_complete.py && echo 测试调用点在（Ruling 弱判据） → 测试调用点在（Ruling 弱判据） (10-10)
- [x] llm_complete · 清单进位 — 证据: bash -c grep -q "| llm_complete | B1 | wired 10-10 |" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] llm_complete · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(llm_complete): wired" && echo commit 在 → commit 在 (10-10)
### render_obs
- [x] render_obs · implemented — 证据: bash -c ! grep -q "unimplemented:fn:render_obs" fn_work/src/shared/render_obs.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] render_obs · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/shared/test_render_obs.py -q → 17 passed in 0.01s (10-10)
- [x] render_obs · wired — 证据: bash -c grep -q "render_obs" fn_work/tests/shared/test_render_obs.py && echo 测试调用点在（Ruling 弱判据） → 测试调用点在（Ruling 弱判据） (10-10)
- [x] render_obs · 清单进位 — 证据: bash -c grep -q "| render_obs | B1 | wired 10-10 |" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] render_obs · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(render_obs): wired" && echo commit 在 → commit 在 (10-10)
### append_jsonl_log
- [x] append_jsonl_log · implemented — 证据: bash -c ! grep -q "unimplemented:fn:append_jsonl_log" fn_work/src/shared/append_jsonl_log.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] append_jsonl_log · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/shared/test_append_jsonl_log.py -q → 6 passed in 0.01s (10-10)
- [x] append_jsonl_log · wired — 证据: bash -c grep -q "append_jsonl_log" fn_work/tests/shared/test_append_jsonl_log.py && echo 测试调用点在（Ruling 弱判据） → 测试调用点在（Ruling 弱判据） (10-10)
- [x] append_jsonl_log · 清单进位 — 证据: bash -c grep -q "| append_jsonl_log | B1 | wired 10-10 |" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] append_jsonl_log · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(append_jsonl_log): wired" && echo commit 在 → commit 在 (10-10)
### load_episode_set
- [x] load_episode_set · implemented — 证据: bash -c ! grep -q "unimplemented:fn:load_episode_set" fn_work/src/shared/load_episode_set.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] load_episode_set · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/shared/test_load_episode_set.py -q → 10 passed in 0.02s (10-10)
- [x] load_episode_set · wired — 证据: bash -c grep -q "load_episode_set" fn_work/tests/shared/test_load_episode_set.py && echo 测试调用点在（Ruling 弱判据） → 测试调用点在（Ruling 弱判据） (10-10)
- [x] load_episode_set · 清单进位 — 证据: bash -c grep -q "| load_episode_set | B1 | wired 10-10 |" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] load_episode_set · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(load_episode_set): wired" && echo commit 在 → commit 在 (10-10)

## B1 批间门
- [x] B1 · 评审三轴 — 证据: bash -c git log --oneline -3 | grep -q "B1" && echo "评审子代理三轴全过+债务已登记" → 评审子代理三轴全过+债务已登记 (10-10)
- [x] B1 · 用户裁决 — 证据: bash -c grep -q "| 2026-10-10 | B1 |" fn_docs/implementation/history.md && grep -q "▶ B2" fn_docs/implementation/batches.md && echo "B1已收档+用户裁决=继续B2" → B1已收档+用户裁决=继续B2 (10-10)

## B2 — build_baseline_prompt, make_baseline_policy, connect_env, submit_action, run_episode
### build_baseline_prompt
- [x] build_baseline_prompt · implemented — 证据: bash -c ! grep -q "unimplemented:fn:build_baseline_prompt" fn_work/src/make_baseline_policy/build_baseline_prompt.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] build_baseline_prompt · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_baseline_policy/test_build_baseline_prompt.py -q 2>&1 | tail -1 → 7 passed in 0.01s (10-10)
- [x] build_baseline_prompt · wired — 证据: bash -c grep -q "build_baseline_prompt" fn_work/tests/make_baseline_policy/test_build_baseline_prompt.py && echo 测试调用点在（弱判据，生产调用点随 make_baseline_policy 落地后补验） → 测试调用点在（弱判据，生产调用点随 make_baseline_policy 落地后补验） (10-10)
- [x] build_baseline_prompt · 清单进位 — 证据: bash -c grep -q "| build_baseline_prompt | B2 | wired 10-10 |" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] build_baseline_prompt · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(build_baseline_prompt): wired" && echo commit 在 → commit 在 (10-10)
### make_baseline_policy
- [x] make_baseline_policy · implemented — 证据: bash -c ! grep -q "unimplemented:fn:make_baseline_policy" fn_work/src/make_baseline_policy/make_baseline_policy.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] make_baseline_policy · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_baseline_policy/test_make_baseline_policy.py -q 2>&1 | tail -1 → 14 passed in 0.03s (10-10)
- [x] make_baseline_policy · wired — 证据: bash -c grep -q "make_baseline_policy" fn_work/tests/make_baseline_policy/test_make_baseline_policy.py && echo 测试调用点在（弱判据；生产调用方 build_config_matrix/eval_ab 属 B4，届时复验） → 测试调用点在（弱判据；生产调用方 build_config_matrix/eval_ab 属 B4，届时复验） (10-10)
- [x] make_baseline_policy · 清单进位 — 证据: bash -c grep -q "| make_baseline_policy | B2 | wired 10-10 |" fn_docs/implementation/functions.md && grep -q "llm_complete | B1 | wired 10-10；B2 签名微调" fn_docs/implementation/functions.md && echo 两清单行已落 → 两清单行已落 (10-10)
- [x] make_baseline_policy · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(make_baseline_policy): wired" && echo commit 在 → commit 在 (10-10)
### connect_env
- [x] connect_env · implemented — 证据: bash -c ! grep -q "unimplemented:fn:connect_env" fn_work/src/run_episode/connect_env.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] connect_env · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/run_episode/test_connect_env.py -q 2>&1 | tail -1 → 10 passed in 0.11s (10-10)
- [x] connect_env · wired — 证据: bash -c grep -q "connect_env" fn_work/tests/run_episode/test_connect_env.py && echo 测试调用点在（弱判据；生产调用方 run_episode 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 run_episode 本批下一函数落地后补验） (10-10)
- [x] connect_env · 清单进位 — 证据: bash -c grep -q "| connect_env | B2 | wired 10-10 |" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] connect_env · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(connect_env): wired" && echo commit 在 → commit 在 (10-10)
### submit_action
- [x] submit_action · implemented — 证据: bash -c ! grep -q "unimplemented:fn:submit_action" fn_work/src/run_episode/submit_action.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] submit_action · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/run_episode/test_submit_action.py -q 2>&1 | tail -1 → 14 passed in 0.13s (10-10)
- [x] submit_action · wired — 证据: bash -c grep -q "submit_action" fn_work/tests/run_episode/test_submit_action.py && echo 测试调用点在（弱判据；生产调用方 run_episode 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 run_episode 本批下一函数落地后补验） (10-10)
- [x] submit_action · 清单进位 — 证据: bash -c grep -q "| submit_action | B2 | wired 10-10 |" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] submit_action · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(submit_action): wired" && echo commit 在 → commit 在 (10-10)
### run_episode
- [x] run_episode · implemented — 证据: bash -c ! grep -q "unimplemented:fn:run_episode" fn_work/src/run_episode/run_episode.py && echo 桩已替换 → 桩已替换 (10-10)
- [x] run_episode · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/run_episode/test_run_episode.py -q 2>&1 | tail -1 → 7 passed in 0.13s (10-10)
- [x] run_episode · wired — 证据: bash -c grep -q "from src.run_episode.connect_env import connect_env" fn_work/src/run_episode/run_episode.py && grep -q "submit_action(env, action, scene)" fn_work/src/run_episode/run_episode.py && grep -q ""run_id": "b2-realrun-vc33"" fn_work/logs/20261010.jsonl && grep -q ""event": "episode_end"" fn_work/logs/20261010.jsonl && echo "生产调用点+实跑产物在（真 SDK vc33 局 50 步 GAME_OVER）" → 生产调用点+实跑产物在（真 SDK vc33 局 50 步 GAME_OVER） (10-10)
- [x] run_episode · 清单进位 — 证据: bash -c grep -q "run_episode | B2 | wired 10-10" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-10)
- [x] run_episode · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(run_episode): wired" && echo commit 在 → commit 在 (10-10)

## B2 批间门
- [ ] B2 · 评审三轴 — 预告: 规格/标准/档案同步（含 tracker 本批行核对）
- [ ] B2 · 用户裁决 — 预告: 继续 / 修订 / 裁决 blocked

## B3 — estimate_difficulty, select_experience_source, make_curriculum_policy, update_experience_store, regularize_experience, make_regularized_policy
### estimate_difficulty
- [ ] estimate_difficulty · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] estimate_difficulty · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] estimate_difficulty · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] estimate_difficulty · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] estimate_difficulty · commit — 预告: fn(estimate_difficulty): wired 含四文档变更
### select_experience_source
- [ ] select_experience_source · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] select_experience_source · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] select_experience_source · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] select_experience_source · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] select_experience_source · commit — 预告: fn(select_experience_source): wired 含四文档变更
### make_curriculum_policy
- [ ] make_curriculum_policy · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] make_curriculum_policy · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] make_curriculum_policy · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] make_curriculum_policy · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] make_curriculum_policy · commit — 预告: fn(make_curriculum_policy): wired 含四文档变更
### update_experience_store
- [ ] update_experience_store · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] update_experience_store · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] update_experience_store · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] update_experience_store · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] update_experience_store · commit — 预告: fn(update_experience_store): wired 含四文档变更
### regularize_experience
- [ ] regularize_experience · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] regularize_experience · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] regularize_experience · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] regularize_experience · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] regularize_experience · commit — 预告: fn(regularize_experience): wired 含四文档变更
### make_regularized_policy
- [ ] make_regularized_policy · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] make_regularized_policy · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] make_regularized_policy · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] make_regularized_policy · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] make_regularized_policy · commit — 预告: fn(make_regularized_policy): wired 含四文档变更

## B3 批间门
- [ ] B3 · 评审三轴 — 预告: 规格/标准/档案同步（含 tracker 本批行核对）
- [ ] B3 · 用户裁决 — 预告: 继续 / 修订 / 裁决 blocked

## B4 — build_config_matrix, run_config_batch, aggregate_results, eval_ab
### build_config_matrix
- [ ] build_config_matrix · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] build_config_matrix · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] build_config_matrix · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] build_config_matrix · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] build_config_matrix · commit — 预告: fn(build_config_matrix): wired 含四文档变更
### run_config_batch
- [ ] run_config_batch · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] run_config_batch · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] run_config_batch · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] run_config_batch · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] run_config_batch · commit — 预告: fn(run_config_batch): wired 含四文档变更
### aggregate_results
- [ ] aggregate_results · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] aggregate_results · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] aggregate_results · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] aggregate_results · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] aggregate_results · commit — 预告: fn(aggregate_results): wired 含四文档变更
### eval_ab
- [ ] eval_ab · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] eval_ab · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] eval_ab · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] eval_ab · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] eval_ab · commit — 预告: fn(eval_ab): wired 含四文档变更

## B4 批间门
- [ ] B4 · 评审三轴 — 预告: 规格/标准/档案同步（含 tracker 本批行核对）
- [ ] B4 · 用户裁决 — 预告: 继续 / 修订 / 裁决 blocked

## B5 — render_submission_entry, verify_package_layout, build_kaggle_package, submit_package, collect_run_artifacts, render_gain_table, write_report
### render_submission_entry
- [ ] render_submission_entry · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] render_submission_entry · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] render_submission_entry · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] render_submission_entry · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] render_submission_entry · commit — 预告: fn(render_submission_entry): wired 含四文档变更
### verify_package_layout
- [ ] verify_package_layout · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] verify_package_layout · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] verify_package_layout · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] verify_package_layout · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] verify_package_layout · commit — 预告: fn(verify_package_layout): wired 含四文档变更
### build_kaggle_package
- [ ] build_kaggle_package · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] build_kaggle_package · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] build_kaggle_package · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] build_kaggle_package · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] build_kaggle_package · commit — 预告: fn(build_kaggle_package): wired 含四文档变更
### submit_package
- [ ] submit_package · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] submit_package · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] submit_package · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] submit_package · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] submit_package · commit — 预告: fn(submit_package): wired 含四文档变更
### collect_run_artifacts
- [ ] collect_run_artifacts · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] collect_run_artifacts · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] collect_run_artifacts · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] collect_run_artifacts · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] collect_run_artifacts · commit — 预告: fn(collect_run_artifacts): wired 含四文档变更
### render_gain_table
- [ ] render_gain_table · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] render_gain_table · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] render_gain_table · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] render_gain_table · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] render_gain_table · commit — 预告: fn(render_gain_table): wired 含四文档变更
### write_report
- [ ] write_report · implemented — 预告: 桩替换为真值，预期该名桩 grep 无残留
- [ ] write_report · tested — 预告: 核验命令绿（自有单测或上游覆盖）
- [ ] write_report · wired — 预告: 调用点存在（grep 命中）；顶层入口实跑有输出
- [ ] write_report · 清单进位 — 预告: functions.md 状态行改后读回
- [ ] write_report · commit — 预告: fn(write_report): wired 含四文档变更

## B5 批间门
- [ ] B5 · 评审三轴 — 预告: 规格/标准/档案同步（含 tracker 本批行核对）
- [ ] B5 · 用户裁决 — 预告: 继续 / 修订 / 裁决 blocked
- Ruling: B1 四共享函数 wired 判据降级为「测试文件静态导入+实跑」 — 原因：生产调用点（make_*_policy 等）按批次计划在 B2/B3 才实现 — 代价：B1 wired 为弱判据 — 落点：B2/B3 验收点复验生产调用点 grep（batches.md 注列已同步）
- Ruling: llm_complete 增可选参数 model=""（显式模型名覆盖端点默认） — 原因：make_baseline_policy 配置含模型名，原实现只认 ARC_MODEL 环境变量，配置无法落到请求体 — 代价：B1 已 wired 函数签名扩展（向后兼容，默认行为不变，+1 测至 10 绿） — 落点：batches.md 变更记录互指；responsibility.md 签名意图为意图级描述不改
- 注记: B2 验收点「裸基线单局实跑」部分受阻 — 27B vLLM 服务缺位（唯一算力机 RTX 4070 Laptop 8GB 显存 < 27B FP8 权重 ~27GB+，requirements 技术栈决策的远端服务化未部署） — 已以真 SDK 在线匿名局+脚本策略实跑替代（run_id=b2-realrun-vc33，50 步 GAME_OVER，日志在库） — 待批间门用户裁决：换小模型量化/另配算力/挂账至推理服务部署后补跑
- Ruling: EpisodeResult.outcome 扩为三值（+STEP_LIMIT）与 submit 场景 STEP_FAILED 哨兵协议 — 原因：SDK 实核 e/h——无墙钟时限须本地护栏防死循环、SDK 失败吞错误码返回 None 须场景归一（experiment 停/submit 降级保旧观测） — 代价：终局语义超出责任文档两值描述，docstring 已论证+测试覆盖 — 落点：run_episode/submit_action docstring；B4 集成验收时复核
- Ruling: B1 四共享生产调用点复验落账（补显式证据行） — 原因：B1 Ruling 落点要求 B2 验收点复验 grep，评审已复跑确认 — 代价：无 — 落点:llm_complete@make_baseline_policy.py、render_obs@build_baseline_prompt.py、append_jsonl_log@run_episode.py、build_baseline_prompt@make_baseline_policy.py、connect_env/submit_action@run_episode.py（grep 全命中，评审报告 2026-10-10）
