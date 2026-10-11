# functions.md —— 函数级实现清单（唯一状态真值）
> fn-implement 独占更新。**代码是真值，本表只是导航。**
> **改任何状态前必须先跑核验命令、在对话中贴出输出，绿了才许改。**
> **改后读回贴出改后行（读回断言）：脚本/命令打印成功不算写入证据，落盘的字节才算。**

| 函数 | 批次 | 状态(日期) | 核验命令+摘要 | commit |
|---|---|---|---|---|
| llm_complete | B1 | wired 10-10；B2 签名微调 10-10 | pytest tests/shared/test_llm_complete.py → 10 passed（+可选 model 覆盖参数，tracker Ruling 行已记） | 本批 |
| render_obs | B1 | wired 10-10；B2 债务②清 10-10 | pytest tests/shared/test_render_obs.py → 22 passed（稳定序列化/截断边界/REQUIRED_FIELDS 六字段回填+逐字段缺失报错/docstring 截断措辞修正） | 本批 |
| append_jsonl_log | B1 | wired 10-10 | pytest → 6 passed（原子追加/镜像/LogWriteError） | 本批 |
| load_episode_set | B1 | wired 10-10；B2 债务①清 10-10 | pytest tests/shared/test_load_episode_set.py → 14 passed（+known_episode_ids 局 ID 存在性校验：精确/短名基础名匹配/未命中报错/不注入跳过） | 本批 |
| build_baseline_prompt | B2 | wired 10-10 | pytest tests/make_baseline_policy/test_build_baseline_prompt.py → 7 passed（固定模板常量/render_obs 视图一致/确定性/异常透传/预算接线/模板协议守卫） | 本批 |
| make_baseline_policy | B2 | wired 10-10 | pytest tests/make_baseline_policy/test_make_baseline_policy.py → 14 passed（构造校验/解析+确定性回退/usage 累计/异常透传/model 透传） | 本批 |
| connect_env | B2 | wired 10-10 | pytest tests/run_episode/test_connect_env.py → 10 passed（假 SDK 注入/真 FrameDataRaw 归一化/make·reset 判空与异常包装/spec 校验） | 本批 |
| submit_action | B2 | wired 10-10 | pytest tests/run_episode/test_submit_action.py → 14 passed（结构校验+错误码/None 场景归一 experiment 抛·submit 哨兵/跨模块动作名守卫） | 本批 |
| run_episode | B2 | wired 10-10；B3 钩子扩展 10-11 | pytest tests/run_episode/test_run_episode.py → 9 passed（+可选 on_episode_start/end 钩子，R3/R4 包装局边界信号，Ruling 已记）；实跑：真 SDK vc33 匿名局 50 步 GAME_OVER（策略为脚本件——27B vLLM 缺位，D1 挂账） | 本批 |
| estimate_difficulty | B3 | wired 10-11 | pytest tests/make_curriculum_policy/test_estimate_difficulty.py → 8 passed（公式分量/钳制/空记录低置信/纯函数/脏记录容错） | 本批 |
| select_experience_source | B3 | wired 10-11 | pytest tests/make_curriculum_policy/test_select_experience_source.py → 10 passed（先易后难+利用计数 score 决胜/平手链/理由串/池校验/确定性） | 本批 |
| make_curriculum_policy | B3 | wired 10-11 | pytest tests/make_curriculum_policy/test_make_curriculum_policy.py → 10 passed（选源落日志/obs 注入转发/局终回填难度/轮转/确定性） | 本批 |
| update_experience_store | B3 | wired 10-11 | pytest tests/make_regularized_policy/test_update_experience_store.py → 9 passed（入库字段/截断标志/容量淘汰最旧/旧条目零改动/空库起库/校验） | 本批 |
| regularize_experience | B3 | wired 10-11 | pytest tests/make_regularized_policy/test_regularize_experience.py → 9 passed（打分截断/相关性·新近度·去重/逐条取舍日志/浅拷贝隔离/确定性） | 本批 |
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
