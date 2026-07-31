# AI 工作流自我优化方案调研

## 调研目标

为 T0159 选择一套可审计、可验证、不会自动绕过 PDCA 门禁的自我优化方案。重点回答：

1. AI 工作流如何从执行轨迹中学习？
2. 哪些优化对象适合自动化，哪些必须由人确认？
3. 如何避免模型用自己的判断循环自证？
4. 什么方案适合当前以文件、门禁和不可变 evidence 为核心的 PDCA 仓库？

## 方法

检索论文、官方项目页和官方文档，比较以下路线：

- 单次任务内的反思与修正；
- 跨任务记忆和技能积累；
- prompt、代码和工作流结构搜索；
- 基于执行轨迹与 reward 的训练；
- 自我修正的已知失效条件。

仅将有外部反馈、可执行评测或明确实验结果的机制作为架构依据。

## 发现

### 1. 反思适合生成诊断，不适合独立充当裁判

[Reflexion](https://arxiv.org/abs/2303.11366) 将任务反馈转成语言反思并保存在 episodic memory 中，使后续尝试能够利用失败经验；[Self-Refine](https://arxiv.org/abs/2303.17651) 则在单次任务内循环执行“生成→反馈→修订”。两者证明语言反馈可以成为低成本改进媒介。

但对自我修正研究的[批判性综述](https://arxiv.org/abs/2406.01297)指出：没有可靠外部反馈时，prompted LLM 的自我修正并不稳定；外部验证器可用的任务效果明显更可靠。因此，本项目中的 LLM 反思只能产生“问题解释”和“改进候选”，不能自己确认候选有效。

**映射到 PDCA**：`flow-audit issues → grounded reflection → candidate`，最终判定必须来自确定性检查、独立 evidence 和用户 verdict。

### 2. 持续学习需要“经验库”，且只保存验证通过的能力

[Voyager](https://voyager.minedojo.org/) 组合了自动 curriculum、可复用 skill library，以及利用环境反馈、执行错误和自验证迭代修复代码的机制。其关键不是无限反思，而是把成功执行的程序保存为可复用技能，并让后续任务从技能库检索。

**映射到 PDCA**：审计记录是原始经验，改进候选不是知识；只有经过测试、Check verdict 和 Act disposition 的流程改动，才能进入 `knowledge/` 或权威 `flows/skills`。

### 3. 工作流优化可以建模为受评测约束的搜索

[AFlow](https://openreview.net/pdf?id=z5uVAKwmjf) 把代码表示的 agent workflow 优化建模为搜索问题，使用执行反馈与树结构经验迭代改进；论文报告六个 benchmark 上平均提升 5.7%。[Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435) 进一步让 meta-agent 编写和组合 agent code，并把历史候选保存在 archive 中。

这类方案适合“候选空间明确、评分函数可信、能反复隔离执行”的场景，但直接作用于生产流程风险过高。

**映射到 PDCA**：搜索器只能在 sandbox 中生成 `flow/skill` patch 候选；候选必须经过固定夹具、历史回放、双轴审查和 final confirmation，才能晋级。

### 4. 文本反馈可优化 prompt 与复合 AI 系统，但前提是目标函数明确

[TextGrad](https://arxiv.org/abs/2406.07496) 用语言反馈在复合 AI 系统的计算图中传播“文本梯度”；[GEPA](https://arxiv.org/abs/2507.19457) 从执行轨迹中反思、提出并测试 prompt 更新，维护 Pareto frontier。GEPA 报告在六项任务上平均超过 GRPO 6%，最多使用少 35 倍的 rollout。[DSPy 官方文档](https://dspy.ai/)也将优化器定义为“针对明确 metric 编译 AI program”。

**映射到 PDCA**：优化器必须接收预先冻结的指标和回归集。没有 metric、baseline 和 holdout 的“自动改 prompt”不属于优化，只是无约束改写。

### 5. 基于 RL 的持续优化能力强，但不是当前 MVP

[Microsoft Agent Lightning](https://www.microsoft.com/en-us/research/project/agent-lightning/) 将 agent 执行轨迹标准化为状态、动作、reward 和后继状态，解耦 agent workflow 与训练系统，并支持错误监控和长程 credit assignment。

该路线适合大量同分布任务、稳定 reward、可训练模型和充足 rollout 预算。当前 PDCA 仓库的样本量小，优化对象主要是流程文件、技能和门禁，而非模型权重，因此直接引入 RL 成本和误优化风险都过高。

## 方案比较

| 路线 | 优化对象 | 反馈 | 优点 | 主要风险 | 本项目定位 |
|---|---|---|---|---|---|
| Reflexion / Self-Refine | 单次回答、计划 | 语言/环境反馈 | 轻量、易接入 | 自我评价偏差 | 仅做诊断和候选生成 |
| Voyager | 技能与任务序列 | 执行结果 | 跨任务积累、可复用 | 错误技能污染库 | 只沉淀验证通过的流程知识 |
| TextGrad / GEPA / DSPy | prompt、复合程序 | 明确 metric | 数据效率高、结果可比较 | 指标设计错误、过拟合 | 第二阶段优化器 |
| AFlow / ADAS | workflow code/graph | benchmark score | 能搜索结构性改进 | 搜索空间大、代码风险 | sandbox 候选搜索 |
| Agent Lightning | 模型 policy | reward/trajectory | 可优化长程行为 | 数据、训练和 reward 成本高 | 暂不进入 MVP |

## 推荐架构

采用“可观测、可提案、不可自行晋级”的六层闭环：

1. **Observe — 观测**
   - 输入：各 record 的 `flow-audit.json`、transition receipt、gate failure、rollback。
   - 输出：不可变的标准化 issue event。

2. **Aggregate — 聚合**
   - 按 `issue.code + transition + affected component` 聚类。
   - 统计任务数、发生次数、首次/最近时间、是否重复、影响范围。
   - 单次 fail 不直接触发流程修改。

3. **Diagnose — 诊断**
   - LLM 只能引用具体 event、PRD、代码和 evidence 形成根因假设。
   - 区分执行偏差、规格缺口、工具缺陷和流程设计缺陷。
   - 产出结构化 `improvement-candidate`，不能直接写权威流程。

4. **Evaluate — 隔离评测**
   - 对候选 patch 运行固定确定性夹具、历史失败回放和当前全量测试。
   - 同时检查“缺陷捕获率”和“误报/额外阻断率”，防止通过弱化门禁来降低失败数。
   - 保留 baseline、candidate、holdout、成本和回归结果。

5. **Promote — 受控晋级**
   - 通过评测的候选创建正常 PDCA 任务。
   - 必须经过 Grill、PRD、final confirmation、Do evidence 和 Check verdict。
   - 优化器没有修改 `flows/`、`skills/`、schema 或 gate 的直接权限。

6. **Verify — 跨周期验证**
   - 部署后观察新的任务窗口。
   - 比较目标 issue 的复发率、缺陷逃逸、误报、重试次数和执行成本。
   - 结果为 improved / neutral / regressed；regressed 触发回滚候选，而不是静默继续演化。

## 推荐 MVP

### 数据产物

- `flow-issue-event`：标准化单次审计问题。
- `flow-issue-backlog`：跨任务聚合的问题队列。
- `improvement-candidate`：问题证据、根因假设、目标文件、预期指标、风险和建议 patch。
- `effectiveness-verdict`：baseline 与后续窗口的效果判定。

### 第一阶段只实现

1. 确定性扫描所有 `records/*/flow-audit.json`。
2. 生成稳定排序的 issue backlog。
3. 对满足触发规则的问题生成“跟进任务草稿”，不自动改文件。
4. 为候选绑定来源 issue ID、baseline metric 和验证计划。
5. 用固定 fixture 演示一次 `record → candidate → confirmed task → post-check` 完整闭环。

### 暂不实现

- 模型权重训练或 RL；
- 无用户确认的自动 patch 合并；
- 仅依赖同一 LLM 自评分的晋级；
- 开放式 workflow code 搜索；
- 没有 holdout 的 prompt 自动优化。

## 指标建议

不能只优化“gate fail 越少越好”，否则系统可能通过弱化门禁取得虚假改善。建议成对使用：

- **目标缺陷复发率**：改进后同类问题是否减少；
- **缺陷逃逸率**：问题是否未被 gate/audit 捕获而进入后续阶段；
- **误报或额外阻断率**：正常任务是否受到不必要影响；
- **first-pass convergence rate**：首次 Do→Check 是否证据完整；
- **rollback/retry rate**：阶段转换是否反复失败；
- **执行成本**：额外时延、模型调用和人工确认次数。

## 结论与建议

最适合本项目的不是完全自治的 recursive self-improvement，而是 **human-governed, eval-driven workflow evolution**：

`immutable observations → deterministic aggregation → evidence-grounded diagnosis → sandbox evaluation → user-confirmed promotion → post-change verification`

建议 T0159 先实现确定性聚合、候选任务草稿和跨周期效果判定。待积累足够样本和稳定 metric 后，再评估 GEPA/DSPy 类 prompt 优化；只有出现大量同分布轨迹、可靠 reward 和模型训练需求时，才考虑 Agent Lightning/RL。

## 参考资料

1. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
2. [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651)
3. [When Can LLMs Actually Correct Their Own Mistakes?](https://arxiv.org/abs/2406.01297)
4. [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://voyager.minedojo.org/)
5. [TextGrad: Automatic Differentiation via Text](https://arxiv.org/abs/2406.07496)
6. [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457)
7. [DSPy official documentation](https://dspy.ai/)
8. [AFlow: Automating Agentic Workflow Generation](https://openreview.net/pdf?id=z5uVAKwmjf)
9. [Automated Design of Agentic Systems](https://arxiv.org/abs/2408.08435)
10. [Agent Lightning — Microsoft Research](https://www.microsoft.com/en-us/research/project/agent-lightning/)
