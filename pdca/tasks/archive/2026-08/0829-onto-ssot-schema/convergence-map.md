# Convergence Map — T0400 定义本体 SSOT 词汇表与 frontmatter schema

| AC | Evidence | 说明 |
|----|----------|------|
| AC-1 | `ssot-readme` (ontology/README.md) | README 定义类型受控词汇起点、关系词汇表（specializes/instance_of/composed_of/part_of/depends_on/relates_to）、attributes 字段结构、组合规则、目录即真理约定 |
| AC-2 | `asset-schema` (schemas/ontology-asset.schema.json) | JSON Schema 定义 pdca.asset/v1 扩展 frontmatter 结构（id/type/layer/attributes/relations/domain 等），字段与 README 一致，可被后续 ontology-validate 消费 |
| AC-3 | `ssot-readme` (ontology/README.md) | README §1 明确三合一用途（知识权威来源+验证契约+关系树驱动任务分解），§7 引用 ADR-0030 的"全部物理归并"边界 |

收敛结论：AC-1/AC-2/AC-3 均已被对应 evidence 覆盖，SSOT 与 schema 可作为后续 T0401（校验脚本）、T0402/T0403（迁移）的统一规范基础。
