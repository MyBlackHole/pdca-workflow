# 定义本体 SSOT 词汇表与 frontmatter schema

## 问题
知识重构需要统一的本体词汇表（类型/关系/属性）与 frontmatter schema 作为 SSOT，供校验脚本与门禁消费。

## 解决方案
创建 `ontology/README.md`（SSOT 文档）与 `schemas/ontology-asset.schema.json`（pdca.asset/v1 扩展）。

## 验收标准

- [ ] AC-1: 存在 `ontology/README.md`，定义类型受控词汇起点（concept/principle/pattern/pitfall/decision/fact/process，可扩展）、关系词汇表（specializes/instance_of/composed_of/part_of/depends_on/relates_to）、attributes 字段结构（name/desc/constraint/testable_signal）、组合规则、目录即真理约定
- [ ] AC-2: 存在 `schemas/ontology-asset.schema.json`，定义 pdca.asset/v1 扩展 frontmatter 结构（id/type/layer/attributes/relations/domain/source_ids/confidence/status），字段与 README 一致，可被后续 ontology-validate 消费
- [ ] AC-3: README 明确三合一用途（知识权威来源 + 验证契约 + 关系树驱动任务分解）与"全部物理归并"边界（ADR-0030）

## 范围外
- 不实现校验脚本（属 T0401）
- 不迁移知识文件（属 T0402/T0403）
