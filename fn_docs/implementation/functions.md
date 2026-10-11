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
| make_baseline_policy | B2 | wired 10-10 | pytest tests/make_baseline_policy/test_make_baseline_policy.py → 15 passed（构造校验/解析+确定性回退/usage 累计/异常透传/model 透传；B4 树外修复 +1：fallback ACTION6 补坐标） | 本批 |
| connect_env | B2 | wired 10-10 | pytest tests/run_episode/test_connect_env.py → 10 passed（假 SDK 注入/真 FrameDataRaw 归一化/make·reset 判空与异常包装/spec 校验） | 本批 |
| submit_action | B2 | wired 10-10 | pytest tests/run_episode/test_submit_action.py → 14 passed（结构校验+错误码/None 场景归一 experiment 抛·submit 哨兵/跨模块动作名守卫） | 本批 |
| run_episode | B2 | wired 10-10；B3 钩子扩展 10-11 | pytest tests/run_episode/test_run_episode.py → 11 passed（+钩子 2 测/D2 obs_summary/用量差值防跨局重复计数——B4 评审 S3 修复）；实跑：真 SDK vc33 匿名局 50 步 GAME_OVER（策略为脚本件——27B vLLM 缺位，D1 挂账） | 本批 |
| estimate_difficulty | B3 | wired 10-11 | pytest tests/make_curriculum_policy/test_estimate_difficulty.py → 8 passed（公式分量/钳制/空记录低置信/纯函数/脏记录容错） | 本批 |
| select_experience_source | B3 | wired 10-11 | pytest tests/make_curriculum_policy/test_select_experience_source.py → 10 passed（先易后难+利用计数 score 决胜/平手链/理由串/池校验/确定性） | 本批 |
| make_curriculum_policy | B3 | wired 10-11 | pytest tests/make_curriculum_policy/test_make_curriculum_policy.py → 10 passed（选源落日志/obs 注入转发/局终回填难度/轮转/确定性） | 本批 |
| update_experience_store | B3 | wired 10-11 | pytest tests/make_regularized_policy/test_update_experience_store.py → 9 passed（入库字段/截断标志/容量淘汰最旧/旧条目零改动/空库起库/校验） | 本批 |
| regularize_experience | B3 | wired 10-11 | pytest tests/make_regularized_policy/test_regularize_experience.py → 9 passed（打分截断/相关性·新近度·去重/逐条取舍日志/浅拷贝隔离/确定性） | 本批 |
| make_regularized_policy | B3 | wired 10-11 | pytest tests/make_regularized_policy/test_make_regularized_policy.py → 9 passed（经验注入转发/两版入库：原始关键步+正则决策 JSONL/跨局累积容量淘汰/构造校验） | 本批 |
| build_config_matrix | B4 | wired 10-11 | pytest tests/eval_ab/test_build_config_matrix.py → 14 passed（默认四配置全因子/规范化参数缺省/纯函数/声明校验七态） | 本批 |
| run_config_batch | B4 | wired 10-11 | pytest tests/eval_ab/test_run_config_batch.py → 7 passed（四组合包装层序/指标数学/任一局失败中止附局 ID/构造失败中止/空局集） | 本批 |
| aggregate_results | B4 | wired 10-11 | pytest tests/eval_ab/test_aggregate_results.py → 8 passed（增益列对 baseline/CSV 落盘 out_dir/文本表对齐/缺列与无 baseline 报错）；签名微调：+可选 out_dir（Ruling 已记） | 本批 |
| eval_ab | B4 | wired 10-11 | pytest tests/eval_ab/test_eval_ab.py → 11 passed；端到端实跑：真 CLI+真 SDK 2 局（vc33/cd82）+假 vLLM 存根（真 HTTP 200 次调用），对照表 stdout+CSV 入库 fn_work/runs/eval-1791683161-s42/ | 本批 |
| render_submission_entry | B5 | wired 10-11 | pytest tests/build_kaggle_package/test_render_submission_entry.py → 10 passed（契约驱动渲染/名字与 dict 双解析/AST 语法合法/显式模板须完整） | 本批 |
| verify_package_layout | B5 | wired 10-11 | pytest tests/build_kaggle_package/test_verify_package_layout.py → 5 passed（完整包过/缺件清单化不抛/入口编译错捕获） | 本批 |
| build_kaggle_package | B5 | wired 10-11 | pytest tests/build_kaggle_package/test_build_kaggle_package.py → 5 passed（真实组包/冻结记录/requirements 派生滤测试依赖/幂等重建） | 本批 |
| submit_package | B5 | wired 10-11 | pytest tests/submit_package/test_submit_package.py → 6 passed（预检拒/重试耗尽附原始输出/三连败恢复）；dry-run 实跑回执 verified=true（arc-prize-2026-arc-agi-3）；R6 验收命令偏差 Ruling 已记 | 本批 |
| collect_run_artifacts | B5 | wired 10-11 | pytest tests/write_report/test_collect_run_artifacts.py → 4 passed（表解析/无表 run/只读性/空目录与缺失报错） | 本批 |
| render_gain_table | B5 | wired 10-11 | pytest tests/write_report/test_render_gain_table.py → 6 passed（markdown 结构/行级溯源链接/多 run 确定性/索引缺项报错） | 本批 |
| write_report | B5 | wired 10-11 | pytest tests/write_report/test_write_report.py → 4 passed（三节结构/数字核对宁停勿错/索引缺项）；实跑：库内 E2E 产物出真报告 runs/eval-1791683161-s42/report.md | 本批 |
