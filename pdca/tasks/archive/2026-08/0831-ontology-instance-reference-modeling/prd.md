# 评估本体独立生成与实例引用的建模策略及链路深度权衡

## 背景

用户提出本体建模策略问题：本体是否应独立生成、实例通过引用复用？该模式的优点是独立本体可记录更详细内容、复用性好；缺点是链路过深导致查询/追溯成本高。

当前仓库已有实践：
- `ontology:domain/tool-production-readiness`（T0464 追补）为独立领域节点，12维+L1-L4+B1-B4 详细沉淀
- `ontology:domain/backup` 等领域根与 `ontology/pattern/*` 的分层
- 但实例侧（如具体 report-web 的 L2 达标实例）尚未形成统一的“实例→本体”引用范式

需系统评估两种策略的适用边界，避免一刀切。

## 目标

对比“独立本体+实例引用”与“内联/聚合”两种建模策略，明确链路深度与表达详细度的权衡阈值，给出可落地的建模规范与实例化指引。

## 范围

- **在内**：策略对比（表达能力、复用度、链路深度、查询成本、维护成本）、阈值与分流标准、决策树/规范、与现有 `ontology:concept/domain-model`、`skill-ontology-check` 的衔接
- **不在**：具体业务本体的批量重构（仅以 T0464 为例验证）

## 关联本体节点

- `ontology:concept/domain-model`
- `ontology:concept/ontology-asset`
- `ontology:concept/pdca-task`
- `ontology:domain/tool-production-readiness`
- `ontology:domain/skill-ontology-check`

## 验收标准

- [ ] AC-1：对比独立本体+引用 vs 内联/聚合的优缺点、链路深度与查询成本，给出量化或半量化评估
- [ ] AC-2：明确链路深度与详细表达的权衡阈值及分流标准（何时独立、何时内联）
- [ ] AC-3：产出建模规范或决策树，可直接用于后续本体设计与审查
- [ ] AC-4：以 T0464 或一个模拟实例验证规范的可用性

## 非目标

- 不对全量 ontology 做批量拆分/合并
- 不引入图数据库等存储选型变更

## 风险

- 阈值过严导致过度拆分、链路过深；过松则独立本体的详细表达优势丧失
- 需与现有 `ontology-validate` 的 `relations` 校验兼容

## 开放问题（待 Grill）

- Q1：独立本体的粒度如何界定（领域/模式/阈值表/清单）？
- Q2：实例引用是强引用（relations 显式边）还是弱引用（文本提及）？
- Q3：链路深度的可接受上限是多少跳？
