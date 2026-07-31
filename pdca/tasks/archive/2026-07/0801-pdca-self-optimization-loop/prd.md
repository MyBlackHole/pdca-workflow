# PDCA 问题记录驱动的自我优化闭环 — 规格文档

## 问题陈述

- **现状**：T0158 已能在阶段转换时检查并记录偏差，但 `flow-audit/v1` 会整体更新，缺少独立不可变事件、阶段中途/人工问题上报、跨任务聚合、治理决策、改进候选和部署后效果验证。
- **目标**：建立 AI 友好、可审计、由用户治理的 PDCA 自我优化闭环，使问题能够从真实发生记录，经过确定性聚合和受控改进，最终由后续周期证据判断是否有效。
- **差距**：当前系统只能回答“本次转换发现了什么”，不能稳定回答“哪些机制问题反复出现、是否值得改、谁授权修改、修改后是否真正改善”。

## 解决方案

采用 `Observe → Aggregate → Diagnose → Evaluate → Promote → Verify` 六层闭环：

1. 所有自动或人工发现的 PDCA 机制问题通过唯一 CLI 上报为独立不可变 Flow Issue Occurrence。
2. 确定性聚合器用版本化 fingerprint 生成可重建的 Flow Issue backlog。
3. AI 可输出 triage 建议、根因假设和 dry-run Improvement Candidate，但不能直接修改权威流程或创建正式任务。
4. false-positive、accepted-risk、impact 晋级、关闭和候选晋级必须引用用户确认并生成不可变 Flow Issue Decision。
5. 经确认的 candidate 才能创建严格 schema 的 Improvement Task，继续走正常 PDCA。
6. 改进部署后按预先冻结的 baseline、指标和观察计划生成 Effectiveness Verdict；只有 `improved` 才将问题转为 `verified`。

`flow-audit/v1` 冻结为历史输入，不回写或迁移。新模型从实现定义的 cutover receipt 开始。

## Seam 分析

### 测试接缝

- **问题上报 CLI**：输入 task/record、source、category、事实字段和 idempotency key；观察退出码、稳定 JSON、事件路径与文件内容。
- **聚合/查询 CLI**：输入事件根目录和 projection/fingerprint 版本；观察排序、digest、分页/limit 和错误码。
- **决策与候选 CLI**：输入 issue、确认引用和候选参数；观察不可变 decision/candidate 文件以及是否保持 dry-run。
- **晋级 CLI**：输入已确认 candidate；观察严格 task 骨架和父子/来源引用，不执行阶段转换。
- **效果验证 CLI**：输入部署回执、冻结观察计划和前后指标；观察 improved/neutral/regressed 结果。
- **转换集成**：通过现有 `transition-phase.py` 公共 seam 观察 transition audit 是否产生新 occurrence。

测试只通过 CLI 与文件合约验证行为，不调用私有函数。使用临时仓库 Fake，不依赖网络、数据库或真实模型。

### 验收可测性

- 每个写操作均有成功、重复、非法输入、路径越界和崩溃/并发边界。
- 聚合器对相同输入重复执行，规范化输出与 digest 必须一致。
- 通过固定反例验证相同 code 的不同组件/规则版本不会错误合并。
- 通过相同缺陷输入做旧/新配对：旧方案遗漏阶段中途问题，新方案可记录且回链。
- 端到端夹具覆盖 occurrence → issue → decision → candidate → task → effectiveness verdict。

## 用户故事

1. 作为执行 PDCA 的 AI，我想通过一个明确命令记录问题，以便不猜测文件位置或字段。
2. 作为流程维护者，我想看到跨任务的紧凑问题 backlog，以便按事实而非印象决定改进。
3. 作为用户，我想确认风险接受、关闭和流程改进授权，以便 AI 不能自行改变治理规则。
4. 作为改进实施者，我想让 candidate 回链原始事件、baseline 和验证计划，以便 Check 能判断证据充分性。
5. 作为流程所有者，我想在后续周期判断改进是 improved、neutral 还是 regressed，以便形成真实反馈闭环。

## 实现决策

- **事实层**：每个 occurrence 独立写入 `records/<record-id>/flow-events/<event-id>.json`，独占创建、禁止覆盖。
- **身份**：event ID 由 record 与 caller-stable idempotency key 确定性生成；重复调用返回 `unchanged`。
- **分类**：
  - source：`transition-audit | test | tool | agent | user | retrospective`
  - category：`conformance-deviation | specification-gap | tooling-failure | gate-false-positive | gate-false-negative | capability-gap | ai-usability`
- **事实与判断分离**：occurrence 保存 `gate_effect`、错误码、状态变化及 `observed|inferred`；impact 由 decision 赋值。
- **聚合身份**：由 `fingerprint_version + rule_id/rule_version + category + transition + affected_component + normalized_location + issue_code` 生成；自由文本不参与。
- **投影层**：backlog 是稳定排序、带输入摘要和 projection version 的派生产物，可删除重建。
- **治理层**：decision、candidate、effectiveness verdict 使用独立严格 schema 和内容摘要；candidate 默认只 dry-run。
- **权限层**：只有引用用户确认的晋级命令可创建 Improvement Task；任何 CLI 都不能自动推进任务阶段。
- **效果层**：candidate 在实施前冻结 baseline、目标指标、规则版本、最小观察机会和最长观察期限。
- **架构记录**：[ADR-0004](../../../../docs/adr/ADR-0004-immutable-flow-issue-events.md)、[ADR-0005](../../../../docs/adr/ADR-0005-human-governed-flow-improvement.md)。

## 测试决策

- 沿用 `unittest`、临时目录、子进程 CLI 和确定性 fixture。
- 单元层验证 schema、ID/fingerprint 规范化和状态 reducer。
- 集成层验证每个 CLI 的文件边界、幂等、稳定错误码和路径安全。
- 端到端层验证完整反馈链，不调用真实 LLM。
- AI 友好度采用 GQM：门禁正确率、导航成功、上下文 bytes 和故障恢复分别报告，不合成主观总分。
- 正常路径与失败路径成对保留；控制产物不能给自身作证。

## 验收标准

- [ ] 新增 occurrence、decision、candidate、effectiveness verdict 的严格 JSON Schema，拒绝未知字段、非法枚举、缺失来源和路径越界。
- [ ] `report-flow-issue` CLI 支持六种 source、七种 category、阶段中途人工上报和 transition audit，上报成功返回稳定 JSON。
- [ ] occurrence 使用独立文件和确定性 event ID；相同 idempotency key 重试返回 `unchanged`，不同内容复用同 key 被稳定拒绝，既有事件不可覆盖。
- [ ] occurrence 将可观察事实与治理判断分离；AI 不能在事件上直接固化 impact 或关闭状态。
- [ ] 聚合器按版本化 fingerprint 稳定聚类；相同 code 的不同组件、位置或 rule version 不会错误合并。
- [ ] 对同一事件集合重复聚合得到相同排序、规范化内容和 SHA-256 digest；损坏事件使聚合 fail-closed 并返回具体路径和错误码。
- [ ] 查询 CLI 默认返回紧凑、可分页/limit 的 JSON 摘要，并能按 issue ID 展开来源事件，不要求 AI 扫描全部 raw files。
- [ ] MVP 生成 shadow backlog，不按固定次数自动创建任务；严重问题和人工选中问题也只生成 dry-run candidate。
- [ ] Flow Issue Decision 必须记录 action、理由、确认引用、确认者和时间；未确认的 false-positive、accepted-risk、关闭、impact 晋级或 candidate 晋级被拒绝。
- [ ] Improvement Candidate 必须回链 issue/event IDs，并冻结根因假设、目标组件、baseline、指标、风险和观察计划；生成 candidate 不修改 `flows/`、`skills/`、schema、gate 或 active tasks。
- [ ] 晋级命令仅对具有有效确认 decision 的 candidate 创建严格 schema Improvement Task，并保持 `phase=plan`；不写 final_confirmation、不自动进入 Do。
- [ ] Effectiveness Verdict 必须引用部署回执和冻结观察计划，输出仅为 improved、neutral 或 regressed；只有 improved 可产生 verified decision，regressed 只生成待确认回滚候选。
- [ ] `flow-audit/v1` 历史文件保持不变；cutover 后 `transition-phase.py` 通过新事件入口记录转换问题。
- [ ] 配对夹具证明阶段中途问题在旧方案中不可记录、在新方案中可记录，同时重复上报、规则升级、路径攻击和错误晋级均被正确处理。
- [ ] 确定性端到端夹具完成 `event → issue → decision → candidate → Improvement Task → effectiveness verdict`，且所有产物可追溯到原始 occurrence。
- [ ] AI 友好度验证提供机器 pass/fail、稳定错误码、相同输入前后配对和上下文 bytes；不把确定性夹具外推为真实模型成功率。

## 范围外

- 模型权重训练、RL、Agent Lightning 接入。
- 无用户确认的自动 patch、自动 merge、自动阶段推进或自动回滚。
- 在缺少历史数据时固化“出现 N 次自动触发”的全局阈值。
- Web UI、数据库、消息队列或远程集中式事件服务。
- 对既有 `flow-audit/v1` 记录做追溯迁移或改写。
- 开放式 AFlow/ADAS 工作流代码搜索和无 holdout 的 prompt 自动优化。

## 备注

- P4 不拆为独立子任务：event、projection、decision、candidate 和 effectiveness 必须通过同一纵向夹具才能证明闭环，拆分会造成跨任务证据依赖和再次产生未执行子任务的风险。
- 实施可按内部垂直切片顺序推进，但 T0159 保持单一 PDCA task。
- Proposed ADR 仅在 P6 完整方案终审通过后转为 Accepted。

---

*由 to-spec 流程合成。术语表见 `pdca/CONTEXT.md`，架构决策见 `docs/adr/`。*
