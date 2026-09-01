# 审查单一本体知识闭环：产出资料链完整性

## 背景

本体已硬指标化（T0493），但单一本体知识（single ontology node）是否“闭环”尚未核验。闭环定义（`ontology/README.md:7` 三合一与 `knowledge-provenance`）：一知识应同时具备 **可测属性（attributes.testable_signal）→ 可追溯关系（relations→guides/relates_to）→ 可复核证据（records/* /evidence）→ 经验沉淀（records/*/conclusion）→ 技能索引（SKILLS-INDEX）** ，形成 Evidence→Experience→Knowledge→Skill 的来源链。当前抽样显示 `skill-tdd` attributes缺失、`skill-wizard/teach` 未回链record、`concept/domain-modeling` 0 attributes，存在断链。

## 目标

- 抽样5节点（skill-wizard/teach/tdd + testable-signal pattern + domain-modeling）核验闭环四要素（attributes/relations/evidence/experience/skill）
- 输出单节点闭环率、断链类型与修复清单

## 范围

- 输入：365 nodes、SKILLS-INDEX 50、records/T0489-T0491、scripts/ontology-validate、knowledge-provenance
- 输出：`records/T0494/report.md` + 证据 + 本结论
- 不做：不改全量ontology，仅抽样+修复建议

## 功能需求

1. attributes闭环：检查 `attributes[].testable_signal` 非空且不含泛化，AC-4门禁
2. relations闭环：每 KnowledgeArtifact 至少1条 `guides`/`relates_to` 且非空悬，AC-5
3. 产出链闭环：evidence(manifest含该知识id或file)→experience(conclusion→disposition含ontology:)→knowledge(frontmatter id可解析)→skill(SKILLS-INDEX可grep)
4. 可追溯：ontology file 正文或 relations 可回链到来源 record（provenance）

## 非功能需求

- 可重跑：`ontology-validate 0 issues` + `grep` + `manifest` 命中均为机器可检

## 验收标准

- [ ] AC-1 抽样5节点attributes已核验（非空、非泛化、可派生三模式）
- [ ] AC-2 抽样5节点relations已核验（非空悬、guides/relates_to）
- [ ] AC-3 产出链已逐节点判定（evidence/experience/knowledge/skill四阶是否闭环）
- [ ] AC-4 闭环率与断链类型已统计（含缺失attributes/断链provenance）
- [ ] AC-5 修复清单已给出（补attributes/补provenance回链/补scaffold）
- [ ] AC-6 报告已登记且 `validate-convergence valid:true`

## 关联本体节点

```
ontology:concept/knowledge-provenance
ontology:pattern/testable-signal-to-test-derivation
ontology:pattern/ontology-modular-reference
ontology:concept/ontology-validate
ontology:concept/ontology-creation-gate
```

## 拆分映射

- attributes核验 -> ontology:pattern/testable-signal-to-test-derivation
- relations核验 -> ontology:concept/ontology-creation-gate
- 产出链判定 -> ontology:concept/knowledge-provenance
