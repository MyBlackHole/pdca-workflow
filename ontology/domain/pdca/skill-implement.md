---
schema: pdca.asset/v1
id: ontology:domain/skill-implement
name: implement
summary: 从规格说明构建实现——红绿重构驱动的垂直切片
description: |
  从 spec 或 ticket 构建实现——以红绿重构循环驱动，每个垂直切片是一个追踪弹（tracer bullet）。
  使用场景：从已确认的 spec 或 ticket 构建功能或修复 bug。
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-implement/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/completion-criterion
    - ontology:concept/tracer-bullet
    - ontology:concept/triage
    - ontology:concept/design-tree
    - ontology:concept/to-spec
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


# Implement — PDCA 版

从 spec 或 ticket 构建实现——以红绿重构循环驱动，每个垂直切片是一个追踪弹。

## 核心做法

1. **从 spec 构建**：spec 是实现的唯一输入；不实现 spec 之外的内容
2. **红绿重构**：先写失败测试（红），再写最少代码通过（绿），然后重构
3. **垂直切片**：每个实现是一个穿过每一层的窄但完整的路径
4. **pre-agreed seams**：在实现前先声明测试接缝
5. **code-review**：实现完成后进行双轴审查
6. **提交**：使用 feature-commit-format 提交

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

## 已知坑

- 实现 spec 之外的内容是范围漂移
- 不写测试直接写实现是盲飞
- 跳过 code-review 直接提交是风险
- 缺少 pre-agreed seams 会导致测试隔离不足
