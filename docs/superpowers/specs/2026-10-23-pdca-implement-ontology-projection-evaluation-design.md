# AI 使用的本体驱动 PDCA 全流程评估与优化设计

> 状态：修订设计稿，待用户审阅。本文定义如何用 OpenCode Mini 观察 PDCA 本体是否实际驱动 AI 完成开发工作，并据证据优化工作流；此稿获审阅前不启动新的现场测试或产品规则修改。

## 1. 目标与自审结论

目标是评估和改进本仓库面向 AI 的 ontology、Skills、阶段门禁与证据协议，使 AI 能从需求建立可追溯模型，按模型投影实现，并由独立验证确认行为符合要求。评价对象是 PDCA 工作流能否约束 AI 的实际决策和工具行为，不是模型对文档的复述能力。

此前设计只安排两个只读文本 probe，不能覆盖建模、任务分解、阶段执行、实现映射、行为验证和返工，因此不足以检验用户目标。现有现场报告也不支持“全流程已通过”：Model attempt-2 的 r2 只通过了有限模型 Check；formatter 曾有 TDD 红绿证据，但后续反例使同一实现 Check 判 fail，attempt 已归档且 `delivery_usable=false`；TCP 适配器和独立 Verify 尚未执行。H11 的完整验收状态仍是 `NOT_RUN`。这些结果应保留为基线，不被后续成功阶段覆盖。

测试对象是 AI 使用的 PDCA 项目。RPC 服务是承载开发需求的隔离业务 fixture；Python 3 仅是此前选定的该 fixture 目标环境参数。它不定义 PDCA 项目的实现语言，也不能代替对本体语义和跨语言流程规则的检查。

## 2. 设计选择

### A. 隔离业务 fixture 上的真实全流程评估与优化（采用）

在 OpenCode Mini 中，以用户此前授权的 TCP JSON RPC 需求为测试业务，基于冻结的 PDCA 规则快照完成建模、任务/节点分解、实现投影、Check、独立 Verify 和终态处置。先保留当前规则快照的基线证据，再按证据定位规则缺陷、提出有界修改，并用新会话及新快照重跑受影响场景。该方法能观察 ontology 是否约束 AI 的实际工作，并检验优化是否消除了已观察问题。

### B. 静态比对 ontology 与 Skill

可辅助定位来源和投影差异，但无法证明 AI 是否按本体执行；不能单独作为本次验收。

### C. 把仓库维护直接登记成正式业务 PDCA 工作

仓库 `AGENTS.md` 将 ontology、规则、Skills、测试和文档维护归为仓库维护入口，不作为正式业务 PDCA 入口。本次在独立 fixture 中测试其面向 AI 的工作流能力；不通过伪造正式业务记录来绕开该维护边界。

## 3. 测试业务与冻结事实

使用此前已确认的合成 RPC 需求作为工作负载：自定义 TCP RPC，4 字节大端长度前缀覆盖 UTF-8 JSON 负载，提供 `format_count(n)` 语义。Python 3 标准库是此前确认的目标项目实现环境。测试开始时从原始用户消息和已批准选择逐项核对 source set、摘要和来源；历史实现报告或模型补写不能冒充用户 source。

已有 `tests/h11-live-scenario.md` 的固定 oracle 只覆盖无状态 formatter 节点，不能用来声称 TCP adapter、组合关系或完整 RPC 已验收。本次以 H11 的隔离、来源与证据要求为宿主约束；formatter 的既有结果只作历史基线。若要评估多节点 RPC 集成，执行计划须为它固定独立 scenario ID、经确认的 source inventory、AC/oracle 和写域；不得静默扩展 H11，也不得把新场景结果回写成 H11 PASS。

Model 阶段必须把已明确的需求与未决定的接口事实分开。凡此前未明确的请求/响应 envelope、错误响应、最大帧长、连接关闭/持续策略、并发或超时等语义，应标为 unknown 并询问或阻塞；不得为完成代码而自行填成产品要求。用户作出的新选择作为具来源的新决定加入后续基线，不回写或改述旧 source。

该工作负载至少要让模型表达 formatter 与 TCP adapter 的职责，以及服务组合和 adapter 对 formatter 的接口/依赖关系。模型可根据来源细化 definitions、work instances、关系和约束；每项细化都须标明直接来源、语义拆分或推论。若资格或组合责任不确定，保持 unknown，不据目录、文件、消息数量直接生成正式节点或任务。

## 4. 评估流程

### 4.1 环境与基线

1. 建立隔离 fixture，分别设置 PDCA Git 工作副本、TARGET_ROOT、control/evidence 与 fixture 内临时目录；不得读写集中真实 `records/`。按 `tests/h11-live-scenario.md` 核验 Skill Base、Instructions、PDCA_ROOT、TARGET_ROOT、绑定和 Git 根来源；测试进程的临时目录指向 fixture 内路径，不向 `/tmp` 写入测试文件、日志、构建物或缓存。
2. 测试快照只能包含执行计划逐项列出的规则、Skill、入口说明和场景文件。不得复制整个工作树，也不得把 `records/`、control/evidence、OpenCode 配置、凭据或无关未跟踪产物带入 fixture。对每个允许文件记录来源路径、Git 状态和 SHA-256；需要的未提交规则必须逐项列入 allowlist 并固定摘要。来源无法核验、目录/绑定无法核验或实际写域不能隔离时，停止并记录 `NOT_RUN`，不能只记录 HEAD 代表未提交规则。
3. 使用专用 OpenCode Mini 会话。运行时确认实际 OpenCode 版本、会话 ID、模型确为用户指定的 `GPT-6 Luna Max`、实际生效配置、Skill/Instructions 物理来源、工具权限与返回；任一不符时不把结果归因给目标模型，保持 `NOT_RUN`。
4. 先对冻结快照测基线，测试中不修改本体、Skills 或 scenario。采集原生消息、工具调用、输入/输出、路径、退出码、对象摘要和权限结果；不以 Mini 最终自述或摘要替代原生证据。

### 4.2 本体建模及分解

Model task 按 Plan→Do→Check→Act 推进。后续 Implement 和 Verify 各自使用独立 task/scene，也分别执行 Plan→Do→Check→Act；任何一个 task 的阶段批准都不授权另一个 task。逐项评估：

- source inventory、直接陈述/语义拆分/推论分类和来源引用是否闭合；
- ontology asset 的定义与工作实例是否分层；关系 schema 与关系 instance 是否分层；约束是否能指出适用对象与来源；
- work root、composition/dependency、DECOMP、NODE qualification 的细化是否保留语义，且没有把文档、消息或操作顺序直接等同于 task/node；
- unknown、冲突、来源缺失与模型缺口是否能在阶段门禁处停止，而非由 Mini 静默补齐；
- Plan/Do/Check/Act 对象是否按实际权限和证据推进，失败与恢复是否保留历史。

### 4.3 按固定本体实现

从已固定且 qualified 的节点启动 Implement，并在该 task 内按 Plan→Do→Check→Act 推进；不得在 Implement 中重定义 ontology。对每条 source requirement 到模型、模型到实现 artifact 的映射，记录精确 source/node、目标 artifact、投影语义、覆盖范围和可观察信号。多节点场景至少覆盖 formatter、TCP adapter 及其组合/接口责任；target artifact 的语言语法不得泄漏为 PDCA 本体规则。

执行实际测试并保留红/绿与失败恢复证据。测试通过只能说明对应观测通过，不能代替独立 Check；当实现发现模型缺失或冲突时，应按固定 EVOLVE 路径停止当前实现，不得先改模型再继续。

### 4.4 独立 Verify 与终态

依固定 source、模型版本、qualified node、mapping、release digest 和 oracle，由 fresh Agent 在独立 Verify task 中按 Plan→Do→Check→Act 执行验证。Verify 必须重新取得实现行为 observations，而不能把 Implement 的报告或 signal 当成 observation；逐项检查 requirement→model、model→implementation、implementation→behavior 和 composition/dependency 四条链。通过与失败场景、未覆盖项、mutant/control 结果、release subject 结果分别记账，不能互相替代。每个阶段按原生确认和权限规则分别推进。

每个 task/scene 保持 task execution、subject conformance、scene coverage 和 delivery usability 分开判定。任何影响 source、scope、语义或映射的 unknown 均阻止 work-level complete。若中途受阻，保留 NOT_RUN/unknown 与已观察失败，不为形成完整流程而虚构完成状态。

## 5. 过程效能与问题归因

基线运行记录可核对的流程摩擦：需求澄清轮次、阶段授权次数、交接/恢复次数、工具调用及失败、资源检查与 phase_started 的先后、写域/路径错误、重复读取、各阶段耗时和上下文用量。耗时拆分宿主/权限等待、provider/传输等待与 Mini 执行；无法拆分时注明归因 unknown。工具次数和速度是次级指标，不能抵消语义错误或缺失证据。

每条 finding 都标注类别及证据：ontology semantics、Skill projection、phase/gate contract、host/configuration、operator/test design 或 provider transport。只有能回链到实际行为的发现才作为规则修改候选。修改前先保留基线；修改后仅改有证据支持的最小范围，逐条注明本体来源、Skill 投影、反例和回归 oracle，再用新的冻结快照/会话重跑受影响的正向与对抗场景。未重跑的场景保持 `NOT_RUN`。

Superpowers 等成熟 Skill 方法（例如 TDD、系统化调试、完成前验证）作为第二层对照：先记录项目现有方法与来源，再只采纳能映射到本体语义、门禁和证据协议的具体实践；不以 Skill 数量或名称相似作为改进证据，也不让外部流程覆盖 PDCA 的规范性本体。外部资料比较安排在基线取证后，记录项目、版本/提交、来源链接及实际映射。

## 6. 验收标准与限制

本次测试报告只有同时满足下列要求，才可声称“在该 fixture、该快照和该 Mini 模型上的 AI 使用全流程评估已完成”：

1. 来源、绑定、模型/宿主配置、隔离根和全部原生会话/工具证据可核验；
2. Model、实现投影、独立 Verify 与终态处置均有各自完整的 phase 记录、授权和实际证据；
3. 多节点关系/约束、需求覆盖、双向 mapping、独立行为 observations 与四条验证链全部可追溯；
4. finding 能区分 PDCA 规则问题与 Mini、provider、宿主、操作者或测试环境问题；
5. 若修改了 PDCA 项目，修改有证据来源，相关回归已按新快照重跑，并如实保留旧基线结果。

此评估只能支持该模型、版本、快照和场景下的结论；单次现场运行不能证明所有模型或所有业务都同样受益。H11 及 H1–H18 的状态必须按各自验收条件单独更新，不能因本次报告完成而自动改成 PASS。

## 7. 执行门

此文档是设计规格，不是运行授权回执。按 `superpowers:brainstorming` 的架构工作流程，先由用户审阅本设计；审阅通过后再整理可执行计划和精确文件/fixture 写域，然后启动现场基线。任何源内容、接口语义或超出已确认 RPC 需求的产品决定，仍在 Model 阶段向用户澄清。未经本门审阅，不运行 OpenCode 测试、不修改 ontology/Skill，也不更新 H11/H1–H18 验收状态。
