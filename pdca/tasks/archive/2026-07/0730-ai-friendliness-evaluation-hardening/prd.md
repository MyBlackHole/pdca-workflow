# AI 友好评测可信度加固 — 规格文档

## 问题陈述

- **现状**：当前 AI 友好度 harness 的六个正常场景只检查 `flow-do` 中的路径标题是否存在，没有按 `scenario_type` 执行路由；`missing_reference` 故障由常量返回；通用夹具没有完整验证 Check/Act 门禁；内容审计报告 bytes 但没有回归预算。
- **目标**：把导航、故障恢复、PDCA 生命周期门禁和内容成本改为可执行、可证伪、可重复的 AI 友好评测合约。
- **差距**：当前 12/12 的静态夹具结果不能证明 scenario 路由行为，也不能防止后续变更绕过 Check/Act 门禁或悄然增加 Agent 上下文成本。

## 解决方案

实现四个协同层：

1. 以严格、机器可读的路由合约定义六类 `scenario_type` 到 Do 路径的唯一映射，提供稳定 JSON 的公共 resolver；人类可读的 `flow-do` 与合约独立交叉校验。
2. 重写 AI 友好夹具，使正常/非法路由和引用断链均调用真实 resolver、引用检查或门禁逻辑，不允许 fixture 直接返回预期错误码。
3. 建立最小真实生命周期 fixture：一条 Plan→Do→Check→Act→archive 成功链，以及每个转换至少一个关键缺失项的失败链。
4. 为 flow/skill 资产建立版本化 UTF-8 bytes baseline；默认拒绝增长，只有显式理由、相关验证和受控 baseline 更新才能豁免。

该方案提高评测 oracle 的可信度和 AI 导航确定性；不声称提升真实模型成功率。

## Seam 分析

### 测试接缝

- **路由 resolver CLI**：输入合法或非法 scenario；观察规范化 route ID、路径锚点、所需步骤及稳定错误码。
- **路由文档一致性**：输入 route contract 和 `flow-do`；观察每个 contract 路由都有对应的人类可读锚点，且额外/缺失映射 fail-closed。
- **真实引用故障**：在临时仓库中移除被流程实际引用的资源；观察真实检查返回路径与稳定错误码，而非测试常量。
- **生命周期转换**：在临时严格仓库调用公共 `transition-phase.py`；观察有效任务顺序生成 receipt，缺确认、PRD/evidence/convergence、conclusion/verdict/check confirmation、disposition 分别被实际 gate 拒绝。
- **内容预算**：输入审计资产与 baseline；观察缺资产、陈旧/非法 baseline、未批准增长和完整性回归的稳定错误码，以及降低或等于 baseline 的通过结果。

### 验收可测性

- 所有新写操作和 CLI 均返回机器可读 JSON、稳定 status 或稳定错误码。
- 路由测试必须在保留全部 Markdown 路径标题但故意篡改合约映射时失败，证明不再由标题存在性自证。
- 生命周期成功 fixture 必须通过实际相邻转换，不允许手工修改 phase；失败 fixture 必须证明对应 gate 的错误码。
- 内容预算测试用同一资产的 bytes 增长前后配对，未更新 baseline 必须失败；具理由的更新才可通过。
- 全部 fixture 可重复运行，不依赖网络、真实模型、数据库或外部 Agent runtime。

## 用户故事

1. 作为执行 PDCA 的 AI，我想通过稳定 resolver 查询当前场景的正确路径，以便不从自然语言标题猜测执行分支。
2. 作为流程维护者，我想看到真实门禁失败而不是测试伪造的错误码，以便相信评测能发现回归。
3. 作为流程维护者，我想让一个完整生命周期 fixture 覆盖关键阶段门禁，以便 Check/Act 的保障不会被遗漏。
4. 作为维护 flow/skill 的作者，我想在内容增长时得到明确预算错误和更新要求，以便权衡必要说明与 Agent 上下文成本。
5. 作为流程所有者，我想明确确定性评测与真实模型表现的边界，以便不把回归测试误报为模型能力提升。

## 实现决策

- 路由合约使用严格 schema，包含六个允许的 scenario、稳定 route ID、文档锚点和必经步骤；resolver 只读取该合约，不解析 Markdown 决定结果。
- `flow-do` 保持面向人的解释性文档；一致性验证只检查合约声明的锚点/引用，不把文档标题当作路由 oracle。
- 生命周期 fixture 共用一个最小有效任务构造器和受控临时仓库。共享阶段语义不按六个 scenario 复制；scenario 差异只由路由合约覆盖。
- 内容 baseline 是受版本控制的结构化资产，记录审计范围、metric、每个资产的 bytes 和更新理由。它是治理配置，不由自动修复命令静默重写。
- 实现遵循 [ADR-0006](../../../../docs/adr/ADR-0006-executable-ai-friendliness-route-contract.md)、[ADR-0007](../../../../docs/adr/ADR-0007-versioned-content-budget.md) 和 [ADR-0008](../../../../docs/adr/ADR-0008-lifecycle-gate-fixtures.md)。

## 测试决策

- 使用现有 `unittest`、子进程 CLI 与临时仓库模式；测试公共 CLI/文件合约，不调用私有实现。
- 正常、篡改和错误路径均成对保留：route 映射漂移、真实断链、各转换关键缺失、预算增长和 baseline 更新。
- 在每次完整运行中验证 resolver、AI 友好夹具、内容审计、workflow/doctor 与全量测试；输出 context bytes 仅为稳定代理，不称为 token 或模型成本。
- 使用 mutation-style 反例：保留路径标题但交换合约映射，或保留代码但改变 baseline，以证明 oracle 本身能拒绝错误。

## 验收标准

- [ ] 路由合约具有严格 schema，恰好覆盖 development、bugfix、research、documentation、design、review；未知字段、重复 scenario、非法 route 或缺失锚点均被拒绝。
- [ ] 公共 resolver 对每个合法 scenario 输出稳定 JSON 的 route ID、路径锚点和步骤；非法 scenario 返回稳定机器可读错误。
- [ ] 正常路由夹具调用公共 resolver；保留所有 `flow-do` 路径标题但篡改合约映射时夹具失败，证明不再以标题存在作为通过条件。
- [ ] 人类可读 `flow-do` 与路由合约存在独立一致性检查，缺失或漂移锚点 fail-closed，但该检查不取代 resolver 行为测试。
- [ ] 引用断链夹具通过实际文件引用或受控临时仓库触发真实检查，输出路径和稳定错误码；测试代码不得直接返回预期错误。
- [ ] 生命周期成功 fixture 只经公共相邻阶段转换完成 Plan→Do→Check→Act→archive，并生成每一步 transition receipt。
- [ ] Plan→Do 失败夹具在缺少 confirmed final confirmation 时由实际门禁拒绝。
- [ ] Do→Check 失败夹具在缺 PRD、实质 evidence 或有效 convergence map 时由实际门禁拒绝。
- [ ] Check→Act 失败夹具在缺 conclusion、verdict 或 check confirmation 时由实际门禁拒绝。
- [ ] Act→archive 失败夹具在缺 disposition 时由实际门禁拒绝。
- [ ] 生命周期和路由夹具重复执行的 JSON 结果、错误码和关键摘要稳定，临时文件不逃逸受控根目录。
- [ ] 内容 baseline 严格覆盖当前受审计的每一个 flow/skill 资产；未知、遗漏、非法或陈旧格式的 baseline 返回稳定错误。
- [ ] 任何资产 bytes 超过 baseline 时预算检查失败；等于或低于 baseline 时通过；增长只有伴随非空理由和显式 baseline 更新才可恢复通过。
- [ ] 内容预算更新仍要求零断链和相关确定性夹具通过；不得用更新 baseline 掩盖引用或行为回归。
- [ ] 评测输出和文档明确说明其只覆盖确定性合约、导航与恢复，不报告或暗示真实 LLM 成功率、延迟或跨模型比较。
- [ ] 全量 `unittest`、AI 友好夹具、内容审计、workflow 校验和 doctor 校验均通过，且没有新增网络、模型或外部运行时依赖。

## 范围外

- 真实 LLM、多模型排行榜、prompt A/B、token/延迟实测或跨模型成功率结论。
- 外部 Agent runner、trace、checkpoint、数据库、消息队列或网络服务。
- 自动压缩或自动更新 baseline；所有内容成本豁免仍由版本控制和审查决定。
- 改变既有 PDCA 阶段语义、用户确认门禁、归档记录或 T0159 的历史证据。
- 为六个 scenario 复制相同的生命周期门禁矩阵。

## 备注

- P4 保持单一纵向任务：路由 resolver、真实生命周期 fixture 和预算检查必须共同证明“评测不再能由标题、常量或报告自证”。拆分会造成中间状态无法证明整体结论。
- 若未来出现固定 Agent runner、冻结工具接口、保留任务集以及成功/恢复/成本指标，应创建独立任务评测真实模型表现，不复用本任务的确定性通过率。
- 网络研究依据记录于 `research-report.md`；其支持可执行 oracle 与交互式 Agent 评测的必要性，不构成当前模型性能证据。

---

*由 Plan 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
