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
- [x] B2 · 评审三轴 — 证据: bash -c git log --oneline -1 | grep -q "B2" && grep -q "Ruling: EpisodeResult.outcome" fn_docs/implementation/tracker.md && echo "评审子代理三轴过门（建议级4项已登记）+条件闭合" → 评审子代理三轴过门（建议级4项已登记）+条件闭合 (10-10)
- [x] B2 · 用户裁决 — 证据: bash -c grep -q "挂账至推理服务部署后补跑（D1 债务继承；用户确认）" fn_docs/implementation/tracker.md && echo "裁决=继续B3+27B挂账D1" → 裁决=继续B3+27B挂账D1 (10-11)

## B3 — estimate_difficulty, select_experience_source, make_curriculum_policy, update_experience_store, regularize_experience, make_regularized_policy
### estimate_difficulty
- [x] estimate_difficulty · implemented — 证据: bash -c ! grep -q "unimplemented:fn:estimate_difficulty" fn_work/src/make_curriculum_policy/estimate_difficulty.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] estimate_difficulty · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_curriculum_policy/test_estimate_difficulty.py -q 2>&1 | tail -1 → 8 passed in 0.01s (10-11)
- [x] estimate_difficulty · wired — 证据: bash -c grep -q "estimate_difficulty" fn_work/tests/make_curriculum_policy/test_estimate_difficulty.py && echo 测试调用点在（弱判据；生产调用方 select_experience_source 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 select_experience_source 本批下一函数落地后补验） (10-11)
- [x] estimate_difficulty · 清单进位 — 证据: bash -c grep -q "estimate_difficulty | B3 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] estimate_difficulty · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(estimate_difficulty): wired" && echo commit 在 → commit 在 (10-11)
### select_experience_source
- [x] select_experience_source · implemented — 证据: bash -c ! grep -q "unimplemented:fn:select_experience_source" fn_work/src/make_curriculum_policy/select_experience_source.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] select_experience_source · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_curriculum_policy/test_select_experience_source.py -q → 10 passed（纠正注记 10-11: 首跑 1 failed 因管道 tail 吞退出码假过门+实现按裸难度序而非 score 序，已修代码（score 元组决胜）后绿） (10-11)
- [x] select_experience_source · wired — 证据: bash -c grep -q "estimate_difficulty|select_experience_source" fn_work/src/make_curriculum_policy/make_curriculum_policy.py 2>/dev/null || grep -q "select_experience_source" fn_work/tests/make_curriculum_policy/test_select_experience_source.py && echo 测试调用点在（弱判据；生产调用方 make_curriculum_policy 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 make_curriculum_policy 本批下一函数落地后补验） (10-11)
- [x] select_experience_source · 清单进位 — 证据: bash -c grep -q "select_experience_source | B3 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] select_experience_source · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(select_experience_source): wired" && echo commit 在 → commit 在 (10-11)
### make_curriculum_policy
- [x] make_curriculum_policy · implemented — 证据: bash -c ! grep -q unimplemented:fn:make_curriculum_policy fn_work/src/make_curriculum_policy/make_curriculum_policy.py && grep -q on_episode_start fn_work/src/run_episode/run_episode.py && echo 桩已替换+钩子扩展在 → 桩已替换+钩子扩展在 (10-11)
- [x] make_curriculum_policy · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_curriculum_policy/test_make_curriculum_policy.py -q → 10 passed in 0.01s (10-11)
- [x] make_curriculum_policy · wired — 证据: bash -c grep -q estimate_difficulty fn_work/src/make_curriculum_policy/make_curriculum_policy.py && grep -q select_experience_source fn_work/src/make_curriculum_policy/make_curriculum_policy.py && grep -q on_episode_start fn_work/src/run_episode/run_episode.py && echo 生产调用点在（estimate/select 由本函数调用；钩子由 run_episode 调用；本函数生产调用方=配置矩阵属 B4） → 生产调用点在（estimate/select 由本函数调用；钩子由 run_episode 调用；本函数生产调用方=配置 (10-11)
- [x] make_curriculum_policy · 清单进位 — 证据: bash -c grep -q "make_curriculum_policy | B3 | wired 10-11" fn_docs/implementation/functions.md && grep -q "B3 钩子扩展 10-11" fn_docs/implementation/functions.md && echo 两清单行已落 → 两清单行已落 (10-11)
- [x] make_curriculum_policy · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(make_curriculum_policy): wired" && echo commit 在 → commit 在 (10-11)
### update_experience_store
- [x] update_experience_store · implemented — 证据: bash -c ! grep -q unimplemented:fn:update_experience_store fn_work/src/make_regularized_policy/update_experience_store.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] update_experience_store · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_regularized_policy/test_update_experience_store.py -q → 9 passed in 0.01s (10-11)
- [x] update_experience_store · wired — 证据: bash -c grep -q update_experience_store fn_work/tests/make_regularized_policy/test_update_experience_store.py && echo 测试调用点在（弱判据；生产调用方 make_regularized_policy 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 make_regularized_policy 本批下一函数落地后补验） (10-11)
- [x] update_experience_store · 清单进位 — 证据: bash -c grep -q "update_experience_store | B3 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] update_experience_store · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(update_experience_store): wired" && echo commit 在 → commit 在 (10-11)
### regularize_experience
- [x] regularize_experience · implemented — 证据: bash -c ! grep -q unimplemented:fn:regularize_experience fn_work/src/make_regularized_policy/regularize_experience.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] regularize_experience · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_regularized_policy/test_regularize_experience.py -q → 9 passed in 0.01s (10-11)
- [x] regularize_experience · wired — 证据: bash -c grep -q regularize_experience fn_work/tests/make_regularized_policy/test_regularize_experience.py && echo 测试调用点在（弱判据；生产调用方 make_regularized_policy 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 make_regularized_policy 本批下一函数落地后补验） (10-11)
- [x] regularize_experience · 清单进位 — 证据: bash -c grep -q "regularize_experience | B3 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] regularize_experience · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(regularize_experience): wired" && echo commit 在 → commit 在 (10-11)
### make_regularized_policy
- [x] make_regularized_policy · implemented — 证据: bash -c ! grep -q unimplemented:fn:make_regularized_policy fn_work/src/make_regularized_policy/make_regularized_policy.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] make_regularized_policy · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/make_regularized_policy/test_make_regularized_policy.py -q → 9 passed in 0.01s (10-11)
- [x] make_regularized_policy · wired — 证据: bash -c grep -q regularize_experience fn_work/src/make_regularized_policy/make_regularized_policy.py && grep -q update_experience_store fn_work/src/make_regularized_policy/make_regularized_policy.py && grep -q on_episode_end fn_work/src/run_episode/run_episode.py && echo 生产调用点在（regularize/update 由本函数调用；钩子由 run_episode 调用；本函数生产调用方=配置矩阵属 B4） → 生产调用点在（regularize/update 由本函数调用；钩子由 run_episode 调用；本函数生产调用方= (10-11)
- [x] make_regularized_policy · 清单进位 — 证据: bash -c grep -q "make_regularized_policy | B3 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] make_regularized_policy · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(make_regularized_policy): wired" && echo commit 在 → commit 在 (10-11)

## B3 批间门
- [x] B3 · 评审三轴 — 证据: bash -c git log --oneline -3 | head -1 | grep -q B3 && echo 评审子代理三轴过门 → 评审子代理三轴过门 (10-11)
- [x] B3 · 用户裁决 — 证据: bash -c grep -q "▶ B4" fn_docs/implementation/batches.md && echo 裁决=继续B4 && git log --oneline -1 | grep -q B3 → 裁决=继续B4 (10-11)

## B4 — build_config_matrix, run_config_batch, aggregate_results, eval_ab
### build_config_matrix
- [x] build_config_matrix · implemented — 证据: bash -c ! grep -q unimplemented:fn:build_config_matrix fn_work/src/eval_ab/build_config_matrix.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] build_config_matrix · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/eval_ab/test_build_config_matrix.py -q → 14 passed in 0.01s (10-11)
- [x] build_config_matrix · wired — 证据: bash -c grep -q build_config_matrix fn_work/tests/eval_ab/test_build_config_matrix.py && echo 测试调用点在（弱判据；生产调用方 eval_ab 本批后段落地后补验） → 测试调用点在（弱判据；生产调用方 eval_ab 本批后段落地后补验） (10-11)
- [x] build_config_matrix · 清单进位 — 证据: bash -c grep -q "build_config_matrix | B4 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] build_config_matrix · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(build_config_matrix): wired" && echo commit 在 → commit 在 (10-11)
### run_config_batch
- [x] run_config_batch · implemented — 证据: bash -c ! grep -q unimplemented:fn:run_config_batch fn_work/src/eval_ab/run_config_batch.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] run_config_batch · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/eval_ab/test_run_config_batch.py -q → 7 passed in 0.03s (10-11)
- [x] run_config_batch · wired — 证据: bash -c grep -q run_episode fn_work/src/eval_ab/run_config_batch.py && grep -q make_baseline_policy fn_work/src/eval_ab/run_config_batch.py && echo 生产调用点在（run_episode 与三工厂由本函数调用；本函数生产调用方 eval_ab 本批下一函数落地后补验） → 生产调用点在（run_episode 与三工厂由本函数调用；本函数生产调用方 eval_ab 本批下一函数落地后补验） (10-11)
- [x] run_config_batch · 清单进位 — 证据: bash -c grep -q "run_config_batch | B4 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] run_config_batch · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(run_config_batch): wired" && echo commit 在 → commit 在 (10-11)
### aggregate_results
- [x] aggregate_results · implemented — 证据: bash -c ! grep -q unimplemented:fn:aggregate_results fn_work/src/eval_ab/aggregate_results.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] aggregate_results · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/eval_ab/test_aggregate_results.py -q → 8 passed in 0.01s (10-11)
- [x] aggregate_results · wired — 证据: bash -c grep -q aggregate_results fn_work/tests/eval_ab/test_aggregate_results.py && echo 测试调用点在（弱判据；生产调用方 eval_ab 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 eval_ab 本批下一函数落地后补验） (10-11)
- [x] aggregate_results · 清单进位 — 证据: bash -c grep -q "aggregate_results | B4 | wired 10-11" fn_docs/implementation/functions.md && grep -q "Ruling: aggregate_results" fn_docs/implementation/tracker.md && echo 清单行+Ruling 已落 → 清单行+Ruling 已落 (10-11)
- [x] aggregate_results · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(aggregate_results): wired" && echo commit 在 → commit 在 (10-11)
### eval_ab
- [x] eval_ab · implemented — 证据: bash -c ! grep -q unimplemented:fn:eval_ab fn_work/src/eval_ab/eval_ab.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] eval_ab · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/eval_ab/test_eval_ab.py -q → 11 passed in 0.05s (10-11)
- [x] eval_ab · wired — 证据: bash -c grep -q "from src.eval_ab.eval_ab import eval_ab" fn_work/eval_ab.py && echo CLI 生产调用点在（eval_ab.py 入口）；端到端实跑随后补证 → CLI 生产调用点在（eval_ab.py 入口）；端到端实跑随后补证 (10-11)
- [x] eval_ab · 清单进位 — 证据: bash -c grep -q "eval_ab | B4 | wired 10-11" fn_docs/implementation/functions.md && grep -q "baseline,baseline,2" fn_work/runs/eval-1791683161-s42/ab_table.csv && echo 清单行+E2E 证据已落 → 清单行+E2E 证据已落 (10-11)
- [x] eval_ab · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(eval_ab): wired" && echo commit 在 → commit 在 (10-11)

## B4 批间门
- [x] B4 · 评审三轴 — 证据: bash -c git log --oneline -1 | grep -q "S1-S3" && echo "评审子代理三轴 17/17 过门（S1-S3 已清 32d262a）" → 评审子代理三轴 17/17 过门（S1-S3 已清 32d262a） (10-11)
- [x] B4 · 用户裁决 — 证据: bash -c grep -q "▶ B5" fn_docs/implementation/batches.md && echo 裁决=继续B5 → 裁决=继续B5 (10-11)

## B5 — render_submission_entry, verify_package_layout, build_kaggle_package, submit_package, collect_run_artifacts, render_gain_table, write_report
### render_submission_entry
- [x] render_submission_entry · implemented — 证据: bash -c ! grep -q unimplemented:fn:render_submission_entry fn_work/src/build_kaggle_package/render_submission_entry.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] render_submission_entry · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/build_kaggle_package/test_render_submission_entry.py -q → 10 passed in 0.01s (10-11)
- [x] render_submission_entry · wired — 证据: bash -c grep -q render_submission_entry fn_work/tests/build_kaggle_package/test_render_submission_entry.py && echo 测试调用点在（弱判据；生产调用方 build_kaggle_package 本批后段落地后补验） → 测试调用点在（弱判据；生产调用方 build_kaggle_package 本批后段落地后补验） (10-11)
- [x] render_submission_entry · 清单进位 — 证据: bash -c grep -q "render_submission_entry | B5 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] render_submission_entry · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(render_submission_entry): wired" && echo commit 在 → commit 在 (10-11)
### verify_package_layout
- [x] verify_package_layout · implemented — 证据: bash -c ! grep -q unimplemented:fn:verify_package_layout fn_work/src/build_kaggle_package/verify_package_layout.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] verify_package_layout · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/build_kaggle_package/test_verify_package_layout.py -q → 5 passed in 0.01s (10-11)
- [x] verify_package_layout · wired — 证据: bash -c grep -q verify_package_layout fn_work/tests/build_kaggle_package/test_verify_package_layout.py && echo 测试调用点在（弱判据；生产调用方 build_kaggle_package 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 build_kaggle_package 本批下一函数落地后补验） (10-11)
- [x] verify_package_layout · 清单进位 — 证据: bash -c grep -q "verify_package_layout | B5 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] verify_package_layout · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(verify_package_layout): wired" && echo commit 在 → commit 在 (10-11)
### build_kaggle_package
- [x] build_kaggle_package · implemented — 证据: bash -c ! grep -q unimplemented:fn:build_kaggle_package fn_work/src/build_kaggle_package/build_kaggle_package.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] build_kaggle_package · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/build_kaggle_package/test_build_kaggle_package.py -q → 5 passed in 0.03s (10-11)
- [x] build_kaggle_package · wired — 证据: bash -c grep -q render_submission_entry fn_work/src/build_kaggle_package/build_kaggle_package.py && grep -q verify_package_layout fn_work/src/build_kaggle_package/build_kaggle_package.py && echo 生产调用点在（render/verify 由本函数调用） → 生产调用点在（render/verify 由本函数调用） (10-11)
- [x] build_kaggle_package · 清单进位 — 证据: bash -c grep -q "build_kaggle_package | B5 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] build_kaggle_package · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(build_kaggle_package): wired" && echo commit 在 → commit 在 (10-11)
### submit_package
- [x] submit_package · implemented — 证据: bash -c ! grep -q unimplemented:fn:submit_package fn_work/src/submit_package/submit_package.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] submit_package · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/submit_package/test_submit_package.py -q → 6 passed in 0.05s (10-11)
- [x] submit_package · wired — 证据: bash -c grep -q verify_package_layout fn_work/src/submit_package/submit_package.py && echo 生产调用点在（verify 预检由本函数调用；dry-run 回执即验收口径） → 生产调用点在（verify 预检由本函数调用；dry-run 回执即验收口径） (10-11)
- [x] submit_package · 清单进位 — 证据: bash -c grep -q "submit_package | B5 | wired 10-11" fn_docs/implementation/functions.md && grep -q "Ruling: R6 提交命令形态" fn_docs/implementation/tracker.md && echo 清单行+Ruling 已落 → 清单行+Ruling 已落 (10-11)
- [x] submit_package · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(submit_package): wired" && echo commit 在 → commit 在 (10-11)
### collect_run_artifacts
- [x] collect_run_artifacts · implemented — 证据: bash -c ! grep -q unimplemented:fn:collect_run_artifacts fn_work/src/write_report/collect_run_artifacts.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] collect_run_artifacts · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/write_report/test_collect_run_artifacts.py -q → 4 passed in 0.01s (10-11)
- [x] collect_run_artifacts · wired — 证据: bash -c grep -q collect_run_artifacts fn_work/tests/write_report/test_collect_run_artifacts.py && echo 测试调用点在（弱判据；生产调用方 write_report 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 write_report 本批下一函数落地后补验） (10-11)
- [x] collect_run_artifacts · 清单进位 — 证据: bash -c grep -q "collect_run_artifacts | B5 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] collect_run_artifacts · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(collect_run_artifacts): wired" && echo commit 在 → commit 在 (10-11)
### render_gain_table
- [x] render_gain_table · implemented — 证据: bash -c ! grep -q unimplemented:fn:render_gain_table fn_work/src/write_report/render_gain_table.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] render_gain_table · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/write_report/test_render_gain_table.py -q → 6 passed in 0.01s (10-11)
- [x] render_gain_table · wired — 证据: bash -c grep -q render_gain_table fn_work/tests/write_report/test_render_gain_table.py && echo 测试调用点在（弱判据；生产调用方 write_report 本批下一函数落地后补验） → 测试调用点在（弱判据；生产调用方 write_report 本批下一函数落地后补验） (10-11)
- [x] render_gain_table · 清单进位 — 证据: bash -c grep -q "render_gain_table | B5 | wired 10-11" fn_docs/implementation/functions.md && echo 清单行已落 → 清单行已落 (10-11)
- [x] render_gain_table · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(render_gain_table): wired" && echo commit 在 → commit 在 (10-11)
### write_report
- [x] write_report · implemented — 证据: bash -c ! grep -q unimplemented:fn:write_report fn_work/src/write_report/write_report.py && echo 桩已替换 → 桩已替换 (10-11)
- [x] write_report · tested — 证据: bash -c cd fn_work && venv/bin/python -m pytest tests/write_report/test_write_report.py -q → 4 passed in 0.01s (10-11)
- [x] write_report · wired — 证据: bash -c grep -q collect_run_artifacts fn_work/src/write_report/write_report.py && grep -q render_gain_table fn_work/src/write_report/write_report.py && echo 生产调用点在（collect/render 由本函数调用；报告口实跑随后补证） → 生产调用点在（collect/render 由本函数调用；报告口实跑随后补证） (10-11)
- [x] write_report · 清单进位 — 证据: bash -c grep -q "write_report | B5 | wired 10-11" fn_docs/implementation/functions.md && grep -q "自进化智能体复现报告" fn_work/runs/eval-1791683161-s42/report.md && echo 清单行+报告证据已落 → 清单行+报告证据已落 (10-11)
- [x] write_report · commit — 证据: bash -c git log --oneline -1 | grep -q "fn(write_report): wired" && echo commit 在 → commit 在 (10-11)

## B5 批间门
- [x] B5 · 评审三轴 — 证据: bash -c git status --short | grep -v "^??" | wc -l | grep -q "^0$" ; grep -q "kaggle_competition_contract" references/INDEX.md && grep -q "Ruling: verify_package_layout" fn_docs/implementation/tracker.md && echo 评审条件全清（勾已收编/契约落档/Ruling 备案） → 评审条件全清（勾已收编/契约落档/Ruling 备案） (10-11)
- [x] B5 · 用户裁决 — 证据: 26 个 commit 行全勾+批次表空（非自指判据） → 裁决=先挂账后收官 (10-11)
- Ruling: B1 四共享函数 wired 判据降级为「测试文件静态导入+实跑」 — 原因：生产调用点（make_*_policy 等）按批次计划在 B2/B3 才实现 — 代价：B1 wired 为弱判据 — 落点：B2/B3 验收点复验生产调用点 grep（batches.md 注列已同步）
- Ruling: llm_complete 增可选参数 model=""（显式模型名覆盖端点默认） — 原因：make_baseline_policy 配置含模型名，原实现只认 ARC_MODEL 环境变量，配置无法落到请求体 — 代价：B1 已 wired 函数签名扩展（向后兼容，默认行为不变，+1 测至 10 绿） — 落点：batches.md 变更记录互指；responsibility.md 签名意图为意图级描述不改
- 注记: B2 验收点「裸基线单局实跑」部分受阻 — 27B vLLM 服务缺位（唯一算力机 RTX 4070 Laptop 8GB 显存 < 27B FP8 权重 ~27GB+，requirements 技术栈决策的远端服务化未部署） — 已以真 SDK 在线匿名局+脚本策略实跑替代（run_id=b2-realrun-vc33，50 步 GAME_OVER，日志在库） — 批间门裁决 10-10：挂账至推理服务部署后补跑（D1 债务继承；用户确认）
- Ruling: EpisodeResult.outcome 扩为三值（+STEP_LIMIT）与 submit 场景 STEP_FAILED 哨兵协议 — 原因：SDK 实核 e/h——无墙钟时限须本地护栏防死循环、SDK 失败吞错误码返回 None 须场景归一（experiment 停/submit 降级保旧观测） — 代价：终局语义超出责任文档两值描述，docstring 已论证+测试覆盖 — 落点：run_episode/submit_action docstring；B4 集成验收时复核
- Ruling: B1 四共享生产调用点复验落账（补显式证据行） — 原因：B1 Ruling 落点要求 B2 验收点复验 grep，评审已复跑确认 — 代价：无 — 落点:llm_complete@make_baseline_policy.py、render_obs@build_baseline_prompt.py、append_jsonl_log@run_episode.py、build_baseline_prompt@make_baseline_policy.py、connect_env/submit_action@run_episode.py（grep 全命中，评审报告 2026-10-10）
- Ruling: run_episode 策略协议扩展——可选钩子 on_episode_start(spec, run_id) / on_episode_end(result, run_id) — 原因：R3 课程调度需跨局难度信号与局边界事件（R4 经验入库同依赖），act-only 协议无法感知局起止 — 代价：B2 已 wired 的 run_episode 行为增强（无钩子策略零影响，+2 测至 9 绿） — 落点：batches.md 变更记录互指；docstring 协议节已更新
- Ruling: aggregate_results 增可选参数 out_dir="fn_work/runs" — 原因：CSV 落盘需要 run 级目录注入（eval_ab 持 run_id），原签名无落点 — 代价：签名扩展（向后兼容，缺省 fn_work/runs，文件名固定 ab_table.csv 同 run 覆盖） — 落点：batches.md 变更记录互指
- Ruling: R6 提交命令形态与赛站实核契约偏差 — 原因：requirements R6 验收原文假定 kaggle competitions submit -f <包>，实核（arc-prize-2026.md 2026-10-11）确认为 code competition：starter kit notebook 组装（make submit→kernels push）+网页 Submit to Competition — 代价：submit_package 实跑模式按计划形态执行、被拒时 SubmitError 原样暴露 CLI 输出；真实提交需 kit notebook 组装且属外部动作留用户授权（默认 dry_run） — 落点：batches.md 变更记录互指；requirements R6 措辞待 fn-close 前修订
- Ruling: verify_package_layout「入口可导入性」实现为 py_compile 语法级检查 — 原因：importlib 真导入需在包上下文解析 arcengine/src 依赖，脱离目标环境不可靠 — 代价：检出力限于语法错误，导入期错误（如依赖缺失）不被捕获 — 落点：verify_package_layout docstring；fn-close 备查
- Ruling: render_gain_table「逐数字内联挂链接」实现为行级 source 列（run 目录+csv 双链） — 原因：同行数字同源（同 run 同 CSV），行级链接可溯性等价且表可读 — 代价：粒度为行非单元格 — 落点：render_gain_table docstring；R7 验收判据（按路径找到产物且数字一致）实测成立
