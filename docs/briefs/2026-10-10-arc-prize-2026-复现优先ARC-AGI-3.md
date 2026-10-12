# 方案书：ARC Prize 2026 × 复现优先 ARC-AGI-3

> 生成：/attack（strategy-gen）｜日期：2026-10-10｜性质：纯参考信息，不影响推进

## 一、赛事

- **情报摘要**（回链 KB-1 条目 `kaggle-arc-prize-2026`，条目载 2026-10 抓取；关键事实 2026-10-10 官网 arcprize.org 交叉核实）：
  - 三赛道、总池 $2,000,000；ARC-AGI-3 赛道聚焦交互游戏环境中的探索/现场目标获取/世界模型构建（赛道页 arcprize.org/competitions/2026/arc-agi-3，10-10 核实）。
  - 时间线（条目）：终交 **2026-11-02**、论文轨 11-08、放榜 12-04；ARC-AGI-3 Milestone #1 已于 09-30 发奖 $37.5K，冠军方案为**本地开源 Qwen 27B FP8**（10-10 网检，中强度——二手转述，Kaggle 页未直核）。
  - 赛制约束（条目，强）：评测**断网**、禁 API 型系统（"no API-based systems like GPT/Claude"）、**强制开源**——对复现型选手是制度性利好（参赛作品=本地开源可复现系统）。
- **对比矩阵**（每格标证据强度：强=KB 条目多源；中=单页实抓未入库；弱=列表卡/待核）：

| 赛事 | 时间窗 | 技术契合 | 通吃度 | 画像匹配 | 竞争密度 | 证据强度 |
|---|---|---|---|---|---|---|
| **ARC Prize 2026 ARC-AGI-3**（kaggle-arc-prize-2026） | 至 11-02，23 天（强） | ★★★ Memento 3 全清该基准 + S4 栈可跑（强） | 低：纯技术赛，无校认定口径（强） | 中：python/ML 强、周 40h 档够；交互 agent 属新领域（强） | 高：全球 Kaggle，Milestone #1 已见强手（中） | 强 |
| BEHAVIOR 2026 Challenge（未入库，10-10 规则页实抓） | **截止日全站未公布**（中） | ★★★ RoboHarness 主场基准（强） | 低（中） | 中低：Isaac Sim 重装、评测包络单卡 24G（中） | 低：小众（弱） | 中——新发现，建议入库 |
| 蚂蚁灵波具身 532514（tianchi-ant-lingbot-vla-2026） | 至 10-26（强，今日三 tab 快照） | ★ 锁基座 lingbot-vla-v2-6b，免训练范式出局（强） | 中：¥28 万现金（强） | 中（强） | 中：1533 队（强） | 强 |
| PTCG Playground（kaggle-pokemon-tcg-playground） | 至 2027-01-08（强） | ★★ S4 可迁移但无直接命中卡；用户已有停摆战役在库（强） | 低：无现金（强） | 高：用户方法论主场（强） | 中 | 强 |
| GSK Pyxis（gsk-pyxis-simulation） | entry 2027-01-04，**赛站仍 404 未上线**（强） | ★★ 方法论契合（强） | 低（强） | 高（强） | TBD 未开赛（强） | 强 |

- **大显身手信号**（近 90 天入库 KB-2 卡 × 赛事 patterns 命中；ARC Prize 为新赛**无 patterns 层**，如实降权——以下按"任务域命中"计）：
  - `arxiv-2610.11794` Memento 3：ARC-AGI-3 全清 25 关、44% 人类动作数（直接同基准命中；无码，作机制参考）。
  - `arxiv-2610.00906` ActiveSaddler（microsoft/AutoSaddler 233★）：课程调度，GAIA2 +4.4pp 且省 4.6× 算力（agent 长程域命中，demo 可跑）。
  - `arxiv-2609.24972` RRSI（google-research）：经验更新正则（同上，demo 可跑）。
  - `gh-BootLoops-ai_bootloops`（168★ MIT）：工具调用不确定性证书（辅助件，demo 可跑）。

## 二、方案

- **一句话主张**：单人复现"课程调度+更新正则"自进化 agent 栈（ActiveSaddler+RRSI）挂本地开源 27B 模型打 ARC-AGI-3，以 11-02 终交为目标——复现验证即产物主体，上榜为顺带结果。
- **一鱼多吃路线**：用户 grill 明示**纯学习**，不设复投序列（grill 纪要 §五）；复现产物为开源仓库，天然可沉淀，不作规划。
- **范围边界**：做什么——ARC-AGI-3 单赛道、remote-compute 远端 27B FP8 直上、S4 双组件复现与增益复测、本地环境闭环自评；不做什么——另两赛道与论文轨（显式排除）、Memento 3 规则书机制复现（无码，只作设计参考）、组队（单人）、基座自训（只用现成开源权重）。
- **推荐结论**：**第一名 = 本方案**（ARC Prize 2026 ARC-AGI-3 复现路线）。理由：①任务域与库内四张近 90 天卡直接命中（含一张同基准全清）；②赛制断网+禁 API+强制开源，与"复现本地开源系统"完全同构，参赛零额外变形；③23 天窗口与单人 40h/周档匹配（画像 config/profile.yaml）。**备选**：BEHAVIOR 2026（契合同级但截止日未公布+重装环境，降权）；PTCG Playground（方法论主场但无现金且用户已停摆一轮，防重复倦怠）。风险如实：与国创材料收口并行（用户知情选择"立即启动"）；Kaggle 竞争密度高，冲奖预期应压低——本方案定位复现，符合用户意图。

## 三、技术栈

| 构件 | 选型 | 依据（kb_tech_ids / 实抓来源） |
|---|---|---|
| 交互环境 | ARC-AGI-3 官方开放环境 + Kaggle 本地评测 | kaggle-arc-prize-2026 条目；arcprize.org 10-10 核实 |
| 基座模型 | 开源 LLM 27B FP8 本地部署（Qwen 系） | Milestone #1 冠军同配置（10-10 网检，中强度）；赛制禁 API 强制本地 |
| 课程调度 | ActiveSaddler（官方仓可跑） | `arxiv-2610.00906`（demo，microsoft 233★） |
| 更新正则 | RRSI（google-research 官方包） | `arxiv-2609.24972`（demo） |
| 不确定性标注（可选） | BootLoops 工具包 | `gh-BootLoops-ai_bootloops`（demo，MIT） |
| 机制参考（不复现） | Memento 3 规则书世界模型 | `arxiv-2610.11794`（paper 无码，仅设计参考） |
| 算力 | remote-compute 远端 GPU（用户既有设施）；8G 笔记本为备胎档 | grill 纪要 §三；config/profile.yaml |

- **合规与风险**：ai_policy 摘引（kaggle-arc-prize-2026 条目，强）："no API-based systems like GPT/Claude"；"No internet access during evaluation"；获奖强制开源。**mode 判定：apply**（赛题本体即构建 AI 系统，AI 使用即参赛内容本身，无辅助/披露争议）。风险：①27B 本地推理算力成本自理且迭代慢（用户已选直上远端，知情）；②Milestone #1 强手在先，终榜名次预期压低；③赛程节点以 Kaggle 赛站为准，条目内个别口径（奖金分配结构）为中强度证据，动手前应到赛站复核一遍。
