# 修复本体缺口三原因（T2115·development）

## 背景

T2107本体有形式无覆盖（缺NFS独立表达、密钥全量、门禁灰度）。病根三条（见`research-report.md`）：
原因1 AC不可判定词→修`pdca-acceptance-criterion`；原因2 Grill无覆盖问→修`grilling-methodology`；
原因3 门禁无覆盖语义→新增覆盖校验脚本。T2116/2117/2118为叶分解，随母票一次交付。

Grill round1（captured:true）：用户确认三件全做。

## 目标

三件修法全部落地且可验证：两处概念文档追加规范、新脚本正反例可跑、既有校验全绿。

## 范围

输入：`ontology/concept/pdca-acceptance-criterion.md`、`grilling-methodology.md`、
`scenario-research-first-gate.md`、`scripts/check-research-ontology-settlement.py`。
输出：两处文档修订 + `scripts/check-ontology-topic-coverage.py` + 自测证据。
不做：不动flow标准流程、不动既有门禁脚本逻辑、不碰他人在改文件。

## 验收标准

- [ ] AC-1 AC规范：`pdca-acceptance-criterion`新增章节映射规则（research类AC逐源章节编号、禁“完整/齐全”类词、坏好例子），`ontology-validate`通过
- [ ] AC-2 Grill必问：`grilling-methodology`新增覆盖必问轮（本体锚定+沉淀计划+章节覆盖清单），`ontology-validate`通过
- [ ] AC-3 覆盖脚本：新脚本对T2107本体跑出缺失3项（非零退出），补齐后通过（零退出）；自带`--help`可用
- [ ] AC-4 门禁引用：`scenario-research-first-gate`引用该脚本为Act推荐自检，`ontology-validate`通过
- [ ] AC-5 回归：`ontology-validate`全绿，`check-research-ontology-settlement --task-dir T2107`仍通过

## 关联本体节点

```
ontology:concept/pdca-acceptance-criterion
ontology:concept/grilling-methodology
ontology:concept/scenario-research-first-gate
ontology:concept/pdca-task
ontology:concept/pdca-evidence
```

## 拆分映射

- AC规范（T2116） -> ontology:concept/pdca-acceptance-criterion
- Grill必问（T2117） -> ontology:concept/grilling-methodology
- 覆盖脚本（T2118） -> ontology:concept/scenario-research-first-gate
