# 本体论闭环研究：知识表达·任务拆分·测试依据·AI权威

**任务**: T0427 本体论闭环：知识表达·任务拆分·测试依据·AI权威
**研究日期**: 2026-08-30
**场景**: research

## 研究方法

1. 扫描 ontology/ 目录下所有节点
2. 检查 PDCA 流程实体建模
3. 检查本体规则节点（ontology-rule-*）
4. 检查 attributes 的 testable_signal 覆盖度
5. 检查闭环完整性（source_task 回链、relates_to 关联）

## 研究发现

### AC-1: PDCA 四流程建模为 ontology/process/ 实体 ✅

| 流程 | 实体 ID | 状态 |
|------|---------|------|
| Plan | ontology:process/flow-plan | 已建模 |
| Do | ontology:process/flow-do | 已建模 |
| Check | ontology:process/flow-check | 已建模 |
| Act | ontology:process/flow-act | 已建模 |

四流程均 `specializes ontology:concept/process`，`part_of ontology:concept/pdca`。

### AC-2: 任务拆分可由本体关系树生成 WBS ✅

- `specializes` 形成以 Entity 为根的有向无环树
- `composed_of` 表达组合关系（如 flow-act composed_of self-optimization-loop）
- `part_of` 表达流程与阶段归属
- `relates_to` 表达跨文档关联

### AC-3: 本体节点 attributes 的 testable_signal 覆盖度 ⚠️

- 239 个节点中 140 个（59%）含 `testable_signal`
- 99 个节点（41%）缺少 `testable_signal`
- 需补充缺失节点的 testable_signal

### AC-4: PDCA 流程由本体支撑 ✅

- PDCA 流程实体通过 `relates_to` 关联到 pdca-phase、pdca-verdict、pdca-evidence 等概念节点
- `ontology:concept/pdca` 为根节点，统领所有 PDCA 概念
- `ontology:concept/pdca-continuous-improvement` 支撑 Act→Plan 循环

### AC-5: 本体创建门禁 self-booting ✅

6 个本体规则节点：
- `ontology:concept/ontology-rule-type-controlled`：type 词汇表控制
- `ontology:concept/ontology-rule-non-dangling`：关系引用非空悬
- `ontology:concept/ontology-rule-acyclic`：关系无环
- `ontology:concept/ontology-rule-attr-testable`：属性 testable_signal 校验
- `ontology:concept/ontology-rule-richness`：关系丰富度
- `ontology:concept/ontology-rule-guides-range`：guides domain/range 约束

`ontology:concept/ontology-validate` 和 `ontology:concept/ontology-creation-gate` 支撑校验器自举。

### AC-6: 闭环验证 ⚠️

- 每条本体知识有 `source_task` 回链 ✅
- `knowledge-provenance` 节点记录知识来源 ✅
- `self-optimization-loop` 节点支撑 Act→Plan 循环 ✅
- 但 41% 节点缺少 `testable_signal`，闭环存在缺口

### AC-7: 证据 + 收敛映射 ✅

- 证据已登记
- 收敛映射 valid:true

## 改进建议

| # | 严重度 | 类别 | 描述 | 建议 |
|---|--------|------|------|------|
| 1 | major | 覆盖度 | 99 个节点缺少 testable_signal | 补充缺失节点的 attributes.testable_signal |
| 2 | major | 闭环缺口 | testable_signal 覆盖度仅 59% | 在 Do 阶段对每个 KnowledgeArtifact 补充 testable_signal |
| 3 | minor | 文档 | 部分流程实体的阶段步骤描述不完整 | 补充 flow-plan/flow-do/flow-check/flow-act 的阶段步骤 |
| 4 | minor | 验证 | `ontology-validate.py` 未校验所有 ontology-rule-* 节点 | 在校验器中添加 ontology-rule 覆盖度校验 |

## 结论

本体论闭环已基本建立：PDCA 四流程建模为实体，本体规则支撑自举门禁，知识来源可追溯。主要缺口是 `testable_signal` 覆盖度仅 59%，需补充缺失节点的测试信号。