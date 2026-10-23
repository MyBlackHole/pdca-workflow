# AI 使用本体驱动 PDCA：RPC 集成评估场景

**场景 ID：`PDCA-AI-RPC-01`**

**状态：场景规约，尚未执行；不改变 H11 或 H1–H18 的验收状态。**

**用途：** 在隔离 RPC 业务 fixture 中观察 OpenCode Mini 是否按 PDCA ontology 建模、分解、实现、验证并保留证据。

本文件是操作员评估 oracle，不作为 Mini 的提示或业务 source 注入；Mini 只接收确认后的业务 source、fixture 内实际加载的 PDCA Instructions/Skills，以及按 LOAD-MAP 当前需要读取的规范性资产。

## 1. 被测对象和场景边界

被测对象是面向 AI 使用的 PDCA ontology、Skills、phase gates 和 evidence contracts。RPC 服务仅是隔离业务负载；Python 3 标准库仅是此前确认的目标 fixture 运行环境，不定义 PDCA 的实现语言或 ontology。

场景覆盖从已确认 source 到 Model、Implement、独立 Verify 和终态处置的实际行为。Model、每个 Implement task、Verify task 分别按 Plan→Do→Check→Act 运行；task 创建、每次 phase_start 和新 source 决定均遵守对应授权门。原生回执、Mini 实际消息/工具事件、Git 路径和目标行为 observations 是判定依据。Mini 自述、成功消息、绿色测试或文件存在本身不是完整性证据。

本场景采用新的 scenario ID、fixture 和 verdict。`tests/h11-live-scenario.md` 的固定 oracle 只覆盖无状态 formatter 节点；其历史观察可作为 formatter 基线，不能证明 TCP adapter、组合关系或本场景通过。H11 与 host acceptance 仍按原条件保持 `NOT_RUN`，除非 H11 自身条件独立满足。

## 2. 已确认的工作负载事实

只有以下事实进入初始 `spec/rpc-service.md`：

1. 目标是开发一个 RPC 程序。
2. RPC 使用自定义 TCP 协议。
3. framing 是 4 字节大端长度前缀，长度覆盖 UTF-8 JSON 负载的字节数。
4. RPC 对外提供 `format_count(n)`；其 formatter oracle 引用 `tests/h11-live-scenario.md` 固定的 source/AC，不得从历史实现报告补入新要求。
5. 目标 fixture 之前选定 Python 3 标准库作为实现环境。

在正式创建 Model task 之前，从原始用户消息重建 source 内容，逐项标明来源位置和分类，记录 `spec/rpc-service.md` 的 SHA-256，并把精确内容展示给用户确认。测试报告中的转述、旧候选和历史 AC 映射都不能冒充原始用户 source。

## 3. 必须显式保留的未决语义

除非用户历史消息已有可逐字核对的决定，下列语义均为 `unknown`。Model 应逐项询问、说明阻塞影响，或留在模型 unknown；不能为使代码可运行而自行选值：

- JSON request/response envelope 的字段名、类型与 method/parameter 表达；
- 成功响应形状、错误响应形状及 `ValueError` 的 RPC 映射；
- 允许的最大 frame 长度及畸形/截断 frame 的处理；
- 单连接允许一个还是多个请求，连接结束条件和半关闭行为；
- 并发、超时及客户端断开时的行为；
- server/client 是否均属于交付范围。

用户对这些事项的新答复单独形成有来源的决定和新 source statement；不得改写先前 source。若某一未决语义阻止忠实建模或实现，停止受影响的 task，保留 unknown 与证据并等待用户决定。

## 4. 隔离和宿主前提

使用 `tests/.pdca-ai-ontology-20261023-01/`，按评估计划建立互不混用的 `pdca-root/`、`target/`、`spec/`、`control/`、`evidence/`、`tmp/`。`pdca-root/` 只承载计划中逐项列出的规则/Skills 快照和 fixture-local records；`target/` 是唯一业务 Git 根，不包含 `.pdca/`；真实集中 `records/` 禁止读取和写入。

按 `tests/h11-live-scenario.md` 核验实际加载的 fixture-local Skill Base、Instructions、Git roots、绑定路径和原生会话证据。OpenCode Mini 必须真实运行于 fixture `target/`，模型必须由运行时证据确认是 GPT-6 Luna Max。provider 凭据留在已配置宿主环境，不复制进 fixture、记录或报告。测试进程的临时与缓存目录指向 fixture 内位置；不向 `/tmp` 写测试文件、日志、构建产物或缓存。

来源副本、模型或权限、binding、Git 根、source digest 或写域任一项无法核验时，停止并记录 `NOT_RUN`/`unknown` 及缺失证据。不得用手工回执、模拟会话 ID、summary 或旧 fixture 代替现场证据。

## 5. Model 评估 oracle

Model task 应在固定 source scope 下执行完整 Plan→Do→Check→Act。逐项检查：

- source inventory 闭合；每项 requirement 区分直接陈述、语义拆分或推论，并能回指 source；
- definition 与 work instance 分层；关系 schema 与 relation instance 分层；约束指明适用对象、语义和来源；
- 服务、formatter、TCP adapter 的职责、composition 与 dependency 只按需求语义建模；不把文件、消息、目录或执行顺序直接当成 ontology 节点或 relation；
- source 到 requirement、requirement 到 AC、work root 到 TREE/NODE/DECOMP seed 的映射可追溯；候选与 fixed 的版本边界明确；
- unknown、冲突、来源不足、qualification 不足能阻止错误的 task 派生或实现；不静默补全；
- resource/capability checks、authorization、phase_started、task state projection 的顺序有原生证据；写域、记录路径和失败恢复符合固定 contracts。

只有 fixed ontology revision、tree、qualified nodes 及其 source/requirement/AC receipt 才可供 Implement 使用。Model Check failure、blocked 或 Act 未固定时，后续 Implement 不得假设有可用模型。

## 6. Implement 评估 oracle

每个合格节点或获批节点集单独建立 Implement task，并执行完整 Plan→Do→Check→Act。Implement Plan 固定 node/revision、source/AC/oracle refs、目标文件、mapping version、读写范围、测试命令与验证信号。

逐条核对：

- `source → requirement → model node/constraint → target artifact` 双向可追溯；mapping 明确投影语义、覆盖和未知；
- 实际读写只在批准的 target scope 与 task-record scope；task boundary 不被误作 phase write authorization；
- TDD 的红/绿均来自同一固定测试和可核验 subject digest；失败、恢复、权限拒绝和路径差错均保留；
- 发现 ontology 缺口或冲突时按 EVOLVE 路径停止，不在 Implement 中改模型或放宽 oracle。

格式化、测试通过和 phase completion 各自只证明对应 claim，不能替代 Check 或独立 Verify。

## 7. Verify 评估 oracle

使用 fresh Agent 建立独立 Verify task，执行自己的 Plan→Do→Check→Act。Verify Plan 固定同一 source、模型版本、qualified node、mapping、release subject digest、oracle、测试范围及隔离读写边界；Verify Agent 对 release target 只读，并独立取得行为 observations。

Verify 必须逐项给出以下四条链的 verdict/ref：

1. requirement → model：固定 source、requirement inventory、scope/coverage；
2. model → implementation：固定 node/constraint 与双向 mapping；
3. implementation → behavior：实际 release subject、运行命令和逐输入 observations；
4. composition/dependency：服务、formatter、adapter 的关系及真实调用行为，或有来源的“不适用”结论。

Positive/negative cases、每项 actual、退出码、subject digest、限制与 counterevidence 都要记录。若运行隔离的 mutant/control，只能判该 control 的检测结果；不得并入 release subject verdict。未知输入或未观测行为保持 `unknown`/`not_run`。

## 8. 过程效能与归因

记录需求澄清轮次、各阶段等待与确认、dispatch/continue 恢复、工具调用和失败、越界路径、资源检查与 phase_started 的时间顺序、重复读取、各阶段耗时及上下文用量。把 Mini/provider/传输等待、操作员等待和 host/tool 等待分开；不能准确拆分时注明归因 `unknown`。

每条 finding 归类为 ontology semantics、Skill projection、phase/gate contract、host/configuration、operator/test design 或 provider/transport，并引用原生事件和固定对象摘要。工具数量和速度仅作次级指标，不能抵消语义/证据失败。

## 9. 结果判定

- **task execution**：由该 task 的原生阶段事件判定；成功识别失败的 task 可为 completed。
- **subject conformance**：只由对应 release subject 的 source/model/behavior observations 判定；确定反例为 fail。
- **scene coverage**：只统计有完整原生 phase、seed、mapping 和行为证据的 scene；缺项不算覆盖。
- **delivery usability**：由获授权的终态处置独立判定；不从 task completed 或 subject pass 推出。
- **evaluation complete**：要求本场景 Model、所有获批 Implement tasks、独立 Verify 与终态证据齐全，四条验证链可追溯，finding 归因有证据；它不自动使 H11/H1–H18 PASS。

若场景正确发现模型缺口、产品反例或宿主阻塞，可完成一次“评估运行”，同时保留对应 `fail`/`unknown`/`not_run`。不得为达成“完整流程”而补造 source、回执或 phase。

## 10. 与优化工作的关系

基线运行期间不修改 PDCA ontology、Skills 或本场景。完成脱敏报告和成熟 Skill 对照后，为每条证据支持的规则 finding 建独立、精确范围的修改计划；修改只针对基线实际揭示的问题。优化后使用新的规则快照与 fresh Mini session 重跑正向和对抗回归，保留旧基线、旧失败和各版本摘要。

本文件是场景规约，不是任务创建或阶段授权。用户只在当前实际对象和授权请求出现后确认该对象/当前阶段；不得预批未来阶段。
