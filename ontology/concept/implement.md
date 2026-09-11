---
schema: pdca.asset/v2
id: ontology:concept/implement
name: Implement
summary: 从规格说明构建实现：红绿重构驱动的垂直切片
type: concept
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
owl_versionIRI: http://pdca.local/ontology/implement/3.4.6
relations:
  specializes:
  - ontology:concept/process
  guides:
  - ontology:concept/pdca-task
revision: 3.4.6
authority: reference
semantic_kind: class
provenance:
  migration_review: structure_and_protocol_only; domain_claims_not_revalidated
  pre_review_revision: 2.0.0
validation:
  claim_status: unverified
  adoption: claim_review_required
---

# Implement

从 spec 或 ticket 构建实现——以红绿重构循环驱动，每个垂直切片是一个追踪弹（tracer bullet）。

## 核心做法

1. **从 spec 构建**：已批准 spec 与原需求/适用约束共同固定实现范围；范围冲突先澄清，不以 spec 覆盖上位义务
2. **红绿重构**：先写失败测试（红），再写最少代码通过（绿），然后重构
3. **垂直切片**：每个实现是一个穿过每一层的窄但完整的路径
4. **pre-agreed seams**：在实现前先声明测试接缝
5. **code-review**：实现完成后进行双轴审查

## 实现流程

1. 读取 spec
2. 声明 pre-agreed seams
3. 编写失败测试（红）
4. 编写最少代码通过（绿）
5. 重构
6. 运行 code-review
7. 提交

## 与相关概念的关系

- `to-spec`：spec 是实现的输入
- `tdd`：红绿重构循环
- `tracer-bullet`：垂直切片实现
- `code-review`：实现后的双轴审查
- `design-it-twice`：接口设计

## AI 效率机制

- spec 驱动实现，减少猜测
- 红绿重构提供快速反馈
- 垂直切片确保完整性
- pre-agreed seams 确保可测试性

## 边界

implement 是实现方法论，不是自动工具；它约束实现流程而非替代编码。


## 类别与采用边界

本节点定义实现方法，指导获权任务内动作，不是完整PDCA任务子类。适用时仍读取原需求、已批准规格与当前协议；方法不能把输入限成一份spec而忽略上位约束。
