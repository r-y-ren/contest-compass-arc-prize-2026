# functions.md —— 函数级实现清单（唯一状态真值）
> fn-implement 独占更新。**代码是真值，本表只是导航。**
> **改任何状态前必须先跑核验命令、在对话中贴出输出，绿了才许改。**
> **改后读回贴出改后行（读回断言）：脚本/命令打印成功不算写入证据，落盘的字节才算。**

| 函数 | 批次 | 状态(日期) | 核验命令+摘要 | commit |
|---|---|---|---|---|
| llm_complete | B1 | wired 10-10 | pytest tests/shared/test_llm_complete.py → 9 passed（experiment 抛错/submit 重试降级全覆盖） | 本批 |
| render_obs | B1 | stub 2026-10-10 | 测试: tests/shared/test_render_obs.py | — |
| append_jsonl_log | B1 | stub 2026-10-10 | 测试: tests/shared/test_append_jsonl_log.py | — |
| load_episode_set | B1 | stub 2026-10-10 | 测试: tests/shared/test_load_episode_set.py | — |
| build_baseline_prompt | B2 | stub 2026-10-10 | 上游覆盖: make_baseline_policy | — |
| make_baseline_policy | B2 | stub 2026-10-10 | 测试: tests/make_baseline_policy/test_make_baseline_policy.py；集成继承 R2 | — |
| connect_env | B2 | stub 2026-10-10 | 上游覆盖: run_episode | — |
| submit_action | B2 | stub 2026-10-10 | 上游覆盖: run_episode | — |
| run_episode | B2 | stub 2026-10-10 | 测试: tests/run_episode/test_run_episode.py；集成继承 R1 | — |
| estimate_difficulty | B3 | stub 2026-10-10 | 测试: tests/make_curriculum_policy/test_estimate_difficulty.py | — |
| select_experience_source | B3 | stub 2026-10-10 | 测试: tests/make_curriculum_policy/test_select_experience_source.py | — |
| make_curriculum_policy | B3 | stub 2026-10-10 | 测试: tests/make_curriculum_policy/test_make_curriculum_policy.py；集成继承 R3 | — |
| update_experience_store | B3 | stub 2026-10-10 | 测试: tests/make_regularized_policy/test_update_experience_store.py | — |
| regularize_experience | B3 | stub 2026-10-10 | 测试: tests/make_regularized_policy/test_regularize_experience.py | — |
| make_regularized_policy | B3 | stub 2026-10-10 | 测试: tests/make_regularized_policy/test_make_regularized_policy.py；集成继承 R4 | — |
| build_config_matrix | B4 | stub 2026-10-10 | 测试: tests/eval_ab/test_build_config_matrix.py | — |
| run_config_batch | B4 | stub 2026-10-10 | 上游覆盖: eval_ab | — |
| aggregate_results | B4 | stub 2026-10-10 | 测试: tests/eval_ab/test_aggregate_results.py | — |
| eval_ab | B4 | stub 2026-10-10 | 测试: tests/eval_ab/test_eval_ab.py；集成=R5: python eval_ab.py --episodes N --seed S 两跑同向 | — |
| render_submission_entry | B5 | stub 2026-10-10 | 上游覆盖: build_kaggle_package | — |
| verify_package_layout | B5 | stub 2026-10-10 | 测试: tests/build_kaggle_package/test_verify_package_layout.py | — |
| build_kaggle_package | B5 | stub 2026-10-10 | 测试: tests/build_kaggle_package/test_build_kaggle_package.py；集成继承 R6 | — |
| submit_package | B5 | stub 2026-10-10 | 集成继承 R6: kaggle submit 回执 | — |
| collect_run_artifacts | B5 | stub 2026-10-10 | 测试: tests/write_report/test_collect_run_artifacts.py | — |
| render_gain_table | B5 | stub 2026-10-10 | 上游覆盖: write_report | — |
| write_report | B5 | stub 2026-10-10 | 测试: tests/write_report/test_write_report.py；可观察判据继承 R7 | — |
