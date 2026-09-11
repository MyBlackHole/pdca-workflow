# 本体定位索引 · 3.4.10

仅定位；不将全索引作为每个任务常驻输入。authority、asset_role、采用证据和实际版本决定适用性。共享定义在ontology，运行事实在records。

| ID | 文件 | revision | authority | 摘要 |
|---|---|---|---|---|
| `ontology:concept/active-discipline` | [active-discipline.md](concept/active-discipline.md) | 3.1.0 | reference | 活跃纪律：讨论代码时积极构建领域模型 |
| `ontology:concept/agent-brief` | [agent-brief.md](concept/agent-brief.md) | 3.1.0 | reference | Agent 简要：持久的 agent 简要文档 |
| `ontology:concept/agent-ready-brief` | [agent-ready-brief.md](concept/agent-ready-brief.md) | 3.1.0 | reference | Agent 就绪简要：完全规范、ready-for-agent |
| `ontology:concept/ai-disclaimer` | [ai-disclaimer.md](concept/ai-disclaimer.md) | 3.1.0 | reference | AI 免责声明：分诊评论必须以 AI 免责声明开头 |
| `ontology:concept/ask-matt` | [ask-matt.md](concept/ask-matt.md) | 3.1.0 | reference | 路由技能：根据用户描述推荐合适的 PDCA 入口 |
| `ontology:concept/audit/project-review` | [project-review.md](concept/audit/project-review.md) | 3.4.1 | normative | 本体项目审查：固定对象、责任覆盖与证据汇聚 |
| `ontology:concept/audit/rule-consistency-review` | [rule-consistency-review.md](concept/audit/rule-consistency-review.md) | 3.4.0 | normative | 规则一致性审查：适用条件与跨文件冲突 |
| `ontology:concept/audit/source-claim-review` | [source-claim-review.md](concept/audit/source-claim-review.md) | 3.4.0 | normative | 资料主张核验：版本、证据与适用性 |
| `ontology:concept/audit/test-contract-review` | [test-contract-review.md](concept/audit/test-contract-review.md) | 3.4.1 | normative | 任务单元测试审查：反例、判定器与返工覆盖 |
| `ontology:concept/auto-induce-evidence` | [auto-induce-evidence.md](concept/auto-induce-evidence.md) | 2.0.0 | normative | 从证据提取知识候选 |
| `ontology:concept/auto-induce-flow-trigger` | [auto-induce-flow-trigger.md](concept/auto-induce-flow-trigger.md) | 2.0.0 | normative | 流程改进候选触发 |
| `ontology:concept/blocking-edges` | [blocking-edges.md](concept/blocking-edges.md) | 3.2.0 | normative | 组成树之外的明确输入依赖 |
| `ontology:concept/capability-protocol` | [capability-protocol.md](concept/capability-protocol.md) | 3.4.10 | normative | 宿主能力：隔离、独立交互和真实测试 |
| `ontology:concept/challenge-glossary` | [challenge-glossary.md](concept/challenge-glossary.md) | 3.1.0 | reference | 挑战术语表：当用户使用与现有术语冲突的词时立即指出 |
| `ontology:concept/cipher-mode-cbc` | [cipher-mode-cbc.md](concept/cipher-mode-cbc.md) | 3.1.0 | reference | CBC 工作模式（链式 P xor C_{i-1}）加密串行、无认证、IV 随机、需 HMAC 补认证 |
| `ontology:concept/cipher-mode-ccm` | [cipher-mode-ccm.md](concept/cipher-mode-ccm.md) | 3.1.0 | reference | CCM：规定格式化与补零，M/L显式，区分CBC-MAC值与输出标签 |
| `ontology:concept/cipher-mode-cfb` | [cipher-mode-cfb.md](concept/cipher-mode-cfb.md) | 3.1.0 | reference | CFB反馈模式；不可与fscrypt CBC-CTS文件名模式混同 |
| `ontology:concept/cipher-mode-ctr` | [cipher-mode-ctr.md](concept/cipher-mode-ctr.md) | 3.1.0 | reference | CTR 工作模式（计数器 SM4(K,nonce\|\|ctr)）均并行、无填充、需HMAC 补认证、nonce 不可重用 |
| `ontology:concept/cipher-mode-ecb` | [cipher-mode-ecb.md](concept/cipher-mode-ecb.md) | 3.1.0 | reference | ECB 工作模式（独立块 C=SM4(K,P)）均并行、无IV、泄露相等性、存储禁用 |
| `ontology:concept/cipher-mode-gcm` | [cipher-mode-gcm.md](concept/cipher-mode-gcm.md) | 3.1.0 | reference | GCM：区分H、J0与标签，固定标准与向量，不用关键词证明算法 |
| `ontology:concept/cipher-mode-ofb` | [cipher-mode-ofb.md](concept/cipher-mode-ofb.md) | 3.1.0 | reference | OFB 工作模式（流 O_{i-1} 反馈）均串行、预计算、IV 不可重用、错误不扩散 |
| `ontology:concept/cipher-mode-xts` | [cipher-mode-xts.md](concept/cipher-mode-xts.md) | 3.1.0 | reference | XTS：数据单元tweak与逐块域乘法；固定输入确定且不提供认证 |
| `ontology:concept/cipher-mode` | [cipher-mode.md](concept/cipher-mode.md) | 3.1.0 | reference | 分组密码工作模式元概念：ECB/CBC/CFB/OFB/CTR/XTS/GCM/CCM 的 chaining 方式抽象 |
| `ontology:concept/co-location` | [co-location.md](concept/co-location.md) | 3.1.0 | reference | 共置：概念的定义、规则、注意事项放在同一标题下 |
| `ontology:concept/codebase-design` | [codebase-design.md](concept/codebase-design.md) | 3.1.0 | reference | 深模块设计：模块/接口/接缝/适配器/深度词汇 |
| `ontology:concept/completion-criterion` | [completion-criterion.md](concept/completion-criterion.md) | 3.1.0 | reference | 完成标准：agent 判断工作完成的条件，需清晰且有需求强度 |
| `ontology:concept/context-pointer` | [context-pointer.md](concept/context-pointer.md) | 2.0.0 | normative | 具名、版本固定的上下文指针 |
| `ontology:decision` | [decision.md](concept/decision.md) | 3.1.0 | reference | Decision 类：具体决定（含理由） |
| `ontology:concept/design-tree` | [design-tree.md](concept/design-tree.md) | 3.1.0 | reference | 设计树：每个决策分支为下游决策的树结构 |
| `ontology:concept/destructive-cleanup-safety` | [destructive-cleanup-safety.md](concept/destructive-cleanup-safety.md) | 3.1.0 | reference | 可恢复破坏性清理的恢复源固定与执行前重验证规则 |
| `ontology:concept/deterministic-fixture` | [deterministic-fixture.md](concept/deterministic-fixture.md) | 3.1.0 | reference | 确定性夹具：输入、预期输出和 pass/fail 信号均固定 |
| `ontology:concept/domain-bcachefs` | [domain-bcachefs.md](concept/domain-bcachefs.md) | 3.1.0 | reference | 领域分支 bcachefs：bcachefs 文件系统知识分组（T2152 默认锚定收紧） |
| `ontology:concept/domain-core` | [domain-core.md](concept/domain-core.md) | 3.1.0 | reference | 领域分支 core：通用核心知识分组（T2152 默认锚定收紧，core- 前缀备用） |
| `ontology:concept/domain-entity` | [domain-entity.md](concept/domain-entity.md) | 3.1.0 | reference | DomainEntity：真实世界实体分组 |
| `ontology:concept/domain-model` | [domain-model.md](concept/domain-model.md) | 3.1.0 | reference | 领域模型：项目术语的活跃维护 |
| `ontology:concept/domain-modeling` | [domain-modeling.md](concept/domain-modeling.md) | 3.1.0 | reference | 领域建模：活跃构建和维护项目领域模型 |
| `ontology:concept/domain-report-center` | [domain-report-center.md](concept/domain-report-center.md) | 3.1.0 | reference | 领域分支 report-center：报表中心知识分组（T2152 默认锚定收紧） |
| `ontology:concept/domain-zfs` | [domain-zfs.md](concept/domain-zfs.md) | 3.1.0 | reference | 领域分支 zfs：ZFS 知识分组（T2152 默认锚定收紧） |
| `ontology:concept/entity` | [entity.md](concept/entity.md) | 3.1.0 | reference | Entity 根：所有实体/知识/过程的顶层类 |
| `ontology:concept/executor-adapter` | [executor-adapter.md](concept/executor-adapter.md) | 3.1.0 | reference | 已退役：executor-adapter |
| `ontology:concept/expand-contract` | [expand-contract.md](concept/expand-contract.md) | 3.1.0 | reference | 展开-收缩：宽重构的序列策略 |
| `ontology:concept/external-evidence-collection` | [external-evidence-collection.md](concept/external-evidence-collection.md) | 2.0.0 | normative | 外部证据导入边界 |
| `ontology:fact` | [fact.md](concept/fact.md) | 3.1.0 | reference | Fact 类：稳定事实/调查状态 |
| `ontology:concept/facts-not-opinions` | [facts-not-opinions.md](concept/facts-not-opinions.md) | 3.1.0 | reference | 事实而非观点：发现事实是 agent 的职责，不是用户的 |
| `ontology:concept/failure-mode` | [failure-mode.md](concept/failure-mode.md) | 3.4.6 | reference | AI 四大失效模式：驱动技能矩阵设计的根本分类 |
| `ontology:concept/frontier` | [frontier.md](concept/frontier.md) | 3.2.0 | normative | 可执行树节点前沿 |
| `ontology:concept/ghash` | [ghash.md](concept/ghash.md) | 3.1.0 | reference | GHASH递推与GCM输入格式分离；不以简化概率式证明实现安全 |
| `ontology:concept/grilling-completion` | [grilling-completion.md](concept/grilling-completion.md) | 2.0.0 | normative | 澄清完成条件 |
| `ontology:concept/grilling-methodology` | [grilling-methodology.md](concept/grilling-methodology.md) | 2.0.0 | normative | 围绕真实不确定性的澄清 |
| `ontology:concept/grounding-dependency` | [grounding-dependency.md](concept/grounding-dependency.md) | 3.1.0 | reference | Grounding 依赖图：概念必须 grounding 后才能被后续块依赖 |
| `ontology:concept/handoff` | [handoff.md](concept/handoff.md) | 3.1.0 | reference | 交接：将当前对话紧凑地压缩为交接文档，使另一个 agent 可以继续工作 |
| `ontology:concept/implement` | [implement.md](concept/implement.md) | 3.4.6 | reference | 从规格说明构建实现：红绿重构驱动的垂直切片 |
| `ontology:concept/information-hierarchy` | [information-hierarchy.md](concept/information-hierarchy.md) | 3.1.0 | reference | 信息层级：步骤（in-file step）→ 文件中引用（in-file reference）→ 披露引用（disclosed reference） |
| `ontology:concept/knowledge-artifact` | [knowledge-artifact.md](concept/knowledge-artifact.md) | 3.1.0 | reference | KnowledgeArtifact：知识实体分组 |
| `ontology:concept/knowledge-provenance` | [knowledge-provenance.md](concept/knowledge-provenance.md) | 2.0.0 | normative | 知识来源与可复核范围 |
| `ontology:concept/leading-words` | [leading-words.md](concept/leading-words.md) | 3.1.0 | reference | 锚定词：用预训练已有词锚定一类行为，以 token 而非句子重复 |
| `ontology:concept/meta-ontology` | [meta-ontology.md](concept/meta-ontology.md) | 2.0.0 | normative | 元本体：规则的语义来源 |
| `ontology:concept/model-invoked` | [model-invoked.md](concept/model-invoked.md) | 3.1.0 | reference | 模型调用技能：agent 可自主触发，常驻上下文负载 |
| `ontology:concept/nbu-data-encryption` | [nbu-data-encryption.md](concept/nbu-data-encryption.md) | 3.1.0 | reference | NBU加密研究资料实例；历史推断待原始二进制与记录核验，不继承任务类 |
| `ontology:concept/no-op-judgment` | [no-op-judgment.md](concept/no-op-judgment.md) | 3.1.0 | reference | no-op 的模型相对判定：是否改变默认行为取决于模型本身 |
| `ontology:concept/ontology-adoption` | [ontology-adoption.md](concept/ontology-adoption.md) | 3.4.0 | normative | 跨树采用清单、影响分析与显式迁移 |
| `ontology:concept/ontology-asset` | [ontology-asset.md](concept/ontology-asset.md) | 3.4.6 | normative | 本体节点序列化与权威边界 |
| `ontology:concept/ontology-creation-gate` | [ontology-creation-gate.md](concept/ontology-creation-gate.md) | 3.4.0 | normative | 本体创建与发布审查 |
| `ontology:concept/ontology-detach-verdict` | [ontology-detach-verdict.md](concept/ontology-detach-verdict.md) | 2.0.0 | normative | 引用解除的审查 |
| `ontology:concept/ontology-evolution` | [ontology-evolution.md](concept/ontology-evolution.md) | 3.4.0 | normative | 共享本体候选、不可变发布与并发修订 |
| `ontology:concept/ontology-fidelity-criterion` | [ontology-fidelity-criterion.md](concept/ontology-fidelity-criterion.md) | 3.0.0 | normative | 本体质量：语义可用而非形式计数 |
| `ontology:concept/ontology-reuse` | [ontology-reuse.md](concept/ontology-reuse.md) | 3.4.0 | normative | 复用优先的建模决策、固定定义与局部扩展 |
| `ontology:concept/ontology-rule-acyclic` | [ontology-rule-acyclic.md](concept/ontology-rule-acyclic.md) | 2.0.0 | normative | 按关系语义检查循环 |
| `ontology:concept/ontology-rule-attr-testable` | [ontology-rule-attr-testable.md](concept/ontology-rule-attr-testable.md) | 2.0.0 | normative | 属性约束与可观察验证 |
| `ontology:concept/ontology-rule-fidelity-body` | [ontology-rule-fidelity-body.md](concept/ontology-rule-fidelity-body.md) | 2.0.0 | normative | 正文应足以支持当前任务 |
| `ontology:concept/ontology-rule-fidelity-diagram` | [ontology-rule-fidelity-diagram.md](concept/ontology-rule-fidelity-diagram.md) | 2.0.0 | normative | 图与来源的实际价值 |
| `ontology:concept/ontology-rule-fidelity-generic` | [ontology-rule-fidelity-generic.md](concept/ontology-rule-fidelity-generic.md) | 2.0.0 | normative | 验证信号必须指向观测 |
| `ontology:concept/ontology-rule-guides-range` | [ontology-rule-guides-range.md](concept/ontology-rule-guides-range.md) | 2.0.0 | normative | 关系的类与实例范围 |
| `ontology:concept/ontology-rule-non-dangling` | [ontology-rule-non-dangling.md](concept/ontology-rule-non-dangling.md) | 2.0.0 | normative | 引用存在且可定位 |
| `ontology:concept/ontology-rule-richness` | [ontology-rule-richness.md](concept/ontology-rule-richness.md) | 2.0.0 | normative | 有意义的领域挂接 |
| `ontology:concept/ontology-rule-type-controlled` | [ontology-rule-type-controlled.md](concept/ontology-rule-type-controlled.md) | 2.0.0 | normative | 类型与目录分组一致 |
| `ontology:concept/ontology-rule` | [ontology-rule.md](concept/ontology-rule.md) | 2.0.0 | normative | 本体规则 |
| `ontology:concept/ontology-validate` | [ontology-validate.md](concept/ontology-validate.md) | 2.0.0 | normative | 本体验证职责（无自带执行器） |
| `ontology:pattern` | [pattern.md](concept/pattern.md) | 3.1.0 | reference | Pattern 类：可复用结构/方法 |
| `ontology:concept/pdca-acceptance-criterion` | [pdca-acceptance-criterion.md](concept/pdca-acceptance-criterion.md) | 3.0.0 | normative | 验收条件与判断层级 |
| `ontology:concept/pdca-ai-friendly-confirmation` | [pdca-ai-friendly-confirmation.md](concept/pdca-ai-friendly-confirmation.md) | 3.4.1 | normative | 按任务独立交互与真实确认 |
| `ontology:concept/pdca-architecture-review-metrics` | [pdca-architecture-review-metrics.md](concept/pdca-architecture-review-metrics.md) | 2.0.0 | normative | 架构审查的可证明指标 |
| `ontology:concept/pdca-architecture` | [pdca-architecture.md](concept/pdca-architecture.md) | 3.0.0 | normative | 规则、执行与事实的三层边界 |
| `ontology:concept/pdca-continuous-improvement` | [pdca-continuous-improvement.md](concept/pdca-continuous-improvement.md) | 3.4.0 | normative | 知识处置、候选与发布 |
| `ontology:concept/pdca-evidence` | [pdca-evidence.md](concept/pdca-evidence.md) | 3.4.9 | normative | 证据、测试运行与不可变版本 |
| `ontology:concept/pdca-execution-contract` | [pdca-execution-contract.md](concept/pdca-execution-contract.md) | 3.4.7 | normative | 节点场景执行契约与不可漂移基线 |
| `ontology:concept/pdca-feedback` | [pdca-feedback.md](concept/pdca-feedback.md) | 2.0.0 | normative | 任务反馈的证据范围 |
| `ontology:concept/pdca-gate-do` | [pdca-gate-do.md](concept/pdca-gate-do.md) | 2.0.0 | normative | Do准入的引用节点 |
| `ontology:concept/pdca-gate` | [pdca-gate.md](concept/pdca-gate.md) | 3.4.7 | normative | 任务自主阶段门禁与测试判据 |
| `ontology:concept/pdca-home` | [pdca-home.md](concept/pdca-home.md) | 3.1.0 | reference | 已退役：pdca-home |
| `ontology:concept/pdca-ontology-ready` | [pdca-ontology-ready.md](concept/pdca-ontology-ready.md) | 3.1.0 | normative | 本体基线可用性 |
| `ontology:concept/pdca-phase-status` | [pdca-phase-status.md](concept/pdca-phase-status.md) | 3.2.0 | normative | 阶段、任务状态与产物结果分离 |
| `ontology:concept/pdca-phase` | [pdca-phase.md](concept/pdca-phase.md) | 3.2.0 | normative | PDCA 方法阶段 |
| `ontology:concept/pdca-provable-skill-increments` | [pdca-provable-skill-increments.md](concept/pdca-provable-skill-increments.md) | 2.0.0 | normative | 流程增量的证据层级 |
| `ontology:concept/pdca-recovery` | [pdca-recovery.md](concept/pdca-recovery.md) | 3.4.10 | normative | 当前任务恢复与失败处置 |
| `ontology:concept/pdca-source-diagram-doc-verification` | [pdca-source-diagram-doc-verification.md](concept/pdca-source-diagram-doc-verification.md) | 2.0.0 | normative | 源码图解的验证步骤 |
| `ontology:concept/pdca-task` | [pdca-task.md](concept/pdca-task.md) | 3.4.10 | normative | 每节点完整任务与全新自主 Agent |
| `ontology:concept/pdca-transition` | [pdca-transition.md](concept/pdca-transition.md) | 3.4.2 | normative | 单阶段转换、回执与幂等 |
| `ontology:concept/pdca-verdict` | [pdca-verdict.md](concept/pdca-verdict.md) | 3.4.7 | normative | 任务判定、被审对象与发布结果 |
| `ontology:concept/pdca` | [pdca.md](concept/pdca.md) | 3.4.10 | normative | 本体树驱动的三场景 AI 工作协议 |
| `ontology:concept/phase-boundary-decision-tree` | [phase-boundary-decision-tree.md](concept/phase-boundary-decision-tree.md) | 3.0.0 | normative | 阶段、场景与等待的边界 |
| `ontology:pitfall` | [pitfall.md](concept/pitfall.md) | 3.1.0 | reference | Pitfall 类：易错点/反模式 |
| `ontology:concept/pointer-wording` | [pointer-wording.md](concept/pointer-wording.md) | 3.1.0 | reference | 指针措辞：上下文指针的措辞决定触发可靠性，弱措辞即方差 bug |
| `ontology:principle` | [principle.md](concept/principle.md) | 3.1.0 | reference | Principle 类：必须遵守的准则 |
| `ontology:concept/process-complexity-ruling` | [process-complexity-ruling.md](concept/process-complexity-ruling.md) | 2.0.0 | normative | 流程复杂度的取舍 |
| `ontology:concept/process-value-verdict` | [process-value-verdict.md](concept/process-value-verdict.md) | 2.0.0 | normative | 流程规则的价值判定 |
| `ontology:concept/process` | [process.md](concept/process.md) | 3.1.0 | reference | Process：执行过程分组 |
| `ontology:concept/progressive-disclosure` | [progressive-disclosure.md](concept/progressive-disclosure.md) | 3.1.0 | reference | 渐进披露：将引用推到指针后方，保护信息层级不被破坏 |
| `ontology:concept/real-project-mechanism-validation` | [real-project-mechanism-validation.md](concept/real-project-mechanism-validation.md) | 2.0.0 | normative | 真实项目验证与模拟区分 |
| `ontology:concept/research-first-compliance` | [research-first-compliance.md](concept/research-first-compliance.md) | 2.0.0 | normative | 调研前置符合性 |
| `ontology:concept/research-first-gate` | [research-first-gate.md](concept/research-first-gate.md) | 2.0.0 | normative | 调研前置依赖由契约决定 |
| `ontology:concept/research-web-mandatory-gate` | [research-web-mandatory-gate.md](concept/research-web-mandatory-gate.md) | 2.0.0 | normative | 外部检索的条件与边界 |
| `ontology:concept/resource-ownership` | [resource-ownership.md](concept/resource-ownership.md) | 3.2.0 | normative | 资源预约、旧执行者隔离与业务操作身份 |
| `ontology:concept/retrospective` | [retrospective.md](concept/retrospective.md) | 3.1.0 | reference | Act 阶段结构化回顾的七类改进候选模型，覆盖导航、校验、规范、指令分层、工具效率、空操作与信息可达性 |
| `ontology:concept/round` | [round.md](concept/round.md) | 3.1.0 | reference | 轮次：每轮询问整个前沿 |
| `ontology:concept/router-skill` | [router-skill.md](concept/router-skill.md) | 2.0.0 | normative | 最小入口 |
| `ontology:concept/runtime-transition-coordinator` | [runtime-transition-coordinator.md](concept/runtime-transition-coordinator.md) | 3.0.0 | normative | 宿主写入协调，不是父 Agent 审批 |
| `ontology:concept/scope-coverage-gate` | [scope-coverage-gate.md](concept/scope-coverage-gate.md) | 2.0.0 | normative | 契约范围与产物覆盖 |
| `ontology:concept/self-optimization-loop` | [self-optimization-loop.md](concept/self-optimization-loop.md) | 2.0.0 | normative | 自我优化：观测到独立验证 |
| `ontology:concept/setup-skill` | [setup-skill.md](concept/setup-skill.md) | 3.1.0 | reference | 已退役：setup-skill |
| `ontology:concept/shared-reference` | [shared-reference.md](concept/shared-reference.md) | 3.1.0 | reference | 共享引用：多个技能共同需要的引用内容 |
| `ontology:concept/sharpen-language` | [sharpen-language.md](concept/sharpen-language.md) | 3.1.0 | reference | 模糊语言精确化：提出精确的规范术语 |
| `ontology:concept/skill-as-ontology` | [skill-as-ontology.md](concept/skill-as-ontology.md) | 3.4.6 | reference | 技能知识定义、调用契约与运行证据的分工；不引入独立生命周期 |
| `ontology:concept/skill-invocation-contract` | [skill-invocation-contract.md](concept/skill-invocation-contract.md) | 2.0.0 | normative | 技能调用的范围 |
| `ontology:concept/skill-invocation` | [skill-invocation.md](concept/skill-invocation.md) | 3.4.6 | reference | 技能调用：基于 ontology 知识单元的调用机制 |
| `ontology:concept/skill-mechanics-detail` | [skill-mechanics-detail.md](concept/skill-mechanics-detail.md) | 2.0.0 | normative | 技能加载边界 |
| `ontology:concept/skill-mechanics` | [skill-mechanics.md](concept/skill-mechanics.md) | 3.4.6 | normative | 技能与流程的分工 |
| `ontology:concept/step` | [step.md](concept/step.md) | 3.1.0 | reference | 步骤：agent 按序执行的动作，含完成标准 |
| `ontology:concept/task-control` | [task-control.md](concept/task-control.md) | 3.2.0 | normative | 任务控制事件、取消超时与安全接续 |
| `ontology:concept/task-decomposition` | [task-decomposition.md](concept/task-decomposition.md) | 3.4.9 | normative | 递归子本体判断：叶子是验收结论，不是父任务预设 |
| `ontology:concept/task-record-identity` | [task-record-identity.md](concept/task-record-identity.md) | 3.4.0 | normative | 任务身份、尝试与唯一记录 |
| `ontology:concept/task-rework` | [task-rework.md](concept/task-rework.md) | 3.4.7 | normative | 失败、返工与回归：任务级闭环 |
| `ontology:concept/task-test-case` | [task-test-case.md](concept/task-test-case.md) | 3.4.6 | normative | 单元测试案例：输入、oracle 与失败诊断 |
| `ontology:concept/task-unit-test` | [task-unit-test.md](concept/task-unit-test.md) | 3.4.7 | normative | 任务单元测试：正例、反例、覆盖与证据 |
| `ontology:concept/teach` | [teach.md](concept/teach.md) | 3.1.0 | reference | 教学技能：多会话教授新技能或概念 |
| `ontology:concept/template-minimal` | [template-minimal.md](concept/template-minimal.md) | 2.0.0 | normative | 模板的最小性 |
| `ontology:concept/timeline-integrity-gate` | [timeline-integrity-gate.md](concept/timeline-integrity-gate.md) | 2.0.0 | normative | 事件顺序与真实时间 |
| `ontology:concept/to-questionnaire` | [to-questionnaire.md](concept/to-questionnaire.md) | 3.1.0 | reference | 问卷技能：将决策转化为 Markdown 问卷 |
| `ontology:concept/to-spec` | [to-spec.md](concept/to-spec.md) | 3.4.6 | reference | 将对话转化为规格说明：grilling 输出的结构化捕获 |
| `ontology:concept/tracer-bullet` | [tracer-bullet.md](concept/tracer-bullet.md) | 3.1.0 | reference | 追踪弹：小而完整的垂直切片 |
| `ontology:concept/triage-state-machine` | [triage-state-machine.md](concept/triage-state-machine.md) | 2.0.0 | normative | 需求分诊不是额外生命周期 |
| `ontology:concept/triage` | [triage.md](concept/triage.md) | 3.1.0 | reference | 分诊：状态机、Agent 就绪简要、AI 免责声明 |
| `ontology:concept/trigger-condition` | [trigger-condition.md](concept/trigger-condition.md) | 3.1.0 | reference | 触发条件：user-invoked 和 model-invoked 技能的形式化触发机制 |
| `ontology:concept/two-loads` | [two-loads.md](concept/two-loads.md) | 3.1.0 | reference | 两种负载：上下文负载（context load）与认知负载（cognitive load） |
| `ontology:concept/user-invoked` | [user-invoked.md](concept/user-invoked.md) | 3.1.0 | reference | 用户调用技能：仅用户手动触发，零上下文负载 |
| `ontology:concept/version-bump-rule` | [version-bump-rule.md](concept/version-bump-rule.md) | 3.1.0 | reference | 本体正文变更必改版本元数据：modified 取落盘日，versionIRI 修订号加一 |
| `ontology:concept/vertical-slice` | [vertical-slice.md](concept/vertical-slice.md) | 3.1.0 | reference | 垂直切片：穿过每一层的窄但完整的路径 |
| `ontology:concept/wait-what` | [wait-what.md](concept/wait-what.md) | 3.1.0 | reference | 上下文缺失时重新 pitch：用 CONTEXT.md 词汇重新表述 |
| `ontology:concept/wizard` | [wizard.md](concept/wizard.md) | 3.1.0 | reference | 向导技能：交互式 bash 向导，引导用户完成步骤 |
| `ontology:concept/work-dependency-graph` | [work-dependency-graph.md](concept/work-dependency-graph.md) | 3.4.2 | normative | 工作实例依赖图、版本提交与检测时机 |
| `ontology:concept/work-node-contract` | [work-node-contract.md](concept/work-node-contract.md) | 3.4.1 | normative | 节点契约：实体、组合和单元测试 |
| `ontology:concept/work-ontology-tree` | [work-ontology-tree.md](concept/work-ontology-tree.md) | 3.4.2 | normative | 工作目标本体树：身份、组成与冻结 |
| `ontology:concept/work-tree-scheduling` | [work-tree-scheduling.md](concept/work-tree-scheduling.md) | 3.4.5 | normative | 树形调度、并行与交付汇聚 |
| `ontology:concept/workflow-state` | [workflow-state.md](concept/workflow-state.md) | 3.2.0 | normative | 任务工作流位置的共同类，区分方法阶段与终态 |
| `ontology:concept/writing-for-agents` | [writing-for-agents.md](concept/writing-for-agents.md) | 3.1.0 | reference | 为 Agent 写作：文档和技能的通用写作原则 |
| `ontology:decision/t2153-opt-backlog` | [t2153-opt-backlog.md](decision/t2153-opt-backlog.md) | 3.1.0 | reference | T2153优化 backlog 决议 Santiago：P0已修2项，P1候选8项，P2候选2项的归口与状态 |
| `ontology:domain/backup` | [backup.md](domain/core/backup.md) | 3.1.0 | reference | backup 领域知识根节点（由 ontology/domain/backup/ 迁移） |
| `ontology:domain/bcachefs` | [bcachefs.md](domain/core/bcachefs.md) | 3.1.0 | reference | Bcachefs 领域本体 — COW btree 文件系统全栈（工具+内核模块） |
| `ontology:domain/benchmark-build-profile-baseline-matching` | [benchmark-build-profile-baseline-matching.md](domain/core/benchmark-build-profile-baseline-matching.md) | 3.1.0 | reference | 基准对照与并发测试的验证口径陷阱 |
| `ontology:domain/benchmark-paired-comparison-noise` | [benchmark-paired-comparison-noise.md](domain/core/benchmark-paired-comparison-noise.md) | 3.1.0 | reference | 噪声环境下性能断言：配对对比测量 |
| `ontology:domain/benchmark-small-pack-streaming-decode` | [benchmark-small-pack-streaming-decode.md](domain/core/benchmark-small-pack-streaming-decode.md) | 3.1.0 | reference | Small-file Pack 流式解码 |
| `ontology:domain/benchmark-small-writer-pool-parallelism` | [benchmark-small-writer-pool-parallelism.md](domain/core/benchmark-small-writer-pool-parallelism.md) | 3.1.0 | reference | Small Writer Pool Parallelism |
| `ontology:domain/benchmark` | [benchmark.md](domain/core/benchmark.md) | 3.1.0 | reference | benchmark 领域知识根节点（由 ontology/domain/benchmark/ 迁移） |
| `ontology:domain/build-config-go-module-in-xmake` | [build-config-go-module-in-xmake.md](domain/core/build-config-go-module-in-xmake.md) | 3.1.0 | reference | 多包 Go Module 接入 xmake 构建体系 |
| `ontology:domain/build-config-hide-static-lib-symbols` | [build-config-hide-static-lib-symbols.md](domain/core/build-config-hide-static-lib-symbols.md) | 3.1.0 | reference | 第三方 C 静态库隐藏 API 符号：覆盖 visibility 宏 |
| `ontology:domain/build-config` | [build-config.md](domain/core/build-config.md) | 3.1.0 | reference | build-config 领域知识根节点（由 ontology/domain/build-config/ 迁移） |
| `ontology:domain/cli-help-cli-help-regression` | [cli-help-cli-help-regression.md](domain/core/cli-help-cli-help-regression.md) | 3.1.0 | reference | CLI help 完整性与回归规范 |
| `ontology:domain/cli-help` | [cli-help.md](domain/core/cli-help.md) | 3.1.0 | reference | cli-help 领域知识根节点（由 ontology/domain/cli-help/ 迁移） |
| `ontology:domain/control-plane-nonblocking-ingress-v81-control-frame-nonblocking` | [control-plane-nonblocking-ingress-v81-control-frame-nonblocking.md](domain/core/control-plane-nonblocking-ingress-v81-control-frame-nonblocking.md) | 3.1.0 | reference | 控制面非阻塞 ingress + 共享 work 池（v81 经验） |
| `ontology:domain/control-plane-nonblocking-ingress-v81-control-plane-perf-fastpath` | [control-plane-nonblocking-ingress-v81-control-plane-perf-fastpath.md](domain/core/control-plane-nonblocking-ingress-v81-control-plane-perf-fastpath.md) | 3.1.0 | reference | v81 控制面性能：纯计算控制帧 fastpath + WRITE 归并 |
| `ontology:domain/control-plane-nonblocking-ingress` | [control-plane-nonblocking-ingress.md](domain/core/control-plane-nonblocking-ingress.md) | 3.1.0 | reference | control-plane-nonblocking-ingress 领域知识根节点（由 ontology/domain/control-plane-nonblocking-ingress/ 迁移） |
| `ontology:domain/core-btree-node-rewrite-key-extent-contract` | [core-btree-node-rewrite-key-extent-contract.md](domain/core/core-btree-node-rewrite-key-extent-contract.md) | 3.1.0 | reference | btree 节点重写 key 构造的 extent 保留契约 |
| `ontology:domain/core-btree-random-op-consistency-proptest-pattern` | [core-btree-random-op-consistency-proptest-pattern.md](domain/core/core-btree-random-op-consistency-proptest-pattern.md) | 3.1.0 | reference | btree 随机操作序列一致性属性测试模式（多 btree id） |
| `ontology:domain/core-btree-split-proptest-enomem-restart-pattern` | [core-btree-split-proptest-enomem-restart-pattern.md](domain/core/core-btree-split-proptest-enomem-restart-pattern.md) | 3.1.0 | reference | btree 分裂压力测试 + ENOMEM restart 修复模式 |
| `ontology:domain/core-combined-op-domain-model` | [core-combined-op-domain-model.md](domain/core/core-combined-op-domain-model.md) | 3.1.0 | reference | 组合 op 域模型：btree × alloc 属性测试设计（T0202） |
| `ontology:domain/core-concurrent-combined-commit-log` | [core-concurrent-combined-commit-log.md](domain/core/core-concurrent-combined-commit-log.md) | 3.1.0 | reference | 并发组合提交日志：多写者 × 崩溃恢复精确断言（T0203） |
| `ontology:domain/core-derived-state-validator-recovery-gate` | [core-derived-state-validator-recovery-gate.md](domain/core/core-derived-state-validator-recovery-gate.md) | 3.1.0 | reference | Derived state validator and recovery publication gate |
| `ontology:domain/core-deterministic-interleave` | [core-deterministic-interleave.md](domain/core/core-deterministic-interleave.md) | 3.1.0 | reference | 事务级确定性交错模式（Deterministic Interleave） |
| `ontology:domain/core-device-bucket-geometry-pointer-contract` | [core-device-bucket-geometry-pointer-contract.md](domain/core/core-device-bucket-geometry-pointer-contract.md) | 3.1.0 | reference | 设备 bucket geometry 与 physical pointer 合约 |
| `ontology:domain/core-discard-boundary-guards` | [core-discard-boundary-guards.md](domain/core/core-discard-boundary-guards.md) | 3.1.0 | reference | discard 边界守卫：open bucket 与设备可写 |
| `ontology:domain/core-discard-worker-fifo-fairness` | [core-discard-worker-fifo-fairness.md](domain/core/core-discard-worker-fifo-fairness.md) | 3.1.0 | reference | discard worker FIFO 公平队列语义 |
| `ontology:domain/core-file-metadata-management-via-lmdb` | [core-file-metadata-management-via-lmdb.md](domain/core/core-file-metadata-management-via-lmdb.md) | 3.1.0 | reference | 文件元信息的 LMDB 管理模型 |
| `ontology:domain/core-foreground-merge-mount-semantics` | [core-foreground-merge-mount-semantics.md](domain/core/core-foreground-merge-mount-semantics.md) | 3.1.0 | reference | 前台合并挂载语义链：merge_count 区分 / 打包追加 / 锁升级 / 谐振规避（T0204） |
| `ontology:domain/core-fsck-repair-fault-injection` | [core-fsck-repair-fault-injection.md](domain/core/core-fsck-repair-fault-injection.md) | 3.1.0 | reference | fsck 修复路径故障注入 |
| `ontology:domain/core-fsck-repair-mode` | [core-fsck-repair-mode.md](domain/core/core-fsck-repair-mode.md) | 3.1.0 | reference | fsck 修复模式模式（Fsck Repair Mode） |
| `ontology:domain/core-fsck-style-cli-healthcheck` | [core-fsck-style-cli-healthcheck.md](domain/core/core-fsck-style-cli-healthcheck.md) | 3.1.0 | reference | fsck 风格 CLI 健康检查入口模式 |
| `ontology:domain/core-journal-key-layout-validation` | [core-journal-key-layout-validation.md](domain/core/core-journal-key-layout-validation.md) | 3.1.0 | reference | Journal btree key 布局校验边界 |
| `ontology:domain/core-journal-reclaim-proptest-pattern` | [core-journal-reclaim-proptest-pattern.md](domain/core/core-journal-reclaim-proptest-pattern.md) | 3.1.0 | reference | journal reclaim 属性测试设计模式 |
| `ontology:domain/core-model-guard-decision-injection` | [core-model-guard-decision-injection.md](domain/core/core-model-guard-decision-injection.md) | 3.1.0 | reference | 模型守卫裁决注入模式（Model Guard-Decision Injection） |
| `ontology:domain/core-open-bucket-lifecycle-and-device-rw` | [core-open-bucket-lifecycle-and-device-rw.md](domain/core/core-open-bucket-lifecycle-and-device-rw.md) | 3.1.0 | reference | open bucket 生命周期与设备 rw 初始化 |
| `ontology:domain/core-persistent-concurrency-crash-recovery` | [core-persistent-concurrency-crash-recovery.md](domain/core/core-persistent-concurrency-crash-recovery.md) | 3.1.0 | reference | 持久化并发交错：并发写者 × 确定性崩溃点 |
| `ontology:domain/core-physical-pointer-derived-state-recovery-boundary` | [core-physical-pointer-derived-state-recovery-boundary.md](domain/core/core-physical-pointer-derived-state-recovery-boundary.md) | 3.1.0 | reference | 物理 pointer 派生状态与恢复边界 |
| `ontology:domain/core-pointer-trigger-derived-chain` | [core-pointer-trigger-derived-chain.md](domain/core/core-pointer-trigger-derived-chain.md) | 3.1.0 | reference | pointer trigger 派生三件套与 AC-1 锚点模式（T0183） |
| `ontology:domain/core-project-goal` | [core-project-goal.md](domain/core/core-project-goal.md) | 3.1.0 | reference | 项目主要目标 |
| `ontology:domain/core-public-guard-assertions` | [core-public-guard-assertions.md](domain/core/core-public-guard-assertions.md) | 3.1.0 | reference | 公开守卫断言套件（verify_guard_invariants 模式） |
| `ontology:domain/core-recovery-derived-state-publication-gate` | [core-recovery-derived-state-publication-gate.md](domain/core/core-recovery-derived-state-publication-gate.md) | 3.1.0 | reference | 派生状态的恢复发布门槛 |
| `ontology:domain/core-recovery-fault-matrix-public-validation` | [core-recovery-fault-matrix-public-validation.md](domain/core/core-recovery-fault-matrix-public-validation.md) | 3.1.0 | reference | Recovery fault matrix and public derived validation |
| `ontology:domain/core-snapshot-table-lifecycle-filter-semantics` | [core-snapshot-table-lifecycle-filter-semantics.md](domain/core/core-snapshot-table-lifecycle-filter-semantics.md) | 3.1.0 | reference | 快照表生命周期与过滤语义验证模式 |
| `ontology:domain/core-tech-poc-aead-auth-encryption` | [core-tech-poc-aead-auth-encryption.md](domain/core/core-tech-poc-aead-auth-encryption.md) | 3.1.0 | reference | 备份传输加密：AEAD 认证加密（AES-GCM vs ChaCha20-Poly1305） |
| `ontology:domain/core-tech-poc-bloom-filter-dedup` | [core-tech-poc-bloom-filter-dedup.md](domain/core/core-tech-poc-bloom-filter-dedup.md) | 3.1.0 | reference | 备份去重索引：布隆过滤器 vs 精确哈希表（实测对照） |
| `ontology:domain/core-tech-poc-frame-multiplexing` | [core-tech-poc-frame-multiplexing.md](domain/core/core-tech-poc-frame-multiplexing.md) | 3.1.0 | reference | 备份传输：单连接多流帧复用（16B 帧头 + 累积缓冲拆帧器） |
| `ontology:domain/core-tech-poc-hash-selection` | [core-tech-poc-hash-selection.md](domain/core/core-tech-poc-hash-selection.md) | 3.1.0 | reference | 备份引擎哈希选型：XXH3 / BLAKE3 / SHA-256（实测对照） |
| `ontology:domain/core-tech-poc-reed-solomon-erasure` | [core-tech-poc-reed-solomon-erasure.md](domain/core/core-tech-poc-reed-solomon-erasure.md) | 3.1.0 | reference | 备份可靠性：Reed-Solomon 纠删码（GF(2^8) RS(5,3) 实测） |
| `ontology:domain/core-tech-poc-zero-copy-transfer` | [core-tech-poc-zero-copy-transfer.md](domain/core/core-tech-poc-zero-copy-transfer.md) | 3.1.0 | reference | 备份传输：零拷贝 sendfile/splice vs 用户态副本（实测对照） |
| `ontology:domain/core-tech-poc` | [core-tech-poc.md](domain/core/core-tech-poc.md) | 3.1.0 | reference | core-tech-poc 领域知识根节点（由 ontology/domain/core-tech-poc/ 迁移） |
| `ontology:domain/core-transactional-pointer-runner-publication` | [core-transactional-pointer-runner-publication.md](domain/core/core-transactional-pointer-runner-publication.md) | 3.1.0 | reference | Transactional pointer runner 与 publication 边界 |
| `ontology:domain/core-trigger-audit-derived-state-boundary` | [core-trigger-audit-derived-state-boundary.md](domain/core/core-trigger-audit-derived-state-boundary.md) | 3.1.0 | reference | Trigger 审计的派生状态边界 |
| `ontology:domain/core-verify-all-aggregate-pattern` | [core-verify-all-aggregate-pattern.md](domain/core/core-verify-all-aggregate-pattern.md) | 3.1.0 | reference | verify_all 聚合校验入口模式 |
| `ontology:domain/core-worker-verify-checkpoint-pattern` | [core-worker-verify-checkpoint-pattern.md](domain/core/core-worker-verify-checkpoint-pattern.md) | 3.1.0 | reference | worker 变体最终一致性检查点模式 |
| `ontology:domain/core` | [core.md](domain/core/core.md) | 3.1.0 | reference | core 领域知识根节点（由 ontology/domain/core/ 迁移） |
| `ontology:domain/data-formats-backup-tools-serialization-practice` | [data-formats-backup-tools-serialization-practice.md](domain/core/data-formats-backup-tools-serialization-practice.md) | 3.1.0 | reference | 备份类程序序列化/存储格式工业实践 |
| `ontology:domain/data-formats-mysql-innodb-physical-read-notes` | [data-formats-mysql-innodb-physical-read-notes.md](domain/core/data-formats-mysql-innodb-physical-read-notes.md) | 3.1.0 | reference | MySQL InnoDB 物理直读 → Parquet 工程要点 |
| `ontology:domain/data-formats-parquet-technical-reference` | [data-formats-parquet-technical-reference.md](domain/core/data-formats-parquet-technical-reference.md) | 3.1.0 | reference | Parquet 技术参考索引 |
| `ontology:domain/data-formats-pg-consistency-verification-method` | [data-formats-pg-consistency-verification-method.md](domain/core/data-formats-pg-consistency-verification-method.md) | 3.1.0 | reference | PG→Parquet 转换校验方法：五维校验 + mutation 基线 |
| `ontology:domain/data-formats-pg-heap-null-bitmap` | [data-formats-pg-heap-null-bitmap.md](domain/core/data-formats-pg-heap-null-bitmap.md) | 3.1.0 | reference | PG heap null bitmap 物理布局（含读写约定） |
| `ontology:domain/data-formats-pg-heap-physical-read-notes` | [data-formats-pg-heap-physical-read-notes.md](domain/core/data-formats-pg-heap-physical-read-notes.md) | 3.1.0 | reference | PG heap 文件物理直读工程要点 |
| `ontology:domain/data-formats-pg-to-parquet-path-benchmark` | [data-formats-pg-to-parquet-path-benchmark.md](domain/core/data-formats-pg-to-parquet-path-benchmark.md) | 3.1.0 | reference | PostgreSQL → Parquet 转换路径性能对照（实测） |
| `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac1-four-versions` | [data-formats-t0250-mysql-parquet-physical-evidence-ac1-four-versions.md](domain/core/data-formats-t0250-mysql-parquet-physical-evidence-ac1-four-versions.md) | 3.1.0 | reference | AC-1 MySQL 四版本 InnoDB .ibd 物理直读验证（5.6/5.7/8.0/8.4） |
| `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac10-pg-100m-frozen-fix` | [data-formats-t0250-mysql-parquet-physical-evidence-ac10-pg-100m-frozen-fix.md](domain/core/data-formats-t0250-mysql-parquet-physical-evidence-ac10-pg-100m-frozen-fix.md) | 3.1.0 | reference | PG 100M 物理直读回归：FROZEN hint-bit 误判根因与修复（AC-10） |
| `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac5-benchmark` | [data-formats-t0250-mysql-parquet-physical-evidence-ac5-benchmark.md](domain/core/data-formats-t0250-mysql-parquet-physical-evidence-ac5-benchmark.md) | 3.1.0 | reference | AC-5 四路径 1M 性能对照（≥3 轮流中位数，ZSTD 写出） |
| `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-ac7-100m-benchmark` | [data-formats-t0250-mysql-parquet-physical-evidence-ac7-100m-benchmark.md](domain/core/data-formats-t0250-mysql-parquet-physical-evidence-ac7-100m-benchmark.md) | 3.1.0 | reference | AC-7 100M 行端到端全路径对照（MySQL 8.0 → Parquet） |
| `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-evidence` | [data-formats-t0250-mysql-parquet-physical-evidence-evidence.md](domain/core/data-formats-t0250-mysql-parquet-physical-evidence-evidence.md) | 3.1.0 | reference | PG 物理直读 → Parquet 验证记录（T0250 Do 阶段） |
| `ontology:domain/data-formats-t0250-mysql-parquet-physical-evidence-research-report` | [data-formats-t0250-mysql-parquet-physical-evidence-research-report.md](domain/core/data-formats-t0250-mysql-parquet-physical-evidence-research-report.md) | 3.1.0 | reference | 调研报告 — MySQL / PostgreSQL 数据文件直接转换 Parquet |
| `ontology:domain/data-formats-t0300-mysql-version-convert-test` | [data-formats-t0300-mysql-version-convert-test.md](domain/core/data-formats-t0300-mysql-version-convert-test.md) | 3.1.0 | reference | MySQL 多版本转换测试（T0300）— 逐版本 .ibd→Parquet 全量对照 |
| `ontology:domain/data-formats-t0301-pg-version-convert-test` | [data-formats-t0301-pg-version-convert-test.md](domain/core/data-formats-t0301-pg-version-convert-test.md) | 3.1.0 | reference | PG 多版本 heap+CLOG 物理直读→Parquet 转换（T0301 实测知识） |
| `ontology:domain/data-formats` | [data-formats.md](domain/core/data-formats.md) | 3.1.0 | reference | data-formats 领域知识根节点（由 ontology/domain/data-formats/ 迁移） |
| `ontology:domain/debugging-c-buffer-api-size-t-frame-validation` | [debugging-c-buffer-api-size-t-frame-validation.md](domain/core/debugging-c-buffer-api-size-t-frame-validation.md) | 3.1.0 | reference | C 缓冲区 API 输出参数类型陷阱与帧校验模式 |
| `ontology:domain/debugging-rpc-epoll-blocking-fd-trap` | [debugging-rpc-epoll-blocking-fd-trap.md](domain/core/debugging-rpc-epoll-blocking-fd-trap.md) | 3.1.0 | reference | rpc-epoll 与业务层 fd 语义冲突：O_NONBLOCK ↔ 阻塞读 |
| `ontology:domain/debugging-stream-frame-integration-traps` | [debugging-stream-frame-integration-traps.md](domain/core/debugging-stream-frame-integration-traps.md) | 3.1.0 | reference | 流帧协议集成陷阱：长度前缀、整块 END、序列化对称 |
| `ontology:domain/debugging` | [debugging.md](domain/core/debugging.md) | 3.1.0 | reference | debugging 领域知识根节点（由 ontology/domain/debugging/ 迁移） |
| `ontology:domain/editor-config-neovim-config-audit` | [editor-config-neovim-config-audit.md](domain/core/editor-config-neovim-config-audit.md) | 3.1.0 | reference | neovim 配置体检方法论：检查清单与可执行命令 |
| `ontology:domain/editor-config` | [editor-config.md](domain/core/editor-config.md) | 3.1.0 | reference | editor-config 领域知识根节点（由 ontology/domain/editor-config/ 迁移） |
| `ontology:domain/encryption-modes` | [encryption-modes.md](domain/core/encryption-modes.md) | 3.1.0 | reference | 工作模式索引：不复制算法公式作为第二权威 |
| `ontology:domain/gm-algorithm-suite` | [gm-algorithm-suite.md](domain/core/gm-algorithm-suite.md) | 3.1.0 | reference | 国密算法体系（SM1-SM4/SM7/SM9）本体与 SM4 分组结构及对称模式族不变量 |
| `ontology:domain/linux-epoll-eventloop-backupstream-v65-v101-arch-evolution` | [linux-epoll-eventloop-backupstream-v65-v101-arch-evolution.md](domain/core/linux-epoll-eventloop-backupstream-v65-v101-arch-evolution.md) | 3.1.0 | reference | backupstream v65→v101 架构演进模式（36 提交学习沉淀） |
| `ontology:domain/linux-epoll-eventloop-dynamic-deadline-wakeup` | [linux-epoll-eventloop-dynamic-deadline-wakeup.md](domain/core/linux-epoll-eventloop-dynamic-deadline-wakeup.md) | 3.1.0 | reference | epoll 事件循环工业对齐：最小堆定时器 + data.ptr + eventfd 唤醒 |
| `ontology:domain/linux-epoll-eventloop-event-loop-time-conservation` | [linux-epoll-eventloop-event-loop-time-conservation.md](domain/core/linux-epoll-eventloop-event-loop-time-conservation.md) | 3.1.0 | reference | 事件循环时间守恒分解（event-loop time conservation accounting） |
| `ontology:domain/linux-epoll-eventloop-multireactor-so-reuseport` | [linux-epoll-eventloop-multireactor-so-reuseport.md](domain/core/linux-epoll-eventloop-multireactor-so-reuseport.md) | 3.1.0 | reference | 多 Reactor 分片：SO_REUSEPORT 多监听（nginx reuseport 同款） |
| `ontology:domain/linux-epoll-eventloop-rpc-conn-idle-reclaim` | [linux-epoll-eventloop-rpc-conn-idle-reclaim.md](domain/core/linux-epoll-eventloop-rpc-conn-idle-reclaim.md) | 3.1.0 | reference | rpc 复用连接空闲回收与时序（POLLRDHUP/EOF） |
| `ontology:domain/linux-epoll-eventloop-transport-ownership-model` | [linux-epoll-eventloop-transport-ownership-model.md](domain/core/linux-epoll-eventloop-transport-ownership-model.md) | 3.1.0 | reference | 并发安全的传输所有权组织方法论：两容器 + 一抽象 + 一契约 |
| `ontology:domain/linux-epoll-eventloop` | [linux-epoll-eventloop.md](domain/core/linux-epoll-eventloop.md) | 3.1.0 | reference | linux-epoll-eventloop 领域知识根节点（由 ontology/domain/linux-epoll-eventloop/ 迁移） |
| `ontology:domain/lmdb-vl32-no-mmap-build-gate` | [lmdb-vl32-no-mmap-build-gate.md](domain/core/lmdb-vl32-no-mmap-build-gate.md) | 3.1.0 | reference | LMDB VL32 No-mmap Build Gate |
| `ontology:domain/lmdb` | [lmdb.md](domain/core/lmdb.md) | 3.1.0 | reference | lmdb 领域知识根节点（由 ontology/domain/lmdb/ 迁移） |
| `ontology:domain/mysql-backup-recovery-consistency` | [mysql-backup-recovery-consistency.md](domain/core/mysql-backup-recovery-consistency.md) | 3.1.0 | reference | MySQL 备份恢复一致性 — 机制与边界 |
| `ontology:domain/mysql-normal-shutdown-visibility-scope` | [mysql-normal-shutdown-visibility-scope.md](domain/core/mysql-normal-shutdown-visibility-scope.md) | 3.1.0 | reference | MySQL 正常关闭场景可见性范围（为什么不需要 undo/trx_sys） |
| `ontology:domain/mysql-schema-nullable-contract` | [mysql-schema-nullable-contract.md](domain/core/mysql-schema-nullable-contract.md) | 3.1.0 | reference | MySQL --schema 必须如实标注 nullable（InnoDB 长度数组契约） |
| `ontology:domain/mysql` | [mysql.md](domain/core/mysql.md) | 3.1.0 | reference | mysql 领域知识根节点（由 ontology/domain/mysql/ 迁移） |
| `ontology:domain/nbu` | [nbu.md](domain/core/nbu.md) | 3.1.0 | reference | nbu 领域知识根节点（由 ontology/domain/nbu/ 迁移） |
| `ontology:domain/network-bandwidth-control-backup-bw-limit-algo-selection` | [network-bandwidth-control-backup-bw-limit-algo-selection.md](domain/core/network-bandwidth-control-backup-bw-limit-algo-selection.md) | 3.1.0 | reference | 备份限流算法选型：动态窗口 vs 令牌桶（实测对照） |
| `ontology:domain/network-bandwidth-control` | [network-bandwidth-control.md](domain/core/network-bandwidth-control.md) | 3.1.0 | reference | network-bandwidth-control 领域知识根节点（由 ontology/domain/network-bandwidth-control/ 迁移） |
| `ontology:domain/observability-structured-logging-jsonl-rotation` | [observability-structured-logging-jsonl-rotation.md](domain/core/observability-structured-logging-jsonl-rotation.md) | 3.1.0 | reference | 生产级备份工具结构化日志基线 |
| `ontology:domain/observability` | [observability.md](domain/core/observability.md) | 3.1.0 | reference | observability 领域知识根节点（由 ontology/domain/observability/ 迁移） |
| `ontology:domain/core/ontology-skill-model` | [ontology-skill-model.md](domain/core/ontology-skill-model.md) | 3.4.6 | reference | 技能知识表达的说明文档实例；知识关系不是固定线性层级 |
| `ontology:domain/out-of-scope` | [out-of-scope.md](domain/core/out-of-scope.md) | 3.1.0 | reference | out-of-scope 领域知识根节点（由 ontology/domain/out-of-scope/ 迁移） |
| `ontology:domain/pg-backup-recovery-wal-replay` | [pg-backup-recovery-wal-replay.md](domain/core/pg-backup-recovery-wal-replay.md) | 3.1.0 | reference | PG 在线备份 → WAL 恢复一致性 — 机制要点 |
| `ontology:domain/pg-pgwrecover-implementation` | [pg-pgwrecover-implementation.md](domain/core/pg-pgwrecover-implementation.md) | 3.1.0 | reference | 自研离线 WAL 恢复引擎（pgwrecover）— 实现要点 |
| `ontology:domain/pg-toast-compressed-varlena-layout` | [pg-toast-compressed-varlena-layout.md](domain/core/pg-toast-compressed-varlena-layout.md) | 3.1.0 | reference | PostgreSQL TOAST 压缩值物理格式（物理直读用） |
| `ontology:domain/pg-visibility-clog-infomask` | [pg-visibility-clog-infomask.md](domain/core/pg-visibility-clog-infomask.md) | 3.1.0 | reference | PG 可见性判定矩阵与测试构造要点 |
| `ontology:domain/pg` | [pg.md](domain/core/pg.md) | 3.1.0 | reference | pg 领域知识根节点（由 ontology/domain/pg/ 迁移） |
| `ontology:domain/reporting-report-graphical-transformation` | [reporting-report-graphical-transformation.md](domain/core/reporting-report-graphical-transformation.md) | 3.1.0 | reference | 报告图形化改造方法论：从文字报告到图示为主的流程 |
| `ontology:domain/reporting` | [reporting.md](domain/core/reporting.md) | 3.1.0 | reference | reporting 领域知识根节点（由 ontology/domain/reporting/ 迁移） |
| `ontology:domain/rpc-rdbcomm-internal-dead-code-vs-public-abi` | [rpc-rdbcomm-internal-dead-code-vs-public-abi.md](domain/core/rpc-rdbcomm-internal-dead-code-vs-public-abi.md) | 3.1.0 | reference | internal-dead-code-vs-public-abi |
| `ontology:domain/rpc-rdbcomm` | [rpc-rdbcomm.md](domain/core/rpc-rdbcomm.md) | 3.1.0 | reference | rpc-rdbcomm 领域知识根节点（由 ontology/domain/rpc-rdbcomm/ 迁移） |
| `ontology:domain/tdd-mocking` | [tdd-mocking.md](domain/core/tdd-mocking.md) | 3.1.0 | reference | mocking 辅助文档 |
| `ontology:domain/tdd-tests` | [tdd-tests.md](domain/core/tdd-tests.md) | 3.1.0 | reference | tests 辅助文档 |
| `ontology:domain/tls-cert-dual-format-and-path-unify` | [tls-cert-dual-format-and-path-unify.md](domain/core/tls-cert-dual-format-and-path-unify.md) | 3.1.0 | reference | cert-dual-format-and-path-unify |
| `ontology:domain/tls-client-ctx-cache-concurrency` | [tls-client-ctx-cache-concurrency.md](domain/core/tls-client-ctx-cache-concurrency.md) | 3.1.0 | reference | 客户端 TLS_CTX 缓存复用与并发安全模式 |
| `ontology:domain/tls-handshake-dup-impl-length-contract` | [tls-handshake-dup-impl-length-contract.md](domain/core/tls-handshake-dup-impl-length-contract.md) | 3.1.0 | reference | 握手协议双端实现必须共享帧长度契约并强制往返测试 |
| `ontology:domain/tls-handshake-reject-frame-consistency` | [tls-handshake-reject-frame-consistency.md](domain/core/tls-handshake-reject-frame-consistency.md) | 3.1.0 | reference | 跨模块握手错误帧一致性审查要点 |
| `ontology:domain/tls` | [tls.md](domain/core/tls.md) | 3.1.0 | reference | tls 领域知识根节点（由 ontology/domain/tls/ 迁移） |
| `ontology:domain/tool-production-readiness` | [tool-production-readiness.md](domain/core/tool-production-readiness.md) | 3.1.0 | reference | 生产级工具就绪度领域知识：12维分级要求、L1-L4成熟度模型与B1-B4检查清单 |
| `ontology:domain/tooling-cpp-api-style-mechanical-refactor-pitfalls` | [tooling-cpp-api-style-mechanical-refactor-pitfalls.md](domain/core/tooling-cpp-api-style-mechanical-refactor-pitfalls.md) | 3.1.0 | reference | C/C++ 大规模 API 风格迁移的机械重构陷阱 |
| `ontology:domain/tooling-layered-checker-shortcircuit-alignment` | [tooling-layered-checker-shortcircuit-alignment.md](domain/core/tooling-layered-checker-shortcircuit-alignment.md) | 3.1.0 | reference | 顺序短路型检查器的失配分层与全量对齐法 |
| `ontology:domain/tooling` | [tooling.md](domain/core/tooling.md) | 3.1.0 | reference | tooling 领域知识根节点（由 ontology/domain/tooling/ 迁移） |
| `ontology:domain/workflow` | [workflow.md](domain/core/workflow.md) | 3.1.0 | reference | workflow 领域知识根节点（由 ontology/domain/workflow/ 迁移） |
| `ontology:domain/core-accounting-delta-reconcile` | [core-accounting-delta-reconcile.md](domain/core-accounting-delta-reconcile.md) | 3.1.0 | reference | 记账双轨delta + 类型矩阵 + 归并读 + 自愈调度 |
| `ontology:domain/core-acl-codec-idempotent` | [core-acl-codec-idempotent.md](domain/core-acl-codec-idempotent.md) | 3.1.0 | reference | ACL长短条目编解码 + 删建幂等 + 标志同步 |
| `ontology:domain/core-alloc-study-guide` | [core-alloc-study-guide.md](domain/core-alloc-study-guide.md) | 3.1.0 | reference | 分配器专题学习指南与节点导航 |
| `ontology:domain/core-alloc-trigger-discard-duplex` | [core-alloc-trigger-discard-duplex.md](domain/core-alloc-trigger-discard-duplex.md) | 3.1.0 | reference | alloc触发器两阶段分流 + discard后台双工 |
| `ontology:domain/core-allocator-wfq-watermark-reservation` | [core-allocator-wfq-watermark-reservation.md](domain/core-allocator-wfq-watermark-reservation.md) | 3.1.0 | reference | WFQ 条纹选盘 + 七档水位 + 双层预留的分配器防饿死与防死锁 |
| `ontology:domain/core-backpointer-dup-to-reflink` | [core-backpointer-dup-to-reflink.md](domain/core-backpointer-dup-to-reflink.md) | 3.1.0 | reference | 双活重复物理空间转reflink共享合并 |
| `ontology:domain/core-backpointer-reverse-index` | [core-backpointer-reverse-index.md](domain/core-backpointer-reverse-index.md) | 3.1.0 | reference | backpointer独立btree逆查 + 匹配校验 + 写缓冲旁路 |
| `ontology:domain/core-bcachefs-study-map` | [core-bcachefs-study-map.md](domain/core-bcachefs-study-map.md) | 3.1.0 | reference | bcachefs学习总导航与设计哲学 |
| `ontology:domain/core-bio-iov-bridge` | [core-bio-iov-bridge.md](domain/core-bio-iov-bridge.md) | 3.1.0 | reference | bio与iov迭代器钉页桥接 + 调用栈暂存 |
| `ontology:domain/core-bkey-packed-encoding` | [core-bkey-packed-encoding.md](domain/core-bkey-packed-encoding.md) | 3.1.0 | reference | bkey 快速解包 + bset 浮点压缩 + 老键零填充拓宽 |
| `ontology:domain/core-btree-commit-batch-filter` | [core-btree-commit-batch-filter.md](domain/core-btree-commit-batch-filter.md) | 3.1.0 | reference | 提交同叶批处理 + 空洞合成 + 快照过滤写位缓存 |
| `ontology:domain/core-btree-gc-mark-sweep` | [core-btree-gc-mark-sweep.md](domain/core-btree-gc-mark-sweep.md) | 3.1.0 | reference | btree GC全序位点 + 单调水位 + 提交补标 + 拓扑journal |
| `ontology:domain/core-btree-node-cache-statemachine` | [core-btree-node-cache-statemachine.md](domain/core-btree-node-cache-statemachine.md) | 3.1.0 | reference | btree节点缓存五态机 + 物理指针哈希 + 食人逐出 |
| `ontology:domain/core-btree-node-scan-rebuild` | [core-btree-node-scan-rebuild.md](domain/core-btree-node-scan-rebuild.md) | 3.1.0 | reference | btree根丢失时裸盘扫描重建与副本归并 |
| `ontology:domain/core-btree-transaction-memory-io` | [core-btree-transaction-memory-io.md](domain/core-btree-transaction-memory-io.md) | 3.1.0 | reference | btree事务 bump 分配 + 队列化写 + SRCU 短等待预算 |
| `ontology:domain/core-btreegc-study-guide` | [core-btreegc-study-guide.md](domain/core-btreegc-study-guide.md) | 3.1.0 | reference | btreeGC专题学习指南与节点导航 |
| `ontology:domain/core-btreesearch-study-guide` | [core-btreesearch-study-guide.md](domain/core-btreesearch-study-guide.md) | 3.1.0 | reference | btree搜索读路径专题学习指南与节点导航 |
| `ontology:domain/core-btreetrans-study-guide` | [core-btreetrans-study-guide.md](domain/core-btreetrans-study-guide.md) | 3.1.0 | reference | btree事务专题学习指南与节点导航 |
| `ontology:domain/core-chardev-control-plane` | [core-chardev-control-plane.md](domain/core-chardev-control-plane.md) | 3.1.0 | reference | chardev外部引用防死锁 + 长任务文件流回传 |
| `ontology:domain/core-checksum-negotiation-narrow` | [core-checksum-negotiation-narrow.md](domain/core-checksum-negotiation-narrow.md) | 3.1.0 | reference | 校验类型协商 + 首字段豁免 + 按需选型 + 裸读分支 |
| `ontology:domain/core-closure-sync-waitlist` | [core-closure-sync-waitlist.md](domain/core-closure-sync-waitlist.md) | 3.1.0 | reference | closure同步休眠语义 + 单归属等待队列 + 返回分化 |
| `ontology:domain/core-compress-algorithm-heuristics` | [core-compress-algorithm-heuristics.md](domain/core-compress-algorithm-heuristics.md) | 3.1.0 | reference | 压缩算法启发选型 + 按需建池 + gather 截断 + 编码上限 |
| `ontology:domain/core-compress-retry-verify` | [core-compress-retry-verify.md](domain/core-compress-retry-verify.md) | 3.1.0 | reference | 压缩失败折半重试 + 重解验证 + 不可压缩传播 |
| `ontology:domain/core-copygc-fragment-selection` | [core-copygc-fragment-selection.md](domain/core-copygc-fragment-selection.md) | 3.1.0 | reference | CopyGC碎片选桶 + 预留 + 去重 + 独立线程 |
| `ontology:domain/core-crypto-study-guide` | [core-crypto-study-guide.md](domain/core-crypto-study-guide.md) | 3.1.0 | reference | 压缩加密专题学习指南与节点导航 |
| `ontology:domain/core-damage-ledger-inherit` | [core-damage-ledger-inherit.md](domain/core-damage-ledger-inherit.md) | 3.1.0 | reference | Damage btree快照继承损伤账本与饱和合并 |
| `ontology:domain/core-datamove-study-guide` | [core-datamove-study-guide.md](domain/core-datamove-study-guide.md) | 3.1.0 | reference | 数据搬迁专题学习指南与节点导航 |
| `ontology:domain/core-device-membership-lifecycle` | [core-device-membership-lifecycle.md](domain/core-device-membership-lifecycle.md) | 3.1.0 | reference | 设备成员槽位分配 + 删除双态 + 移除流水线回滚 |
| `ontology:domain/core-dio-read-engine` | [core-dio-read-engine.md](domain/core-dio-read-engine.md) | 3.1.0 | reference | DIO读对齐截断 + 分片闭包 + 脏旗防回挂 |
| `ontology:domain/core-dio-write-engine` | [core-dio-write-engine.md](domain/core-dio-write-engine.md) | 3.1.0 | reference | DIO写iov暂存 + 预留快检 + FDM防死锁 + 双阶段结算 |
| `ontology:domain/core-ec-four-lectures` | [core-ec-four-lectures.md](domain/core-ec-four-lectures.md) | 3.1.0 | reference | EC四讲教学收束：写洞/生命期/修复/重建 |
| `ontology:domain/core-ec-repair-evacuate-retry` | [core-ec-repair-evacuate-retry.md](domain/core-ec-repair-evacuate-retry.md) | 3.1.0 | reference | EC修复单坏即降级 + 缺口疏散 + retry 队列 + 意图锁防删 |
| `ontology:domain/core-ec-rs-algorithm` | [core-ec-rs-algorithm.md](domain/core-ec-rs-algorithm.md) | 3.1.0 | reference | EC底层RS算法复用与分级恢复 |
| `ontology:domain/core-ec-rs-math` | [core-ec-rs-math.md](domain/core-ec-rs-math.md) | 3.1.0 | reference | RS纠删数学原理：异或P与syndrome Q |
| `ontology:domain/core-ec-rs-principle` | [core-ec-rs-principle.md](domain/core-ec-rs-principle.md) | 3.1.0 | reference | RS纠删数学原理：有限域/生成矩阵/编解码全流程 |
| `ontology:domain/core-ec-stripe-alloc` | [core-ec-stripe-alloc.md](domain/core-ec-stripe-alloc.md) | 3.1.0 | reference | 条带分配质心算法与离群重分配 |
| `ontology:domain/core-ec-stripe-geometry` | [core-ec-stripe-geometry.md](domain/core-ec-stripe-geometry.md) | 3.1.0 | reference | 条带几何结构：变长段与拓宽计数 |
| `ontology:domain/core-ec-study-guide` | [core-ec-study-guide.md](domain/core-ec-study-guide.md) | 3.1.0 | reference | EC纠删专题学习指南与节点导航 |
| `ontology:domain/core-format-compat-stable-evolution` | [core-format-compat-stable-evolution.md](domain/core-format-compat-stable-evolution.md) | 3.1.0 | reference | FEATURE/COMPAT 双位 + stable 映射 + X 宏防漂移的格式演进 |
| `ontology:domain/core-fsck-autofix-graded-self-healing` | [core-fsck-autofix-graded-self-healing.md](domain/core-fsck-autofix-graded-self-healing.md) | 3.1.0 | reference | AUTOFIX 分级表 + 精准调度 + 持久化限流的自愈错误体系 |
| `ontology:domain/core-fsck-interactive-error-handling` | [core-fsck-interactive-error-handling.md](domain/core-fsck-interactive-error-handling.md) | 3.1.0 | reference | 拓扑双路径 + 事务转储 + 写错超时降级 + 提问解锁 |
| `ontology:domain/core-fsck-orphan-reattach` | [core-fsck-orphan-reattach.md](domain/core-fsck-orphan-reattach.md) | 3.1.0 | reference | 失亲inode重挂 + 反向指针摘除 + 计数重建 |
| `ontology:domain/core-inode-acl-opts-shortcircuit` | [core-inode-acl-opts-shortcircuit.md](domain/core-inode-acl-opts-shortcircuit.md) | 3.1.0 | reference | ACL负缓存快路 + opts零值短路 + pack唯一维护 |
| `ontology:domain/core-interior-gc-update-gate` | [core-interior-gc-update-gate.md](domain/core-interior-gc-update-gate.md) | 3.1.0 | reference | interior更新双路径门控 + 最高水位特权 + GC读写互斥 |
| `ontology:domain/core-journal-entry-selfheal-validate` | [core-journal-entry-selfheal-validate.md](domain/core-journal-entry-selfheal-validate.md) | 3.1.0 | reference | journal条目边校验边删坏键自愈 |
| `ontology:domain/core-journal-lifecycle-flush` | [core-journal-lifecycle-flush.md](domain/core-journal-lifecycle-flush.md) | 3.1.0 | reference | journal开关机状态机 + 按序刷 + 免刷区 + 重写区间 |
| `ontology:domain/core-journal-pin-leak-tradeoff` | [core-journal-pin-leak-tradeoff.md](domain/core-journal-pin-leak-tradeoff.md) | 3.1.0 | reference | 错误路径泄漏pin换正确性权衡讲解 |
| `ontology:domain/core-journal-pin-lifetime-flush` | [core-journal-pin-lifetime-flush.md](domain/core-journal-pin-lifetime-flush.md) | 3.1.0 | reference | journal Pin存活期钉住与分类型有序回刷 |
| `ontology:domain/core-journal-seq-blacklist-pin-reclaim` | [core-journal-seq-blacklist-pin-reclaim.md](domain/core-journal-seq-blacklist-pin-reclaim.md) | 3.1.0 | reference | journal seq 黑名单保序 + pin 分级 reclaim + clean 段跳过回放 |
| `ontology:domain/core-journal-space-topk-ram` | [core-journal-space-topk-ram.md](domain/core-journal-space-topk-ram.md) | 3.1.0 | reference | journal三视角记账 + Top-K短板 + RAM钳制 + 快慢水位 |
| `ontology:domain/core-journal-study-guide` | [core-journal-study-guide.md](domain/core-journal-study-guide.md) | 3.1.0 | reference | journal崩溃恢复专题学习指南与节点导航 |
| `ontology:domain/core-journal-three-conflicts` | [core-journal-three-conflicts.md](domain/core-journal-three-conflicts.md) | 3.1.0 | reference | journal三矛盾场景化讲解：保序/空间/回收 |
| `ontology:domain/core-journal-watermark-thread` | [core-journal-watermark-thread.md](domain/core-journal-watermark-thread.md) | 3.1.0 | reference | journal水位四条件 + 双指针推进 + 节拍刷盘线程 |
| `ontology:domain/core-journal-write-assembly` | [core-journal-write-assembly.md](domain/core-journal-write-assembly.md) | 3.1.0 | reference | jset动态组装 + 写校验分叉 + 空预留压缩 |
| `ontology:domain/core-lru-bitmap-selfheal` | [core-lru-bitmap-selfheal.md](domain/core-lru-bitmap-selfheal.md) | 3.1.0 | reference | LRU位图点操作 + 缺失自愈 + 反向校验归位 |
| `ontology:domain/core-move-unified-relocation-engine` | [core-move-unified-relocation-engine.md](domain/core-move-unified-relocation-engine.md) | 3.1.0 | reference | move 统一搬迁引擎 + 谓词注入 + copygc 单一判据 |
| `ontology:domain/core-nocow-logged-op-crashsafe` | [core-nocow-logged-op-crashsafe.md](domain/core-nocow-logged-op-crashsafe.md) | 3.1.0 | reference | nocow符号锁 + logged_op截断状态机 + fallocate双路径 |
| `ontology:domain/core-observability-status-text-matrix` | [core-observability-status-text-matrix.md](domain/core-observability-status-text-matrix.md) | 3.1.0 | reference | 全子系统 status_to_text 自白矩阵 + sysfs 统一通道 |
| `ontology:domain/core-observability-study-guide` | [core-observability-study-guide.md](domain/core-observability-study-guide.md) | 3.1.0 | reference | 可观测体系专题学习指南与节点导航 |
| `ontology:domain/core-pagecache-buffered-direct-io` | [core-pagecache-buffered-direct-io.md](domain/core-pagecache-buffered-direct-io.md) | 3.1.0 | reference | 页缓存两态锁 + 缓冲写节流 + 直接读裁剪 |
| `ontology:domain/core-quota-charge-enforce` | [core-quota-charge-enforce.md](domain/core-quota-charge-enforce.md) | 3.1.0 | reference | 配额预留联动 + 三档收费 + 超限强制 + 迁移回滚 |
| `ontology:domain/core-quota-study-guide` | [core-quota-study-guide.md](domain/core-quota-study-guide.md) | 3.1.0 | reference | 配额记账专题学习指南与节点导航 |
| `ontology:domain/core-read-fragment-bounce` | [core-read-fragment-bounce.md](domain/core-read-fragment-bounce.md) | 3.1.0 | reference | 读片段浅继承 + 弹跳全读置位 |
| `ontology:domain/core-read-promote-tiering` | [core-read-promote-tiering.md](domain/core-read-promote-tiering.md) | 3.1.0 | reference | 读提升三否决 + 双路径 + 限流 + 整区分片 |
| `ontology:domain/core-read-replica-pick` | [core-read-replica-pick.md](domain/core-read-replica-pick.md) | 3.1.0 | reference | 读副本延迟加权择优 + 重试分级 + EC降级 |
| `ontology:domain/core-reconcile-phased-orchestration` | [core-reconcile-phased-orchestration.md](domain/core-reconcile-phased-orchestration.md) | 3.1.0 | reference | reconcile九阶段流水线 + 选项双沿打标 + 物理有序扇出 |
| `ontology:domain/core-reconcile-study-guide` | [core-reconcile-study-guide.md](domain/core-reconcile-study-guide.md) | 3.1.0 | reference | reconcile编排专题学习指南与节点导航 |
| `ontology:domain/core-recovery-study-guide` | [core-recovery-study-guide.md](domain/core-recovery-study-guide.md) | 3.1.0 | reference | recovery全流程专题学习指南与节点导航 |
| `ontology:domain/core-reflink-trigger-refcount-self-delete` | [core-reflink-trigger-refcount-self-delete.md](domain/core-reflink-trigger-refcount-self-delete.md) | 3.1.0 | reference | reflink 触发器计分 + 归零自删 + pad 弹性填洞 |
| `ontology:domain/core-sb-error-persistence-display` | [core-sb-error-persistence-display.md](domain/core-sb-error-persistence-display.md) | 3.1.0 | reference | 错误段严格校验 + 倒序展示 + 饱和钳位 + 写回折叠 |
| `ontology:domain/core-sb-persistent-counters` | [core-sb-persistent-counters.md](domain/core-sb-persistent-counters.md) | 3.1.0 | reference | SB持久计数器stable映射 + 延迟采样 + ioctl查询 |
| `ontology:domain/core-scrub-deferred-repair` | [core-scrub-deferred-repair.md](domain/core-scrub-deferred-repair.md) | 3.1.0 | reference | scrub只记不修 + journal异步修 + 两次连续好停 |
| `ontology:domain/core-six-intent-seq-deadlock-free-locking` | [core-six-intent-seq-deadlock-free-locking.md](domain/core-six-intent-seq-deadlock-free-locking.md) | 3.1.0 | reference | SIX三态锁 intent 占位 + seq 乐观重锁 + 等待图环检测的无死锁并发 |
| `ontology:domain/core-six-slowpath-wakeup` | [core-six-slowpath-wakeup.md](domain/core-six-slowpath-wakeup.md) | 3.1.0 | reference | six trylock 回补 + 降级升级 + 定向唤醒 + 等待图快照 |
| `ontology:domain/core-six-usage-discipline` | [core-six-usage-discipline.md](domain/core-six-usage-discipline.md) | 3.1.0 | reference | SIX锁调用方四规范：快慢分发/预标记/持有跟踪/身份快照 |
| `ontology:domain/core-sixlock-study-guide` | [core-sixlock-study-guide.md](domain/core-sixlock-study-guide.md) | 3.1.0 | reference | SIX锁专题学习指南与节点导航 |
| `ontology:domain/core-snapshot-delete-execution` | [core-snapshot-delete-execution.md](domain/core-snapshot-delete-execution.md) | 3.1.0 | reference | 快照删除 v2 索引 + dying 下迁 + 先迁后验落盘序 |
| `ontology:domain/core-snapshot-study-guide` | [core-snapshot-study-guide.md](domain/core-snapshot-study-guide.md) | 3.1.0 | reference | 快照专题学习指南与节点导航 |
| `ontology:domain/core-str-hash-multialgo` | [core-str-hash-multialgo.md](domain/core-str-hash-multialgo.md) | 3.1.0 | reference | str_hash四算法选型 + 掩码 + whiteout跳过 + 快照查找 |
| `ontology:domain/core-str-hash-seed-callers` | [core-str-hash-seed-callers.md](domain/core-str-hash-seed-callers.md) | 3.1.0 | reference | str_hash种子派生兼容 + 调用面差异 |
| `ontology:domain/core-superblock-readback-validation` | [core-superblock-readback-validation.md](domain/core-superblock-readback-validation.md) | 3.1.0 | reference | 超块选优读 + 写前校验读回 + 错误计数有序合并 |
| `ontology:domain/core-superblock-study-guide` | [core-superblock-study-guide.md](domain/core-superblock-study-guide.md) | 3.1.0 | reference | superblock管理专题学习指南与节点导航 |
| `ontology:domain/core-thread-stdio-framework` | [core-thread-stdio-framework.md](domain/core-thread-stdio-framework.md) | 3.1.0 | reference | kthread与fd管道后台交互线程框架 |
| `ontology:domain/core-time-stats-cheap-instrumentation` | [core-time-stats-cheap-instrumentation.md](domain/core-time-stats-cheap-instrumentation.md) | 3.1.0 | reference | time_stats 懒升级埋点 + 双均值防漂移 + X 宏一源多用 |
| `ontology:domain/core-userspace-device-manage` | [core-userspace-device-manage.md](domain/core-userspace-device-manage.md) | 3.1.0 | reference | 设备增删上下线改态扩容疏散全命令集 |
| `ontology:domain/core-userspace-device-scan` | [core-userspace-device-scan.md](domain/core-userspace-device-scan.md) | 3.1.0 | reference | 设备快扫补扫 + 无udev兜底 + 死SB过滤 + 显式信任 |
| `ontology:domain/core-userspace-fsck-routing` | [core-userspace-fsck-routing.md](domain/core-userspace-fsck-routing.md) | 3.1.0 | reference | fsck在线三选路由 + 版本仲裁 + fd中继取码 |
| `ontology:domain/core-userspace-key-rotate` | [core-userspace-key-rotate.md](domain/core-userspace-key-rotate.md) | 3.1.0 | reference | 密钥多盘校验 + 原子替换 + 魔数判别 + 内存清零 |
| `ontology:domain/core-userspace-mount-flow` | [core-userspace-mount-flow.md](domain/core-userspace-mount-flow.md) | 3.1.0 | reference | 挂载只读重试 + 三路选项分流 + 无降级问答证伪 |
| `ontology:domain/core-userspace-reconcile-wait` | [core-userspace-reconcile-wait.md](domain/core-userspace-reconcile-wait.md) | 3.1.0 | reference | reconcile判空双计数 + 先唤醒 + 双模等待 |
| `ontology:domain/core-userspace-scrub-progress` | [core-userspace-scrub-progress.md](domain/core-userspace-scrub-progress.md) | 3.1.0 | reference | scrub按盘起任务 + 事件解析 + 原地重绘 + 位图退出码 |
| `ontology:domain/core-userspace-study-guide` | [core-userspace-study-guide.md](domain/core-userspace-study-guide.md) | 3.1.0 | reference | 用户态运维专题学习指南与节点导航 |
| `ontology:domain/core-userspace-unlock-keyring-policy` | [core-userspace-unlock-keyring-policy.md](domain/core-userspace-unlock-keyring-policy.md) | 3.1.0 | reference | 用户态解锁四档策略 + keyring 优先 + systemd 桥接 |
| `ontology:domain/core-userspace-usage-matrix` | [core-userspace-usage-matrix.md](domain/core-userspace-usage-matrix.md) | 3.1.0 | reference | 用量冗余矩阵 + degraded折算 + EC分组 |
| `ontology:domain/core-userspace-wait-multipath` | [core-userspace-wait-multipath.md](domain/core-userspace-wait-multipath.md) | 3.1.0 | reference | 事件驱动等盘 + dev_idx判齐 + 多路径归一防环 |
| `ontology:domain/core-util-containers-varint-fifo` | [core-util-containers-varint-fifo.md](domain/core-util-containers-varint-fifo.md) | 3.1.0 | reference | varint快慢双实现 + darray栈快径 + fifo镜像扩容 |
| `ontology:domain/core-util-sync-primitives` | [core-util-sync-primitives.md](domain/core-util-sync-primitives.md) | 3.1.0 | reference | seqmutex乐观重锁 + io时钟调度 + vstruct遍历 |
| `ontology:domain/core-vfs-compat-shim` | [core-vfs-compat-shim.md](domain/core-vfs-compat-shim.md) | 3.1.0 | reference | 跨内核VFS拆除路径双分支垫片 |
| `ontology:domain/core-vfs-folio-reservation-writeback` | [core-vfs-folio-reservation-writeback.md](domain/core-vfs-folio-reservation-writeback.md) | 3.1.0 | reference | folio双预留记账 + 免读快路 + 聚合回写 + 重映射 |
| `ontology:domain/core-vfs-namespace-operations` | [core-vfs-namespace-operations.md](domain/core-vfs-namespace-operations.md) | 3.1.0 | reference | SEEK双检 + splice直通 + fallocate四分支 + 配额迁移 |
| `ontology:domain/core-writepath-study-guide` | [core-writepath-study-guide.md](domain/core-writepath-study-guide.md) | 3.1.0 | reference | 写路径全链路专题学习指南与节点导航 |
| `ontology:domain/core-xattr-virtual-options` | [core-xattr-virtual-options.md](domain/core-xattr-virtual-options.md) | 3.1.0 | reference | xattr虚拟选项双命名空间 + 哈希描述符复用 |
| `ontology:domain/ai-efficiency-ai-execution-and-invocation-contracts` | [ai-efficiency-ai-execution-and-invocation-contracts.md](domain/pdca/ai-efficiency-ai-execution-and-invocation-contracts.md) | 3.1.0 | reference | 执行与调用契约 |
| `ontology:domain/ai-efficiency-ai-friendliness-review-methodology` | [ai-efficiency-ai-friendliness-review-methodology.md](domain/pdca/ai-efficiency-ai-friendliness-review-methodology.md) | 3.1.0 | reference | AI友好性审查 |
| `ontology:domain/ai-efficiency-contract-scope-limiting` | [ai-efficiency-contract-scope-limiting.md](domain/pdca/ai-efficiency-contract-scope-limiting.md) | 3.1.0 | reference | 限制契约范围 |
| `ontology:domain/ai-efficiency-contract-test-pattern` | [ai-efficiency-contract-test-pattern.md](domain/pdca/ai-efficiency-contract-test-pattern.md) | 3.1.0 | reference | 契约测试对比真实实现 |
| `ontology:domain/ai-efficiency-frontier-batch-grilling` | [ai-efficiency-frontier-batch-grilling.md](domain/pdca/ai-efficiency-frontier-batch-grilling.md) | 3.1.0 | reference | 按依赖前沿澄清 |
| `ontology:domain/ai-efficiency-knowledge-assets-and-ai-workflow` | [ai-efficiency-knowledge-assets-and-ai-workflow.md](domain/pdca/ai-efficiency-knowledge-assets-and-ai-workflow.md) | 3.1.0 | reference | 知识资产按需消费 |
| `ontology:domain/ai-efficiency-lever-audit-limits` | [ai-efficiency-lever-audit-limits.md](domain/pdca/ai-efficiency-lever-audit-limits.md) | 3.1.0 | reference | 静态审计的局限 |
| `ontology:domain/ai-efficiency-mattpocock-skills-enhancement-mechanisms` | [ai-efficiency-mattpocock-skills-enhancement-mechanisms.md](domain/pdca/ai-efficiency-mattpocock-skills-enhancement-mechanisms.md) | 3.1.0 | reference | 技能说明的增强方法 |
| `ontology:domain/ai-efficiency-skills-candidate-review` | [ai-efficiency-skills-candidate-review.md](domain/pdca/ai-efficiency-skills-candidate-review.md) | 3.1.0 | reference | 技能候选审查 |
| `ontology:domain/ai-efficiency-ticket-dag-ready-set` | [ai-efficiency-ticket-dag-ready-set.md](domain/pdca/ai-efficiency-ticket-dag-ready-set.md) | 3.1.0 | reference | 独立任务DAG与资源约束 |
| `ontology:domain/ai-efficiency-unified-entrypoint-discipline` | [ai-efficiency-unified-entrypoint-discipline.md](domain/pdca/ai-efficiency-unified-entrypoint-discipline.md) | 3.1.0 | reference | 入口仅做导航 |
| `ontology:domain/ai-efficiency-uplift-assessment-before-adoption` | [ai-efficiency-uplift-assessment-before-adoption.md](domain/pdca/ai-efficiency-uplift-assessment-before-adoption.md) | 3.1.0 | reference | 采用前说明收益假设 |
| `ontology:domain/ai-efficiency-writing-for-agents-levers` | [ai-efficiency-writing-for-agents-levers.md](domain/pdca/ai-efficiency-writing-for-agents-levers.md) | 3.1.0 | reference | 面向AI的说明结构 |
| `ontology:domain/ai-efficiency` | [ai-efficiency.md](domain/pdca/ai-efficiency.md) | 3.1.0 | reference | AI工作效率的证据边界 |
| `ontology:domain/ontology-deep-integration-overview` | [ontology-deep-integration-overview.md](domain/pdca/ontology-deep-integration-overview.md) | 3.1.0 | reference | 本体驱动的集成视图 |
| `ontology:domain/ontology-hybrid-develop-bottomup` | [ontology-hybrid-develop-bottomup.md](domain/pdca/ontology-hybrid-develop-bottomup.md) | 3.1.0 | reference | 从叶到根的实现 |
| `ontology:domain/ontology-hybrid-leaf-middleout` | [ontology-hybrid-leaf-middleout.md](domain/pdca/ontology-hybrid-leaf-middleout.md) | 3.1.0 | reference | 局部切入的建模 |
| `ontology:domain/ontology-hybrid-methodology` | [ontology-hybrid-methodology.md](domain/pdca/ontology-hybrid-methodology.md) | 3.1.0 | reference | 目标树的生成与实现方向 |
| `ontology:domain/ontology-hybrid-research-topdown` | [ontology-hybrid-research-topdown.md](domain/pdca/ontology-hybrid-research-topdown.md) | 3.1.0 | reference | 从问题到机制的研究 |
| `ontology:domain/pdca/rdb-tools-independent-call-chain` | [rdb-tools-independent-call-chain.md](domain/pdca/rdb-tools-independent-call-chain.md) | 3.1.0 | reference | 6200 release 工具按可触发操作展开、跨端闭合的调用链设计与审查规则 |
| `ontology:domain/skill-advance-phase` | [skill-advance-phase.md](domain/pdca/skill-advance-phase.md) | 3.1.0 | reference | 阶段推进动作 |
| `ontology:domain/skill-ask-matt` | [skill-ask-matt.md](domain/pdca/skill-ask-matt.md) | 3.1.0 | reference | 以问题发现设计盲点 |
| `ontology:domain/skill-bug-analysis` | [skill-bug-analysis.md](domain/pdca/skill-bug-analysis.md) | 3.1.0 | reference | 定位缺陷根因 |
| `ontology:domain/skill-bug-commit-format` | [skill-bug-commit-format.md](domain/pdca/skill-bug-commit-format.md) | 3.1.0 | reference | Commit bug fixes with structured format including description, root cause, solution, impact scope, and performance impact. |
| `ontology:domain/skill-build-config` | [skill-build-config.md](domain/pdca/skill-build-config.md) | 3.1.0 | reference | Set up build configuration for new projects, manage dependencies, and switch between build systems. |
| `ontology:domain/skill-chinese-environment` | [skill-chinese-environment.md](domain/pdca/skill-chinese-environment.md) | 3.1.0 | reference | Set up projects for Chinese-speaking developers with all output in Chinese. |
| `ontology:domain/skill-code-comments` | [skill-code-comments.md](domain/pdca/skill-code-comments.md) | 3.1.0 | reference | Add Chinese annotation comments to code and embed business-understanding diagrams alongside source code. |
| `ontology:domain/skill-code-review-checklist` | [skill-code-review-checklist.md](domain/pdca/skill-code-review-checklist.md) | 3.1.0 | reference | 审查覆盖清单 |
| `ontology:domain/skill-code-review` | [skill-code-review.md](domain/pdca/skill-code-review.md) | 3.1.0 | reference | 按正确性与风险审查 |
| `ontology:domain/skill-codebase-design` | [skill-codebase-design.md](domain/pdca/skill-codebase-design.md) | 3.1.0 | reference | 把本体约束映射为模块设计 |
| `ontology:domain/skill-commit-format` | [skill-commit-format.md](domain/pdca/skill-commit-format.md) | 3.1.0 | reference | Commit changes with structured format following conventional commits. |
| `ontology:domain/skill-context-orchestration` | [skill-context-orchestration.md](domain/pdca/skill-context-orchestration.md) | 3.1.0 | reference | 阶段上下文组织 |
| `ontology:domain/skill-context-retrieval` | [skill-context-retrieval.md](domain/pdca/skill-context-retrieval.md) | 3.1.0 | reference | 精准上下文检索 |
| `ontology:domain/skill-design-it-twice` | [skill-design-it-twice.md](domain/pdca/skill-design-it-twice.md) | 3.1.0 | reference | 比较两种实质不同的设计 |
| `ontology:domain/skill-diagnosing-bugs` | [skill-diagnosing-bugs.md](domain/pdca/skill-diagnosing-bugs.md) | 3.1.0 | reference | 证据驱动诊断 |
| `ontology:domain/skill-domain-modeling-work` | [skill-domain-modeling-work.md](domain/pdca/skill-domain-modeling-work.md) | 3.1.0 | reference | 根到叶生成当前节点与子目标 |
| `ontology:domain/skill-domain-modeling` | [skill-domain-modeling.md](domain/pdca/skill-domain-modeling.md) | 3.1.0 | reference | 建立领域语义模型 |
| `ontology:domain/skill-feature-commit-format` | [skill-feature-commit-format.md](domain/pdca/skill-feature-commit-format.md) | 3.1.0 | reference | Commit new features with structured format including requirement description, background, implementation, impact scope, and testing verification. |
| `ontology:domain/skill-grill` | [skill-grill.md](domain/pdca/skill-grill.md) | 3.1.0 | reference | 澄清关键假设 |
| `ontology:domain/skill-grilling` | [skill-grilling.md](domain/pdca/skill-grilling.md) | 3.1.0 | reference | 逐轮收敛需求 |
| `ontology:domain/skill-handoff-work` | [skill-handoff-work.md](domain/pdca/skill-handoff-work.md) | 3.1.0 | reference | 交接包核验 |
| `ontology:domain/skill-handoff` | [skill-handoff.md](domain/pdca/skill-handoff.md) | 3.1.0 | reference | 持久化交接 |
| `ontology:domain/skill-implement` | [skill-implement.md](domain/pdca/skill-implement.md) | 3.1.0 | reference | 按已确认契约实现 |
| `ontology:domain/skill-improve-codebase-architecture` | [skill-improve-codebase-architecture.md](domain/pdca/skill-improve-codebase-architecture.md) | 3.1.0 | reference | 受控的架构改进 |
| `ontology:domain/skill-ontology-check` | [skill-ontology-check.md](domain/pdca/skill-ontology-check.md) | 3.1.0 | reference | 本体语义与结构审查 |
| `ontology:domain/skill-project-goal` | [skill-project-goal.md](domain/pdca/skill-project-goal.md) | 3.1.0 | reference | 目标与非目标 |
| `ontology:domain/skill-prototype` | [skill-prototype.md](domain/pdca/skill-prototype.md) | 3.1.0 | reference | 可丢弃的验证性原型 |
| `ontology:domain/skill-register-evidence` | [skill-register-evidence.md](domain/pdca/skill-register-evidence.md) | 3.1.0 | reference | 登记可复核证据 |
| `ontology:domain/skill-research` | [skill-research.md](domain/pdca/skill-research.md) | 3.1.0 | reference | 来源驱动的领域调研 |
| `ontology:domain/skill-resolving-merge-conflicts` | [skill-resolving-merge-conflicts.md](domain/pdca/skill-resolving-merge-conflicts.md) | 3.1.0 | reference | Resolve merge conflicts systematically and efficiently. |
| `ontology:domain/skill-retrospective` | [skill-retrospective.md](domain/pdca/skill-retrospective.md) | 3.1.0 | reference | 回顾有价值的改进 |
| `ontology:domain/skill-secure-coding` | [skill-secure-coding.md](domain/pdca/skill-secure-coding.md) | 3.1.0 | reference | Review code for security vulnerabilities and implement security-critical logic. |
| `ontology:domain/skill-tdd` | [skill-tdd.md](domain/pdca/skill-tdd.md) | 3.1.0 | reference | 用真实失败和通过验证实现 |
| `ontology:domain/skill-teach` | [skill-teach.md](domain/pdca/skill-teach.md) | 3.1.0 | reference | 将知识组织成可验证的教学材料 |
| `ontology:domain/skill-testing-strategy` | [skill-testing-strategy.md](domain/pdca/skill-testing-strategy.md) | 3.1.0 | reference | 按节点建立详细正反例与返工测试 |
| `ontology:domain/skill-to-questionnaire` | [skill-to-questionnaire.md](domain/pdca/skill-to-questionnaire.md) | 3.1.0 | reference | Turn a decision you cannot answer alone into a Markdown questionnaire. |
| `ontology:domain/skill-to-spec` | [skill-to-spec.md](domain/pdca/skill-to-spec.md) | 3.1.0 | reference | 将对话转化为规格说明——grilling 输出的结构化捕获 |
| `ontology:domain/skill-to-tickets` | [skill-to-tickets.md](domain/pdca/skill-to-tickets.md) | 3.1.0 | reference | 逐目标节点建立完整任务 |
| `ontology:domain/skill-triage-work` | [skill-triage-work.md](domain/pdca/skill-triage-work.md) | 3.1.0 | reference | 把需求绑定到场景和目标节点 |
| `ontology:domain/skill-triage` | [skill-triage.md](domain/pdca/skill-triage.md) | 3.1.0 | reference | 确定本体职责和范围 |
| `ontology:domain/skill-verify-convergence` | [skill-verify-convergence.md](domain/pdca/skill-verify-convergence.md) | 3.1.0 | reference | 约束、案例、实现和证据逐项收敛 |
| `ontology:domain/skill-wait-wait` | [skill-wait-wait.md](domain/pdca/skill-wait-wait.md) | 3.1.0 | reference | 发现偏差时暂停 |
| `ontology:domain/skill-wayfinder` | [skill-wayfinder.md](domain/pdca/skill-wayfinder.md) | 3.1.0 | reference | 以目标定位资料 |
| `ontology:domain/skill-wayfinding-chart` | [skill-wayfinding-chart.md](domain/pdca/skill-wayfinding-chart.md) | 3.1.0 | reference | 导航索引 |
| `ontology:domain/skill-wayfinding-work` | [skill-wayfinding-work.md](domain/pdca/skill-wayfinding-work.md) | 3.1.0 | reference | 从导航到执行输入 |
| `ontology:domain/skill-web-research` | [skill-web-research.md](domain/pdca/skill-web-research.md) | 3.1.0 | reference | 外部来源检索 |
| `ontology:domain/skill-wizard` | [skill-wizard.md](domain/pdca/skill-wizard.md) | 3.1.0 | reference | 分步获取配置输入 |
| `ontology:domain/skill-write-conclusion` | [skill-write-conclusion.md](domain/pdca/skill-write-conclusion.md) | 3.1.0 | reference | 形成验收结论 |
| `ontology:domain/skill-write-journal` | [skill-write-journal.md](domain/pdca/skill-write-journal.md) | 3.1.0 | reference | 记录工作事实 |
| `ontology:domain/skill-writing-great-skills` | [skill-writing-great-skills.md](domain/pdca/skill-writing-great-skills.md) | 3.1.0 | reference | 为AI编写可执行说明 |
| `ontology:domain/workflow-code-review-dual-axis` | [workflow-code-review-dual-axis.md](domain/pdca/workflow-code-review-dual-axis.md) | 3.1.0 | reference | 审查的行为与工程两轴 |
| `ontology:domain/workflow-skill-invocation-convention` | [workflow-skill-invocation-convention.md](domain/pdca/workflow-skill-invocation-convention.md) | 3.1.0 | reference | 技能不取得流程控制权 |
| `ontology:domain/rdb-config-audit-findings` | [rdb-config-audit-findings.md](domain/report-center/rdb-config-audit-findings.md) | 3.1.0 | reference | rdb.conf 配置解析契约与审计结论（T0369） |
| `ontology:domain/rdb-config-optim-roadmap` | [rdb-config-optim-roadmap.md](domain/report-center/rdb-config-optim-roadmap.md) | 3.1.0 | reference | rdb config 优化路线图（T0386） |
| `ontology:domain/rdb-config-wire-tool-config-to-registry` | [rdb-config-wire-tool-config-to-registry.md](domain/report-center/rdb-config-wire-tool-config-to-registry.md) | 3.1.0 | reference | 将工具配置接入 rdb config 参数注册表的复用要点 |
| `ontology:domain/rdb-config` | [rdb-config.md](domain/report-center/rdb-config.md) | 3.1.0 | reference | rdb-config 领域知识根节点（由 ontology/domain/rdb-config/ 迁移） |
| `ontology:domain/report-center-async-export-distributed-quota-patterns` | [report-center-async-export-distributed-quota-patterns.md](domain/report-center/report-center-async-export-distributed-quota-patterns.md) | 3.1.0 | reference | 异步导出与分布式配额模式（report-center） |
| `ontology:domain/report-center-auth-rpc-compensation-patterns` | [report-center-auth-rpc-compensation-patterns.md](domain/report-center/report-center-auth-rpc-compensation-patterns.md) | 3.1.0 | reference | report-center 认证服务与 RPC 补偿模式 |
| `ontology:domain/report-center-cli-from-scratch-lazy-import` | [report-center-cli-from-scratch-lazy-import.md](domain/report-center/report-center-cli-from-scratch-lazy-import.md) | 3.1.0 | reference | CLI 从零重写 + 惰性导入 + Keyset 分页（T0217 沉淀） |
| `ontology:domain/report-center-db-adapter-pg-practices` | [report-center-db-adapter-pg-practices.md](domain/report-center/report-center-db-adapter-pg-practices.md) | 3.1.0 | reference | Repository/Adapter 数据访问层 + PG 迁移 — 可复用实践 |
| `ontology:domain/report-center-deployment-assembly-patterns` | [report-center-deployment-assembly-patterns.md](domain/report-center/report-center-deployment-assembly-patterns.md) | 3.1.0 | reference | Report Center 部署装配模式 |
| `ontology:domain/report-center-report-center-decomposition-index` | [report-center-report-center-decomposition-index.md](domain/report-center/report-center-report-center-decomposition-index.md) | 3.1.0 | reference | CDM 报表中心（需求 140）落地拆解索引 |
| `ontology:domain/report-center-report-web-report-sql-patterns` | [report-center-report-web-report-sql-patterns.md](domain/report-center/report-center-report-web-report-sql-patterns.md) | 3.1.0 | reference | report-web 固定报表 SQL 构建模式与坑位 |
| `ontology:domain/report-center` | [report-center.md](domain/report-center/report-center.md) | 3.1.0 | reference | report-center 领域知识根节点（由 ontology/domain/report-center/ 迁移） |
| `ontology:domain/backup-crypto-gm-support-surfaces` | [backup-crypto-gm-support-surfaces.md](domain/zfs/backup-crypto-gm-support-surfaces.md) | 3.1.0 | reference | 备份国密支撑面：S3 静态加密 / CPU 指令集 / NFS 内核边界 |
| `ontology:domain/backup-crypto-medium-model` | [backup-crypto-medium-model.md](domain/zfs/backup-crypto-medium-model.md) | 3.1.0 | reference | 备份国密介质承接模型 |
| `ontology:domain/backup-crypto-openssh-gm-support` | [backup-crypto-openssh-gm-support.md](domain/zfs/backup-crypto-openssh-gm-support.md) | 3.1.0 | reference | OpenSSH 国密支持面（SM2/SM3/SM4）— openEuler 24.03 SP4 |
| `ontology:domain/backup-crypto` | [backup-crypto.md](domain/zfs/backup-crypto.md) | 3.1.0 | reference | backup-crypto 领域知识根节点（由 ontology/domain/backup-crypto/ 迁移） |
| `ontology:domain/backup-gs-roach-gm-encrypt-support` | [backup-gs-roach-gm-encrypt-support.md](domain/zfs/backup-gs-roach-gm-encrypt-support.md) | 3.1.0 | reference | gs_roach 国密加密能力边界 |
| `ontology:domain/backup-ob-backup-gm-encrypt-support` | [backup-ob-backup-gm-encrypt-support.md](domain/zfs/backup-ob-backup-gm-encrypt-support.md) | 3.1.0 | reference | OceanBase 备份加密与国密 SM4 能力边界 |
| `ontology:domain/backup-xtrabackup-incremental-schemes` | [backup-xtrabackup-incremental-schemes.md](domain/zfs/backup-xtrabackup-incremental-schemes.md) | 3.1.0 | reference | XtraBackup 8.0 系列增量备份方案速览（通用知识） |
| `ontology:domain/kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method` | [kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method.md](domain/zfs/kernel-debugging-device-mapper-blk-mq-uaf-vmcore-method.md) | 3.1.0 | reference | Device-mapper blk-mq UAF 的 vmcore—源码闭环方法 |
| `ontology:domain/kernel-debugging` | [kernel-debugging.md](domain/zfs/kernel-debugging.md) | 3.1.0 | reference | kernel-debugging 领域知识根节点（由 ontology/domain/kernel-debugging/ 迁移） |
| `ontology:domain/nbu-nbu-dte-architecture` | [nbu-nbu-dte-architecture.md](domain/zfs/nbu-nbu-dte-architecture.md) | 3.1.0 | reference | NBU DTE 传输加密架构 |
| `ontology:domain/zfs-crypto` | [zfs-crypto.md](domain/zfs/zfs-crypto.md) | 3.1.0 | reference | OpenZFS 存储加密体系（含 SM4-GCM 国密扩展）的端到端领域知识 |
| `ontology:entity/aio-tools-6200-release` | [aio-tools-6200-release.md](entity/aio-tools-6200-release.md) | 3.1.0 | reference | aio-tools 6200/release 快照实体（6.2.0.0-release fe9d4364，14 模块+libs+third_party，488 文件/18.9万 LOC，11 变量双层版本链，xmake 四阶段 CI，fsdeamon↔aio-speedd 主链路+rdbcomm 32/5MB） |
| `ontology:entity/backup-crypto-entity` | [backup-crypto-entity.md](entity/backup-crypto-entity.md) | 3.1.0 | reference | Backup Crypto 实体（BackupSystem 叶） |
| `ontology:entity/backup-system` | [backup-system.md](entity/backup-system.md) | 3.1.0 | reference | Backup 系统聚合（composed_of Xtrabackup + Crypto） |
| `ontology:entity/backup-xtrabackup-entity` | [backup-xtrabackup-entity.md](entity/backup-xtrabackup-entity.md) | 3.1.0 | reference | Backup Xtrabackup 实体（BackupSystem 叶） |
| `ontology:entity/bcachefs-alloc` | [bcachefs-alloc.md](entity/bcachefs-alloc.md) | 3.1.0 | reference | bcachefs Alloc 实体 — bucket 四态、open_bucket 顺序写、WFQ 分配与 background copygc/discard/reclaim 协同 |
| `ontology:entity/bcachefs-btree-bset` | [bcachefs-btree-bset.md](entity/bcachefs-btree-bset.md) | 3.1.0 | reference | 待补固定源码的bset研究入口；原不一致状态机和伪可编译代码已撤回 |
| `ontology:entity/bcachefs-btree` | [bcachefs-btree.md](entity/bcachefs-btree.md) | 3.1.0 | reference | bcachefs Btree 引擎本体 — 可实现规约：btree_cache 五态机 + struct btree(six+format+bset[3]) + B+树 COW 分裂/bpos寻址/iter-path 遍历及 journal pin 原子性（29 btree_id 为实例化参数） |
| `ontology:entity/bcachefs-cli` | [bcachefs-cli.md](entity/bcachefs-cli.md) | 3.1.0 | reference | bcachefs CLI 实体 — COMMAND_GROUPS 8 组 >35 leaf、CmdKind 三形态（typed/raw/group）与 dispatch/symlink 及 Cargo/Make/DKMS 三构建 |
| `ontology:entity/bcachefs-device` | [bcachefs-device.md](entity/bcachefs-device.md) | 3.1.0 | reference | bcachefs Device 实体 — device 组多态子命令、sb_field_members 事务与 replicas/disk_groups 及 udev/多路径 |
| `ontology:entity/bcachefs-format` | [bcachefs-format.md](entity/bcachefs-format.md) | 3.1.0 | reference | bcachefs Format 实体 — per-device 选项解析、BCH_SB_FIELDS x-macro 超块与多副本 super 写入 |
| `ontology:entity/bcachefs-fsck` | [bcachefs-fsck.md](entity/bcachefs-fsck.md) | 3.1.0 | reference | bcachefs Fsck 实体 — bch2_fs_recovery 26  passes、journal replay 与 check_topology/allocations/extents 分工 |
| `ontology:entity/bcachefs-journal-rewind` | [bcachefs-journal-rewind.md](entity/bcachefs-journal-rewind.md) | 3.1.0 | reference | bcachefs Journal Rewind 实体 — rewind_limit 下界、JSET_NO_FLUSH 候选枚举与 overwrite 旧值回退 |
| `ontology:entity/bcachefs-journal` | [bcachefs-journal.md](entity/bcachefs-journal.md) | 3.1.0 | reference | bcachefs 日志实体 — jset 环形 bucket、16 种 jset_entry 类型分工、journal_buf 预约环与 pin 追踪及 reclaim |
| `ontology:entity/bcachefs-mount` | [bcachefs-mount.md](entity/bcachefs-mount.md) | 3.1.0 | reference | bcachefs Mount 实体 — bdev/handle/ioctl 三层 wrappers 与 degrade 路由及 fstab 集成 |
| `ontology:entity/bcachefs-super` | [bcachefs-super.md](entity/bcachefs-super.md) | 3.1.0 | reference | bcachefs Super 实体 — bch_sb 固定头（csum/version/magic/uuid/seq）+ BCH_SB_FIELDS 15+ 可扩展字段（members/journal/crypt/recovery/counters）与 super_io 多副本 |
| `ontology:entity/bcachefs-system` | [bcachefs-system.md](entity/bcachefs-system.md) | 3.1.0 | reference | bcachefs 全栈系统聚合（composed_of 12 叶 format/mount/fsck/device/journal/journal-rewind/btree/btree-bset/alloc/transaction/super/cli，C4 L2/L3 至 journal/btree/alloc pipeline 可建模） |
| `ontology:entity/bcachefs-transaction` | [bcachefs-transaction.md](entity/bcachefs-transaction.md) | 3.1.0 | reference | bcachefs Transaction 实体 — btree_trans bump 内存、six 三态锁（read/intent/write+seq 乐观）与 25 种 restart 重试及 journal 并发环 |
| `ontology:entity/evidence-convergence-map` | [evidence-convergence-map.md](entity/evidence-convergence-map.md) | 2.0.0 | normative | 证据类型：convergence-map |
| `ontology:entity/evidence-review` | [evidence-review.md](entity/evidence-review.md) | 2.0.0 | normative | 证据类型：review |
| `ontology:entity/evidence-test-result` | [evidence-test-result.md](entity/evidence-test-result.md) | 3.0.0 | normative | 证据类型：逐案例真实测试结果 |
| `ontology:entity/exec-stdin-pump` | [exec-stdin-pump.md](entity/exec-stdin-pump.md) | 3.1.0 | reference | ExecStdinPump：TLS exec stdin 泵实体 |
| `ontology:entity/mtls-handshake` | [mtls-handshake.md](entity/mtls-handshake.md) | 3.1.0 | reference | MTLSHandshake：mTLS 握手实体 |
| `ontology:entity/ontology-deep-integration-knowledge` | [ontology-deep-integration-knowledge.md](entity/ontology-deep-integration-knowledge.md) | 3.1.0 | reference | ontology-deep-integration-knowledge |
| `ontology:entity/ontology-deep-integration-split` | [ontology-deep-integration-split.md](entity/ontology-deep-integration-split.md) | 3.1.0 | reference | ontology-deep-integration-split |
| `ontology:entity/ontology-deep-integration-test` | [ontology-deep-integration-test.md](entity/ontology-deep-integration-test.md) | 3.1.0 | reference | ontology-deep-integration-test |
| `ontology:entity/ontology-deep-integration-tree` | [ontology-deep-integration-tree.md](entity/ontology-deep-integration-tree.md) | 3.1.0 | reference | 本体组成树与有界节点上下文 |
| `ontology:entity/ontology-deep-integration` | [ontology-deep-integration.md](entity/ontology-deep-integration.md) | 3.1.0 | reference | ontology-deep-integration |
| `ontology:entity/phase-act` | [phase-act.md](entity/phase-act.md) | 3.2.0 | normative | 阶段值：act |
| `ontology:entity/phase-archive` | [phase-archive.md](entity/phase-archive.md) | 3.2.0 | normative | 工作流正常归档终态，不属于方法阶段 |
| `ontology:entity/phase-check` | [phase-check.md](entity/phase-check.md) | 3.2.0 | normative | 阶段值：check |
| `ontology:entity/phase-do` | [phase-do.md](entity/phase-do.md) | 3.2.0 | normative | 阶段值：do |
| `ontology:entity/phase-plan` | [phase-plan.md](entity/phase-plan.md) | 3.2.0 | normative | 阶段值：plan |
| `ontology:entity/report-center-collection-entity` | [report-center-collection-entity.md](entity/report-center-collection-entity.md) | 3.1.0 | reference | ReportCenter Collection 子系统实体（ReportCenterSystem 叶） |
| `ontology:entity/report-center-system` | [report-center-system.md](entity/report-center-system.md) | 3.1.0 | reference | ReportCenter 系统聚合（composed_of Web + Collection） |
| `ontology:entity/report-center-web-entity` | [report-center-web-entity.md](entity/report-center-web-entity.md) | 3.1.0 | reference | ReportCenter Web 子系统实体（ReportCenterSystem 叶） |
| `ontology:entity/tls-configuration` | [tls-configuration.md](entity/tls-configuration.md) | 3.1.0 | reference | TLSConfiguration：TLS 配置实体 |
| `ontology:entity/tls-session` | [tls-session.md](entity/tls-session.md) | 3.1.0 | reference | TLSSession：TLS 会话实体 |
| `ontology:entity/tls-test-harness` | [tls-test-harness.md](entity/tls-test-harness.md) | 3.1.0 | reference | TLSTestHarness：链接级测试工具实体 |
| `ontology:entity/transition-act-archive` | [transition-act-archive.md](entity/transition-act-archive.md) | 3.2.0 | normative | 转换：act → archive |
| `ontology:entity/transition-check-act` | [transition-check-act.md](entity/transition-check-act.md) | 3.2.0 | normative | 转换：check → act |
| `ontology:entity/transition-do-check` | [transition-do-check.md](entity/transition-do-check.md) | 3.2.0 | normative | 转换：do → check |
| `ontology:entity/transition-plan-do` | [transition-plan-do.md](entity/transition-plan-do.md) | 3.2.0 | normative | 转换：plan → do |
| `ontology:entity/verdict-confirmed` | [verdict-confirmed.md](entity/verdict-confirmed.md) | 2.0.0 | normative | 结论类型：confirmed |
| `ontology:entity/verdict-partial` | [verdict-partial.md](entity/verdict-partial.md) | 2.0.0 | normative | 结论类型：partial |
| `ontology:entity/verdict-rejected` | [verdict-rejected.md](entity/verdict-rejected.md) | 2.0.0 | normative | 结论类型：rejected |
| `ontology:entity/x509-certificate` | [x509-certificate.md](entity/x509-certificate.md) | 3.1.0 | reference | X509Certificate：证书实体 |
| `ontology:entity/zfs-arc` | [zfs-arc.md](entity/zfs-arc.md) | 3.1.0 | reference | ZFS ARC 实体 — Adaptive Replacement Cache 自适应缓存与 L2ARC/dbuf 协作 |
| `ontology:entity/zfs-ddt` | [zfs-ddt.md](entity/zfs-ddt.md) | 3.1.0 | reference | OpenZFS zfs-2.3.0：DDT/BRT边界重建，旧状态图与伪接口撤回 |
| `ontology:entity/zfs-dmu` | [zfs-dmu.md](entity/zfs-dmu.md) | 3.1.0 | reference | ZFS DMU 实体 — dnode/dbuf 对象-块两级抽象与读写/脏数据路径 |
| `ontology:entity/zfs-dsl` | [zfs-dsl.md](entity/zfs-dsl.md) | 3.1.0 | reference | ZFS DSL 实体 — dsl_pool/dsl_dataset/dsl_dir 数据集层与快照克隆语义 |
| `ontology:entity/zfs-spa` | [zfs-spa.md](entity/zfs-spa.md) | 3.1.0 | reference | ZFS SPA 实体 — Storage Pool Allocator 池分配器与 TXG 三状态机及 metaslab 空间分配 |
| `ontology:entity/zfs-system` | [zfs-system.md](entity/zfs-system.md) | 3.1.0 | reference | ZFS 全栈系统聚合（composed_of DMU/DSL/SPA/ZIO/ZPL/ARC/VDEV/ZIL 八叶，C4 L2/L3 至 ZIO/VDEV pipeline 可建模） |
| `ontology:entity/zfs-vdev` | [zfs-vdev.md](entity/zfs-vdev.md) | 3.1.0 | reference | ZFS VDEV 实体 — 虚拟设备拓扑与队列调度及故障状态机 |
| `ontology:entity/zfs-zil` | [zfs-zil.md](entity/zfs-zil.md) | 3.1.0 | reference | ZFS ZIL 实体 — 意图日志 LWB 链与 slog 分离及重放可测 |
| `ontology:entity/zfs-zio` | [zfs-zio.md](entity/zfs-zio.md) | 3.1.1 | reference | ZFS ZIO 位图阶段与 transform 栈；已修正文内冲突，仅固定对照版本，采用仍需 claim-review |
| `ontology:entity/zfs-zpl` | [zfs-zpl.md](entity/zfs-zpl.md) | 3.1.0 | reference | ZFS ZPL 实体 — POSIX 层 zfs_znode/zpl_inode 与 DMU 对象映射、SA/bonus 及 ZIL 意图日志 |
| `ontology:fact/tls-exec-truncation-investigation-state` | [tls-exec-truncation-investigation-state.md](fact/tls-exec-truncation-investigation-state.md) | 3.1.0 | reference | TLS exec stdin 偶发截断调查状态与已知事实 |
| `ontology:pattern/audit/project-review-composition` | [project-review-composition.md](pattern/audit/project-review-composition.md) | 3.4.0 | normative | 项目审查组成模式：角色复用与递归展开 |
| `ontology:pattern/backup-mtls-admin-gate` | [backup-mtls-admin-gate.md](pattern/backup-mtls-admin-gate.md) | 3.1.0 | reference | rpc 明文 admin 面需 mTLS 强制或 allow_list 校验，避免 sh -c 任意执行 |
| `ontology:pattern/backupstream-plain-tls-ingress` | [backupstream-plain-tls-ingress.md](pattern/backupstream-plain-tls-ingress.md) | 3.1.0 | reference | backupstream 80 v80 架构：plain/TLS 双路径 ingress 与线程模型 |
| `ontology:pattern/clean-segment-fastpath` | [clean-segment-fastpath.md](pattern/clean-segment-fastpath.md) | 3.1.0 | reference | clean段加速加校验回退模式 |
| `ontology:pattern/deadlock-detect-restart` | [deadlock-detect-restart.md](pattern/deadlock-detect-restart.md) | 3.1.0 | reference | 等待图环检测加幂等重启消灭死锁模式 |
| `ontology:pattern/gm-symmetric-modes` | [gm-symmetric-modes.md](pattern/gm-symmetric-modes.md) | 3.1.0 | reference | 模式选型研究边界：先固定协议与支持证据 |
| `ontology:pattern/gmssl-tlcp-mtls` | [gmssl-tlcp-mtls.md](pattern/gmssl-tlcp-mtls.md) | 3.1.0 | reference | GMSSL 3.1.2 TLCP mTLS 支持速查与集成策略 |
| `ontology:pattern/graded-selfhealing-schedule` | [graded-selfhealing-schedule.md](pattern/graded-selfhealing-schedule.md) | 3.1.0 | reference | 错误分级加精准调度加持久限流自愈模式 |
| `ontology:pattern/intent-staged-update` | [intent-staged-update.md](pattern/intent-staged-update.md) | 3.1.0 | reference | intent占位分阶段多节点原子更新模式 |
| `ontology:pattern/knowledge-map-building` | [knowledge-map-building.md](pattern/knowledge-map-building.md) | 3.1.0 | reference | 知识地图构建方法论：05主03辅骨架、版本化目录布局、§〇版本路由、孤岛裁决、三项实证 |
| `ontology:pattern/link-level-mtls-test-pattern` | [link-level-mtls-test-pattern.md](pattern/link-level-mtls-test-pattern.md) | 3.1.0 | reference | 链接级 mTLS/握手测试模式与测试证书 CN 约束 |
| `ontology:pattern/mtls-four-module-supplementary-review` | [mtls-four-module-supplementary-review.md](pattern/mtls-four-module-supplementary-review.md) | 3.1.0 | reference | 四模块 TLS/mTLS 已 commit 修改补充审查范式 |
| `ontology:pattern/mtls-handshake-enum-unify` | [mtls-handshake-enum-unify.md](pattern/mtls-handshake-enum-unify.md) | 3.1.0 | reference | 四模块握手算法枚举与名称映射收敛重构 |
| `ontology:pattern/mtls-handshake-netorder-libobk` | [mtls-handshake-netorder-libobk.md](pattern/mtls-handshake-netorder-libobk.md) | 3.1.0 | reference | libobk 握手 body 网络序改造经验 |
| `ontology:pattern/mtls-server-alg-whitelist` | [mtls-server-alg-whitelist.md](pattern/mtls-server-alg-whitelist.md) | 3.1.0 | reference | 服务端握手算法白名单校验四模块落地范式 |
| `ontology:pattern/ontology-evaluation-oops` | [ontology-evaluation-oops.md](pattern/ontology-evaluation-oops.md) | 3.1.0 | reference | 本体缺陷检查 |
| `ontology:pattern/ontology-metrics` | [ontology-metrics.md](pattern/ontology-metrics.md) | 3.1.0 | reference | 本体结构指标的用途 |
| `ontology:pattern/ontology-modular-reference` | [ontology-modular-reference.md](pattern/ontology-modular-reference.md) | 3.1.0 | reference | 模块化本体引用 |
| `ontology:pattern/ontology-reuse-reengineering` | [ontology-reuse-reengineering.md](pattern/ontology-reuse-reengineering.md) | 3.3.0 | normative | 复用优先的本体演进 |
| `ontology:pattern/oss-https-tls` | [oss-https-tls.md](pattern/oss-https-tls.md) | 3.1.0 | reference | oss HTTPS / TLS 配置模型 |
| `ontology:pattern/production-ontology-scientific-gate` | [production-ontology-scientific-gate.md](pattern/production-ontology-scientific-gate.md) | 3.1.0 | reference | 面向实际使用的本体质量审查 |
| `ontology:pattern/research-diagram-methodology` | [research-diagram-methodology.md](pattern/research-diagram-methodology.md) | 3.1.0 | reference | 用图解释关键机制 |
| `ontology:pattern/sbt-config-mtls-override` | [sbt-config-mtls-override.md](pattern/sbt-config-mtls-override.md) | 3.1.0 | reference | init_sbt_config 配置文件键解析模式（dmsbtex） |
| `ontology:pattern/scientific-research-arc42` | [scientific-research-arc42.md](pattern/scientific-research-arc42.md) | 3.1.0 | reference | 科学调研arc42支：12节全架构文档模板（对齐arc42.org） |
| `ontology:pattern/scientific-research-c4` | [scientific-research-c4.md](pattern/scientific-research-c4.md) | 3.1.0 | reference | 科学调研C4支：4层级+4补充图与边缘交叉靶（对齐c4model.com） |
| `ontology:pattern/scientific-research-diataxis` | [scientific-research-diataxis.md](pattern/scientific-research-diataxis.md) | 3.1.0 | reference | 科学调研Diátaxis支：四象限 tutorial/how-to/reference/explanation（对齐diataxis.fr Procida） |
| `ontology:pattern/scientific-research-lifecycle` | [scientific-research-lifecycle.md](pattern/scientific-research-lifecycle.md) | 3.1.0 | reference | 研究的闭环 |
| `ontology:pattern/scientific-research-methodology` | [scientific-research-methodology.md](pattern/scientific-research-methodology.md) | 3.1.0 | reference | 研究结论与证据的对应 |
| `ontology:pattern/seq-blacklist-ordering` | [seq-blacklist-ordering.md](pattern/seq-blacklist-ordering.md) | 3.1.0 | reference | seq黑名单保序重放模式 |
| `ontology:pattern/seq-optimistic-relock` | [seq-optimistic-relock.md](pattern/seq-optimistic-relock.md) | 3.1.0 | reference | seq版本号乐观掉锁重拿模式 |
| `ontology:pattern/sm4-nfs-encryption` | [sm4-nfs-encryption.md](pattern/sm4-nfs-encryption.md) | 3.1.0 | reference | SM4 NFS 文件存储加密子模式（aio-speed预加密落盘，原文件名+管理侧清单） |
| `ontology:pattern/sm4-s3-encryption` | [sm4-s3-encryption.md](pattern/sm4-s3-encryption.md) | 3.1.0 | reference | SM4 S3 对象存储加密子模式（s3file 工具 SM4 加密上传） |
| `ontology:pattern/sm4-storage-encryption` | [sm4-storage-encryption.md](pattern/sm4-storage-encryption.md) | 3.1.0 | reference | 国密SM4全流程存储加密模式（ZFS/S3/NFS/备份四场景，155 MB/s 基线，TLS_SM4_GCM_SM3 阈值表） |
| `ontology:pattern/sm4-zfs-encryption` | [sm4-zfs-encryption.md](pattern/sm4-zfs-encryption.md) | 3.1.0 | reference | 私有SM4-ZFS扩展候选：缺固定实现，禁止当上游通用操作 |
| `ontology:pattern/testable-signal-to-test-derivation` | [testable-signal-to-test-derivation.md](pattern/testable-signal-to-test-derivation.md) | 3.1.0 | reference | 从信号派生可观察测试 |
| `ontology:pattern/unified-first-stage-mtls-time` | [unified-first-stage-mtls-time.md](pattern/unified-first-stage-mtls-time.md) | 3.1.0 | reference | RPC/rdbcomm 统一第一阶段握手经验 |
| `ontology:pattern/unified-relocation-engine` | [unified-relocation-engine.md](pattern/unified-relocation-engine.md) | 3.1.0 | reference | 单引擎加谓词注入统一搬迁模式 |
| `ontology:pattern/watermark-staged-reclaim` | [watermark-staged-reclaim.md](pattern/watermark-staged-reclaim.md) | 3.1.0 | reference | 多条件水位分级回收模式 |
| `ontology:pattern/weighted-fair-allocation` | [weighted-fair-allocation.md](pattern/weighted-fair-allocation.md) | 3.1.0 | reference | 虚拟时间加权公平分配模式 |
| `ontology:pattern/zfs-scrub-resilver` | [zfs-scrub-resilver.md](pattern/zfs-scrub-resilver.md) | 3.1.0 | reference | ZFS scrub/resilver运维pattern：scan/queue/repair三态与vdev关联 |
| `ontology:pitfall/backup-snapshot-race` | [backup-snapshot-race.md](pitfall/backup-snapshot-race.md) | 3.1.0 | reference | BackupHelper Snapshot 无超时与 m_sync_stat 竞态致提前 OnCopy 产出缺事件快照 |
| `ontology:pitfall/mtls-param-review-findings` | [mtls-param-review-findings.md](pitfall/mtls-param-review-findings.md) | 3.1.0 | reference | mTLS 参数链路审查发现四模块横向一致性陷阱 |
| `ontology:pitfall/research-plan-ontology-prompt-gap` | [research-plan-ontology-prompt-gap.md](pitfall/research-plan-ontology-prompt-gap.md) | 3.1.0 | reference | 契约要求调研但Plan期未声明本体计划的pitfall：须在Grill确认锚点与沉淀动作 |
| `ontology:pitfall/tls-cert-reload-appdata-safety` | [tls-cert-reload-appdata-safety.md](pitfall/tls-cert-reload-appdata-safety.md) | 3.1.0 | reference | TLS 证书 ctx 热加载的安全陷阱 |
| `ontology:pitfall/tls-keygen-sign-uaf-serial` | [tls-keygen-sign-uaf-serial.md](pitfall/tls-keygen-sign-uaf-serial.md) | 3.1.0 | reference | tls-keygen 签发链路 UAF 与序列号硬编码导致并发证书异常 |
| `ontology:pitfall/zfs-tunable-misconfig` | [zfs-tunable-misconfig.md](pitfall/zfs-tunable-misconfig.md) | 3.1.0 | reference | ZFS tunable误配pitfall：arc_p/metaslab_weight/l2arc_write_max阈值联动反模式 |
| `ontology:principle/cli-tls-mtls-configuration` | [cli-tls-mtls-configuration.md](principle/cli-tls-mtls-configuration.md) | 3.1.0 | reference | 工具 CLI TLS/mTLS 配置约定 |
| `ontology:principle/compat-cautious-evolution` | [compat-cautious-evolution.md](principle/compat-cautious-evolution.md) | 3.1.0 | reference | 兼容审慎演进原则 |
| `ontology:principle/fail-explicit-never-silent` | [fail-explicit-never-silent.md](principle/fail-explicit-never-silent.md) | 3.1.0 | reference | 显式失败禁止静默原则 |
| `ontology:principle/mtls-review-fd-session-boundary` | [mtls-review-fd-session-boundary.md](principle/mtls-review-fd-session-boundary.md) | 3.1.0 | reference | RPC/rdbcomm mTLS 审查：连接对象必须携带传输状态 |
| `ontology:principle/observability-first` | [observability-first.md](principle/observability-first.md) | 3.1.0 | reference | 可观测优先原则 |
| `ontology:principle/ontology-governs-ontology` | [ontology-governs-ontology.md](principle/ontology-governs-ontology.md) | 3.1.0 | reference | 本体演进也服从已固定规则 |
| `ontology:principle/structured-mtls-failure-diagnostics` | [structured-mtls-failure-diagnostics.md](principle/structured-mtls-failure-diagnostics.md) | 3.1.0 | reference | mTLS 失败日志应同时表达角色、阶段、算法与凭据路径 |
| `ontology:process/code-review-process` | [code-review-process.md](process/code-review-process.md) | 3.1.0 | reference | CodeReviewProcess：四模块补充审查过程 |
| `ontology:process/flow-act` | [flow-act.md](process/flow-act.md) | 3.4.1 | normative | Act：交付、失败返工与知识处置 |
| `ontology:process/flow-check` | [flow-check.md](process/flow-check.md) | 3.4.9 | normative | Check：当前任务自检与明确失败判定 |
| `ontology:process/flow-do` | [flow-do.md](process/flow-do.md) | 3.4.9 | normative | Do：实现节点、运行测试与有限修复 |
| `ontology:process/flow-plan` | [flow-plan.md](process/flow-plan.md) | 3.4.9 | normative | Plan：固定当前节点目标与单元测试 |
| `ontology:process/independent-work-review` | [independent-work-review.md](process/independent-work-review.md) | 3.4.9 | normative | 独立审查：定义与实现逐项对应 |
| `ontology:process/pdca-flow-model` | [pdca-flow-model.md](process/pdca-flow-model.md) | 3.0.0 | normative | 三场景与当前任务阶段入口 |
| `ontology:process/select-task-subgraph` | [select-task-subgraph.md](process/select-task-subgraph.md) | 3.4.9 | normative | 当前节点的有界上下文选择 |
| `ontology:process/work-scenarios` | [work-scenarios.md](process/work-scenarios.md) | 3.4.2 | normative | 三场景整树交接与逐节点覆盖 |
