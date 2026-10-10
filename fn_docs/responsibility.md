# 责任文档：ARC-AGI-3 自进化智能体复现（复现优先）
> 由 fn-divide 产出与独占更新；fn-implement 只读。进度与状态见 implementation.md。
> 职责字段是**重写规约**：凭职责详述 + 签名意图（输入/输出），必须能完美复现该函数功能。
> ⚠ 实现期发现结构性变化（函数增/删/拆/并/职责或调用关系变化）必须回本阶段改本文档。
> 存量探查结论（规则 4）：本战役为全新代码库，无既有函数可改——全部 [新增]；ActiveSaddler/RRSI 官方仓以 fork 冻结方式作外部依赖引用，不作改造对象。

## 结构概览（纯结构，不带职责）
- run_episode ← R1
  - connect_env
  - submit_action
- make_baseline_policy ← R2
  - build_baseline_prompt
- make_curriculum_policy ← R3
  - select_experience_source
    - estimate_difficulty
- make_regularized_policy ← R4
  - update_experience_store
  - regularize_experience
- eval_ab ← R5
  - build_config_matrix
  - run_config_batch
  - aggregate_results
- build_kaggle_package ← R6
  - render_submission_entry
  - verify_package_layout
  - submit_package
- write_report ← R7
  - collect_run_artifacts
  - render_gain_table

## 需求覆盖矩阵（P1 在 R 号后标注；非功能约束不进矩阵，fn-close 终检对照 requirements 非功能节）
| 需求 | 顶层函数 |
|---|---|
| R1 | run_episode |
| R2 | make_baseline_policy |
| R3 | make_curriculum_policy |
| R4 | make_regularized_policy |
| R5 | eval_ab |
| R6 | build_kaggle_package, submit_package |
| R7 | write_report |

## 共享函数（shared/：多顶层共用；矩阵挂全部受益需求）
- **llm_complete**（调用方：make_baseline_policy, make_regularized_policy, make_curriculum_policy 内层策略）
  - 职责：对远端 vLLM 服务发一次对话补全请求：拼请求体（模型名/消息列表/采样参数）、发送、解析回复文本；失败按场景哲学处置（实验态抛错码停，提交态有限重试）；记录请求耗时与 token 用量。
  - 签名意图：输入: messages 列表 + 采样参数 + 场景标记（experiment|submit）/ 输出: 回复文本 + 用量统计 / 错误: 服务不可达/超时/非 200 → 实验态抛 LLMServiceError，提交态重试耗尽降级返回安全回退动作文本
  - tested 策略：自有单测（mock HTTP）
  - 核验命令：测试: tests/test_llm_complete.py
- **render_obs**（调用方：build_baseline_prompt, regularize_experience, render_submission_entry）
  - 职责：把官方 SDK 的观测对象转成提示词可用的文本视图（局面序列化 + 可选截断），格式稳定可复现。
  - 签名意图：输入: SDK 观测对象 + 长度预算 / 输出: 文本视图 / 错误: 观测缺字段 → ObsFormatError（带字段名）
  - tested 策略：自有单测
  - 核验命令：测试: tests/test_render_obs.py
- **append_jsonl_log**（调用方：run_episode, run_config_batch, submit_package）
  - 职责：向当日 JSONL 日志文件原子追加一条结构化记录（时间戳+事件类型+载荷），保证进程内外可并发追加不丢行；同时镜像到控制台。
  - 签名意图：输入: run_id/事件类型/载荷字典 / 输出: 无（副作用写盘）/ 错误: 磁盘失败 → LogWriteError（不吞异常）
  - tested 策略：自有单测
  - 核验命令：测试: tests/test_jsonl_log.py
- **load_episode_set**（调用方：eval_ab, build_kaggle_package）
  - 职责：读取局集配置（局 ID 列表+种子），校验引用的局在官方 SDK 中存在，返回规范化局集对象。
  - 签名意图：输入: 配置文件路径 / 输出: 局集对象（episode_ids, seed）/ 错误: 配置缺失/局 ID 无效 → ConfigError
  - tested 策略：自有单测
  - 核验命令：测试: tests/test_episode_set.py

## 功能块 run_episode ← R1
R1 要求接入官方 ARC-AGI-3 SDK 并实现 obs→LLM→action 主循环：输入为 SDK 观测流，输出为每步合法 action 与局终状态，非法动作/超时按 SDK 错误码记录；验收=指定局集 N≥20 局零未捕获异常且日志含每步 obs 摘要/action/耗时。本块只管"跑一局"的通用循环，策略由 R2-R4 的工厂注入。

- **run_episode** [L0|新增]
  - 职责：执行一局完整交互：连接环境后进入步循环——取观测、调注入策略的 act 得动作、提交动作、写步日志；收到终局信号后汇总 EpisodeResult（局 ID、结局、步数、总耗时、token 用量）。策略抛出的实验态异常不捕获（失败即停哲学由上层场景决定）。
  - 签名意图：输入: episode spec（局 ID+种子）、策略对象、run_id / 输出: EpisodeResult / 错误: SDK 连接失败→EnvError；策略异常透传
  - 调用方：程序入口（单局调试）、run_config_batch
  - tested 策略：自有单测（假环境+假策略）
  - 核验命令：测试: tests/test_run_episode.py；集成继承 R1 验收（见 eval_ab 集成跑）
  - **connect_env** [L1|新增]
    - 职责：按 episode spec 初始化官方 SDK 环境句柄（锁定 SDK 版本，取得初始观测），返回环境句柄。
    - 签名意图：输入: episode spec / 输出: env 句柄 + 初始观测 / 错误: SDK 异常包装为 EnvError（带局 ID）
    - 调用方：run_episode
    - tested 策略：上游覆盖: run_episode
    - 核验命令：上游覆盖: run_episode
  - **submit_action** [L1|新增]
    - 职责：向环境提交一步动作并接收返回：合法→下一观测/终局信号；非法动作/超时→按 SDK 错误码记录日志并按场景处置（实验态停、提交态请求安全回退）。
    - 签名意图：输入: env 句柄 + action + 场景标记 / 输出: 下一观测或终局信号 / 错误: 非法动作→IllegalActionError（含错误码）
    - 调用方：run_episode
    - tested 策略：上游覆盖: run_episode
    - 核验命令：上游覆盖: run_episode

## 功能块 make_baseline_policy ← R2
R2 要求最小裸基线：vLLM 冻结 27B + 固定提示词、无任何自进化组件，作为一切对比起点；验收=eval_ab.py baseline 模式产出成功率与平均步数、同 seed 两跑一致。

- **make_baseline_policy** [L0|新增]
  - 职责：构造裸基线策略对象：act(obs)＝固定提示词＋当前观测渲染→llm_complete→解析出动作；无记忆、无经验、无课程。同输入同 seed 输出确定（采样参数固定并记入日志）。
  - 签名意图：输入: 配置（模型名/采样参数/场景标记）/ 输出: 策略对象（含 act 方法）/ 错误: 配置缺字段→ConfigError
  - 调用方：run_episode（经 eval_ab 配置矩阵注入）、render_submission_entry
  - tested 策略：自有单测（mock llm_complete）
  - 核验命令：测试: tests/test_baseline_policy.py；集成继承 R2 验收（eval_ab --config baseline）
  - **build_baseline_prompt** [L1|新增]
    - 职责：拼装固定系统提示词＋render_obs 观测视图为消息列表；模板文本为常量，改动须记 requirements 变更。
    - 签名意图：输入: 观测对象 / 输出: messages 列表 / 错误: render_obs 异常透传
    - 调用方：make_baseline_policy
    - tested 策略：上游覆盖: make_baseline_policy
    - 核验命令：上游覆盖: make_baseline_policy

## 功能块 make_curriculum_policy ← R3
R3 为 ActiveSaddler 课程调度的降级实现（作用于练习局编排层，不动权重）：按局历史难度信号选择下一经验源；验收=A/B 表中 baseline+R3 相对 baseline 变化方向有输出、组件决策每步落日志。

- **make_curriculum_policy** [L0|新增]
  - 职责：构造课程调度策略（包装内层策略，默认包装 baseline）：跨局维护难度信号与经验源池，每局开始前由 select_experience_source 选定本局经验源（如提示中的示例局选择），把选择与理由写入日志；局内行为转发内层策略。
  - 签名意图：输入: 内层策略 + 课程配置 / 输出: 包装策略对象 / 错误: 内层策略接口不符→PolicyWrapError
  - 调用方：run_episode（经配置矩阵注入）、render_submission_entry
  - tested 策略：自有单测
  - 核验命令：测试: tests/test_curriculum_policy.py；集成继承 R3 验收（eval_ab 对照行）
  - **select_experience_source** [L1|新增]
    - 职责：依据各候选经验源的难度估计与已选历史，选出下一局使用的经验源；策略为 ActiveSaddler 论文思路的编排层降级（先易后难+利用计数），决策可解释并逐次返回理由字符串。
    - 签名意图：输入: 经验源难度表 + 已选历史 / 输出: 经验源 ID + 理由 / 错误: 池空→CurriculumError
    - 调用方：make_curriculum_policy
    - tested 策略：自有单测
    - 核验命令：测试: tests/test_select_experience_source.py
    - **estimate_difficulty** [L2|新增]
      - 职责：从某经验源的历史局记录（成功率/步数/尝试次数）计算标量难度信号；纯函数、无副作用。
      - 签名意图：输入: 历史局记录列表 / 输出: 难度标量 / 错误: 记录为空→返回默认难度并标注低置信
      - 调用方：select_experience_source
      - tested 策略：自有单测
      - 核验命令：测试: tests/test_estimate_difficulty.py

## 功能块 make_regularized_policy ← R4
R4 为 RRSI 经验更新正则的降级实现（作用于经验记忆层，不动权重）：局终把经验入库、入提示前筛选/正则化；验收=A/B 表对照行 + 决策日志。

- **make_regularized_policy** [L0|新增]
  - 职责：构造经验正则策略（包装内层策略）：维护经验库，每步 act 时取 regularize_experience 输出的经验子集并入提示；局终调 update_experience_store 入库本局经验（保留原始与正则两版）。
  - 签名意图：输入: 内层策略 + 记忆配置（容量/正则参数）/ 输出: 包装策略对象 / 错误: PolicyWrapError
  - 调用方：run_episode（经配置矩阵注入）、render_submission_entry
  - tested 策略：自有单测
  - 核验命令：测试: tests/test_regularized_policy.py；集成继承 R4 验收（eval_ab 对照行）
  - **update_experience_store** [L1|新增]
    - 职责：把一局的结局与关键步序列写入经验库（带时间戳与局 ID），按容量上限淘汰最旧；只写不改旧条目。
    - 签名意图：输入: EpisodeResult + 关键步摘要 + 经验库 / 输出: 更新后的经验库 / 错误: 摘要超限→截断并记录截断标志
    - 调用方：make_regularized_policy
    - tested 策略：自有单测
    - 核验命令：测试: tests/test_experience_store.py
  - **regularize_experience** [L1|新增]
    - 职责：从经验库生成本步入提示的经验子集：按相关性/新近度/去重正则打分截断（RRSI 论文思路的记忆层降级），输出子集与逐条取舍理由。
    - 签名意图：输入: 经验库 + 当前观测 + 预算 / 输出: 经验子集 + 取舍日志 / 错误: 库空→返回空子集（首局冷启动）
    - 调用方：make_regularized_policy
    - tested 策略：自有单测
    - 核验命令：测试: tests/test_regularize_experience.py

## 功能块 eval_ab ← R5
R5 为 A/B 评测总入口：同局集同种子跑 ≥4 配置（baseline/+课程/+正则/全开），失败即停，输出 CSV+控制台对照表；验收=两独立运行增益方向一致。

- **eval_ab** [L0|新增]
  - 职责：评测主流程：load_episode_set 载局集 → build_config_matrix 展开配置 → 逐配置 run_config_batch（实验态异常哲学：任何失败立即终止整跑并报错误码）→ aggregate_results 出表；全程写 run 级日志与产物索引。
  - 签名意图：输入: --episodes N --seed S --configs …（CLI 参数）/ 输出: 对照表（CSV+stdout）+ runs 产物目录 / 错误: 任一配置失败→ExperimentAbortError（非零退出码）
  - 调用方：程序入口（eval_ab.py main）
  - tested 策略：自有单测（小局集端到端，假 LLM）
  - 核验命令：测试: tests/test_eval_ab.py；集成=R5 验收原文：`python eval_ab.py --episodes N --seed S` 输出四行对照表，两次独立运行增益方向一致
  - **build_config_matrix** [L1|新增]
    - 职责：由配置声明展开为待跑配置列表（名字→策略工厂组合+场景标记=experiment）；纯函数。
    - 签名意图：输入: 配置声明（默认四配置）/ 输出: 配置列表 / 错误: 声明非法→ConfigError
    - 调用方：eval_ab
    - tested 策略：自有单测
    - 核验命令：测试: tests/test_config_matrix.py
  - **run_config_batch** [L1|新增]
    - 职责：单配置跑完整个局集：逐局调 run_episode、逐局写日志与结果、失败即抛停；返回该配置指标（成功率/平均步数/token 用量/耗时）。
    - 签名意图：输入: 配置 + 局集 + run_id / 输出: 配置指标 + 逐局结果列表 / 错误: 任一局失败→ExperimentAbortError（附局 ID）
    - 调用方：eval_ab
    - tested 策略：上游覆盖: eval_ab
    - 核验命令：上游覆盖: eval_ab
  - **aggregate_results** [L1|新增]
    - 职责：把各配置指标汇成对照表并计算相对 baseline 的增益列；输出 CSV 文件与对齐的控制台表；纯函数。
    - 签名意图：输入: 各配置指标字典列表 / 输出: 对照表（CSV 路径+文本）/ 错误: 指标缺列→ReportDataError
    - 调用方：eval_ab
    - tested 策略：自有单测
    - 核验命令：测试: tests/test_aggregate_results.py

## 功能块 build_kaggle_package ← R6
R6 为提交件：按赛站契约打包最优配置（提交态异常=有限重试→降级继续）；验收=kaggle CLI 提交成功且赛站可查接收。

- **build_kaggle_package** [L0|新增]
  - 职责：打包主流程：选定最优配置（由对照表指定或参数传入）→ render_submission_entry 生成入口 → verify_package_layout 自检 → 落成可提交包目录（含依赖清单与冻结 commit 记录）。
  - 签名意图：输入: 最优配置名 + 输出目录 / 输出: 包目录路径 / 错误: 契约校验失败→PackageError
  - 调用方：程序入口（打包脚本）
  - tested 策略：自有单测（假契约）
  - 核验命令：测试: tests/test_kaggle_package.py；集成继承 R6 验收（submit_package 后赛站可查）
  - **render_submission_entry** [L1|新增]
    - 职责：按赛站提交契约渲染入口文件：组装选定策略（场景标记=submit，含降级回退路径）、固定依赖与配置常量；契约字段以 scaffold 期核得的赛站文档为准。
    - 签名意图：输入: 最优配置 + 契约模板 / 输出: 入口文件内容 / 错误: 契约模板缺字段→PackageError
    - 调用方：build_kaggle_package
    - tested 策略：上游覆盖: build_kaggle_package
    - 核验命令：上游覆盖: build_kaggle_package
  - **verify_package_layout** [L1|新增]
    - 职责：对照契约清单逐项检查包内文件存在性与入口可导入性，输出差异清单；纯校验不改包。
    - 签名意图：输入: 包目录 / 输出: 通过/差异清单 / 错误: 无（差异以清单返回）
    - 调用方：build_kaggle_package
    - tested 策略：自有单测
    - 核验命令：测试: tests/test_verify_layout.py
  - **submit_package** [L1|新增]（与 build 同块，操作型）
    - 职责：调 Kaggle CLI 提交包文件，解析回执确认接收状态并写日志；网络失败有限重试后报错（提交态哲学）。
    - 签名意图：输入: 赛站 ID + 包路径 / 输出: 提交回执（接收状态+时间戳）/ 错误: 重试耗尽→SubmitError（附 CLI 原始输出）
    - 调用方：程序入口（提交操作）
    - tested 策略：上游覆盖: build_kaggle_package（集成）
    - 核验命令：继承 R6 验收：`kaggle competitions submit <赛站ID> -f <包>` 成功且赛站可查

## 功能块 write_report ← R7
R7 为复现报告：增益表+配置说明+每个数字的运行产物路径；验收=审阅者按路径能找到产物且数字一致。

- **write_report** [L0|新增]
  - 职责：报告主流程：collect_run_artifacts 建运行产物索引 → 由对照表与索引组装报告（增益表节+配置说明节+溯源附录）→ 写出 markdown 文件；报告中每个数字必须携带其 run 产物路径。
  - 签名意图：输入: runs 目录 + 对照表 CSV 路径 / 输出: 报告 markdown 路径 / 错误: 产物索引与对照表数字对不上→ReportDataError（宁停勿错）
  - 调用方：程序入口（报告脚本）
  - tested 策略：自有单测
  - 核验命令：测试: tests/test_write_report.py；可观察判据继承 R7（路径可溯、数字一致）
  - **collect_run_artifacts** [L1|新增]
    - 职责：扫描 fn_work/runs/ 汇集运行产物索引（run_id→指标/配置/时间/文件路径），只读不改。
    - 签名意图：输入: runs 目录 / 输出: 产物索引 / 错误: 目录不存在→ReportDataError
    - 调用方：write_report
    - tested 策略：自有单测
    - 核验命令：测试: tests/test_collect_artifacts.py
  - **render_gain_table** [L1|新增]
    - 职责：把对照表渲染为报告用 markdown 表，逐数字内联挂产物路径链接；纯函数。
    - 签名意图：输入: 对照表数据 + 产物索引 / 输出: markdown 表文本 / 错误: 索引缺项→ReportDataError
    - 调用方：write_report
    - tested 策略：上游覆盖: write_report
    - 核验命令：上游覆盖: write_report
