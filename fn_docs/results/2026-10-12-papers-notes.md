# 论文机制实抓笔记（2026-10-12 拉取）

> 两篇均为实抓确认存在的 2026 论文（WebSearch + arXiv 站内搜索 + 摘要页/HTML 全文 WebFetch）。
> 每机制点带来源 URL 与原文关键句。抓取子代理：fn-analyze。

## 论文一：ActiveSaddler（课程调度复现对象）

**定位**：Sungho Park, Wonjoong Kim, Jue Zhang, Wook-Shin Han, Pengfei Gao, Chanyoung Park, Yongqiang Yao, Rao Fu, Elsie Nallipogu, Qingwei Lin, Victor Rühle. *ActiveSaddler: Automated Curriculum Learning for Agent Harness Optimization*. arXiv:2610.00906, v1 提交 2026-10-01（唯一版本）。Microsoft 相关团队。
来源：https://arxiv.org/abs/2610.00906 · 全文 https://arxiv.org/html/2610.00906v1

### 核心机制（每条一句话 + 原文关键句）

1. **问题框架**：把"用哪些场景给 harness 优化器提供反馈"从固定顺序变成自动课程学习——"prior work fixes which training scenarios generate feedback"，ActiveSaddler 将其建模为非平稳 bandit："models the evolving curriculum as a non-stationary bandit with dynamically instantiated optimization targets"。（abs 页）
2. **难度/失败信号估计**：不用显式难度分数，而是把复发失败抽象成可复用"失败模式臂"（failure-pattern arms）；每臂的学习潜力由 LLM 打分 φ_t(a)=g_select(a, I_<t) ∈ [0,1]，指令要求"jointly consider four factors——severity、fixability、breadth、side-effect risk"。（html 全文方法节）
3. **调度决策规则**：温度控制 softmax（Boltzmann）选择臂：q_t(a)=exp(φ_t(a)/τ_sel)/Σexp(φ_t(a′)/τ_sel)，a_t~Categorical(q_t)，τ_sel=0.15；不是 UCB/Thompson（二者仅作为更差的消融对照）。（html 全文）
4. **臂的动态组织**：失败先独立抽象成候选症状 c_t(e)=g_ext(e, δ_t(e))，再由 g_norm 对齐已有模式——"links each candidate to an existing atomic pattern, composes multiple existing patterns when needed, or instantiates a new arm for a previously unseen failure pattern"；臂集事先未知、在线扩张，不删除，靠每轮重打分让低效用臂在 softmax 中自然衰减（"preserving the possibility of revisiting lower-scored arms"）。（html 全文）
5. **探索机制**：LLM 探索控制器每轮二值决策 d_t ∈ {unseen, arm}（Draw 采未见场景 / Pull 拉臂）；无臂强制探索、有臂可拉臂；全部访问过后有 regression-rediscovery 规则重开旧场景。（html 全文）
6. **与权重的关系**：完全不动权重——学习式 harness 优化更新的是"external harness state... analogous to model training but without updating model weights"，ActiveSaddler 只换课程、"harness-update mechanism unchanged"。（html 全文）
7. **效果数字**：GAIA2 与 Terminal-Bench 2.0 上 test Pass@1 分别 +4.4 与 +7.5 个百分点（相对固定场景顺序基线）。（abs 页）

### 与本项目降级实现的对照观察（如实）
- requirements 术语表把 R3 描述为"先易后难选择经验来源"——原论文实为**失败模式驱动的 bandit 课程**（ revisit 已知弱点 vs 探索新场景），并非字面的易→难难度阶梯；"先易后难"是对"从可解决的失败模式学起"的意译。
- 原论文的场景选择服务于 **harness 编辑的反馈生成**（优化循环里选哪些任务练），本项目降级为练习局编排层，粒度差异应在复现报告口径中登记。

## 论文二：RRSI（经验更新正则复现对象）

**定位**：Peng Xia, Rujun Han, Zifeng Wang, Yanfei Chen, Yufan Zhuang, Yoonho Lee, Chengsong Huang, Han Yu, Zhongying CuiZhu, Yifei Ming, Huaxiu Yao, Burak Gokturk, Tomas Pfister, Chen-Yu Lee. *RRSI: Regularized Recursive Self-Improvement of Agent Harnesses*. arXiv:2609.24972（v1 2026-09-21 / v2 09-23 / v3 2026-10-04，Google）。代码 github.com/google-research/rrsi。
来源：https://arxiv.org/abs/2609.24972 · 全文 https://arxiv.org/html/2609.24972v3

### 核心机制（每条一句话 + 原文关键句）

1. **问题框架**：harness（"prompts, control flow, tooling, memory, and context management"）递归自改进会过拟合——"may overfit by memorizing the training tasks, showing large in-distribution gains that shrink or even vanish on out-of-distribution benchmarks"；RRSI 把正则化原则引入提案与选择两端。（abs 页）
2. **经验/记忆结构**：每个原子编辑一条记录——"the component it modifies, the hypothesis it tests, the source diff, the resulting score and cost changes, and whether the candidate was accepted"，形式化 ℒₜ={(tᵢ, ℓᵢ, hᵢ, dᵢ, ΔSᵢ, ΔCᵢ, aᵢ)}；可编辑组件词表：prompt, control_flow, config, output_plumbing, context_mgmt, client_tool, skill, memory, subagent，且"RRSI deliberately leaves Ω(H) open"（组件可增删改）。（html 全文方法节）
3. **正则化规则一（提案端）**：时间退火编辑预算（余弦日程）bₜ=⌈b_min+(b_max−b_min)·½(1+cos(πt/T))⌉ 从 3-4 降至 1，即"an L0-style constraint on the update"（‖zₜ‖₀ ≤ bₜ）；停滞检测 σₜ（3 轮窗口无超噪声带改进）时保留 m_draft=1/2 个候选槽给未探索集 𝒰ₜ 促新颖轨迹。（html 全文）
4. **正则化规则二（筛选端·critic）**：泄漏批评者读 diff 拒绝显式编码任务名/实体名/任务特定值/答案的编辑——"rejects edits that explicitly encode task names, entity names, task-specific values, answers"，在完整评测**之前**筛（防虚高分）。（html 全文）
5. **正则化规则三（筛选端·pruner）**：连续剪枝窗判据 gₜ(ℓ)=max{ΔSᵢ: ℓᵢ=ℓ, t−tᵢ≤n_prune} ≤ 0（n_prune∈{4,5} 轮）则组件标记删除——"mechanisms with insufficient evidence of utility are removed entirely"（太 minimal/太贵/不再有用的改动整件移除）。（html 全文）
6. **选择判据**：无独立 held-out 集，进化集上正则化门控：噪声调整底线 Ŝ(H′) ≥ S★−δ（δ 由基线 harness 重复运行校准）+ 成本规则 ΔC ≤ β₀+β₁ΔS（或改进不显著时 w_sΔS−w_cΔC+w_nνₜ>0，νₜ 计新颖结构组件），最优可接纳者胜出、无则留任。（html 全文）
7. **入提示方式**：经验不直接拼进提示，而是**作为 harness 编辑的对象与条件**——进化历史条件化提案器的编辑建议，被接受的编辑直接改写 agent 的 prompts/memory/context 管理（即"经验以 harness 变更的形式沉淀进提示"）。（abs+html 综合）
8. **防退化机制与权重关系**：critic+pruner+预算退火三重防过拟合/防噪声沉淀，30% 更少 policy tokens；骨干全程冻结——"The policy is frozen throughout Claude Opus 4.8 across all three domains"，明确只研究"harness-level recursive self-improvement with frozen backbone models"。（html 全文）
9. **效果数字**：8 基准（编码/agentic workspace/工程设计），进化集 +6.0 分，5 个 OOD 基准 +4.3 分，token 省 30%。（abs 页）

### 与本项目降级实现的对照观察（如实）
- requirements 术语表把 R4 描述为"筛选/正则化历史经验再入提示"——原论文的正则化对象是**harness 编辑流**（提案预算+批评者+剪枝者），不是把经验文本筛后拼提示；本项目"筛选正则化经验入提示"是对其精神（防过拟合、留有用弃噪声）的提示层降级，机制保真度有限，应在复现报告登记。

## 附：抓取中发现的强相关邻文（备察，非复现对象）

- **Learn2Play Bench: How Well Do LLM Agents Learn from Experience in Unfamiliar Environments?**（arXiv:2610.08215，v2 2026-10-08，Yibo Li 等）：新设计规则反直觉文字游戏测交互学习，发现"retaining full action/feedback records beats summarizing them into rules"（保留完整动作/反馈记录优于摘要成规则）——对本项目"经验入提示"形态选择有直接参考价值。来源：https://arxiv.org/abs/2610.08215
- **ReSAIL: Mitigating Collapse in Iterative Agent Self-Distillation**（arXiv:2609.39306）：迭代自蒸馏崩溃缓解，选信息性交互步+保持 PI 条件行为，末轮成功率 +22.5%。来源：arXiv 搜索结果页。

## 不确定度声明

- 两篇论文均**确认存在**且 ID/作者/日期经 arXiv 站内搜索与摘要页二次核实；正文机制取自 arXiv HTML 渲染版（2610.00906v1 / 2609.24972v3），未逐字比对 PDF，公式转写可能有排版级误差（如 ℒₜ 记号）。
- 初次搜索结果曾把 ActiveSaddler 误指为 2610.08215（实为 Learn2Play Bench），已通过 arXiv 站内搜索纠正——快照只采信纠正后来源。
- 两文均为 2026 年 9-10 月新文，coverage 站（aiweekly/neurohive）转述的数字与摘要页一致方采用。
