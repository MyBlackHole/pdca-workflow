# T0461 结论：建立 testable_signal 到测试用例派生机制

## 上下文

当前本体 178 个 attributes 中 53 具体/125 泛化（泛化全部集中在 domain 层），GAP-01 的本质是信号质量问题（70% 不可直接派生断言），非链路缺口。本任务不批量精化 122 个泛化，而是建立"新增时强制具体 + 示范派生"的机制，使本体真正驱动测试生成。

## 假设与结果

### AC-1：新增 ontology/pattern/testable-signal-to-test-derivation.md 描述3种派生模式且 validate 通过

**结果**: 通过。证据 `ac1-pattern` 登记 `ontology/pattern/testable-signal-to-test-derivation.md`（`type: pattern`，`specializes: pattern`，`guides: pdca-task, ai-efficiency` 合法，`relates_to: ontology-asset, ontology-validate, ontology-rule-attr-testable, skill-ontology-check` 规避 AC-6），含 `attributes.testable_signal` 具体描述，描述 3 种派生模式（属性断言/契约测试/收敛验证）及示例与选择指南，`ontology-validate: OK`。

### AC-2：skill-ontology-check.md 增加泛化信号校验指引

**结果**: 通过。证据 `ac2-skill-check` 登记修改后的 `ontology/domain/skill-ontology-check.md`，在"步骤"新增步骤 6（新增 KnowledgeArtifact 的 `attributes.testable_signal` 不得为泛化描述，要求动词+对象+判定标准），并在"与 ontology-validate.py 的衔接"中将 AC-4 扩展为"脚本仅机检非空 + 本 skill 步骤 6 人工补位，派生见 testable-signal-to-test-derivation 三模式"。

### AC-3：示范精化2个 domain 节点的 testable_signal 为具体信号

**结果**: 通过。证据 `ac3-domain-refinement` 登记 `ac3_refinement.md`（覆盖 2 个 domain 精化）：`ai-efficiency-contract-test-pattern` 改为"运行 scripts/seam_contract.py 校验 PRD 声明的 seam 清单与实际测试文件的一致性，且契约测试套件全部通过"（契约测试型）；`ai-efficiency-knowledge-assets-and-ai-workflow` 改为"检查资产 source_ids 非空且可追溯至 Evidence/Experience，并对抽样查询执行四维评估达标"（收敛验证型）。relations 不变，`ontology-validate: OK`。

### AC-4：ontology-validate 通过且 islands:0

**结果**: 通过。证据 `ac4-validate` 含 `ontology-validate: OK` 且 `ontology_graph: nodes: 349, edges: 754, islands: 0`，无孤岛。

## 分析

本任务以"建机制而非补数据"解决 GAP-01：`pattern/testable-signal-to-test-derivation` 提供 3 模式与选择指南，`skill-ontology-check` 提供新增时的非泛化约束，2 个示范精化验证派生可行性。剩余 120 个泛化可结合实际测试派生需求逐步精化，不宜批量。

## 失败原因（无）

4 AC 均已验证通过，无失败。

## 适用边界

示范精化的 2 个节点为代表性选择（契约测试型与收敛验证型各 1），覆盖主要派生模式；其余泛化的精化需结合实际派生需求逐步推进。

## 下一轮建议

1. 新增本体节点时按 `skill-ontology-check` 步骤 6 要求提供具体 testable_signal
2. 结合 `testable-signal-to-test-derivation` 的 3 模式，在后续开发任务中试用派生流程
3. 对高频使用的 domain 节点优先精化泛化信号

## 证据索引

- `ac1-pattern`: pattern 节点（3种派生模式）
- `ac2-skill-check`: skill-ontology-check 扩展（非泛化指引）
- `ac3-domain-refinement`: 2 个 domain 示范精化
- `ac4-validate`: validate + graph 输出
- `convergence-map`: 4 AC → 4 evidence id
